import pytest
import os
import sys
from decimal import Decimal
from datetime import datetime, timedelta
from typing import Dict, Any

# Ensure backend path is in sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from services.payment_system import (
    PaymentSystem,
    Subscription,
    Receipt,
    PaymentError,
    InsufficientFundsError,
    SubscriptionError
)

class TestSubscription:
    """Test suite for Subscription class."""

    def test_subscription_creation(self):
        """Test subscription initialization."""
        customer_id = "cust_123"
        plan_id = "plan_abc"

        subscription = Subscription(customer_id, plan_id)

        assert subscription.customer_id == customer_id
        assert subscription.plan_id == plan_id
        assert subscription.status == Subscription.STATUS_ACTIVE
        assert subscription.auto_renew is True
        assert subscription.metadata == {}

        # Verify expiration date logic
        # Allowing a small delta for execution time
        expected_expiration = datetime.utcnow() + timedelta(days=30)
        assert abs((subscription.expires_at - expected_expiration).total_seconds()) < 5

    def test_subscription_is_active(self):
        """Test active subscription check."""
        subscription = Subscription("cust_123", "plan_abc")
        assert subscription.is_active() is True

        # Manually expire the subscription
        subscription.expires_at = datetime.utcnow() - timedelta(days=1)
        assert subscription.is_active() is False
        assert subscription.is_expired() is True

    def test_subscription_renewal(self):
        """Test subscription renewal."""
        subscription = Subscription("cust_123", "plan_abc", duration_days=30)
        original_expiry = subscription.expires_at

        # Renew for another 30 days
        subscription.renew(duration_days=30)

        new_expiry = subscription.expires_at
        assert new_expiry > original_expiry
        assert subscription.status == Subscription.STATUS_ACTIVE

    def test_subscription_cancellation(self):
        """Test subscription cancellation."""
        subscription = Subscription("cust_123", "plan_abc")
        subscription.cancel()

        assert subscription.status == Subscription.STATUS_CANCELLED
        assert subscription.auto_renew is False
        assert subscription.is_active() is False

    def test_subscription_renewal_error(self):
        """Test renewal error for cancelled subscription."""
        subscription = Subscription("cust_123", "plan_abc")
        subscription.cancel()

        with pytest.raises(SubscriptionError, match="Cannot renew cancelled subscription"):
            subscription.renew()

    def test_subscription_to_dict(self):
        """Test subscription to dictionary conversion."""
        subscription = Subscription("cust_123", "plan_abc")
        data = subscription.to_dict()

        assert data['customer_id'] == "cust_123"
        assert data['plan_id'] == "plan_abc"
        assert data['status'] == Subscription.STATUS_ACTIVE
        assert 'subscription_id' in data
        assert 'created_at' in data
        assert 'expires_at' in data


class TestReceipt:
    """Test suite for Receipt class."""

    def test_receipt_creation(self):
        """Test receipt initialization."""
        transaction_id = "txn_123"
        amount = Decimal("29.99")
        customer_id = "cust_123"

        receipt = Receipt(transaction_id, amount, customer_id)

        assert receipt.transaction_id == transaction_id
        assert receipt.amount == amount
        assert receipt.customer_id == customer_id
        assert receipt.currency == "USD"
        assert isinstance(receipt.receipt_id, str)
        assert isinstance(receipt.timestamp, datetime)

    def test_receipt_to_dict(self):
        """Test receipt to dictionary conversion."""
        receipt = Receipt("txn_123", Decimal("10.00"), "cust_123")
        data = receipt.to_dict()

        assert data['transaction_id'] == "txn_123"
        assert data['amount'] == "10.00"
        assert data['customer_id'] == "cust_123"
        assert 'receipt_id' in data
        assert 'timestamp' in data


class TestPaymentSystem:
    """Test suite for PaymentSystem class."""

    def setup_method(self):
        """Setup method for tests."""
        self.payment_system = PaymentSystem()

    def test_initialization(self):
        """Test payment system initialization."""
        assert self.payment_system.subscriptions == {}
        assert self.payment_system.receipts == []
        assert self.payment_system._transaction_counter == 0

    def test_check_subscription_not_found(self):
        """Test checking non-existent subscription."""
        result = self.payment_system.check_subscription("non_existent_cust")
        assert result is None

    def test_check_subscription_found(self):
        """Test checking existing subscription."""
        # Manually inject a subscription for testing
        customer_id = "cust_123"
        subscription = Subscription(customer_id, "plan_abc")
        self.payment_system.subscriptions[subscription.subscription_id] = subscription

        result = self.payment_system.check_subscription(customer_id)
        assert result is not None
        assert result['customer_id'] == customer_id
        assert result['plan_id'] == "plan_abc"

    def test_charge_payment_success(self):
        """Test successful payment charge."""
        customer_id = "cust_123"
        amount = Decimal("50.00")

        result = self.payment_system.charge_payment(
            customer_id, amount, description="Test Payment"
        )

        assert result['success'] is True
        assert result['transaction_id'].startswith("txn_")
        assert result['amount'] == str(amount)
        assert len(self.payment_system.receipts) == 1
        assert self.payment_system.receipts[0].amount == amount

    def test_charge_payment_invalid_amount(self):
        """Test payment with invalid amount."""
        with pytest.raises(PaymentError, match="Payment amount must be positive"):
            self.payment_system.charge_payment("cust_123", Decimal("0"))

        with pytest.raises(PaymentError, match="Payment amount must be positive"):
            self.payment_system.charge_payment("cust_123", Decimal("-10.00"))

    def test_charge_payment_missing_customer(self):
        """Test payment with missing customer ID."""
        with pytest.raises(PaymentError, match="Customer ID is required"):
            self.payment_system.charge_payment("", Decimal("10.00"))

    def test_charge_payment_insufficient_funds(self):
        """Test payment with insufficient funds (simulated)."""
        # Test large amount simulation
        with pytest.raises(InsufficientFundsError, match="Payment declined - insufficient funds"):
            self.payment_system.charge_payment("cust_123", Decimal("1001.00"))

        # Test specific customer simulation
        with pytest.raises(InsufficientFundsError, match="Payment declined - insufficient funds"):
            self.payment_system.charge_payment("test_insufficient_funds", Decimal("10.00"))

    def test_charge_payment_receipt_storage(self):
        """Test that receipts are stored correctly."""
        customer_id = "cust_123"
        amount = Decimal("25.00")

        self.payment_system.charge_payment(customer_id, amount)

        assert len(self.payment_system.receipts) == 1
        receipt = self.payment_system.receipts[0]
        assert receipt.customer_id == customer_id
        assert receipt.amount == amount

    def test_generate_receipt_direct(self):
        """Test direct receipt generation."""
        receipt = self.payment_system.generate_receipt(
            "txn_manual", "cust_123", Decimal("15.00")
        )

        assert receipt.transaction_id == "txn_manual"
        assert receipt.amount == Decimal("15.00")
        assert len(self.payment_system.receipts) == 1
