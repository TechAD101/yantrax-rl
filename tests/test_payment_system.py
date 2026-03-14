import pytest
import os
import sys
from decimal import Decimal
from datetime import datetime, timedelta
from unittest.mock import patch

# Add backend to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from services.payment_system import (
    PaymentSystem, Subscription, Receipt,
    PaymentError, InsufficientFundsError, SubscriptionError
)

# --- Receipt Tests ---

def test_receipt_initialization():
    transaction_id = "txn_123"
    amount = Decimal("50.00")
    customer_id = "cust_1"
    description = "Test Payment"

    receipt = Receipt(transaction_id, amount, customer_id, description)

    assert receipt.transaction_id == transaction_id
    assert receipt.amount == amount
    assert receipt.customer_id == customer_id
    assert receipt.description == description
    assert receipt.currency == "USD"
    assert isinstance(receipt.receipt_id, str)
    assert isinstance(receipt.timestamp, datetime)

def test_receipt_to_dict():
    receipt = Receipt("txn_123", Decimal("50.00"), "cust_1", "Test", metadata={"key": "val"})
    d = receipt.to_dict()

    assert d['transaction_id'] == "txn_123"
    assert d['amount'] == "50.00"
    assert d['customer_id'] == "cust_1"
    assert d['description'] == "Test"
    assert d['metadata'] == {"key": "val"}
    assert 'receipt_id' in d
    assert 'timestamp' in d

def test_receipt_str():
    receipt = Receipt("txn_123", Decimal("50.00"), "cust_1", "Test")
    s = str(receipt)
    assert "Receipt" in s
    assert "USD 50.00" in s
    assert "Test" in s

# --- Subscription Tests ---

def test_subscription_initialization():
    sub = Subscription("cust_1", "premium_plan")
    assert sub.customer_id == "cust_1"
    assert sub.plan_id == "premium_plan"
    assert sub.status == Subscription.STATUS_ACTIVE
    assert sub.auto_renew is True
    assert sub.is_active() is True
    assert sub.is_expired() is False

def test_subscription_expiration():
    # Create a subscription that expired 1 day ago
    sub = Subscription("cust_1", "plan_1", duration_days=-1)
    assert sub.is_active() is False
    assert sub.is_expired() is True

def test_subscription_renew():
    sub = Subscription("cust_1", "plan_1", duration_days=1)
    sub.renew(duration_days=10)
    assert sub.status == Subscription.STATUS_ACTIVE
    # expires_at should be roughly 10 days from now
    expected_expiry = datetime.utcnow() + timedelta(days=10)
    assert (sub.expires_at - expected_expiry).total_seconds() < 5

def test_subscription_renew_cancelled_fails():
    sub = Subscription("cust_1", "plan_1")
    sub.cancel()
    with pytest.raises(SubscriptionError, match="Cannot renew cancelled subscription"):
        sub.renew()

def test_subscription_cancel():
    sub = Subscription("cust_1", "plan_1")
    sub.cancel()
    assert sub.status == Subscription.STATUS_CANCELLED
    assert sub.auto_renew is False
    # Cancellation doesn't necessarily mean it's not active if it hasn't expired yet
    # But wait, looking at is_active implementation:
    # return (self.status == self.STATUS_ACTIVE and datetime.utcnow() < self.expires_at)
    assert sub.is_active() is False

def test_subscription_to_dict():
    sub = Subscription("cust_1", "plan_1")
    d = sub.to_dict()
    assert d['customer_id'] == "cust_1"
    assert d['plan_id'] == "plan_1"
    assert d['status'] == Subscription.STATUS_ACTIVE
    assert d['is_active'] is True

# --- PaymentSystem Tests ---

@pytest.fixture
def payment_system():
    return PaymentSystem()

def test_check_subscription_empty(payment_system):
    assert payment_system.check_subscription("non_existent") is None

def test_check_subscription_found(payment_system):
    sub = Subscription("cust_123", "pro_plan")
    payment_system.subscriptions[sub.subscription_id] = sub

    result = payment_system.check_subscription("cust_123")
    assert result is not None
    assert result['customer_id'] == "cust_123"
    assert result['plan_id'] == "pro_plan"

def test_charge_payment_success(payment_system):
    amount = Decimal("29.99")
    customer_id = "cust_1"
    result = payment_system.charge_payment(customer_id, amount, "Monthly sub")

    assert result['success'] is True
    assert result['amount'] == "29.99"
    assert result['currency'] == "USD"
    assert 'transaction_id' in result
    assert 'receipt' in result
    assert len(payment_system.receipts) == 1

def test_charge_payment_invalid_amount(payment_system):
    with pytest.raises(PaymentError, match="Payment amount must be positive"):
        payment_system.charge_payment("cust_1", Decimal("-10.00"))

    with pytest.raises(PaymentError, match="Payment amount must be positive"):
        payment_system.charge_payment("cust_1", Decimal("0.00"))

def test_charge_payment_missing_customer(payment_system):
    with pytest.raises(PaymentError, match="Customer ID is required"):
        payment_system.charge_payment("", Decimal("10.00"))

def test_charge_payment_insufficient_funds(payment_system):
    with pytest.raises(InsufficientFundsError, match="Payment declined - insufficient funds"):
        payment_system.charge_payment("test_insufficient_funds", Decimal("10.00"))

def test_charge_payment_too_high_amount(payment_system):
    # Simulation fails for amounts > 1000
    with pytest.raises(InsufficientFundsError, match="Payment declined - insufficient funds"):
        payment_system.charge_payment("cust_1", Decimal("1000.01"))

def test_generate_receipt(payment_system):
    receipt = payment_system.generate_receipt("txn_999", "cust_1", Decimal("15.00"))
    assert receipt.transaction_id == "txn_999"
    assert receipt.amount == Decimal("15.00")
    assert len(payment_system.receipts) == 1
    assert payment_system.receipts[0] == receipt

def test_payment_system_unexpected_error(payment_system):
    # Mock _simulate_payment_processing to raise an unexpected Exception
    with patch.object(PaymentSystem, '_simulate_payment_processing', side_effect=Exception("Unexpected boom")):
        with pytest.raises(PaymentError, match="Payment processing failed: Unexpected boom"):
            payment_system.charge_payment("cust_1", Decimal("10.00"))

def test_check_subscription_unexpected_error(payment_system):
    # Mock to_dict to raise error
    sub = Subscription("cust_1", "plan_1")
    payment_system.subscriptions[sub.subscription_id] = sub

    with patch.object(Subscription, 'to_dict', side_effect=RuntimeError("Broken")):
        with pytest.raises(SubscriptionError, match="Failed to check subscription: Broken"):
            payment_system.check_subscription("cust_1")
