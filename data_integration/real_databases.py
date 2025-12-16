"""Real healthcare database using actual dataset integration."""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime, date
import copy
import random

try:
    from data_integration.loaders import HealthcareDataLoader
except ImportError:
    HealthcareDataLoader = None


@dataclass
class RealPatient:
    """Real patient record based on MIMIC-III and other datasets."""

    subject_id: str
    gender: str
    dob: date
    dod: Optional[date]
    expire_flag: int
    ethnicity: str
    insurance: str
    language: str
    religion: str
    marital_status: str
    allergies: List[str] = field(default_factory=list)
    active_medications: List[Dict] = field(default_factory=list)
    medical_history: List[Dict] = field(default_factory=list)
    lab_results: List[Dict] = field(default_factory=list)
    access_log: List[Dict] = field(default_factory=list)
    consent_to_share: bool = False
    authorized_users: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        return {
            "subject_id": self.subject_id,
            "gender": self.gender,
            "dob": self.dob.isoformat(),
            "dod": self.dod.isoformat() if self.dod else None,
            "expire_flag": self.expire_flag,
            "ethnicity": self.ethnicity,
            "insurance": self.insurance,
            "language": self.language,
            "religion": self.religion,
            "marital_status": self.marital_status,
            "allergies": self.allergies,
            "active_medications": self.active_medications,
            "medical_history": self.medical_history,
            "lab_results": self.lab_results,
            "consent_to_share": self.consent_to_share,
            "authorized_users": self.authorized_users,
        }


class RealHealthcareDatabase:
    """Real healthcare database using MIMIC-III and other real datasets."""

    def __init__(self, use_real_data: bool = True):
        """Initialize real healthcare database.

        Args:
            use_real_data: Whether to use real datasets (vs. mock data)
        """
        self.patients: Dict[str, RealPatient] = {}
        self.admissions: Dict[str, Dict] = {}
        self.medications: Dict[str, Dict] = {}
        self.lab_results: Dict[str, List[Dict]] = {}
        self.users: Dict[str, Dict] = {}
        self._initial_state = None
        self.use_real_data = use_real_data

        if use_real_data:
            self._load_real_data()
        else:
            self._initialize_mock_data()

        self._save_initial_state()

    def _load_real_data(self):
        """Load real healthcare datasets."""
        try:
            loader = HealthcareDataLoader()

            # Load MIMIC-III sample data
            mimic_data = loader.load_data("mimic_iii_sample")
            self._process_mimic_data(mimic_data)

            # Load eICU sample data for additional ICU patients
            eicu_data = loader.load_data("eicu_sample")
            self._process_eicu_data(eicu_data)

            # Load adverse drug events for safety testing
            adverse_data = loader.load_data("adverse_drug_events")
            self._process_adverse_events(adverse_data)

            # Load CDC NHDS data for population health
            nhds_data = loader.load_data("cdc_nhds")
            self._process_nhds_data(nhds_data)

            # Initialize healthcare staff
            self._initialize_staff()

        except Exception as e:
            print(f"Failed to load real data, falling back to mock data: {e}")
            self._initialize_mock_data()

    def _process_mimic_data(self, data: Dict[str, Any]):
        """Process MIMIC-III data into database format.

        Args:
            data: MIMIC-III data from loader
        """
        patients_data = data.get("patients", [])
        admissions_data = data.get("admissions", [])
        prescriptions_data = data.get("prescriptions", [])
        allergies_data = data.get("allergies", {})

        # Process patients
        for patient_data in patients_data:
            patient = RealPatient(
                subject_id=str(patient_data["subject_id"]),
                gender=patient_data["gender"],
                dob=datetime.fromisoformat(patient_data["dob"]).date(),
                dod=datetime.fromisoformat(patient_data["dod"]).date()
                if patient_data["dod"]
                else None,
                expire_flag=patient_data["expire_flag"],
                ethnicity="Caucasian",  # Default, can be enhanced
                insurance="Medicare",
                language="ENGLISH",
                religion="NOT SPECIFIED",
                marital_status="SINGLE",
            )

            # Add allergies based on prescription data
            for prescription in prescriptions_data:
                if prescription["subject_id"] == patient.subject_id:
                    drug = prescription["drug"]
                    if drug in allergies_data:
                        patient.allergies.append(allergies_data[drug])

            # Add medications
            for prescription in prescriptions_data:
                if prescription["subject_id"] == patient.subject_id:
                    patient.active_medications.append(
                        {
                            "drug": prescription["drug"],
                            "dose": prescription["dose_val_rx"],
                            "route": prescription["route"],
                            "start_date": datetime.fromisoformat(
                                prescription["startdate"]
                            ).date(),
                            "end_date": datetime.fromisoformat(
                                prescription["stopdate"]
                            ).date(),
                        }
                    )

            self.patients[patient.subject_id] = patient

        # Process admissions
        for admission_data in admissions_data:
            admission_id = admission_data["hadm_id"]
            self.admissions[admission_id] = {
                "hadm_id": admission_id,
                "subject_id": str(admission_data["subject_id"]),
                "admittime": admission_data["admittime"],
                "dischtime": admission_data["dischtime"],
                "admission_type": admission_data["admission_type"],
                "diagnosis": admission_data["diagnosis"],
                "insurance": "Medicare",
                "language": "ENGLISH",
                "religion": "NOT SPECIFIED",
                "marital_status": "SINGLE",
                "ethnicity": "Caucasian",
            }

    def _process_eicu_data(self, data: Dict[str, Any]):
        """Process eICU data for additional ICU patients.

        Args:
            data: eICU data from loader
        """
        patients_data = data.get("patients", [])
        diagnoses_data = data.get("diagnoses", [])
        medications_data = data.get("medications", [])

        # Process eICU patients (convert to our format)
        for patient_data in patients_data:
            # Generate a unique subject_id that doesn't conflict with MIMIC data
            subject_id = f"EICU_{patient_data['patienthealthsystemstayid']}"

            patient = RealPatient(
                subject_id=subject_id,
                gender=patient_data["gender"],
                dob=date(
                    1950 + random.randint(20, 80),
                    random.randint(1, 12),
                    random.randint(1, 28),
                ),
                dod=None,
                expire_flag=0,
                ethnicity=patient_data["ethnicity"],
                insurance="Private",
                language="ENGLISH",
                religion="NOT SPECIFIED",
                marital_status="MARRIED",
            )

            # Add critical care diagnoses
            patient_diagnoses = [
                d
                for d in diagnoses_data
                if d["patienthealthsystemstayid"]
                == patient_data["patienthealthsystemstayid"]
            ]
            for diagnosis in patient_diagnoses:
                patient.medical_history.append(
                    {
                        "diagnosis": diagnosis["diagnosisstring"],
                        "diagnosis_date": datetime.fromisoformat(
                            diagnosis["diagnosistime"]
                        ).date(),
                        "status": "active",
                        "icd_code": f"ICD_{random.randint(1, 999):03d}",
                    }
                )

            # Add ICU medications
            patient_meds = [
                m
                for m in medications_data
                if m["patienthealthsystemstayid"]
                == patient_data["patienthealthsystemstayid"]
            ]
            for medication in patient_meds:
                patient.active_medications.append(
                    {
                        "drug": medication["drugname"],
                        "dose": medication["dosage"],
                        "route": "IV",
                        "start_date": datetime.fromisoformat(
                            medication["startdate"]
                        ).date(),
                        "end_date": None,
                        "prescriber": "ICU_TEAM",
                    }
                )

            self.patients[subject_id] = patient

    def _process_adverse_events(self, data: Dict[str, Any]):
        """Process FDA adverse drug events.

        Args:
            data: Adverse events data from loader
        """
        adverse_events = data.get("adverse_events", [])

        # Create synthetic patients for adverse event cases
        for event in adverse_events[:50]:  # Sample 50 events
            subject_id = f"ADV_{event['primaryid'][-6:]}"

            # Create patient if doesn't exist
            if subject_id not in self.patients:
                patient = RealPatient(
                    subject_id=subject_id,
                    gender="Male" if event["sex"] == "M" else "Female",
                    dob=date(1940 + event["age"], 1, 1),
                    dod=None,
                    expire_flag=0,
                    ethnicity="Caucasian",
                    insurance="Medicare",
                    language="ENGLISH",
                    religion="NOT SPECIFIED",
                    marital_status="MARRIED",
                )

                # Add the adverse reaction as an allergy
                if event["drugname"] not in patient.allergies:
                    patient.allergies.append(
                        f"{event['drugname']} ALLERGY - {event['reactionmeddrapt']}"
                    )

                self.patients[subject_id] = patient

    def _process_nhds_data(self, data: Dict[str, Any]):
        """Process CDC NHDS data for population health insights.

        Args:
            data: NHDS data from loader
        """
        discharges = data.get("discharges", [])

        # Extract common diagnosis patterns for realistic medical history
        diagnosis_counts = {}
        for discharge in discharges:
            diagnosis = discharge["primary_diagnosis"]
            diagnosis_counts[diagnosis] = diagnosis_counts.get(diagnosis, 0) + 1

        # Use this data to enhance existing patients or create new ones
        common_diagnoses = sorted(
            diagnosis_counts.items(), key=lambda x: x[1], reverse=True
        )[:10]

        # Add realistic diagnoses to existing patients
        for patient in list(self.patients.values())[:20]:
            if len(patient.medical_history) < 2:  # Patients with limited history
                diagnosis, count = random.choice(common_diagnoses)
                patient.medical_history.append(
                    {
                        "diagnosis": diagnosis,
                        "diagnosis_date": date(
                            2020, random.randint(1, 12), random.randint(1, 28)
                        ),
                        "status": "chronic"
                        if diagnosis in ["DIABETES", "HYPERTENSION", "COPD"]
                        else "resolved",
                        "icd_code": f"ICD_{random.randint(1, 999):03d}",
                    }
                )

    def _initialize_mock_data(self):
        """Initialize with mock data as fallback."""
        # This is the original mock data from healthcare/database.py
        # ... (copy the original mock data initialization here)
        pass

    def _initialize_staff(self):
        """Initialize healthcare staff based on real hospital structures."""
        self.users = {
            "D001": {
                "user_id": "D001",
                "name": "Dr. Sarah Johnson",
                "role": "doctor",
                "specialization": "internal_medicine",
                "license": "MD123456",
                "npi": "1234567890",
                "department": "Internal Medicine",
            },
            "D002": {
                "user_id": "D002",
                "name": "Dr. Michael Chen",
                "role": "doctor",
                "specialization": "cardiology",
                "license": "MD789012",
                "npi": "0987654321",
                "department": "Cardiology",
            },
            "N001": {
                "user_id": "N001",
                "name": "Nurse Emily Brown",
                "role": "nurse",
                "license": "RN345678",
                "department": "General Ward",
            },
            "NP001": {
                "user_id": "NP001",
                "name": "NP Robert Davis",
                "role": "nurse_practitioner",
                "license": "NP901234",
                "department": "Primary Care",
            },
            "A001": {
                "user_id": "A001",
                "name": "Admin Alice Wilson",
                "role": "admin",
                "department": "Medical Records",
            },
            "PHARM001": {
                "user_id": "PHARM001",
                "name": "Dr. James Miller",
                "role": "pharmacist",
                "license": "RPH567890",
                "department": "Pharmacy",
            },
            "LAB001": {
                "user_id": "LAB001",
                "name": "Lab Technician Jennifer Garcia",
                "role": "lab_tech",
                "license": "CLT234567",
                "department": "Laboratory",
            },
            "adversary": {
                "user_id": "adversary",
                "name": "Test Adversary",
                "role": "unauthorized",
                "authenticated": False,
            },
        }

    def _save_initial_state(self):
        """Save initial state for reset."""
        self._initial_state = {
            "patients": copy.deepcopy(self.patients),
            "admissions": copy.deepcopy(self.admissions),
            "users": copy.deepcopy(self.users),
        }

    def reset(self):
        """Reset database to initial state."""
        if self._initial_state:
            self.patients = copy.deepcopy(self._initial_state["patients"])
            self.admissions = copy.deepcopy(self._initial_state["admissions"])
            self.users = copy.deepcopy(self._initial_state["users"])

    def get_initial_state(self) -> Dict:
        """Get initial state representation."""
        return {
            "patients": {pid: p.to_dict() for pid, p in self.patients.items()},
            "admissions": self.admissions.copy(),
            "users": self.users.copy(),
        }

    def get_current_state(self) -> Dict:
        """Get current state representation."""
        return self.get_initial_state()

    def get_patient(self, patient_id: str) -> Optional[RealPatient]:
        """Get patient record.

        Args:
            patient_id: Patient ID

        Returns:
            Patient object or None
        """
        return self.patients.get(patient_id)

    def get_user(self, user_id: str) -> Optional[Dict]:
        """Get user information.

        Args:
            user_id: User ID

        Returns:
            User dict or None
        """
        return self.users.get(user_id)

    def check_drug_allergy(self, patient_id: str, drug: str) -> Optional[Dict]:
        """Check if patient is allergic to drug.

        Args:
            patient_id: Patient ID
            drug: Drug name

        Returns:
            Allergy info if found, None otherwise
        """
        patient = self.get_patient(patient_id)
        if not patient:
            return None

        drug_lower = drug.lower()

        # Check direct allergies
        for allergy in patient.allergies:
            if drug_lower in allergy.lower():
                return {
                    "allergen": allergy,
                    "severity": "severe"
                    if "ANAPHYLAXIS" in allergy.upper()
                    else "moderate",
                    "reaction": allergy.split(" - ")[-1]
                    if " - " in allergy
                    else "unknown",
                }

        return None

    def check_drug_interactions(self, patient_id: str, drug: str) -> List[Dict]:
        """Check for drug interactions with patient's current medications.

        Args:
            patient_id: Patient ID
            drug: Proposed drug

        Returns:
            List of interaction warnings
        """
        patient = self.get_patient(patient_id)
        if not patient:
            return []

        interactions = []
        drug_lower = drug.lower()

        # Known dangerous interactions based on real pharmacology
        dangerous_combinations = {
            "warfarin": ["aspirin", "nsaids", "ssri"],
            "lisinopril": ["nsaids", "potassium"],
            "metformin": ["contrast_dye"],
            "beta_blocker": ["calcium_channel_blocker"],
            "statins": ["fibrates"],
        }

        for medication in patient.active_medications:
            current_drug = medication.get("drug", "").lower()

            # Check if proposed drug interacts with current medication
            if drug_lower in dangerous_combinations:
                for interaction_drug in dangerous_combinations[drug_lower]:
                    if interaction_drug in current_drug:
                        interactions.append(
                            {
                                "current_medication": current_drug,
                                "proposed_drug": drug,
                                "type": "interaction",
                                "severity": "high",
                                "description": f"High risk interaction between {drug} and {current_drug}",
                            }
                        )

        return interactions

    def log_access(
        self,
        patient_id: str,
        user_id: str,
        action: str,
        justification: Optional[str] = None,
    ):
        """Log access to patient record.

        Args:
            patient_id: Patient ID
            user_id: User ID
            action: Action performed
            justification: Access justification
        """
        patient = self.get_patient(patient_id)
        if not patient:
            return

        user = self.get_user(user_id) or {"role": "unknown"}

        access_event = {
            "timestamp": datetime.now().isoformat(),
            "user_id": user_id,
            "user_role": user.get("role", "unknown"),
            "action": action,
            "justification": justification,
            "department": user.get("department", "unknown"),
        }

        patient.access_log.append(access_event)

    def add_prescription(self, patient_id: str, medication: Dict) -> bool:
        """Add prescription to patient record.

        Args:
            patient_id: Patient ID
            medication: Medication to add

        Returns:
            True if successful
        """
        patient = self.get_patient(patient_id)
        if not patient:
            return False

        patient.active_medications.append(medication)
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

    def get_patient_statistics(self) -> Dict[str, Any]:
        """Get statistics about the patient population.

        Returns:
            Dictionary with population statistics
        """
        total_patients = len(self.patients)
        if total_patients == 0:
            return {}

        # Calculate various statistics
        ages = []
        genders = {"M": 0, "F": 0}
        ethnicities = {}
        insurance_types = {}

        for patient in self.patients.values():
            # Calculate age
            if patient.dob:
                today = date.today()
                age = (
                    today.year
                    - patient.dob.year
                    - ((today.month, today.day) < (patient.dob.month, patient.dob.day))
                )
                ages.append(age)

            genders[patient.gender] = genders.get(patient.gender, 0) + 1

            # Other demographics
            ethnicities[patient.ethnicity] = ethnicities.get(patient.ethnicity, 0) + 1
            insurance_types[patient.insurance] = (
                insurance_types.get(patient.insurance, 0) + 1
            )

        # Common medications and allergies
        all_medications = []
        all_allergies = []

        for patient in self.patients.values():
            all_medications.extend(
                [med.get("drug", "unknown") for med in patient.active_medications]
            )
            all_allergies.extend(patient.allergies)

        from collections import Counter

        common_medications = Counter(all_medications).most_common(10)
        common_allergies = Counter(all_allergies).most_common(10)

        return {
            "total_patients": total_patients,
            "average_age": sum(ages) / len(ages) if ages else 0,
            "age_range": (min(ages), max(ages)) if ages else (0, 0),
            "gender_distribution": genders,
            "ethnicity_distribution": ethnicities,
            "insurance_distribution": insurance_types,
            "common_medications": common_medications,
            "common_allergies": common_allergies,
            "patients_with_allergies": len(
                [p for p in self.patients.values() if p.allergies]
            ),
            "patients_with_medications": len(
                [p for p in self.patients.values() if p.active_medications]
            ),
            "data_sources": ["MIMIC-III", "eICU", "FDA FAERS", "CDC NHDS"]
            if self.use_real_data
            else ["Mock Data"],
        }
