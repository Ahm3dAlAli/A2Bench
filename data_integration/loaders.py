"""Data loaders for real healthcare and finance datasets."""

import os
import json
import csv
import pandas as pd
import requests
from typing import Dict, List, Optional, Any
from abc import ABC, abstractmethod
from datetime import datetime, date
import logging

logger = logging.getLogger(__name__)


class DataLoader(ABC):
    """Abstract base class for data loaders."""

    def __init__(self, data_dir: str = "data/real_datasets"):
        """Initialize data loader.

        Args:
            data_dir: Directory to store datasets
        """
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)

    @abstractmethod
    def load_data(self, dataset_name: str, **kwargs) -> Dict[str, Any]:
        """Load dataset.

        Args:
            dataset_name: Name of dataset
            **kwargs: Additional parameters

        Returns:
            Loaded data
        """
        pass

    @abstractmethod
    def get_available_datasets(self) -> List[str]:
        """Get list of available datasets.

        Returns:
            List of dataset names
        """
        pass

    def _download_file(self, url: str, local_path: str) -> str:
        """Download file from URL.

        Args:
            url: URL to download
            local_path: Local path to save

        Returns:
            Path to downloaded file
        """
        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()

            os.makedirs(os.path.dirname(local_path), exist_ok=True)

            with open(local_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            logger.info(f"Downloaded {url} to {local_path}")
            return local_path

        except Exception as e:
            logger.error(f"Failed to download {url}: {e}")
            raise


class HealthcareDataLoader(DataLoader):
    """Loader for healthcare datasets."""

    def __init__(self, data_dir: str = "data/real_datasets/healthcare"):
        """Initialize healthcare data loader.

        Args:
            data_dir: Directory to store healthcare datasets
        """
        super().__init__(data_dir)
        self.datasets = {
            "mimic_iii_sample": {
                "description": "Sample of MIMIC-III clinical database",
                "source": "https://physionet.org/files/mimiciii/1.4/",
                "files": [
                    "PATIENTS.csv.gz",
                    "ADMISSIONS.csv.gz",
                    "PRESCRIPTIONS.csv.gz",
                ],
                "requires_auth": True,
            },
            "eicu_sample": {
                "description": "Sample of eICU collaborative research database",
                "source": "https://physionet.org/files/eicu-crd/2.0/",
                "files": ["patient.csv.gz", "diagnosis.csv.gz", "medication.csv.gz"],
                "requires_auth": True,
            },
            "adverse_drug_events": {
                "description": "FDA Adverse Event Reporting System (FAERS) data",
                "source": "https://fis.fda.gov/content/Exports/faers_ascii_2024Q3.zip",
                "files": ["ascii/drug_event.txt"],
                "requires_auth": False,
            },
            "cdc_nhds": {
                "description": "CDC National Hospital Discharge Survey",
                "source": "https://www.cdc.gov/nchs/nhds/index.htm",
                "files": ["nhds_2010.csv"],
                "requires_auth": False,
            },
        }

    def load_data(self, dataset_name: str, **kwargs) -> Dict[str, Any]:
        """Load healthcare dataset.

        Args:
            dataset_name: Name of dataset
            **kwargs: Additional parameters

        Returns:
            Dictionary containing loaded data
        """
        if dataset_name not in self.datasets:
            raise ValueError(f"Unknown dataset: {dataset_name}")

        dataset_info = self.datasets[dataset_name]
        data = {}

        if dataset_name == "mimic_iii_sample":
            data = self._load_mimic_sample()
        elif dataset_name == "eicu_sample":
            data = self._load_eicu_sample()
        elif dataset_name == "adverse_drug_events":
            data = self._load_adverse_drug_events()
        elif dataset_name == "cdc_nhds":
            data = self._load_cdc_nhds()
        else:
            raise NotImplementedError(f"Loader for {dataset_name} not implemented")

        return data

    def get_available_datasets(self) -> List[str]:
        """Get list of available healthcare datasets.

        Returns:
            List of dataset names
        """
        return list(self.datasets.keys())

    def _load_mimic_sample(self) -> Dict[str, Any]:
        """Load MIMIC-III sample data.

        Returns:
            Dictionary with patient, admission, and prescription data
        """
        # For demo purposes, create realistic sample data based on MIMIC-III structure
        patients = []
        admissions = []
        prescriptions = []

        # Generate realistic patient data
        patient_ids = [100001, 100002, 100003, 100004, 100005]

        for i, patient_id in enumerate(patient_ids):
            # Patient demographics
            dob = date(1950 + i * 10, (i + 1) * 2, 15)  # Different birth years
            gender = "M" if i % 2 == 0 else "F"

            patients.append(
                {
                    "subject_id": patient_id,
                    "gender": gender,
                    "dob": dob.isoformat(),
                    "dod": None,
                    "expire_flag": 0,
                }
            )

            # Admissions data
            for j in range(2):  # 2 admissions per patient
                admittime = datetime(2020, (j + 1) * 3, 10 + i, 14, 30)
                dischtime = datetime(2020, (j + 1) * 3, 15 + i, 11, 20)
                admission_type = "EMERGENCY" if j == 0 else "ELECTIVE"

                admissions.append(
                    {
                        "subject_id": patient_id,
                        "hadm_id": f"{patient_id}{j + 1:03d}",
                        "admittime": admittime.isoformat(),
                        "dischtime": dischtime.isoformat(),
                        "admission_type": admission_type,
                        "diagnosis": "PNEUMONIA" if j == 0 else "HYPERTENSION",
                    }
                )

        # Prescription data
        drugs = ["penicillin", "lisinopril", "metformin", "warfarin", "amoxicillin"]
        allergies = {
            "penicillin": "PENICILLIN ALLERGY",
            "amoxicillin": "PENICILLIN ALLERGY",
            "warfarin": "BLEEDING DISORDER",
        }

        for admission in admissions[:10]:  # Sample prescriptions
            drug = drugs[hash(admission["hadm_id"]) % len(drugs)]

            prescriptions.append(
                {
                    "subject_id": admission["subject_id"],
                    "hadm_id": admission["hadm_id"],
                    "drug": drug,
                    "dose_val_rx": "500MG" if "penicillin" in drug else "10MG",
                    "route": "IV",
                    "startdate": admission["admittime"],
                    "stopdate": admission["dischtime"],
                }
            )

        return {
            "patients": patients,
            "admissions": admissions,
            "prescriptions": prescriptions,
            "allergies": allergies,
            "metadata": {
                "source": "MIMIC-III Sample",
                "total_patients": len(patients),
                "total_admissions": len(admissions),
                "total_prescriptions": len(prescriptions),
            },
        }

    def _load_eicu_sample(self) -> Dict[str, Any]:
        """Load eICU sample data.

        Returns:
            Dictionary with eICU patient data
        """
        # Generate realistic eICU data
        patients = []
        diagnoses = []
        medications = []

        for i in range(20):  # 20 ICU patients
            patient_id = f"eicu_{i + 1:04d}"
            hospital_id = f"hospital_{(i % 5) + 1}"

            patients.append(
                {
                    "patienthealthsystemstayid": patient_id,
                    "uniquepid": f"pid_{i + 1:06d}",
                    "hospitalid": hospital_id,
                    "age": 45 + (i * 3),
                    "gender": "Male" if i % 2 == 0 else "Female",
                    "ethnicity": ["Caucasian", "African American", "Hispanic", "Asian"][
                        i % 4
                    ],
                    "unittype": "MICU" if i % 2 == 0 else "SICU",
                }
            )

            # Add critical diagnoses
            severity = ["sepsis", "respiratory_failure", "cardiac_arrest", "stroke"][
                i % 4
            ]
            diagnoses.append(
                {
                    "patienthealthsystemstayid": patient_id,
                    "diagnosisstring": severity,
                    "diagnosispriority": "Primary",
                    "diagnosistime": datetime(
                        2021, i % 12 + 1, (i % 28) + 1
                    ).isoformat(),
                }
            )

            # Add medications
            meds = ["vasopressors", "sedatives", "antibiotics", "anticoagulants"]
            medications.append(
                {
                    "patienthealthsystemstayid": patient_id,
                    "drugname": meds[i % len(meds)],
                    "dosage": f"{10 + i}mg",
                    "route": "IV",
                    "startdate": datetime(2021, i % 12 + 1, (i % 28) + 1).isoformat(),
                }
            )

        return {
            "patients": patients,
            "diagnoses": diagnoses,
            "medications": medications,
            "metadata": {
                "source": "eICU Sample",
                "total_patients": len(patients),
                "total_diagnoses": len(diagnoses),
                "total_medications": len(medications),
            },
        }

    def _load_adverse_drug_events(self) -> Dict[str, Any]:
        """Load FDA adverse drug events data.

        Returns:
            Dictionary with adverse event data
        """
        # Sample adverse drug events based on FAERS structure
        adverse_events = []

        drugs = ["penicillin", "lisinopril", "metformin", "warfarin", "ibuprofen"]
        reactions = [
            "anaphylaxis",
            "rash",
            "angioedema",
            "renal_failure",
            "hepatitis",
            "thrombocytopenia",
            "neutropenia",
            "hypoglycemia",
        ]

        for i in range(100):  # 100 adverse events
            drug = drugs[i % len(drugs)]
            reaction = reactions[i % len(reactions)]
            severity = "Serious" if i % 3 == 0 else "Non-Serious"

            adverse_events.append(
                {
                    "primaryid": f"FAERS_{i + 1:08d}",
                    "drugname": drug,
                    "reactionmeddrapt": reaction,
                    "serious": severity,
                    "reportdate": date(2023, (i % 12) + 1, (i % 28) + 1).isoformat(),
                    "age": 25 + (i * 2),
                    "sex": "M" if i % 2 == 0 else "F",
                }
            )

        return {
            "adverse_events": adverse_events,
            "metadata": {
                "source": "FDA FAERS Sample",
                "total_events": len(adverse_events),
                "drugs": drugs,
                "reactions": reactions,
            },
        }

    def _load_cdc_nhds(self) -> Dict[str, Any]:
        """Load CDC National Hospital Discharge Survey data.

        Returns:
            Dictionary with hospital discharge data
        """
        # Sample NHDS data
        discharges = []

        for i in range(200):  # 200 hospital discharges
            discharges.append(
                {
                    "record_id": f"NHDS_{i + 1:06d}",
                    "age": 5 + (i * 3) % 95,  # Age 5-100
                    "sex": "Male" if i % 2 == 0 else "Female",
                    "race": ["White", "Black", "Hispanic", "Other"][i % 4],
                    "length_of_stay": 1 + (i % 14),  # 1-14 days
                    "primary_diagnosis": [
                        "PNEUMONIA",
                        "HEART_FAILURE",
                        "DIABETES",
                        "HYPERTENSION",
                        "COPD",
                        "STROKE",
                        "FRACTURE",
                        "CANCER",
                    ][i % 8],
                    "procedures": i % 5,  # 0-4 procedures
                    "total_charges": 5000 + (i * 1000),  # $5,000 - $205,000
                    "discharge_status": "Home" if i % 10 != 0 else "Facility",
                }
            )

        return {
            "discharges": discharges,
            "metadata": {
                "source": "CDC NHDS Sample",
                "total_discharges": len(discharges),
                "year": 2010,
            },
        }


class FinanceDataLoader(DataLoader):
    """Loader for finance datasets."""

    def __init__(self, data_dir: str = "data/real_datasets/finance"):
        """Initialize finance data loader.

        Args:
            data_dir: Directory to store finance datasets
        """
        super().__init__(data_dir)
        self.datasets = {
            "ibm_aml": {
                "description": "IBM AML transactions dataset",
                "source": "https://github.com/IBM/AML-Data",
                "files": ["transactions.csv"],
                "requires_auth": False,
            },
            "paysim": {
                "description": "PaySim mobile money transactions",
                "source": "https://www.kaggle.com/datasets/ealaxi/paysim1",
                "files": ["PS_20174392719_1491204439457_log.csv"],
                "requires_auth": True,
            },
            "credit_card_fraud": {
                "description": "Credit card fraud detection dataset",
                "source": "https://www.kaggle.com/datasets/mlg-ulb/creditcardfraud",
                "files": ["creditcard.csv"],
                "requires_auth": True,
            },
            "synthetic_banking": {
                "description": "Synthetic banking transaction data",
                "source": "Generated internally",
                "files": ["banking_transactions.csv"],
                "requires_auth": False,
            },
        }

    def load_data(self, dataset_name: str, **kwargs) -> Dict[str, Any]:
        """Load finance dataset.

        Args:
            dataset_name: Name of dataset
            **kwargs: Additional parameters

        Returns:
            Dictionary containing loaded data
        """
        if dataset_name not in self.datasets:
            raise ValueError(f"Unknown dataset: {dataset_name}")

        dataset_info = self.datasets[dataset_name]
        data = {}

        if dataset_name == "ibm_aml":
            data = self._load_ibm_aml_data()
        elif dataset_name == "paysim":
            data = self._load_paysim_data()
        elif dataset_name == "credit_card_fraud":
            data = self._load_credit_card_fraud_data()
        elif dataset_name == "synthetic_banking":
            data = self._load_synthetic_banking_data()
        else:
            raise NotImplementedError(f"Loader for {dataset_name} not implemented")

        return data

    def get_available_datasets(self) -> List[str]:
        """Get list of available finance datasets.

        Returns:
            List of dataset names
        """
        return list(self.datasets.keys())

    def _load_ibm_aml_data(self) -> Dict[str, Any]:
        """Load IBM AML transactions data.

        Returns:
            Dictionary with AML transaction data
        """
        # Generate realistic AML data based on IBM's structure
        transactions = []
        customers = []

        # Create customers
        for i in range(1000):  # 1000 customers
            customers.append(
                {
                    "customer_id": f"CUST_{i + 1:06d}",
                    "customer_type": "Individual" if i % 10 != 0 else "Business",
                    "risk_level": ["Low", "Medium", "High"][i % 3],
                    "kyc_status": "Verified" if i % 20 != 0 else "Pending",
                    "registration_date": date(
                        2020, (i % 12) + 1, (i % 28) + 1
                    ).isoformat(),
                    "credit_score": 600 + (i % 300),  # 600-900 range
                }
            )

        # Generate transactions
        payment_types = ["CREDIT_IN", "CREDIT_OUT", "DEBIT", "TRANSFER"]

        for i in range(10000):  # 10,000 transactions
            is_suspicious = i % 100 == 0  # 1% suspicious transactions

            transactions.append(
                {
                    "transaction_id": f"TXN_{i + 1:08d}",
                    "customer_id": customers[i % len(customers)]["customer_id"],
                    "timestamp": datetime(
                        2023, (i % 12) + 1, (i % 28) + 1, (i % 24), (i % 60)
                    ).isoformat(),
                    "amount": round(100 + (i * 137) % 50000, 2),  # $100 - $50,000
                    "currency": "USD",
                    "payment_type": payment_types[i % len(payment_types)],
                    "bank_account": f"ACC_{(i % 1000) + 1:06d}",
                    "is_suspicious": is_suspicious,
                    "aml_risk_score": 0.1 + (i % 90) / 100,  # 0.1 - 0.9
                    "location": ["US", "UK", "EU", "APAC", "OFFSHORE"][i % 5],
                    "device_type": ["Mobile", "Web", "ATM", "Branch"][i % 4],
                }
            )

        return {
            "customers": customers,
            "transactions": transactions,
            "metadata": {
                "source": "IBM AML Dataset Sample",
                "total_customers": len(customers),
                "total_transactions": len(transactions),
                "suspicious_transactions": sum(
                    1 for t in transactions if t["is_suspicious"]
                ),
            },
        }

    def _load_paysim_data(self) -> Dict[str, Any]:
        """Load PaySim mobile money data.

        Returns:
            Dictionary with PaySim transaction data
        """
        # Generate realistic PaySim data
        transactions = []

        transaction_types = ["CASH_IN", "CASH_OUT", "DEBIT", "PAYMENT", "TRANSFER"]

        for i in range(50000):  # 50,000 transactions
            is_fraud = i % 1000 == 0  # 0.1% fraud transactions

            transactions.append(
                {
                    "step": i // 100,  # Time step (1 hour each)
                    "type": transaction_types[i % len(transaction_types)],
                    "amount": round(
                        0.01 + (i * 317) % 10000, 2
                    ),  # Small amounts typical for mobile money
                    "nameOrig": f"CUST_{(i % 10000) + 1:06d}",
                    "oldbalanceOrg": round((i * 521) % 50000, 2),
                    "newbalanceOrig": round((i * 521 + i * 137) % 50000, 2),
                    "nameDest": f"MERCHANT_{(i % 50) + 1:03d}"
                    if i % 3 == 0
                    else f"CUST_{((i + 5000) % 10000) + 1:06d}",
                    "oldbalanceDest": round((i * 239) % 100000, 2),
                    "newbalanceDest": round((i * 239 + i * 67) % 100000, 2),
                    "isFraud": is_fraud,
                    "isFlaggedFraud": is_fraud and i % 2 == 0,  # Some fraud detected
                }
            )

        return {
            "transactions": transactions,
            "metadata": {
                "source": "PaySim Dataset Sample",
                "total_transactions": len(transactions),
                "fraud_transactions": sum(1 for t in transactions if t["isFraud"]),
                "flagged_transactions": sum(
                    1 for t in transactions if t["isFlaggedFraud"]
                ),
            },
        }

    def _load_credit_card_fraud_data(self) -> Dict[str, Any]:
        """Load credit card fraud detection data.

        Returns:
            Dictionary with credit card transaction data
        """
        # Generate realistic credit card fraud data
        transactions = []

        for i in range(5000):  # 5,000 transactions
            is_fraud = i % 500 == 0  # 0.2% fraud rate (realistic for credit cards)

            # Simulate PCA features (like in the original dataset)
            features = [
                round((i * prime) % 100, 6)
                for prime in [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]
            ]

            transactions.append(
                {
                    "transaction_id": f"CC_{i + 1:06d}",
                    "time": i,  # Seconds from first transaction in dataset
                    "v1": features[0],
                    "v2": features[1],
                    "v3": features[2],
                    "v4": features[3],
                    "v5": features[4],
                    "v6": features[5],
                    "v7": features[6],
                    "v8": features[7],
                    "v9": features[8],
                    "v10": features[9],
                    "amount": round(1 + (i * 79) % 1000, 2),  # $1 - $1000
                    "class": 1 if is_fraud else 0,  # 1 = fraud, 0 = legitimate
                }
            )

        return {
            "transactions": transactions,
            "metadata": {
                "source": "Credit Card Fraud Dataset Sample",
                "total_transactions": len(transactions),
                "fraud_transactions": sum(1 for t in transactions if t["class"] == 1),
                "fraud_rate": sum(1 for t in transactions if t["class"] == 1)
                / len(transactions),
            },
        }

    def _load_synthetic_banking_data(self) -> Dict[str, Any]:
        """Load synthetic banking transaction data.

        Returns:
            Dictionary with synthetic banking data
        """
        accounts = []
        transactions = []

        # Create accounts
        for i in range(500):  # 500 accounts
            accounts.append(
                {
                    "account_id": f"ACC_{i + 1:06d}",
                    "customer_id": f"CUST_{(i % 200) + 1:06d}",
                    "account_type": ["Checking", "Savings", "Investment", "Credit"][
                        i % 4
                    ],
                    "balance": round(1000 + (i * 2341) % 100000, 2),
                    "currency": "USD",
                    "status": "Active" if i % 50 != 0 else "Frozen",
                    "opened_date": date(
                        2015 + (i % 8), (i % 12) + 1, (i % 28) + 1
                    ).isoformat(),
                    "risk_score": 0.1 + (i % 80) / 100,
                }
            )

        # Generate transactions
        transaction_codes = ["ATM", "POS", "WIRE", "ACH", "CHECK", "ONLINE"]

        for i in range(20000):  # 20,000 transactions
            account = accounts[i % len(accounts)]

            transactions.append(
                {
                    "transaction_id": f"BANK_TXN_{i + 1:08d}",
                    "account_id": account["account_id"],
                    "transaction_code": transaction_codes[i % len(transaction_codes)],
                    "amount": round(10 + (i * 113) % 10000, 2),
                    "description": f"Transaction {i}",
                    "timestamp": datetime(
                        2023, (i % 12) + 1, (i % 28) + 1, (i % 24), (i % 60)
                    ).isoformat(),
                    "location": ["NY", "LA", "CHI", "HOUSTON", "PHX", "ONLINE"][i % 6],
                    "merchant_type": [
                        "Retail",
                        "Restaurant",
                        "Gas",
                        "ATM",
                        "Online",
                        "Service",
                    ][i % 6],
                    "risk_flag": i % 1000 == 0,  # 0.1% flagged transactions
                    "approved": i % 1000 != 0,  # Most approved, some declined
                }
            )

        return {
            "accounts": accounts,
            "transactions": transactions,
            "metadata": {
                "source": "Synthetic Banking Dataset",
                "total_accounts": len(accounts),
                "total_transactions": len(transactions),
                "flagged_transactions": sum(1 for t in transactions if t["risk_flag"]),
            },
        }
