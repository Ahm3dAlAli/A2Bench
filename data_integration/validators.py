"""Data validators for real healthcare and finance datasets."""

from typing import Dict, List, Optional, Any
from abc import ABC, abstractmethod
import logging

logger = logging.getLogger(__name__)


class DataValidator(ABC):
    """Abstract base class for data validators."""

    def __init__(self):
        """Initialize data validator."""
        pass

    @abstractmethod
    def validate_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate data structure and content.

        Args:
            data: Data to validate

        Returns:
            Validation results
        """
        pass


class HealthcareDataValidator(DataValidator):
    """Validator for healthcare datasets."""

    def validate_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate healthcare data structure and content.

        Args:
            data: Data to validate

        Returns:
            Validation results
        """
        results = {"is_valid": True, "errors": [], "warnings": [], "statistics": {}}

        # Validate required fields
        required_sections = ["metadata"]
        for section in required_sections:
            if section not in data:
                results["is_valid"] = False
                results["errors"].append(f"Missing required section: {section}")

        # Validate patient data if present
        if "patients" in data:
            patient_validation = self._validate_patients(data["patients"])
            results.update(patient_validation)

        # Validate demographics
        if "patients" in data:
            demo_validation = self._validate_demographics(data["patients"])
            results.update(demo_validation)

        return results

    def _validate_patients(self, patients: List[Dict]) -> Dict[str, Any]:
        """Validate patient data structure.

        Args:
            patients: Patient data list

        Returns:
            Validation results
        """
        results = {
            "total_patients": len(patients),
            "valid_patients": 0,
            "invalid_patients": 0,
            "missing_required_fields": [],
        }

        required_fields = ["subject_id", "gender", "dob"]

        for patient in patients:
            patient_valid = True
            for field in required_fields:
                if field not in patient or not patient[field]:
                    patient_valid = False
                    results["missing_required_fields"].append(
                        f"Patient missing {field}"
                    )

            if patient_valid:
                results["valid_patients"] += 1
            else:
                results["invalid_patients"] += 1

        if results["invalid_patients"] > 0:
            results["is_valid"] = False
            results["errors"].append(f"{results['invalid_patients']} invalid patients")

        return results

    def _validate_demographics(self, patients: List[Dict]) -> Dict[str, Any]:
        """Validate patient demographics.

        Args:
            patients: Patient data list

        Returns:
            Demographics validation results
        """
        results = {
            "gender_distribution": {"M": 0, "F": 0, "U": 0},
            "age_distribution": {},
            "age_issues": 0,
        }

        for patient in patients:
            # Validate gender
            gender = patient.get("gender", "U")
            if gender in results["gender_distribution"]:
                results["gender_distribution"][gender] += 1
            else:
                results["gender_distribution"]["U"] += 1

            # Validate age range
            dob = patient.get("dob")
            if dob:
                try:
                    from datetime import date

                    if isinstance(dob, str):
                        dob = date.fromisoformat(dob)
                    today = date.today()
                    age = today.year - dob.year
                    if age < 0 or age > 120:
                        results["age_issues"] += 1
                except:
                    results["age_issues"] += 1
                    results["age_distribution"]["invalid"] = (
                        results.get("age_distribution", {}).get("invalid", 0) + 1
                    )
                else:
                    results["age_distribution"]["missing"] = (
                        results.get("age_distribution", {}).get("missing", 0) + 1
                    )
            else:
                results["age_distribution"]["missing"] = (
                    results.get("age_distribution", {}).get("missing", 0) + 1
                )

        return results


class FinanceDataValidator(DataValidator):
    """Validator for finance datasets."""

    def validate_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate finance data structure and content.

        Args:
            data: Data to validate

        Returns:
            Validation results
        """
        results = {"is_valid": True, "errors": [], "warnings": [], "statistics": {}}

        # Validate required fields
        required_sections = ["metadata"]
        for section in required_sections:
            if section not in data:
                results["is_valid"] = False
                results["errors"].append(f"Missing required section: {section}")

        # Validate customer data if present
        if "customers" in data:
            customer_validation = self._validate_customers(data["customers"])
            results.update(customer_validation)

        # Validate transaction patterns
        if "transactions" in data:
            transaction_validation = self._validate_transactions(data["transactions"])
            results.update(transaction_validation)

        return results

    def _validate_customers(self, customers: List[Dict]) -> Dict[str, Any]:
        """Validate customer data structure.

        Args:
            customers: Customer data list

        Returns:
            Validation results
        """
        results = {
            "total_customers": len(customers),
            "valid_customers": 0,
            "invalid_customers": 0,
            "missing_required_fields": [],
            "kyc_status_distribution": {},
        }

        required_fields = ["customer_id", "customer_type", "risk_level", "kyc_status"]

        for customer in customers:
            customer_valid = True
            for field in required_fields:
                if field not in customer or not customer[field]:
                    customer_valid = False
                    results["missing_required_fields"].append(
                        f"Customer missing {field}"
                    )

            # Validate KYC status
            kyc_status = customer.get("kyc_status", "Unknown")
            results["kyc_status_distribution"][kyc_status] = (
                results["kyc_status_distribution"].get(kyc_status, 0) + 1
            )

            # Validate risk level
            risk_level = customer.get("risk_level", "Unknown")
            if risk_level not in ["Low", "Medium", "High"]:
                results["warnings"].append(f"Unknown risk level: {risk_level}")

            if customer_valid:
                results["valid_customers"] += 1
            else:
                results["invalid_customers"] += 1

        if results["invalid_customers"] > 0:
            results["is_valid"] = False
            results["errors"].append(
                f"{results['invalid_customers']} invalid customers"
            )

        return results

    def _validate_transactions(self, transactions: List[Dict]) -> Dict[str, Any]:
        """Validate transaction data structure.

        Args:
            transactions: Transaction data list

        Returns:
            Validation results
        """
        results = {
            "total_transactions": len(transactions),
            "valid_transactions": 0,
            "invalid_transactions": 0,
            "missing_required_fields": [],
            "amount_issues": 0,
            "suspicious_count": 0,
        }

        required_fields = ["transaction_id", "amount", "currency", "transaction_type"]

        for transaction in transactions:
            transaction_valid = True

            # Check required fields
            for field in required_fields:
                if field not in transaction:
                    transaction_valid = False
                    results["missing_required_fields"].append(
                        f"Transaction missing {field}"
                    )

            # Validate amount
            amount = transaction.get("amount")
            if not isinstance(amount, (int, float)) or amount < 0:
                transaction_valid = False
                results["amount_issues"] += 1

            # Check for suspicious transactions
            if transaction.get("is_suspicious", False):
                results["suspicious_count"] += 1

            if transaction_valid:
                results["valid_transactions"] += 1
            else:
                results["invalid_transactions"] += 1

        if results["invalid_transactions"] > 0:
            results["is_valid"] = False
            results["errors"].append(
                f"{results['invalid_transactions']} invalid transactions"
            )

        # Calculate fraud rate
        if results["total_transactions"] > 0:
            results["fraud_rate"] = (
                results["suspicious_count"] / results["total_transactions"]
            )
        else:
            results["fraud_rate"] = 0.0

        return results
