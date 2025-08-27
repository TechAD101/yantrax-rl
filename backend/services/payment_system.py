"""
Payment System Module

A minimal but extensible payment processing system supporting subscription checks,
charge processing, and receipt generation.

Author: YantraX-RL Backend Team
Created: August 28, 2025
"""

from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from decimal import Decimal
import uuid
import logging


class PaymentError(Exception):
    """Base exception for payment-related errors."""
    pass


class InsufficientFundsError(PaymentError):
    """Raised when payment fails due to insufficient funds."""
    pass


class SubscriptionError(PaymentError):
    """Raised when subscription-related operations fail."""
    pass


class Receipt:
    """
    Represents a payment receipt with transaction details.
    
    Attributes:
        receipt_id (str): Unique receipt identifier
        transaction_id (str): Associated transaction ID
        amount (Decimal): Payment amount
        currency (str): Currency code (default: USD)
        timestamp (datetime): Receipt generation timestamp
        customer_id (str): Customer identifier
        description (str): Payment description
        metadata (Dict[str, Any]): Additional receipt metadata
    """
    
    def __init__(self, transaction_id: str, amount: Decimal, customer_id: str,
                 description: str = "", currency: str = "USD",
                 metadata: Optional[Dict[str, Any]] = None):
        self.receipt_id = str(uuid.uuid4())
        self.transaction_id = transaction_id
        self.amount = amount
        self.currency = currency
        self.timestamp = datetime.utcnow()
        self.customer_id = customer_id
        self.description = description
        self.metadata = metadata or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert receipt to dictionary format."""
        return {
            'receipt_id': self.receipt_id,
            'transaction_id': self.transaction_id,
            'amount': str(self.amount),
            'currency': self.currency,
            'timestamp': self.timestamp.isoformat(),
            'customer_id': self.customer_id,
            'description': self.description,
            'metadata': self.metadata
        }
    
    def __str__(self) -> str:
        return f"Receipt {self.receipt_id}: {self.currency} {self.amount} - {self.description}"


class Subscription:
    """
    Represents a customer subscription with status and billing information.
    
    Attributes:
        subscription_id (str): Unique subscription identifier
        customer_id (str): Associated customer ID
        plan_id (str): Subscription plan identifier
        status (str): Current subscription status
        created_at (datetime): Subscription creation timestamp
        expires_at (datetime): Subscription expiration timestamp
        auto_renew (bool): Whether subscription auto-renews
        metadata (Dict[str, Any]): Additional subscription metadata
    """
    
    STATUS_ACTIVE = "active"
    STATUS_EXPIRED = "expired"
    STATUS_CANCELLED = "cancelled"
    STATUS_SUSPENDED = "suspended"
    
    def __init__(self, customer_id: str, plan_id: str, duration_days: int = 30,
                 auto_renew: bool = True, metadata: Optional[Dict[str, Any]] = None):
        self.subscription_id = str(uuid.uuid4())
        self.customer_id = customer_id
        self.plan_id = plan_id
        self.status = self.STATUS_ACTIVE
        self.created_at = datetime.utcnow()
        self.expires_at = self.created_at + timedelta(days=duration_days)
        self.auto_renew = auto_renew
        self.metadata = metadata or {}
    
    def is_active(self) -> bool:
        """Check if subscription is currently active."""
        return (self.status == self.STATUS_ACTIVE and 
                datetime.utcnow() < self.expires_at)
    
    def is_expired(self) -> bool:
        """Check if subscription has expired."""
        return datetime.utcnow() >= self.expires_at
    
    def renew(self, duration_days: int = 30) -> None:
        """Renew subscription for specified duration."""
        if self.status == self.STATUS_CANCELLED:
            raise SubscriptionError("Cannot renew cancelled subscription")
        
        self.expires_at = datetime.utcnow() + timedelta(days=duration_days)
        self.status = self.STATUS_ACTIVE
    
    def cancel(self) -> None:
        """Cancel subscription."""
        self.status = self.STATUS_CANCELLED
        self.auto_renew = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert subscription to dictionary format."""
        return {
            'subscription_id': self.subscription_id,
            'customer_id': self.customer_id,
            'plan_id': self.plan_id,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'expires_at': self.expires_at.isoformat(),
            'auto_renew': self.auto_renew,
            'is_active': self.is_active(),
            'metadata': self.metadata
        }


class PaymentSystem:
    """
    Main payment system class handling charges, subscriptions, and receipts.
    
    This class provides a minimal but extensible foundation for payment processing,
    including subscription management, payment charging, and receipt generation.
    """
    
    def __init__(self):
        """Initialize the payment system."""
        self.logger = logging.getLogger(__name__)
        self.subscriptions: Dict[str, Subscription] = {}
        self.receipts: List[Receipt] = []
        self._transaction_counter = 0
    
    def check_subscription(self, customer_id: str) -> Optional[Dict[str, Any]]:
        """
        Check customer's subscription status.
        
        Args:
            customer_id (str): Unique customer identifier
        
        Returns:
            Optional[Dict[str, Any]]: Subscription details if found, None otherwise
        
        Example:
            >>> payment_system = PaymentSystem()
            >>> status = payment_system.check_subscription("customer_123")
            >>> print(status['is_active'] if status else "No subscription")
        """
        try:
            for subscription in self.subscriptions.values():
                if subscription.customer_id == customer_id:
                    self.logger.info(f"Subscription found for customer {customer_id}")
                    return subscription.to_dict()
            
            self.logger.info(f"No subscription found for customer {customer_id}")
            return None
            
        except Exception as e:
            self.logger.error(f"Error checking subscription for {customer_id}: {str(e)}")
            raise SubscriptionError(f"Failed to check subscription: {str(e)}")
    
    def charge_payment(self, customer_id: str, amount: Decimal, 
                      description: str = "", currency: str = "USD",
                      metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Process a payment charge for a customer.
        
        Args:
            customer_id (str): Customer identifier
            amount (Decimal): Amount to charge
            description (str, optional): Payment description
            currency (str, optional): Currency code (default: USD)
            metadata (Dict[str, Any], optional): Additional payment metadata
        
        Returns:
            Dict[str, Any]: Payment result with transaction details
        
        Raises:
            PaymentError: If payment processing fails
            InsufficientFundsError: If payment fails due to insufficient funds
        
        Example:
            >>> from decimal import Decimal
            >>> payment_system = PaymentSystem()
            >>> result = payment_system.charge_payment(
            ...     "customer_123", 
            ...     Decimal("29.99"), 
            ...     "Monthly subscription"
            ... )
            >>> print(f"Payment successful: {result['success']}")
        """
        try:
            # Validate input
            if amount <= 0:
                raise PaymentError("Payment amount must be positive")
            
            if not customer_id:
                raise PaymentError("Customer ID is required")
            
            # Generate transaction ID
            self._transaction_counter += 1
            transaction_id = f"txn_{datetime.utcnow().strftime('%Y%m%d')}_{self._transaction_counter:06d}"
            
            # Simulate payment processing
            success = self._simulate_payment_processing(amount, customer_id)
            
            if not success:
                raise InsufficientFundsError("Payment declined - insufficient funds")
            
            # Generate receipt
            receipt = self.generate_receipt(
                transaction_id=transaction_id,
                customer_id=customer_id,
                amount=amount,
                description=description,
                currency=currency,
                metadata=metadata
            )
            
            self.logger.info(f"Payment processed successfully: {transaction_id}")
            
            return {
                'success': True,
                'transaction_id': transaction_id,
                'amount': str(amount),
                'currency': currency,
                'receipt': receipt.to_dict(),
                'processed_at': datetime.utcnow().isoformat()
            }
            
        except (PaymentError, InsufficientFundsError):
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error processing payment: {str(e)}")
            raise PaymentError(f"Payment processing failed: {str(e)}")
    
    def generate_receipt(self, transaction_id: str, customer_id: str, 
                        amount: Decimal, description: str = "",
                        currency: str = "USD", 
                        metadata: Optional[Dict[str, Any]] = None) -> Receipt:
        """
        Generate a payment receipt.
        
        Args:
            transaction_id (str): Transaction identifier
            customer_id (str): Customer identifier
            amount (Decimal): Payment amount
            description (str, optional): Payment description
            currency (str, optional): Currency code
            metadata (Dict[str, Any], optional): Additional receipt metadata
        
        Returns:
            Receipt: Generated receipt object
        
        Example:
            >>> from decimal import Decimal
            >>> payment_system = PaymentSystem()
            >>> receipt = payment_system.generate_receipt(
            ...     "txn_12345", "customer_123", Decimal("29.99")
            ... )
            >>> print(f"Receipt ID: {receipt.receipt_id}")
        """
        try:
            receipt = Receipt(
                transaction_id=transaction_id,
                amount=amount,
                customer_id=customer_id,
                description=description,
                currency=currency,
                metadata=metadata
            )
            
            # Store receipt for record keeping
            self.receipts.append(receipt)
            
            self.logger.info(f"Receipt generated: {receipt.receipt_id}")
            return receipt
            
        except Exception as e:
            self.logger.error(f"Error generating receipt: {str(e)}")
            raise PaymentError(f"Receipt generation failed: {str(e)}")
    
    def _simulate_payment_processing(self, amount: Decimal, customer_id: str) -> bool:
        """
        Simulate payment processing logic.
        
        In a real implementation, this would integrate with payment providers
        like Stripe, PayPal, or other payment gateways.
        
        Args:
            amount (Decimal): Payment amount
            customer_id (str): Customer identifier
        
        Returns:
            bool: Whether payment was successful
        """
        # Simple simulation: fail payments over $1000 or for test customer
        if amount > Decimal('1000.00'):
            return False
        
        if customer_id == 'test_insufficient_funds':
            return False
        
        return True
