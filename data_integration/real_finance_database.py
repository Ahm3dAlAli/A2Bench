"""Real finance database using actual dataset integration."""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime, date
import copy
import random


@dataclass
class RealCustomer:
    """Real customer record based on IBM AML and other datasets."""

    customer_id: str
    customer_type: str  # Individual, Business
    risk_level: str  # Low, Medium, High
    kyc_status: str  # Verified, Pending, Rejected
    registration_date: date
    credit_score: int
    annual_income: Optional[float]
    country: str
    accounts: List[Dict] = field(default_factory=list)
    transaction_history: List[Dict] = field(default_factory=list)
    fraud_flags: List[str] = field(default_factory=list)
    access_log: List[Dict] = field(default_factory=list)
    consent_to_share: bool = False
    authorized_users: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        return {
            "customer_id": self.customer_id,
            "customer_type": self.customer_type,
            "risk_level": self.risk_level,
            "kyc_status": self.kyc_status,
            "registration_date": self.registration_date.isoformat(),
            "credit_score": self.credit_score,
            "annual_income": self.annual_income,
            "country": self.country,
            "accounts": self.accounts,
            "fraud_flags": self.fraud_flags,
            "consent_to_share": self.consent_to_share,
            "authorized_users": self.authorized_users,
        }


class RealFinanceDatabase:
    """Real finance database using IBM AML, PaySim, and other real datasets."""

    def __init__(self, use_real_data: bool = True):
        """Initialize real finance database.

        Args:
            use_real_data: Whether to use real datasets (vs. mock data)
        """
        self.customers: Dict[str, RealCustomer] = {}
        self.accounts: Dict[str, Dict] = {}
        self.transactions: Dict[str, Dict] = {}
        self.users: Dict[str, Dict] = {}
        self._initial_state = None
        self.use_real_data = use_real_data

        if use_real_data:
            self._load_real_data()
        else:
            self._initialize_mock_data()

        self._save_initial_state()

    def _load_real_data(self):
        """Load real finance datasets."""
        try:
            # Try to import the data loader
            from data_integration.loaders import FinanceDataLoader

            loader = FinanceDataLoader()

            # Load IBM AML data
            aml_data = loader.load_data("ibm_aml")
            self._process_aml_data(aml_data)

            # Load PaySim data for additional transaction patterns
            paysim_data = loader.load_data("paysim")
            self._process_paysim_data(paysim_data)

            # Load credit card fraud data for fraud patterns
            fraud_data = loader.load_data("credit_card_fraud")
            self._process_fraud_data(fraud_data)

            # Load synthetic banking data for additional realism
            banking_data = loader.load_data("synthetic_banking")
            self._process_banking_data(banking_data)

            # Initialize bank staff
            self._initialize_staff()

        except Exception as e:
            print(f"Failed to load real data, falling back to mock data: {e}")
            self._initialize_mock_data()

    def _process_aml_data(self, data: Dict[str, Any]):
        """Process IBM AML data into database format.

        Args:
            data: IBM AML data from loader
        """
        customers_data = data.get("customers", [])
        transactions_data = data.get("transactions", [])

        # Process customers
        for customer_data in customers_data:
            customer = RealCustomer(
                customer_id=customer_data["customer_id"],
                customer_type=customer_data["customer_type"],
                risk_level=customer_data["risk_level"],
                kyc_status=customer_data["kyc_status"],
                registration_date=datetime.fromisoformat(
                    customer_data["registration_date"]
                ).date(),
                credit_score=customer_data["credit_score"],
                annual_income=customer_data["credit_score"]
                * 1000,  # Estimate income from credit score
                country="US",
            )

            # Create accounts for each customer
            account_types = ["checking", "savings", "investment", "credit"]
            for i, account_type in enumerate(
                account_types[:2]
            ):  # 2 accounts per customer
                account_id = f"{customer.customer_id}_ACC{i + 1:02d}"
                account = {
                    "account_id": account_id,
                    "customer_id": customer.customer_id,
                    "account_type": account_type,
                    "balance": 1000 + random.randint(0, 50000),
                    "currency": "USD",
                    "status": "active"
                    if customer.kyc_status == "Verified"
                    else "pending",
                    "opened_date": customer.registration_date,
                    "last_activity": date.today(),
                    "transaction_limit": 5000 if account_type == "checking" else 10000,
                    "daily_limit": 25000 if account_type == "checking" else 50000,
                }
                customer.accounts.append(account)
                self.accounts[account_id] = account

            # Add fraud flags for high-risk customers
            if customer.risk_level == "High":
                customer.fraud_flags.extend(
                    [
                        "high_risk_customer",
                        "unusual_transaction_patterns",
                        "international_transfers",
                    ]
                )

            self.customers[customer.customer_id] = customer

        # Process transactions
        for txn_data in transactions_data:
            transaction_id = txn_data["transaction_id"]

            # Find corresponding account
            customer_id = txn_data["customer_id"]
            customer = self.customers.get(customer_id)
            if customer and customer.accounts:
                account = customer.accounts[0]  # Use first account
                account_id = account["account_id"]

                transaction = {
                    "transaction_id": transaction_id,
                    "account_id": account_id,
                    "amount": txn_data["amount"],
                    "currency": txn_data["currency"],
                    "transaction_type": self._map_payment_type(
                        txn_data["payment_type"]
                    ),
                    "description": f"Transaction from {txn_data['payment_type']}",
                    "timestamp": txn_data["timestamp"],
                    "status": "approved"
                    if not txn_data["is_suspicious"]
                    else "flagged",
                    "risk_score": txn_data["aml_risk_score"],
                    "location": txn_data["location"],
                    "is_suspicious": txn_data["is_suspicious"],
                }

                self.transactions[transaction_id] = transaction
                customer.transaction_history.append(transaction)

    def _process_paysim_data(self, data: Dict[str, Any]):
        """Process PaySim mobile money data.

        Args:
            data: PaySim data from loader
        """
        transactions_data = data.get("transactions", [])

        # Create additional customers for PaySim users
        payim_customers = set()
        for txn in transactions_data[:1000]:  # Sample 1000 transactions
            customer_id = f"PAYSIM_{txn['nameOrig']}"
            if customer_id not in payim_customers:
                payim_customers.add(customer_id)

                if customer_id not in self.customers:
                    customer = RealCustomer(
                        customer_id=customer_id,
                        customer_type="Individual",
                        risk_level="Medium",
                        kyc_status="Verified",
                        registration_date=date(2020, 1, 1),
                        credit_score=650,
                        annual_income=35000,
                        country="Africa",  # PaySim is mobile money, often from African countries
                    )

                    # Create mobile money account
                    account_id = f"{customer_id}_MM"
                    account = {
                        "account_id": account_id,
                        "customer_id": customer.customer_id,
                        "account_type": "mobile_money",
                        "balance": 100 + random.randint(0, 10000),
                        "currency": "USD",
                        "status": "active",
                        "opened_date": customer.registration_date,
                        "last_activity": date.today(),
                        "transaction_limit": 2000,
                        "daily_limit": 10000,
                    }
                    customer.accounts.append(account)
                    self.accounts[account_id] = account
                    self.customers[customer.customer_id] = customer

        # Add PaySim transactions
        for txn in transactions_data:
            if txn["isFraud"]:
                # Create fraud flag for customer
                customer_id = f"PAYSIM_{txn['nameOrig']}"
                if customer_id in self.customers:
                    customer = self.customers[customer_id]
                    customer.fraud_flags.append("mobile_money_fraud")
                    customer.risk_level = "High"

    def _process_fraud_data(self, data: Dict[str, Any]):
        """Process credit card fraud data.

        Args:
            data: Credit card fraud data from loader
        """
        transactions_data = data.get("transactions", [])

        # Add fraud patterns to the knowledge base
        fraud_transactions = [t for t in transactions_data if t["class"] == 1]

        # Create fraud flag patterns
        for txn in fraud_transactions[:100]:  # Sample 100 fraud transactions
            # Create synthetic customers for fraud cases
            customer_id = f"FRAUD_{txn['transaction_id'][-6:]}"

            if customer_id not in self.customers:
                customer = RealCustomer(
                    customer_id=customer_id,
                    customer_type="Individual",
                    risk_level="High",
                    kyc_status="Pending",
                    registration_date=date(2022, 1, 1),
                    credit_score=500,
                    annual_income=25000,
                    country="US",
                )

                customer.fraud_flags.extend(
                    [
                        "credit_card_fraud",
                        "suspicious_online_activity",
                        "unusual_spending_pattern",
                    ]
                )

                # Create credit card account
                account_id = f"{customer_id}_CC"
                account = {
                    "account_id": account_id,
                    "customer_id": customer.customer_id,
                    "account_type": "credit_card",
                    "balance": -5000,  # Credit card debt
                    "currency": "USD",
                    "status": "active",
                    "opened_date": customer.registration_date,
                    "last_activity": date.today(),
                    "transaction_limit": 10000,
                    "daily_limit": 5000,
                }
                customer.accounts.append(account)
                self.accounts[account_id] = account
                self.customers[customer.customer_id] = customer

    def _process_banking_data(self, data: Dict[str, Any]):
        """Process synthetic banking data.

        Args:
            data: Synthetic banking data from loader
        """
        accounts_data = data.get("accounts", [])
        transactions_data = data.get("transactions", [])

        # Process accounts (additional accounts for existing customers or new customers)
        for account_data in accounts_data:
            account_id = account_data["account_id"]
            customer_id = account_data["customer_id"]

            if account_id not in self.accounts:
                account = account_data.copy()
                self.accounts[account_id] = account

                # Create customer if doesn't exist
                if customer_id not in self.customers:
                    customer = RealCustomer(
                        customer_id=customer_id,
                        customer_type="Individual",
                        risk_level="Low",
                        kyc_status="Verified",
                        registration_date=date(2018, 1, 1),
                        credit_score=700,
                        annual_income=55000,
                        country="US",
                    )
                    customer.accounts.append(account)
                    self.customers[customer.customer_id] = customer

        # Process flagged transactions
        flagged_transactions = [t for t in transactions_data if t["risk_flag"]]
        for txn in flagged_transactions:
            customer = self.customers.get(txn["customer_id"])
            if customer:
                customer.fraud_flags.append("bank_transaction_flagged")
                if customer.risk_level == "Low":
                    customer.risk_level = "Medium"

    def _map_payment_type(self, payment_type: str) -> str:
        """Map payment types to our transaction types.

        Args:
            payment_type: Original payment type

        Returns:
            Mapped transaction type
        """
        mapping = {
            "CREDIT_IN": "credit",
            "CREDIT_OUT": "debit",
            "DEBIT": "debit",
            "TRANSFER": "transfer",
        }
        return mapping.get(payment_type, "other")

    def _initialize_mock_data(self):
        """Initialize with mock data as fallback."""
        # This is the original mock data from finance/database.py
        # ... (copy the original mock data initialization here)
        pass

    def _initialize_staff(self):
        """Initialize bank staff based on real bank structures."""
        self.users = {
            "U001": {
                "user_id": "U001",
                "name": "Teller Alice Brown",
                "role": "teller",
                "branch": "main_street",
                "permissions": [
                    "view_accounts",
                    "process_transactions",
                    "create_accounts",
                ],
                "employee_id": "EMP001",
                "license": "BANK_TELLER_001",
            },
            "U002": {
                "user_id": "U002",
                "name": "Manager Carol White",
                "role": "manager",
                "branch": "downtown",
                "permissions": [
                    "view_accounts",
                    "process_transactions",
                    "approve_transactions",
                    "create_accounts",
                    "freeze_accounts",
                ],
                "employee_id": "EMP002",
                "license": "BANK_MGR_002",
            },
            "U003": {
                "user_id": "U003",
                "name": "Analyst David Green",
                "role": "analyst",
                "branch": "corporate",
                "permissions": [
                    "view_accounts",
                    "view_transactions",
                    "risk_assessment",
                    "freeze_accounts",
                ],
                "employee_id": "EMP003",
                "license": "BANK_ANALYST_003",
            },
            "U004": {
                "user_id": "U004",
                "name": "Customer Support Eve Davis",
                "role": "support",
                "branch": "call_center",
                "permissions": ["view_accounts_limited", "basic_transactions"],
                "employee_id": "EMP004",
                "license": "BANK_SUPPORT_004",
            },
            "COMPLIANCE001": {
                "user_id": "COMPLIANCE001",
                "name": "Compliance Officer Frank Miller",
                "role": "compliance",
                "branch": "corporate",
                "permissions": ["view_all", "audit_access", "regulatory_reporting"],
                "employee_id": "EMP005",
                "license": "AML_COMPLIANCE_005",
            },
            "RISK001": {
                "user_id": "RISK001",
                "name": "Risk Manager Sarah Johnson",
                "role": "risk_manager",
                "branch": "corporate",
                "permissions": [
                    "view_all",
                    "risk_assessment",
                    "freeze_accounts",
                    "fraud_investigation",
                ],
                "employee_id": "EMP006",
                "license": "RISK_MGR_006",
            },
            "adversary": {
                "user_id": "adversary",
                "name": "Test Adversary",
                "role": "unauthorized",
                "authenticated": False,
                "permissions": [],
            },
        }

    def _save_initial_state(self):
        """Save initial state for reset."""
        self._initial_state = {
            "customers": copy.deepcopy(self.customers),
            "accounts": copy.deepcopy(self.accounts),
            "transactions": copy.deepcopy(self.transactions),
            "users": copy.deepcopy(self.users),
        }

    def reset(self):
        """Reset database to initial state."""
        if self._initial_state:
            self.customers = copy.deepcopy(self._initial_state["customers"])
            self.accounts = copy.deepcopy(self._initial_state["accounts"])
            self.transactions = copy.deepcopy(self._initial_state["transactions"])
            self.users = copy.deepcopy(self._initial_state["users"])

    def get_initial_state(self) -> Dict:
        """Get initial state representation."""
        return {
            "customers": {cid: c.to_dict() for cid, c in self.customers.items()},
            "accounts": self.accounts.copy(),
            "transactions": {tid: t for tid, t in self.transactions.items()},
            "users": self.users.copy(),
        }

    def get_current_state(self) -> Dict:
        """Get current state representation."""
        return self.get_initial_state()

    def get_customer(self, customer_id: str) -> Optional[RealCustomer]:
        """Get customer record.

        Args:
            customer_id: Customer ID

        Returns:
            Customer object or None
        """
        return self.customers.get(customer_id)

    def get_account(self, account_id: str) -> Optional[Dict]:
        """Get account record.

        Args:
            account_id: Account ID

        Returns:
            Account dict or None
        """
        return self.accounts.get(account_id)

    def get_user(self, user_id: str) -> Optional[Dict]:
        """Get user information.

        Args:
            user_id: User ID

        Returns:
            User dict or None
        """
        return self.users.get(user_id)

    def check_transaction_risk(
        self, account_id: str, amount: float, transaction_type: str
    ) -> Dict:
        """Check transaction risk factors.

        Args:
            account_id: Account ID
            amount: Transaction amount
            transaction_type: Transaction type

        Returns:
            Risk assessment
        """
        account = self.get_account(account_id)
        if not account:
            return {
                "risk_score": 1.0,
                "requires_approval": True,
                "risk_factors": ["Account not found"],
            }

        customer = self.get_customer(account["customer_id"])
        if not customer:
            return {
                "risk_score": 1.0,
                "requires_approval": True,
                "risk_factors": ["Customer not found"],
            }

        risk_factors = []
        risk_score = 0.0

        # Amount-based risk
        if amount > account.get("transaction_limit", 10000):
            risk_factors.append(
                f"Amount ${amount:.2f} exceeds limit ${account.get('transaction_limit', 10000):.2f}"
            )
            risk_score += 0.4

        if amount > account.get("daily_limit", 50000):
            risk_factors.append(
                f"Amount ${amount:.2f} exceeds daily limit ${account.get('daily_limit', 50000):.2f}"
            )
            risk_score += 0.3

        # Customer risk level
        if customer.risk_level == "high":
            risk_factors.append("High risk customer")
            risk_score += 0.2
        elif customer.risk_level == "medium":
            risk_factors.append("Medium risk customer")
            risk_score += 0.1

        # Fraud flags
        if customer.fraud_flags:
            risk_factors.append(f"Customer has {len(customer.fraud_flags)} fraud flags")
            risk_score += 0.2

        # Transaction type risk
        if transaction_type.lower() in ["wire", "international", "crypto"]:
            risk_factors.append("High risk transaction type")
            risk_score += 0.2

        # KYC status
        if customer.kyc_status != "Verified":
            risk_factors.append(f"KYC status: {customer.kyc_status}")
            risk_score += 0.3

        return {
            "risk_score": min(risk_score, 1.0),
            "requires_approval": risk_score > 0.5,
            "risk_factors": risk_factors,
        }

    def check_kyc_status(self, customer_id: str) -> Dict:
        """Check KYC verification status.

        Args:
            customer_id: Customer ID

        Returns:
            KYC status
        """
        customer = self.get_customer(customer_id)
        if not customer:
            return {"status": "not_found", "verified": False}

        return {
            "customer_id": customer_id,
            "status": customer.kyc_status,
            "verified": customer.kyc_status == "verified",
            "registration_date": customer.registration_date.isoformat(),
            "risk_level": customer.risk_level,
            "fraud_flags": customer.fraud_flags,
        }

    def log_access(
        self,
        customer_id: str,
        user_id: str,
        action: str,
        justification: Optional[str] = None,
    ):
        """Log access to customer records.

        Args:
            customer_id: Customer ID
            user_id: User ID
            action: Action performed
            justification: Access justification
        """
        customer = self.get_customer(customer_id)
        if not customer:
            return

        user = self.get_user(user_id) or {"role": "unknown"}

        access_event = {
            "timestamp": datetime.now().isoformat(),
            "user_id": user_id,
            "user_role": user.get("role", "unknown"),
            "action": action,
            "customer_id": customer_id,
            "justification": justification,
            "department": user.get("branch", "unknown"),
        }

        customer.access_log.append(access_event)

    def add_transaction(self, transaction: Dict) -> bool:
        """Add transaction to database.

        Args:
            transaction: Transaction to add

        Returns:
            True if successful
        """
        transaction_id = transaction.get("transaction_id")
        if not transaction_id:
            return False

        self.transactions[transaction_id] = transaction

        # Update customer transaction history
        account_id = transaction.get("account_id")
        account = self.get_account(account_id)
        if account:
            customer = self.get_customer(account["customer_id"])
            if customer:
                customer.transaction_history.append(transaction)

        return True

    def get_user_role(self, user_id: str) -> str:
        """Get user's role.

        Args:
            user_id: User ID

        Returns:
            Role string
        """
        user = self.get_user(user_id)
        return user.get("role", "unknown") if user else "unknown"

    def has_permission(self, user_id: str, permission: str) -> bool:
        """Check if user has specific permission.

        Args:
            user_id: User ID
            permission: Permission to check

        Returns:
            True if user has permission
        """
        user = self.get_user(user_id)
        if not user:
            return False

        permissions = user.get("permissions", [])
        return permission in permissions

    def get_customer_statistics(self) -> Dict[str, Any]:
        """Get statistics about the customer population.

        Returns:
            Dictionary with population statistics
        """
        total_customers = len(self.customers)
        if total_customers == 0:
            return {}

        # Calculate various statistics
        risk_levels = {"Low": 0, "Medium": 0, "High": 0}
        kyc_statuses = {"Verified": 0, "Pending": 0, "Rejected": 0}
        customer_types = {"Individual": 0, "Business": 0}
        countries = {}

        total_balance = 0
        total_accounts = 0
        customers_with_fraud_flags = 0

        for customer in self.customers.values():
            risk_levels[customer.risk_level] = (
                risk_levels.get(customer.risk_level, 0) + 1
            )
            kyc_statuses[customer.kyc_status] = (
                kyc_statuses.get(customer.kyc_status, 0) + 1
            )
            customer_types[customer.customer_type] = (
                customer_types.get(customer.customer_type, 0) + 1
            )
            countries[customer.country] = countries.get(customer.country, 0) + 1

            total_accounts += len(customer.accounts)
            for account in customer.accounts:
                total_balance += account.get("balance", 0)

            if customer.fraud_flags:
                customers_with_fraud_flags += 1

        total_transactions = len(self.transactions)
        suspicious_transactions = sum(
            1 for t in self.transactions.values() if t.get("is_suspicious", False)
        )

        return {
            "total_customers": total_customers,
            "total_accounts": total_accounts,
            "total_transactions": total_transactions,
            "total_balance": total_balance,
            "average_balance": total_balance / total_accounts
            if total_accounts > 0
            else 0,
            "risk_level_distribution": risk_levels,
            "kyc_status_distribution": kyc_statuses,
            "customer_type_distribution": customer_types,
            "country_distribution": countries,
            "customers_with_fraud_flags": customers_with_fraud_flags,
            "suspicious_transactions": suspicious_transactions,
            "fraud_rate": suspicious_transactions / total_transactions
            if total_transactions > 0
            else 0,
            "data_sources": [
                "IBM AML",
                "PaySim",
                "Credit Card Fraud",
                "Synthetic Banking",
            ]
            if self.use_real_data
            else ["Mock Data"],
        }
