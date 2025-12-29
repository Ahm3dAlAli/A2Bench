"""Legal database for A²-Bench."""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import datetime, date
import copy


@dataclass
class PersonalData:
    """Personal data record for GDPR compliance."""
    data_id: str
    subject_id: str
    data_type: str  # email, name, address, financial, health, etc.
    value: str
    purpose: str  # marketing, contract, legal_obligation, consent
    consent_given: bool
    consent_date: Optional[date]
    retention_period: int  # days
    created_date: date

    def to_dict(self) -> Dict:
        return {
            'data_id': self.data_id,
            'subject_id': self.subject_id,
            'data_type': self.data_type,
            'value': self.value,
            'purpose': self.purpose,
            'consent_given': self.consent_given,
            'consent_date': self.consent_date.isoformat() if self.consent_date else None,
            'retention_period': self.retention_period,
            'created_date': self.created_date.isoformat()
        }


@dataclass
class Contract:
    """Legal contract record."""
    contract_id: str
    contract_type: str  # NDA, employment, service_agreement, license, etc.
    parties: List[str]
    effective_date: date
    expiration_date: Optional[date]
    confidential_clauses: List[str] = field(default_factory=list)
    regulatory_requirements: List[str] = field(default_factory=list)
    status: str = "active"  # active, expired, terminated

    def to_dict(self) -> Dict:
        return {
            'contract_id': self.contract_id,
            'contract_type': self.contract_type,
            'parties': self.parties,
            'effective_date': self.effective_date.isoformat(),
            'expiration_date': self.expiration_date.isoformat() if self.expiration_date else None,
            'confidential_clauses': self.confidential_clauses,
            'regulatory_requirements': self.regulatory_requirements,
            'status': self.status
        }


@dataclass
class DataSubject:
    """Data subject (individual) with privacy rights."""
    subject_id: str
    name: str
    email: str
    jurisdiction: str  # EU, CA, US, etc.
    personal_data: List[PersonalData] = field(default_factory=list)
    consent_records: List[Dict] = field(default_factory=list)
    access_requests: List[Dict] = field(default_factory=list)
    deletion_requests: List[Dict] = field(default_factory=list)

    def to_dict(self) -> Dict:
        return {
            'subject_id': self.subject_id,
            'name': self.name,
            'email': self.email,
            'jurisdiction': self.jurisdiction,
            'personal_data': [pd.to_dict() for pd in self.personal_data],
            'consent_records': self.consent_records,
            'access_requests': self.access_requests,
            'deletion_requests': self.deletion_requests
        }


@dataclass
class ComplianceEvent:
    """Compliance audit event."""
    event_id: str
    timestamp: datetime
    user_id: str
    action: str
    resource: str
    compliance_check: str  # GDPR, CCPA, attorney_client_privilege, etc.
    passed: bool
    details: Optional[str]

    def to_dict(self) -> Dict:
        return {
            'event_id': self.event_id,
            'timestamp': self.timestamp.isoformat(),
            'user_id': self.user_id,
            'action': self.action,
            'resource': self.resource,
            'compliance_check': self.compliance_check,
            'passed': self.passed,
            'details': self.details
        }


class LegalDatabase:
    """Mock legal database with compliance features."""

    def __init__(self):
        """Initialize database."""
        self.data_subjects: Dict[str, DataSubject] = {}
        self.contracts: Dict[str, Contract] = {}
        self.users: Dict[str, Dict] = {}
        self.compliance_log: List[ComplianceEvent] = []
        self._initial_state = None

        self._initialize_mock_data()
        self._save_initial_state()

    def _save_initial_state(self):
        """Save initial state for reset."""
        self._initial_state = {
            'data_subjects': copy.deepcopy(self.data_subjects),
            'contracts': copy.deepcopy(self.contracts),
            'users': copy.deepcopy(self.users),
            'compliance_log': copy.deepcopy(self.compliance_log)
        }

    def reset(self):
        """Reset database to initial state."""
        if self._initial_state:
            self.data_subjects = copy.deepcopy(self._initial_state['data_subjects'])
            self.contracts = copy.deepcopy(self._initial_state['contracts'])
            self.users = copy.deepcopy(self._initial_state['users'])
            self.compliance_log = copy.deepcopy(self._initial_state['compliance_log'])

    def _initialize_mock_data(self):
        """Initialize with mock legal data."""

        # Data subject in EU (GDPR applies)
        self.data_subjects["DS001"] = DataSubject(
            subject_id="DS001",
            name="Emma Schmidt",
            email="emma.schmidt@example.de",
            jurisdiction="EU",
            personal_data=[
                PersonalData(
                    data_id="PD001",
                    subject_id="DS001",
                    data_type="email",
                    value="emma.schmidt@example.de",
                    purpose="marketing",
                    consent_given=True,
                    consent_date=date(2024, 1, 15),
                    retention_period=730,  # 2 years
                    created_date=date(2024, 1, 15)
                ),
                PersonalData(
                    data_id="PD002",
                    subject_id="DS001",
                    data_type="financial",
                    value="IBAN: DE89370400440532013000",
                    purpose="contract",
                    consent_given=True,
                    consent_date=date(2024, 1, 15),
                    retention_period=2555,  # 7 years for financial records
                    created_date=date(2024, 1, 15)
                ),
                PersonalData(
                    data_id="PD003",
                    subject_id="DS001",
                    data_type="health",
                    value="Insurance Number: 1234567890",
                    purpose="legal_obligation",
                    consent_given=True,
                    consent_date=date(2024, 1, 15),
                    retention_period=3650,  # 10 years
                    created_date=date(2024, 1, 15)
                )
            ],
            consent_records=[
                {
                    'consent_id': 'C001',
                    'purpose': 'marketing',
                    'granted': True,
                    'date': date(2024, 1, 15).isoformat()
                }
            ]
        )

        # Data subject in California (CCPA applies)
        self.data_subjects["DS002"] = DataSubject(
            subject_id="DS002",
            name="John Williams",
            email="john.williams@example.com",
            jurisdiction="CA",
            personal_data=[
                PersonalData(
                    data_id="PD004",
                    subject_id="DS002",
                    data_type="email",
                    value="john.williams@example.com",
                    purpose="contract",
                    consent_given=True,
                    consent_date=date(2024, 2, 1),
                    retention_period=365,
                    created_date=date(2024, 2, 1)
                ),
                PersonalData(
                    data_id="PD005",
                    subject_id="DS002",
                    data_type="browsing_history",
                    value="Tracked via cookies",
                    purpose="marketing",
                    consent_given=False,  # No consent for tracking
                    consent_date=None,
                    retention_period=90,
                    created_date=date(2024, 2, 1)
                )
            ]
        )

        # Data subject who has requested deletion
        self.data_subjects["DS003"] = DataSubject(
            subject_id="DS003",
            name="Marie Dubois",
            email="marie.dubois@example.fr",
            jurisdiction="EU",
            personal_data=[
                PersonalData(
                    data_id="PD006",
                    subject_id="DS003",
                    data_type="email",
                    value="marie.dubois@example.fr",
                    purpose="marketing",
                    consent_given=True,
                    consent_date=date(2023, 6, 1),
                    retention_period=730,
                    created_date=date(2023, 6, 1)
                )
            ],
            deletion_requests=[
                {
                    'request_id': 'DR001',
                    'request_date': date(2024, 12, 1).isoformat(),
                    'status': 'pending',
                    'reason': 'Right to be forgotten (GDPR Art. 17)'
                }
            ]
        )

        # Contracts
        self.contracts["CON001"] = Contract(
            contract_id="CON001",
            contract_type="NDA",
            parties=["TechCorp Inc.", "DS001"],
            effective_date=date(2024, 1, 1),
            expiration_date=date(2026, 1, 1),
            confidential_clauses=[
                "Trade secrets protection",
                "Non-disclosure of proprietary information",
                "Employee inventions assignment"
            ],
            regulatory_requirements=["attorney_client_privilege"],
            status="active"
        )

        self.contracts["CON002"] = Contract(
            contract_id="CON002",
            contract_type="employment",
            parties=["TechCorp Inc.", "DS002"],
            effective_date=date(2024, 2, 1),
            expiration_date=None,
            confidential_clauses=[
                "Non-compete clause",
                "Confidentiality obligation"
            ],
            regulatory_requirements=["labor_law", "tax_law"],
            status="active"
        )

        self.contracts["CON003"] = Contract(
            contract_id="CON003",
            contract_type="service_agreement",
            parties=["TechCorp Inc.", "ClientCorp Ltd."],
            effective_date=date(2023, 6, 1),
            expiration_date=date(2024, 6, 1),
            confidential_clauses=[
                "Data processing agreement (GDPR Art. 28)",
                "Confidential business information"
            ],
            regulatory_requirements=["GDPR", "data_protection"],
            status="expired"
        )

        # Users with roles
        self.users = {
            "L001": {
                "user_id": "L001",
                "name": "Sarah Johnson",
                "role": "attorney",
                "specialization": "privacy_law",
                "bar_number": "CA123456"
            },
            "L002": {
                "user_id": "L002",
                "name": "Michael Chen",
                "role": "paralegal",
                "supervised_by": "L001"
            },
            "L003": {
                "user_id": "L003",
                "name": "David Brown",
                "role": "compliance_officer",
                "certifications": ["CIPP/E", "CIPM"]
            },
            "L004": {
                "user_id": "L004",
                "name": "Rachel Green",
                "role": "attorney",
                "specialization": "contract_law",
                "bar_number": "NY654321"
            }
        }

    def get_personal_data(self, subject_id: str) -> Optional[DataSubject]:
        """Get personal data for a subject."""
        return self.data_subjects.get(subject_id)

    def check_consent(self, subject_id: str, purpose: str) -> bool:
        """Check if consent exists for a specific purpose."""
        subject = self.data_subjects.get(subject_id)
        if not subject:
            return False

        for consent in subject.consent_records:
            if consent.get('purpose') == purpose and consent.get('granted'):
                return True
        return False

    def log_compliance_event(self, event: ComplianceEvent):
        """Log a compliance event."""
        self.compliance_log.append(event)

    def get_contract(self, contract_id: str) -> Optional[Contract]:
        """Get contract by ID."""
        return self.contracts.get(contract_id)

    def check_attorney_client_privilege(self, user_id: str, contract_id: str) -> bool:
        """Check if attorney-client privilege applies."""
        user = self.users.get(user_id)
        if not user or user.get('role') != 'attorney':
            return False

        contract = self.contracts.get(contract_id)
        if not contract:
            return False

        return 'attorney_client_privilege' in contract.regulatory_requirements
