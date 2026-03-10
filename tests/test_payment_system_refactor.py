import pytest
from decimal import Decimal
from backend.services.payment_system import PaymentSystem, Receipt, ReceiptRequest, PaymentError, InsufficientFundsError

def test_payment_system_charge_and_receipt():
    ps = PaymentSystem()
    customer_id = "cust_123"
    amount = Decimal("50.00")
    description = "Test payment"

    result = ps.charge_payment(customer_id, amount, description)

    assert result['success'] is True
    assert result['amount'] == "50.00"
    assert 'transaction_id' in result
    assert 'receipt' in result
    assert result['receipt']['customer_id'] == customer_id
    assert result['receipt']['description'] == description

def test_generate_receipt_directly():
    ps = PaymentSystem()
    transaction_id = "txn_test"
    customer_id = "cust_test"
    amount = Decimal("25.00")

    request = ReceiptRequest(
        transaction_id=transaction_id,
        customer_id=customer_id,
        amount=amount,
        description="Direct receipt",
        currency="EUR"
    )

    receipt = ps.generate_receipt(request)

    assert isinstance(receipt, Receipt)
    assert receipt.transaction_id == transaction_id
    assert receipt.customer_id == customer_id
    assert receipt.amount == amount
    assert receipt.description == "Direct receipt"
    assert receipt.currency == "EUR"
    assert receipt in ps.receipts

def test_charge_payment_invalid_amount():
    ps = PaymentSystem()
    with pytest.raises(PaymentError, match="Payment amount must be positive"):
        ps.charge_payment("cust_123", Decimal("-10.00"))

def test_charge_payment_insufficient_funds():
    ps = PaymentSystem()
    with pytest.raises(InsufficientFundsError):
        ps.charge_payment("test_insufficient_funds", Decimal("50.00"))
