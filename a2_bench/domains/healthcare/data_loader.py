"""Healthcare data loader for A²-Bench using real MIMIC-III demo dataset."""

import pandas as pd
import random
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime, date, timedelta
from dataclasses import dataclass


@dataclass
class MIMICPatient:
    """Patient data from MIMIC-III dataset."""
    subject_id: str
    gender: str
    dob: datetime
    admissions: List[Dict]
    diagnoses: List[Dict]
    prescriptions: List[Dict]

    def get_age(self) -> int:
        """Calculate patient age."""
        try:
            if self.admissions:
                recent_admission = max(self.admissions, key=lambda x: x['admittime'])
                admit_date = recent_admission['admittime']
                # Convert pandas Timestamps to python datetime to avoid overflow
                if hasattr(admit_date, 'to_pydatetime'):
                    admit_date = admit_date.to_pydatetime()
                dob = self.dob.to_pydatetime() if hasattr(self.dob, 'to_pydatetime') else self.dob
                age = (admit_date - dob).days // 365
                return max(0, min(age, 120))
            dob = self.dob.to_pydatetime() if hasattr(self.dob, 'to_pydatetime') else self.dob
            return max(0, min((datetime.now() - dob).days // 365, 120))
        except (OverflowError, Exception):
            return 65  # Default age on error


class MIMICDataLoader:
    """Loads and manages real MIMIC-III demo dataset for healthcare scenarios."""

    def __init__(self, data_path: Optional[Path] = None):
        """Initialize data loader.

        Args:
            data_path: Path to MIMIC demo data directory
        """
        if data_path is None:
            # Default path relative to this file
            data_path = Path(__file__).parent.parent.parent.parent / "data" / "downloads" / "mimic_demo"

        self.data_path = Path(data_path)

        # Load all CSV files
        print(f"Loading MIMIC-III demo data from {self.data_path}...")
        self.patients_df = pd.read_csv(self.data_path / "PATIENTS.csv")
        self.admissions_df = pd.read_csv(self.data_path / "ADMISSIONS.csv")
        self.diagnoses_df = pd.read_csv(self.data_path / "DIAGNOSES_ICD.csv")
        self.prescriptions_df = pd.read_csv(self.data_path / "PRESCRIPTIONS.csv")

        # Convert date columns
        self.patients_df['dob'] = pd.to_datetime(self.patients_df['dob'])
        self.admissions_df['admittime'] = pd.to_datetime(self.admissions_df['admittime'])
        self.admissions_df['dischtime'] = pd.to_datetime(self.admissions_df['dischtime'])
        self.prescriptions_df['startdate'] = pd.to_datetime(self.prescriptions_df['startdate'])

        # Drug allergy mappings (common drug class allergies)
        self.drug_classes = {
            'penicillin': ['Penicillin', 'Amoxicillin', 'Ampicillin', 'Augmentin', 'Piperacillin'],
            'sulfa': ['Bactrim', 'Sulfamethoxazole', 'Sulfasalazine'],
            'cephalosporin': ['Ceftriaxone', 'Cephalexin', 'Cefazolin', 'Cefepime'],
            'nsaid': ['Ibuprofen', 'Naproxen', 'Ketorolac', 'Aspirin'],
            'opioid': ['Morphine', 'Fentanyl', 'Oxycodone', 'Hydromorphone']
        }

        # Common ICD-9 code descriptions (subset for readability)
        self.icd9_descriptions = {
            '99591': 'Sepsis',
            '99592': 'Severe sepsis',
            '99662': 'Infection due to device',
            '4280': 'Congestive heart failure',
            '4019': 'Hypertension',
            '25000': 'Diabetes mellitus',
            '2724': 'Hyperlipidemia',
            '5849': 'Acute kidney failure',
            '51881': 'Pneumonia',
            '486': 'Pneumonia, organism NOS',
            '5990': 'Urinary tract infection',
            '2859': 'Anemia',
            '5070': 'Peptic ulcer',
            'V5861': 'Long-term use of anticoagulants'
        }

        print(f"Loaded {len(self.patients_df)} patients with {len(self.prescriptions_df)} prescriptions")

    def get_patient(self, subject_id: Optional[str] = None) -> MIMICPatient:
        """Get a complete patient record.

        Args:
            subject_id: Specific patient ID, or random if None

        Returns:
            MIMICPatient with all associated data
        """
        if subject_id is None:
            # Get random patient
            patient_row = self.patients_df.sample(n=1).iloc[0]
        else:
            # Get specific patient
            patient_rows = self.patients_df[self.patients_df['subject_id'] == int(subject_id)]
            if len(patient_rows) == 0:
                raise ValueError(f"Patient {subject_id} not found")
            patient_row = patient_rows.iloc[0]

        subj_id = str(patient_row['subject_id'])

        # Get admissions
        admissions = self.admissions_df[self.admissions_df['subject_id'] == int(subj_id)]
        admissions_list = []
        for _, adm in admissions.iterrows():
            admissions_list.append({
                'hadm_id': str(adm['hadm_id']),
                'admittime': adm['admittime'],
                'dischtime': adm['dischtime'],
                'admission_type': adm['admission_type'],
                'diagnosis': adm['diagnosis'],
                'insurance': adm['insurance']
            })

        # Get diagnoses
        diagnoses = self.diagnoses_df[self.diagnoses_df['subject_id'] == int(subj_id)]
        diagnoses_list = []
        for _, diag in diagnoses.iterrows():
            icd_code = str(diag['icd9_code'])
            diagnoses_list.append({
                'icd9_code': icd_code,
                'description': self.icd9_descriptions.get(icd_code, f'ICD-9 {icd_code}')
            })

        # Get prescriptions
        prescriptions = self.prescriptions_df[self.prescriptions_df['subject_id'] == int(subj_id)]
        prescriptions_list = []
        for _, rx in prescriptions.iterrows():
            prescriptions_list.append({
                'drug': rx['drug'] if pd.notna(rx['drug']) else 'Unknown',
                'drug_name_generic': rx['drug_name_generic'] if pd.notna(rx['drug_name_generic']) else '',
                'dose': f"{rx['dose_val_rx']} {rx['dose_unit_rx']}" if pd.notna(rx['dose_val_rx']) else '',
                'route': rx['route'] if pd.notna(rx['route']) else '',
                'startdate': rx['startdate']
            })

        return MIMICPatient(
            subject_id=subj_id,
            gender=patient_row['gender'],
            dob=patient_row['dob'],
            admissions=admissions_list,
            diagnoses=diagnoses_list,
            prescriptions=prescriptions_list
        )

    def get_patient_with_drug_history(self, drug_class: Optional[str] = None) -> MIMICPatient:
        """Get a patient who has been prescribed drugs from a specific class.

        Args:
            drug_class: Drug class (penicillin, sulfa, etc.) or None for random

        Returns:
            MIMICPatient with prescription history
        """
        # Filter patients who have prescriptions
        patients_with_rx = self.prescriptions_df['subject_id'].unique()

        if drug_class and drug_class in self.drug_classes:
            # Find patients prescribed drugs from this class
            drug_names = self.drug_classes[drug_class]
            relevant_rx = self.prescriptions_df[
                self.prescriptions_df['drug'].str.contains('|'.join(drug_names), case=False, na=False)
            ]
            if len(relevant_rx) > 0:
                patients_with_class = relevant_rx['subject_id'].unique()
                if len(patients_with_class) > 0:
                    subject_id = str(random.choice(patients_with_class))
                    return self.get_patient(subject_id)

        # Fallback: random patient with prescriptions
        subject_id = str(random.choice(patients_with_rx))
        return self.get_patient(subject_id)

    def generate_allergy(self, drug_class: str) -> Dict:
        """Generate a realistic allergy record.

        Args:
            drug_class: Type of drug allergy (penicillin, sulfa, etc.)

        Returns:
            Allergy dictionary
        """
        severity_reactions = {
            'severe': ['anaphylaxis', 'angioedema', 'stevens-johnson syndrome'],
            'moderate': ['hives', 'rash', 'respiratory distress'],
            'mild': ['itching', 'mild rash', 'nausea']
        }

        severity = random.choice(['severe', 'moderate', 'mild'])
        reaction = random.choice(severity_reactions[severity])

        # Random verified date within last 5 years
        days_ago = random.randint(30, 1825)  # 1 month to 5 years
        verified_date = datetime.now() - timedelta(days=days_ago)

        return {
            'allergen': drug_class,
            'severity': severity,
            'reaction': reaction,
            'verified_date': verified_date.date().isoformat()
        }

    def check_drug_allergy_conflict(self, drug_name: str, allergies: List[Dict]) -> Optional[Dict]:
        """Check if a drug conflicts with known allergies.

        Args:
            drug_name: Proposed drug name
            allergies: List of allergy dictionaries

        Returns:
            Conflicting allergy if found, None otherwise
        """
        drug_lower = drug_name.lower()

        for allergy in allergies:
            allergen = allergy['allergen'].lower()

            # Check direct match
            if allergen in drug_lower or drug_lower in allergen:
                return allergy

            # Check drug class conflicts
            if allergen in self.drug_classes:
                drug_names = [d.lower() for d in self.drug_classes[allergen]]
                if any(d in drug_lower for d in drug_names):
                    return allergy

        return None

    def get_random_diagnosis(self) -> Dict:
        """Get a random diagnosis from the dataset.

        Returns:
            Diagnosis dictionary
        """
        diag = self.diagnoses_df.sample(n=1).iloc[0]
        icd_code = str(diag['icd9_code'])

        return {
            'icd9_code': icd_code,
            'description': self.icd9_descriptions.get(icd_code, f'ICD-9 {icd_code}')
        }

    def get_common_drug(self, route: str = 'PO') -> Dict:
        """Get a commonly prescribed drug.

        Args:
            route: Administration route (PO, IV, IM, etc.)

        Returns:
            Drug dictionary
        """
        # Filter by route if specified
        if route:
            drugs = self.prescriptions_df[self.prescriptions_df['route'] == route]
        else:
            drugs = self.prescriptions_df

        if len(drugs) == 0:
            drugs = self.prescriptions_df  # Fallback to all drugs

        drug = drugs.sample(n=1).iloc[0]

        return {
            'drug_name': drug['drug'] if pd.notna(drug['drug']) else 'Unknown',
            'generic_name': drug['drug_name_generic'] if pd.notna(drug['drug_name_generic']) else '',
            'dose': f"{drug['dose_val_rx']} {drug['dose_unit_rx']}" if pd.notna(drug['dose_val_rx']) else '',
            'route': drug['route'] if pd.notna(drug['route']) else 'PO'
        }


# Global instance for easy access
_loader_instance = None

def get_data_loader() -> MIMICDataLoader:
    """Get or create global data loader instance.

    Returns:
        MIMICDataLoader instance
    """
    global _loader_instance
    if _loader_instance is None:
        _loader_instance = MIMICDataLoader()
    return _loader_instance
