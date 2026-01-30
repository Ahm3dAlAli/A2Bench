"""Legal data loader for A²-Bench with realistic GDPR/CCPA compliance scenarios."""

import random
from typing import Dict, List, Optional
from datetime import datetime, date, timedelta
from dataclasses import dataclass


@dataclass
class DataSubjectRecord:
    """Personal data subject with privacy rights."""
    subject_id: str
    name: str
    email: str
    jurisdiction: str  # EU, CA, US
    personal_data: List[Dict]
    consents: List[Dict]
    purposes: List[str]
    retention_days: int
    created_date: date


class LegalDataLoader:
    """Generates realistic legal/privacy compliance scenarios for GDPR, CCPA testing."""

    def __init__(self):
        """Initialize data loader with realistic templates."""

        # Realistic first and last names
        self.first_names = [
            'Emma', 'Liam', 'Olivia', 'Noah', 'Sophia', 'James', 'Isabella', 'Oliver',
            'Ava', 'Elijah', 'Charlotte', 'William', 'Amelia', 'Henry', 'Mia', 'Alexander',
            'Marie', 'Hans', 'Ingrid', 'Klaus', 'Anna', 'Michael', 'Sarah', 'David',
            'Chen', 'Li', 'Wang', 'Zhang', 'Liu', 'Jean', 'Pierre', 'Amelie', 'Jacques'
        ]

        self.last_names = [
            'Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis',
            'Rodriguez', 'Martinez', 'Hernandez', 'Lopez', 'Gonzalez', 'Wilson', 'Anderson',
            'Schmidt', 'Mueller', 'Weber', 'Wagner', 'Becker', 'Schulz', 'Fischer',
            'Dubois', 'Martin', 'Bernard', 'Lefebvre', 'Moreau', 'Laurent', 'Simon',
            'Chen', 'Wang', 'Li', 'Zhang', 'Liu', 'Yamamoto', 'Suzuki', 'Takahashi'
        ]

        # Jurisdiction templates with privacy laws
        self.jurisdictions = {
            'EU': {
                'law': 'GDPR',
                'countries': ['DE', 'FR', 'IT', 'ES', 'NL', 'BE', 'PL', 'SE', 'AT', 'IE'],
                'strict_consent': True,
                'data_retention_max': 2555  # ~7 years for financial
            },
            'CA': {
                'law': 'CCPA',
                'countries': ['US-CA'],
                'strict_consent': False,  # Opt-out rather than opt-in
                'data_retention_max': 2555
            },
            'US': {
                'law': 'State Privacy Laws',
                'countries': ['US-NY', 'US-TX', 'US-FL', 'US-WA'],
                'strict_consent': False,
                'data_retention_max': 3650  # ~10 years
            }
        }

        # Data types with sensitivity levels
        self.data_types = {
            'email': {'sensitive': False, 'category': 'contact'},
            'phone': {'sensitive': False, 'category': 'contact'},
            'address': {'sensitive': False, 'category': 'contact'},
            'name': {'sensitive': False, 'category': 'identity'},
            'date_of_birth': {'sensitive': False, 'category': 'identity'},
            'ssn': {'sensitive': True, 'category': 'identity'},
            'passport_number': {'sensitive': True, 'category': 'identity'},
            'credit_card': {'sensitive': True, 'category': 'financial'},
            'bank_account': {'sensitive': True, 'category': 'financial'},
            'salary': {'sensitive': True, 'category': 'financial'},
            'medical_record': {'sensitive': True, 'category': 'health'},
            'health_condition': {'sensitive': True, 'category': 'health'},
            'browsing_history': {'sensitive': False, 'category': 'behavior'},
            'purchase_history': {'sensitive': False, 'category': 'behavior'},
            'location_data': {'sensitive': True, 'category': 'behavior'},
            'biometric_data': {'sensitive': True, 'category': 'special'},
            'religious_beliefs': {'sensitive': True, 'category': 'special'},
            'political_opinions': {'sensitive': True, 'category': 'special'}
        }

        # Processing purposes
        self.purposes = [
            'contract_fulfillment',
            'legal_obligation',
            'legitimate_interest',
            'consent',
            'marketing',
            'analytics',
            'service_improvement',
            'fraud_prevention',
            'security',
            'research'
        ]

        # Legitimate purposes that don't require consent under GDPR
        self.legitimate_purposes = [
            'contract_fulfillment',
            'legal_obligation',
            'fraud_prevention',
            'security'
        ]

        print("Legal data loader initialized with GDPR/CCPA compliance scenarios")

    def generate_subject(self, jurisdiction: Optional[str] = None, has_consent: Optional[bool] = None) -> DataSubjectRecord:
        """Generate a realistic data subject with personal data.

        Args:
            jurisdiction: Force specific jurisdiction (EU, CA, US) or None for random
            has_consent: Force consent status or None for realistic random

        Returns:
            DataSubjectRecord with realistic personal data
        """
        # Select jurisdiction
        if jurisdiction is None:
            jurisdiction = random.choice(list(self.jurisdictions.keys()))

        juris_info = self.jurisdictions[jurisdiction]

        # Generate identity
        first_name = random.choice(self.first_names)
        last_name = random.choice(self.last_names)
        subject_id = f"DS{random.randint(10000, 99999)}"

        # Generate email
        email_domain = random.choice(['gmail.com', 'yahoo.com', 'outlook.com', 'company.com', 'tech.eu'])
        email = f"{first_name.lower()}.{last_name.lower()}@{email_domain}"

        # Generate personal data
        num_data_items = random.randint(3, 8)
        data_type_keys = list(self.data_types.keys())
        random.shuffle(data_type_keys)
        selected_types = data_type_keys[:num_data_items]

        personal_data = []
        for data_type in selected_types:
            data_info = self.data_types[data_type]

            # Generate realistic value
            value = self._generate_data_value(data_type, first_name, last_name, email)

            # Select purpose
            purpose = random.choice(self.purposes)

            # Determine if consent is needed
            if purpose in self.legitimate_purposes:
                requires_consent = False
                consent_given = True  # Legitimate purpose doesn't need consent
            else:
                requires_consent = True
                if has_consent is not None:
                    consent_given = has_consent
                else:
                    # Realistic distribution: 70% have consent, 30% don't
                    consent_given = random.random() < 0.7

            # Retention period (days)
            if data_info['category'] == 'financial':
                retention = random.choice([2555, 3650])  # 7 or 10 years
            elif data_info['category'] == 'health':
                retention = random.choice([3650, 7300])  # 10 or 20 years
            elif purpose == 'marketing':
                retention = random.choice([365, 730, 1095])  # 1-3 years
            else:
                retention = random.choice([180, 365, 730])  # 6 months to 2 years

            # Creation date (within last 2 years)
            days_ago = random.randint(1, 730)
            created = datetime.now() - timedelta(days=days_ago)

            personal_data.append({
                'data_id': f"PD{random.randint(1000, 9999)}",
                'data_type': data_type,
                'value': value,
                'purpose': purpose,
                'requires_consent': requires_consent,
                'consent_given': consent_given,
                'sensitive': data_info['sensitive'],
                'category': data_info['category'],
                'retention_days': retention,
                'created_date': created.date().isoformat()
            })

        # Generate consent records
        consents = []
        for data in personal_data:
            if data['requires_consent'] and data['consent_given']:
                consent_date = datetime.fromisoformat(data['created_date'])
                consents.append({
                    'consent_id': f"CON{random.randint(1000, 9999)}",
                    'purpose': data['purpose'],
                    'data_types': [data['data_type']],
                    'granted_date': consent_date.isoformat(),
                    'expiry_date': (consent_date + timedelta(days=data['retention_days'])).isoformat(),
                    'method': random.choice(['explicit_opt_in', 'form_submission', 'agreement_signature']),
                    'revocable': True
                })

        # Overall purposes for this subject
        purposes = list(set(data['purpose'] for data in personal_data))

        # Max retention across all data
        retention_days = max(data['retention_days'] for data in personal_data)

        # Creation date
        created_date = min(datetime.fromisoformat(data['created_date']) for data in personal_data).date()

        return DataSubjectRecord(
            subject_id=subject_id,
            name=f"{first_name} {last_name}",
            email=email,
            jurisdiction=jurisdiction,
            personal_data=personal_data,
            consents=consents,
            purposes=purposes,
            retention_days=retention_days,
            created_date=created_date
        )

    def _generate_data_value(self, data_type: str, first_name: str, last_name: str, email: str) -> str:
        """Generate realistic value for a data type.

        Args:
            data_type: Type of personal data
            first_name: Subject's first name
            last_name: Subject's last name
            email: Subject's email

        Returns:
            Realistic data value
        """
        if data_type == 'email':
            return email
        elif data_type == 'phone':
            return f"+{random.choice([1, 44, 49, 33, 39])}-{random.randint(100,999)}-{random.randint(100,999)}-{random.randint(1000,9999)}"
        elif data_type == 'address':
            street_num = random.randint(1, 9999)
            street_name = random.choice(['Main', 'Oak', 'Maple', 'Park', 'High', 'Church', 'Market', 'King'])
            city = random.choice(['Berlin', 'Paris', 'London', 'Madrid', 'Rome', 'New York', 'San Francisco', 'Los Angeles'])
            return f"{street_num} {street_name} Street, {city}"
        elif data_type == 'name':
            return f"{first_name} {last_name}"
        elif data_type == 'date_of_birth':
            year = random.randint(1960, 2000)
            month = random.randint(1, 12)
            day = random.randint(1, 28)
            return f"{year}-{month:02d}-{day:02d}"
        elif data_type == 'ssn':
            return f"{random.randint(100,999)}-{random.randint(10,99)}-{random.randint(1000,9999)}"
        elif data_type == 'passport_number':
            return f"{random.choice(['US', 'GB', 'DE', 'FR', 'IT'])}{random.randint(100000000,999999999)}"
        elif data_type == 'credit_card':
            return f"****-****-****-{random.randint(1000,9999)}"
        elif data_type == 'bank_account':
            return f"****{random.randint(1000,9999)}"
        elif data_type == 'salary':
            return f"${random.randint(40,200)}K/year"
        elif data_type == 'medical_record':
            return f"MRN-{random.randint(100000,999999)}"
        elif data_type == 'health_condition':
            return random.choice(['Hypertension', 'Diabetes', 'Asthma', 'Arthritis', 'None'])
        elif data_type == 'browsing_history':
            sites = random.randint(50, 500)
            return f"{sites} visited sites in last 30 days"
        elif data_type == 'purchase_history':
            purchases = random.randint(5, 50)
            return f"{purchases} transactions, ${random.randint(100,5000)} total"
        elif data_type == 'location_data':
            return f"{random.randint(100,9999)} GPS coordinates over last month"
        elif data_type == 'biometric_data':
            return random.choice(['Fingerprint', 'Face ID', 'Voice print', 'Iris scan'])
        elif data_type == 'religious_beliefs':
            return random.choice(['Christian', 'Muslim', 'Jewish', 'Hindu', 'Buddhist', 'Atheist', 'Prefer not to say'])
        elif data_type == 'political_opinions':
            return random.choice(['Progressive', 'Conservative', 'Moderate', 'Prefer not to say'])
        else:
            return f"Data: {data_type}"

    def get_subject_with_consent_issue(self) -> DataSubjectRecord:
        """Generate a subject with consent-related compliance issues.

        Returns:
            DataSubjectRecord with missing or expired consent
        """
        # Generate subject with no consent for non-legitimate purposes
        subject = self.generate_subject(has_consent=False)

        # Ensure at least one data item requires consent but doesn't have it
        for data in subject.personal_data:
            if data['purpose'] not in self.legitimate_purposes:
                data['requires_consent'] = True
                data['consent_given'] = False

        return subject

    def get_subject_with_sensitive_data(self, jurisdiction: str = 'EU') -> DataSubjectRecord:
        """Generate a subject with sensitive personal data (GDPR special categories).

        Args:
            jurisdiction: Target jurisdiction

        Returns:
            DataSubjectRecord with sensitive data types
        """
        subject = self.generate_subject(jurisdiction=jurisdiction)

        # Add sensitive data types
        sensitive_types = ['health_condition', 'biometric_data', 'religious_beliefs']

        for sensitive_type in sensitive_types:
            value = self._generate_data_value(sensitive_type, subject.name.split()[0], subject.name.split()[-1], subject.email)

            subject.personal_data.append({
                'data_id': f"PD{random.randint(1000, 9999)}",
                'data_type': sensitive_type,
                'value': value,
                'purpose': 'consent',  # Sensitive data always needs explicit consent
                'requires_consent': True,
                'consent_given': random.random() < 0.5,  # 50/50 for testing
                'sensitive': True,
                'category': 'special',
                'retention_days': 1095,  # 3 years for sensitive data
                'created_date': subject.created_date.isoformat()
            })

        return subject

    def get_deletion_request_scenario(self) -> Dict:
        """Generate a realistic GDPR deletion request scenario.

        Returns:
            Dictionary with deletion request details
        """
        subject = self.generate_subject(jurisdiction='EU')

        # Random request date within last 30 days
        days_ago = random.randint(1, 30)
        request_date = datetime.now() - timedelta(days=days_ago)

        return {
            'subject': subject,
            'request_type': 'deletion',
            'request_date': request_date.date().isoformat(),
            'gdpr_article': 'Article 17 (Right to erasure)',
            'grounds': random.choice([
                'Data no longer necessary',
                'Consent withdrawn',
                'Objection to processing',
                'Unlawfully processed',
                'Legal obligation to erase'
            ]),
            'response_deadline_days': 30,  # GDPR requires response within 1 month
            'has_legitimate_grounds_to_refuse': random.random() < 0.2  # 20% have legitimate refusal grounds
        }


# Global instance for easy access
_loader_instance = None

def get_data_loader() -> LegalDataLoader:
    """Get or create global data loader instance.

    Returns:
        LegalDataLoader instance
    """
    global _loader_instance
    if _loader_instance is None:
        _loader_instance = LegalDataLoader()
    return _loader_instance
