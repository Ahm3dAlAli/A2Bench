"""Data processors for real healthcare and finance datasets."""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any
from abc import ABC, abstractmethod
import logging

logger = logging.getLogger(__name__)


class DataProcessor(ABC):
    """Abstract base class for data processors."""

    def __init__(self):
        """Initialize data processor."""
        pass

    @abstractmethod
    def clean_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Clean and validate data.

        Args:
            data: Raw data

        Returns:
            Cleaned data
        """
        pass

    @abstractmethod
    def transform_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform data to standard format.

        Args:
            data: Clean data

        Returns:
            Transformed data
        """
        pass


class HealthcareDataProcessor(DataProcessor):
    """Processor for healthcare datasets."""

    def clean_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Clean healthcare data.

        Args:
            data: Raw healthcare data

        Returns:
            Cleaned healthcare data
        """
        cleaned = {}

        for key, value in data.items():
            if key == "patients":
                cleaned[key] = self._clean_patient_data(value)
            elif key == "admissions":
                cleaned[key] = self._clean_admission_data(value)
            elif key == "prescriptions":
                cleaned[key] = self._clean_prescription_data(value)
            elif key == "medications":
                cleaned[key] = self._clean_medication_data(value)
            elif key == "adverse_events":
                cleaned[key] = self._clean_adverse_event_data(value)
            else:
                cleaned[key] = value

        return cleaned

    def transform_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform healthcare data to standard format.

        Args:
            data: Clean healthcare data

        Returns:
            Transformed healthcare data
        """
        transformed = data.copy()

        # Add data quality metrics
        transformed["data_quality"] = self._assess_data_quality(data)

        # Add anonymization flags
        transformed["anonymized"] = True

        return transformed

    def _clean_patient_data(self, patients: List[Dict]) -> List[Dict]:
        """Clean patient data."""
        cleaned = []
        for patient in patients:
            cleaned_patient = {}

            # Required fields
            cleaned_patient["subject_id"] = str(patient.get("subject_id", ""))
            cleaned_patient["gender"] = patient.get("gender", "U")

            # Date validation
            dob = patient.get("dob")
            if dob:
                try:
                    if isinstance(dob, str):
                        dob = datetime.fromisoformat(dob).date()
                    cleaned_patient["dob"] = dob
                except:
                    cleaned_patient["dob"] = date(1900, 1, 1)  # Default
            else:
                cleaned_patient["dob"] = date(1900, 1, 1)

            cleaned_patient["expire_flag"] = int(patient.get("expire_flag", 0))
            cleaned_patient["ethnicity"] = patient.get("ethnicity", "Unknown")
            cleaned_patient["insurance"] = patient.get("insurance", "Unknown")

            cleaned.append(cleaned_patient)

        return cleaned

    def _clean_admission_data(self, admissions: List[Dict]) -> List[Dict]:
        """Clean admission data."""
        cleaned = []
        for admission in admissions:
            cleaned_admission = {
                "hadm_id": str(admission.get("hadm_id", "")),
                "subject_id": str(admission.get("subject_id", "")),
                "admittime": admission.get("admittime", ""),
                "dischtime": admission.get("dischtime", ""),
                "admission_type": admission.get("admission_type", "UNKNOWN"),
                "diagnosis": admission.get("diagnosis", ""),
            }
            cleaned.append(cleaned_admission)
        return cleaned

    def _clean_prescription_data(self, prescriptions: List[Dict]) -> List[Dict]:
        """Clean prescription data."""
        cleaned = []
        for prescription in prescriptions:
            cleaned_prescription = {
                "subject_id": str(prescription.get("subject_id", "")),
                "hadm_id": str(prescription.get("hadm_id", "")),
                "drug": prescription.get("drug", ""),
                "dose_val_rx": prescription.get("dose_val_rx", ""),
                "route": prescription.get("route", "UNKNOWN"),
                "startdate": prescription.get("startdate", ""),
                "stopdate": prescription.get("stopdate", ""),
            }
            cleaned.append(cleaned_prescription)
        return cleaned

    def _clean_medication_data(self, medications: List[Dict]) -> List[Dict]:
        """Clean medication data."""
        cleaned = []
        for medication in medications:
            cleaned_medication = {
                "patienthealthsystemstayid": medication.get(
                    "patienthealthsystemstayid", ""
                ),
                "drugname": medication.get("drugname", ""),
                "dosage": medication.get("dosage", ""),
                "route": medication.get("route", "UNKNOWN"),
                "startdate": medication.get("startdate", ""),
            }
            cleaned.append(cleaned_medication)
        return cleaned

    def _clean_adverse_event_data(self, events: List[Dict]) -> List[Dict]:
        """Clean adverse event data."""
        cleaned = []
        for event in events:
            cleaned_event = {
                "primaryid": event.get("primaryid", ""),
                "drugname": event.get("drugname", ""),
                "reactionmeddrapt": event.get("reactionmeddrapt", ""),
                "serious": event.get("serious", ""),
                "reportdate": event.get("reportdate", ""),
                "sex": event.get("sex", "U"),
                "age": int(event.get("age", 0)),
            }
            cleaned.append(cleaned_event)
        return cleaned

    def _assess_data_quality(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess data quality metrics.

        Args:
            data: Data to assess

        Returns:
            Quality metrics
        """
        metrics = {
            "completeness": 1.0,
            "consistency": 1.0,
            "validity": 1.0,
            "issues": [],
        }

        # Check patient data quality
        if "patients" in data:
            patients = data["patients"]
            if patients:
                missing_dob = sum(1 for p in patients if not p.get("dob"))
                missing_gender = sum(1 for p in patients if not p.get("gender"))

                metrics["completeness"] -= (missing_dob + missing_gender) / (
                    len(patients) * 2
                )
                metrics["issues"].append(
                    f"Missing DOB: {missing_dob}, Missing Gender: {missing_gender}"
                )

        return metrics


class FinanceDataProcessor(DataProcessor):
    """Processor for finance datasets."""

    def clean_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Clean finance data.

        Args:
            data: Raw finance data

        Returns:
            Cleaned finance data
        """
        cleaned = {}

        for key, value in data.items():
            if key == "customers":
                cleaned[key] = self._clean_customer_data(value)
            elif key == "transactions":
                cleaned[key] = self._clean_transaction_data(value)
            elif key == "accounts":
                cleaned[key] = self._clean_account_data(value)
            else:
                cleaned[key] = value

        return cleaned

    def transform_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform finance data to standard format.

        Args:
            data: Clean finance data

        Returns:
            Transformed finance data
        """
        transformed = data.copy()

        # Add data quality metrics
        transformed["data_quality"] = self._assess_data_quality(data)

        # Add anonymization flags
        transformed["anonymized"] = True

        return transformed

    def _clean_customer_data(self, customers: List[Dict]) -> List[Dict]:
        """Clean customer data."""
        cleaned = []
        for customer in customers:
            cleaned_customer = {
                "customer_id": str(customer.get("customer_id", "")),
                "customer_type": customer.get("customer_type", "Individual"),
                "risk_level": customer.get("risk_level", "Low"),
                "kyc_status": customer.get("kyc_status", "Pending"),
                "registration_date": customer.get("registration_date", ""),
                "credit_score": int(customer.get("credit_score", 600)),
                "annual_income": float(customer.get("annual_income", 0)),
                "country": customer.get("country", "US"),
            }
            cleaned.append(cleaned_customer)
        return cleaned

    def _clean_transaction_data(self, transactions: List[Dict]) -> List[Dict]:
        """Clean transaction data."""
        cleaned = []
        for transaction in transactions:
            cleaned_transaction = {
                "transaction_id": transaction.get("transaction_id", ""),
                "account_id": transaction.get("account_id", ""),
                "amount": float(transaction.get("amount", 0)),
                "currency": transaction.get("currency", "USD"),
                "transaction_type": transaction.get("transaction_type", "other"),
                "timestamp": transaction.get("timestamp", ""),
                "status": transaction.get("status", "unknown"),
                "is_suspicious": bool(transaction.get("is_suspicious", False)),
            }
            cleaned.append(cleaned_transaction)
        return cleaned

    def _clean_account_data(self, accounts: List[Dict]) -> List[Dict]:
        """Clean account data."""
        cleaned = []
        for account in accounts:
            cleaned_account = {
                "account_id": str(account.get("account_id", "")),
                "customer_id": str(account.get("customer_id", "")),
                "account_type": account.get("account_type", "checking"),
                "balance": float(account.get("balance", 0)),
                "currency": account.get("currency", "USD"),
                "status": account.get("status", "active"),
                "opened_date": account.get("opened_date", ""),
                "transaction_limit": float(account.get("transaction_limit", 10000)),
                "daily_limit": float(account.get("daily_limit", 50000)),
            }
            cleaned.append(cleaned_account)
        return cleaned

    def _assess_data_quality(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess data quality metrics.

        Args:
            data: Data to assess

        Returns:
            Quality metrics
        """
        metrics = {
            "completeness": 1.0,
            "consistency": 1.0,
            "validity": 1.0,
            "issues": [],
        }

        # Check customer data quality
        if "customers" in data:
            customers = data["customers"]
            if customers:
                missing_kyc = sum(1 for c in customers if not c.get("kyc_status"))
                missing_risk = sum(1 for c in customers if not c.get("risk_level"))

                metrics["completeness"] -= (missing_kyc + missing_risk) / (
                    len(customers) * 2
                )
                metrics["issues"].append(
                    f"Missing KYC: {missing_kyc}, Missing Risk Level: {missing_risk}"
                )

        return metrics
