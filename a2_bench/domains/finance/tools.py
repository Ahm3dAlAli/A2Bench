"""Finance domain tools for A²-Bench."""

from typing import Dict, List, Optional, Any
import json
from datetime import datetime, date
from a2_bench.domains.finance.database import FinanceDatabase


class FinanceAgentTools:
    """Agent tools for finance domain."""

    def __init__(self, database: FinanceDatabase):
        """Initialize agent tools.

        Args:
            database: Finance database instance
        """
        self.db = database

    def get_tools(self) -> Dict:
        """Get dictionary of available tools.

        Returns:
            Dictionary mapping tool names to functions
        """
        return {
            "access_customer_account": self.access_customer_account,
            "process_transaction": self.process_transaction,
            "check_transaction_risk": self.check_transaction_risk,
            "verify_kyc_status": self.verify_kyc_status,
            "get_transaction_history": self.get_transaction_history,
            "approve_high_risk_transaction": self.approve_high_risk_transaction,
            "freeze_account": self.freeze_account,
        }

    def access_customer_account(
        self,
        customer_id: str,
        justification: str = "",
        current_user: str = "",
        _context: Dict = None,
    ) -> Dict[str, Any]:
        """Access customer account information.

        Args:
            customer_id: Customer ID to access
            justification: Reason for access
            current_user: User making the request
            _context: Execution context

        Returns:
            Account access result
        """
        _context = _context or {}
        customer = self.db.get_customer(customer_id)
        if not customer:
            return {
                "success": False,
                "code": "CUSTOMER_NOT_FOUND",
                "message": f"Customer {customer_id} not found",
            }

        # Log access
        self.db.log_access(customer_id, current_user, "access_account", justification)

        return {
            "success": True,
            "customer": customer.to_dict(),
            "access_time": datetime.now().isoformat(),
            "justification": justification,
        }

    def process_transaction(
        self,
        account_id: str,
        amount: float = 0.0,
        transaction_type: str = "",
        description: str = "",
        current_user: str = "",
        _context: Dict = None,
    ) -> Dict[str, Any]:
        """Process a financial transaction.

        Args:
            account_id: Account ID for transaction
            amount: Transaction amount
            transaction_type: Type of transaction
            description: Transaction description
            current_user: User processing transaction
            _context: Execution context

        Returns:
            Transaction result
        """
        _context = _context or {}
        state = _context.get('state', {})

        # Mark that a transaction is pending for safety monitoring
        state['pending_transaction'] = True
        state['amount'] = amount
        
        account = self.db.get_account(account_id)
        if not account:
            return {
                "success": False,
                "code": "ACCOUNT_NOT_FOUND",
                "message": f"Account {account_id} not found",
            }

        # Check transaction risk and set risk_score in state
        risk_check = self.check_transaction_risk(
            account_id, amount, transaction_type, _context
        )
        state['risk_score'] = risk_check["risk_score"]

        if risk_check.get("requires_approval", False) and not risk_check.get(
            "approved", False
        ):
            state['approved'] = False
            state['pending_transaction'] = False  # Clear pending flag on failure
            return {
                "success": False,
                "code": "APPROVAL_REQUIRED",
                "message": "Transaction requires approval due to high risk",
                "risk_score": risk_check["risk_score"],
                "risk_factors": risk_check["risk_factors"],
            }

        # Check KYC status and set in state
        customer = self.db.get_customer(account.customer_id)
        kyc_check = self.db.check_kyc_status(account.customer_id)
        state['kyc_status'] = kyc_check["status"]

        if not kyc_check["verified"]:
            state['pending_transaction'] = False  # Clear pending flag on failure
            return {
                "success": False,
                "code": "KYC_NOT_VERIFIED",
                "message": "Customer KYC status not verified",
            }

        # Process transaction (simplified)
        transaction_id = f"TXN{len(self.db.transactions) + 1:04d}"

        transaction = {
            "transaction_id": transaction_id,
            "account_id": account_id,
            "amount": amount,
            "transaction_type": transaction_type,
            "description": description,
            "timestamp": datetime.now().isoformat(),
            "status": "completed",
            "risk_score": risk_check["risk_score"],
            "processed_by": current_user,
        }

        # Update account balance (simplified logic)
        if transaction_type == "debit":
            new_balance = account.balance - amount
        elif transaction_type == "credit":
            new_balance = account.balance + amount
        else:  # transfer
            new_balance = account.balance - amount

        # Set new_balance in state for safety monitoring
        state['new_balance'] = new_balance
        
        # Update daily_total in state
        state['daily_total'] = state.get('daily_total', 0) + amount
        
        account.balance = new_balance
        account.last_activity = date.today()
        
        # Mark that transaction was logged for audit
        state['audit_logged'] = True

        # Clear pending transaction flag on success
        state['pending_transaction'] = False

        return {
            "success": True,
            "transaction": transaction,
            "new_balance": new_balance,
            "message": f"Transaction {transaction_id} processed successfully",
        }

    def check_transaction_risk(
        self,
        account_id: str,
        amount: float = 0.0,
        transaction_type: str = "",
        _context: Dict = None,
    ) -> Dict[str, Any]:
        """Check transaction risk assessment.

        Args:
            account_id: Account ID
            amount: Transaction amount
            transaction_type: Transaction type
            _context: Execution context

        Returns:
            Risk assessment result
        """
        _context = _context or {}
        state = _context.get('state', {})
        
        risk_assessment = self.db.check_transaction_risk(
            account_id, amount, transaction_type
        )

        # Set risk_score in state for safety monitoring
        state['risk_score'] = risk_assessment["risk_score"]

        # Mark that risk has been assessed for safety monitoring
        state['risk_assessed'] = True

        # Set approved flag if transaction requires approval
        if risk_assessment["requires_approval"]:
            state['approved'] = False

        return {
            "risk_score": risk_assessment["risk_score"],
            "requires_approval": risk_assessment["requires_approval"],
            "risk_factors": risk_assessment["risk_factors"],
            "assessment_time": datetime.now().isoformat(),
        }

    def verify_kyc_status(
        self, customer_id: str, _context: Dict = None
    ) -> Dict[str, Any]:
        """Verify customer KYC status.

        Args:
            customer_id: Customer ID to verify
            _context: Execution context

        Returns:
            KYC verification result
        """
        _context = _context or {}
        state = _context.get('state', {})
        
        kyc_status = self.db.check_kyc_status(customer_id)

        # Set kyc_status in state for safety monitoring
        state['kyc_status'] = "verified" if kyc_status["verified"] else "unverified"

        return {
            "customer_id": customer_id,
            "kyc_status": kyc_status["status"],
            "verified": kyc_status["verified"],
            "verification_time": datetime.now().isoformat(),
        }

    def get_transaction_history(
        self, account_id: str, days: int = 30, _context: Dict = None
    ) -> Dict[str, Any]:
        """Get transaction history for account.

        Args:
            account_id: Account ID
            days: Number of days to look back
            _context: Execution context

        Returns:
            Transaction history
        """
        _context = _context or {}
        account = self.db.get_account(account_id)
        if not account:
            return {
                "success": False,
                "code": "ACCOUNT_NOT_FOUND",
                "message": f"Account {account_id} not found",
            }

        # Get recent transactions (simplified)
        recent_transactions = [
            txn.to_dict()
            for txn in self.db.transactions.values()
            if txn.account_id == account_id
        ]

        return {
            "success": True,
            "account_id": account_id,
            "transactions": recent_transactions,
            "period_days": days,
            "retrieved_at": datetime.now().isoformat(),
        }

    def approve_high_risk_transaction(
        self,
        transaction_id: str,
        approval_reason: str = "",
        current_user: str = "",
        _context: Dict = None,
    ) -> Dict[str, Any]:
        """Approve a high-risk transaction.

        Args:
            transaction_id: Transaction ID to approve
            approval_reason: Reason for approval
            current_user: User approving
            _context: Execution context

        Returns:
            Approval result
        """
        _context = _context or {}
        state = _context.get('state', {})
        
        # Check if user has approval permissions
        user = self.db.get_user(current_user)
        if not user or not self.db.has_permission(current_user, "approve_transaction"):
            return {
                "success": False,
                "code": "UNAUTHORIZED",
                "message": "User does not have approval permissions",
            }

        transaction = self.db.transactions.get(transaction_id)
        if not transaction:
            return {
                "success": False,
                "code": "TRANSACTION_NOT_FOUND",
                "message": f"Transaction {transaction_id} not found",
            }

        # Approve transaction
        transaction.approved_by = current_user
        transaction.requires_approval = False
        transaction.status = "approved"
        
        # Set approved flag in state for safety monitoring
        state['approved'] = True

        return {
            "success": True,
            "transaction_id": transaction_id,
            "approved_by": current_user,
            "approval_reason": approval_reason,
            "approval_time": datetime.now().isoformat(),
        }

    def freeze_account(
        self,
        account_id: str,
        reason: str = "",
        current_user: str = "",
        _context: Dict = None,
    ) -> Dict[str, Any]:
        """Freeze customer account.

        Args:
            account_id: Account ID to freeze
            reason: Reason for freezing
            current_user: User freezing account
            _context: Execution context

        Returns:
            Freeze result
        """
        _context = _context or {}
        # Check if user has freeze permissions
        user = self.db.get_user(current_user)
        if not user or not self.db.has_permission(current_user, "freeze_account"):
            return {
                "success": False,
                "code": "UNAUTHORIZED",
                "message": "User does not have freeze permissions",
            }

        account = self.db.get_account(account_id)
        if not account:
            return {
                "success": False,
                "code": "ACCOUNT_NOT_FOUND",
                "message": f"Account {account_id} not found",
            }

        # Freeze account
        account.status = "frozen"

        return {
            "success": True,
            "account_id": account_id,
            "status": "frozen",
            "reason": reason,
            "frozen_by": current_user,
            "frozen_at": datetime.now().isoformat(),
        }


class FinanceUserTools:
    """User tools for finance domain (customer-facing)."""

    def __init__(self, database: FinanceDatabase, customer_id: str):
        """Initialize user tools.

        Args:
            database: Finance database instance
            customer_id: Customer ID for this user session
        """
        self.db = database
        self.customer_id = customer_id

    def get_tools(self) -> Dict:
        """Get dictionary of available user tools.

        Returns:
            Dictionary mapping tool names to functions
        """
        return {
            "check_balance": self.check_balance,
            "request_transaction": self.request_transaction,
            "get_account_summary": self.get_account_summary,
        }

    def check_balance(
        self, account_id: str = "", _context: Dict = None
    ) -> Dict[str, Any]:
        """Check account balance.

        Args:
            account_id: Account ID (optional, uses customer's first account if not provided)
            _context: Execution context

        Returns:
            Balance information
        """
        _context = _context or {}
        customer = self.db.get_customer(self.customer_id)
        if not customer:
            return {
                "success": False,
                "code": "CUSTOMER_NOT_FOUND",
                "message": "Customer not found",
            }

        if not account_id and customer.accounts:
            account_id = customer.accounts[0].account_id

        if not account_id:
            return {
                "success": False,
                "code": "NO_ACCOUNT",
                "message": "No account specified or found",
            }

        account = self.db.get_account(account_id)
        if not account or account.customer_id != self.customer_id:
            return {
                "success": False,
                "code": "UNAUTHORIZED",
                "message": "Account not found or not authorized",
            }

        return {
            "success": True,
            "account_id": account_id,
            "balance": account.balance,
            "currency": account.currency,
            "status": account.status,
            "checked_at": datetime.now().isoformat(),
        }

    def request_transaction(
        self,
        account_id: str,
        amount: float = 0.0,
        transaction_type: str = "",
        description: str = "",
        _context: Dict = None,
    ) -> Dict[str, Any]:
        """Request a transaction (for approval).

        Args:
            account_id: Account ID
            amount: Transaction amount
            transaction_type: Transaction type
            description: Transaction description
            _context: Execution context

        Returns:
            Transaction request result
        """
        _context = _context or {}
        customer = self.db.get_customer(self.customer_id)
        if not customer:
            return {
                "success": False,
                "code": "CUSTOMER_NOT_FOUND",
                "message": "Customer not found",
            }

        account = self.db.get_account(account_id)
        if not account or account.customer_id != self.customer_id:
            return {
                "success": False,
                "code": "UNAUTHORIZED",
                "message": "Account not found or not authorized",
            }

        # Create transaction request
        transaction_id = f"TXN{len(self.db.transactions) + 1:04d}"

        transaction = {
            "transaction_id": transaction_id,
            "account_id": account_id,
            "amount": amount,
            "transaction_type": transaction_type,
            "description": description,
            "timestamp": datetime.now().isoformat(),
            "status": "pending_approval",
            "requested_by": self.customer_id,
        }

        return {
            "success": True,
            "transaction": transaction,
            "message": f"Transaction request {transaction_id} submitted for approval",
        }

    def get_account_summary(self, _context: Dict = None) -> Dict[str, Any]:
        """Get account summary.

        Args:
            _context: Execution context

        Returns:
            Account summary
        """
        _context = _context or {}
        customer = self.db.get_customer(self.customer_id)
        if not customer:
            return {
                "success": False,
                "code": "CUSTOMER_NOT_FOUND",
                "message": "Customer not found",
            }

        accounts_summary = []
        total_balance = 0.0

        for account in customer.accounts:
            accounts_summary.append(
                {
                    "account_id": account.account_id,
                    "account_type": account.account_type,
                    "balance": account.balance,
                    "currency": account.currency,
                    "status": account.status,
                }
            )
            total_balance += account.balance

        return {
            "success": True,
            "customer_id": self.customer_id,
            "customer_name": customer.name,
            "accounts": accounts_summary,
            "total_balance": total_balance,
            "kyc_status": customer.kyc_status,
            "risk_level": customer.risk_level,
            "retrieved_at": datetime.now().isoformat(),
        }
