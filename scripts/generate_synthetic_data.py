"""Generate realistic synthetic datasets for A2Bench experiments."""

import json
import random
import csv
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict
import numpy as np

# Base paths
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"


def generate_patient_data(num_patients: int = 100) -> List[Dict]:
    """Generate synthetic patient data similar to Synthea output."""

    first_names = ["John", "Mary", "James", "Patricia", "Robert", "Jennifer", "Michael", "Linda",
                   "William", "Elizabeth", "David", "Barbara", "Richard", "Susan", "Joseph", "Jessica"]
    last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
                  "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson"]

    # Common medications
    medications = [
        "lisinopril", "metformin", "atorvastatin", "levothyroxine", "metoprolol",
        "amlodipine", "omeprazole", "simvastatin", "losartan", "gabapentin"
    ]

    # Common allergies with cross-reactions
    allergies = {
        "penicillin": ["amoxicillin", "ampicillin", "penicillin"],
        "sulfa": ["sulfamethoxazole", "sulfasalazine"],
        "nsaid": ["ibuprofen", "naproxen", "aspirin"],
        "none": []
    }

    patients = []

    for i in range(num_patients):
        patient_id = f"P{i+1:04d}"
        age = random.randint(18, 85)
        allergy_type = random.choice(list(allergies.keys()))

        # Generate current medications (more likely if older)
        num_meds = min(random.choices([0, 1, 2, 3, 4], weights=[20, 30, 25, 15, 10])[0],
                      int(age / 20))
        current_meds = random.sample(medications, num_meds) if num_meds > 0 else []

        patient = {
            "id": patient_id,
            "first_name": random.choice(first_names),
            "last_name": random.choice(last_names),
            "date_of_birth": (datetime.now() - timedelta(days=age*365)).strftime("%Y-%m-%d"),
            "age": age,
            "gender": random.choice(["M", "F"]),
            "allergies": allergies[allergy_type],
            "current_medications": current_meds,
            "conditions": [],
            "last_visit": (datetime.now() - timedelta(days=random.randint(1, 365))).strftime("%Y-%m-%d")
        }

        # Add conditions based on age and medications
        if "metformin" in current_meds:
            patient["conditions"].append("Type 2 Diabetes")
        if "lisinopril" in current_meds or "metoprolol" in current_meds:
            patient["conditions"].append("Hypertension")
        if "atorvastatin" in current_meds or "simvastatin" in current_meds:
            patient["conditions"].append("Hyperlipidemia")

        patients.append(patient)

    return patients


def generate_financial_transactions(num_transactions: int = 1000) -> List[Dict]:
    """Generate synthetic financial transaction data."""

    transaction_types = [
        "debit", "credit", "wire_transfer", "international_transfer",
        "check", "atm_withdrawal", "pos_purchase"
    ]

    merchant_categories = [
        "groceries", "gas_station", "restaurant", "retail", "online_shopping",
        "utilities", "healthcare", "travel", "entertainment"
    ]

    countries = ["US", "GB", "DE", "FR", "CA", "MX", "JP", "CN", "IN", "BR"]
    risk_countries = ["RU", "KP", "IR", "SY"]  # High-risk for AML

    transactions = []
    customers = [f"C{i:04d}" for i in range(1, 51)]  # 50 customers
    accounts = [f"ACC{i:05d}" for i in range(1, 101)]  # 100 accounts

    # Generate normal and suspicious transactions
    for i in range(num_transactions):
        trans_id = f"T{i+1:06d}"
        customer_id = random.choice(customers)
        account_id = random.choice(accounts)
        trans_type = random.choice(transaction_types)

        # Base transaction amount
        if trans_type == "pos_purchase":
            amount = round(random.uniform(5, 500), 2)
        elif trans_type == "atm_withdrawal":
            amount = round(random.choices([20, 40, 60, 80, 100, 200, 500],
                                        weights=[20, 25, 20, 15, 10, 7, 3])[0], 2)
        elif trans_type in ["wire_transfer", "international_transfer"]:
            amount = round(random.uniform(100, 50000), 2)
        else:
            amount = round(random.uniform(10, 10000), 2)

        # Determine if fraudulent/suspicious (5% of transactions)
        is_suspicious = random.random() < 0.05

        if is_suspicious:
            # Make it more suspicious
            if trans_type == "international_transfer":
                amount = round(random.uniform(50000, 150000), 2)
                country = random.choice(risk_countries)
            else:
                amount *= random.uniform(5, 20)  # Unusually large amount
                country = "US"
        else:
            country = "US" if trans_type != "international_transfer" else random.choice(countries)

        # Calculate risk score
        risk_score = 0.0

        if amount > 10000:
            risk_score += 0.3
        if amount > 50000:
            risk_score += 0.3
        if country in risk_countries:
            risk_score += 0.4
        if trans_type == "international_transfer":
            risk_score += 0.1

        # Add structuring pattern detection
        if 9000 < amount < 10000:  # Just under reporting threshold
            risk_score += 0.2

        risk_score = min(risk_score, 1.0)

        transaction = {
            "transaction_id": trans_id,
            "customer_id": customer_id,
            "account_id": account_id,
            "timestamp": (datetime.now() - timedelta(days=random.randint(0, 365),
                                                    hours=random.randint(0, 23),
                                                    minutes=random.randint(0, 59))).isoformat(),
            "transaction_type": trans_type,
            "amount": amount,
            "currency": "USD",
            "merchant_category": random.choice(merchant_categories) if trans_type == "pos_purchase" else None,
            "country": country,
            "risk_score": round(risk_score, 3),
            "is_fraudulent": is_suspicious,
            "requires_kyc": amount > 10000,
            "requires_aml_screening": trans_type == "international_transfer" or amount > 10000
        }

        transactions.append(transaction)

    return transactions


def generate_customer_data(num_customers: int = 50) -> List[Dict]:
    """Generate synthetic customer data for finance domain."""

    customers = []

    for i in range(num_customers):
        customer_id = f"C{i+1:04d}"

        # KYC status (90% verified)
        kyc_verified = random.random() < 0.9

        # Account status
        account_status = random.choices(
            ["active", "suspended", "closed"],
            weights=[85, 10, 5]
        )[0]

        # Risk tier
        risk_tier = random.choices(
            ["low", "medium", "high"],
            weights=[70, 25, 5]
        )[0]

        customer = {
            "customer_id": customer_id,
            "kyc_verified": kyc_verified,
            "kyc_verification_date": (datetime.now() - timedelta(days=random.randint(30, 1000))).strftime("%Y-%m-%d") if kyc_verified else None,
            "account_status": account_status,
            "risk_tier": risk_tier,
            "customer_since": (datetime.now() - timedelta(days=random.randint(365, 3650))).strftime("%Y-%m-%d"),
            "country": random.choices(["US", "GB", "CA", "DE"], weights=[70, 15, 10, 5])[0],
            "daily_transaction_limit": random.choice([5000, 10000, 25000, 50000, 100000]),
            "monthly_transaction_limit": random.choice([50000, 100000, 250000, 500000])
        }

        customers.append(customer)

    return customers


def save_datasets():
    """Generate and save all datasets."""

    print("Generating synthetic datasets...")

    # Healthcare data
    print("  Generating patient data...")
    patients = generate_patient_data(100)
    healthcare_dir = DATA_DIR / "healthcare" / "real_data"
    healthcare_dir.mkdir(parents=True, exist_ok=True)

    with open(healthcare_dir / "patients.json", 'w') as f:
        json.dump(patients, f, indent=2)
    print(f"    ✓ Saved {len(patients)} patients to {healthcare_dir / 'patients.json'}")

    # Finance data
    print("  Generating financial transaction data...")
    transactions = generate_financial_transactions(1000)
    finance_dir = DATA_DIR / "finance" / "real_data"
    finance_dir.mkdir(parents=True, exist_ok=True)

    with open(finance_dir / "transactions.json", 'w') as f:
        json.dump(transactions, f, indent=2)
    print(f"    ✓ Saved {len(transactions)} transactions to {finance_dir / 'transactions.json'}")

    # Also save as CSV for compatibility
    with open(finance_dir / "transactions.csv", 'w', newline='') as f:
        if transactions:
            writer = csv.DictWriter(f, fieldnames=transactions[0].keys())
            writer.writeheader()
            writer.writerows(transactions)
    print(f"    ✓ Saved transactions to {finance_dir / 'transactions.csv'}")

    print("  Generating customer data...")
    customers = generate_customer_data(50)

    with open(finance_dir / "customers.json", 'w') as f:
        json.dump(customers, f, indent=2)
    print(f"    ✓ Saved {len(customers)} customers to {finance_dir / 'customers.json'}")

    # Generate summary statistics
    print("\nDataset Statistics:")
    print(f"  Healthcare:")
    print(f"    - Patients: {len(patients)}")
    print(f"    - Patients with allergies: {sum(1 for p in patients if p['allergies'])}")
    print(f"    - Patients on medications: {sum(1 for p in patients if p['current_medications'])}")

    print(f"  Finance:")
    print(f"    - Transactions: {len(transactions)}")
    print(f"    - Suspicious transactions: {sum(1 for t in transactions if t['is_fraudulent'])}")
    print(f"    - High-risk transactions: {sum(1 for t in transactions if t['risk_score'] > 0.7)}")
    print(f"    - Transactions requiring KYC: {sum(1 for t in transactions if t['requires_kyc'])}")
    print(f"    - Customers: {len(customers)}")
    print(f"    - KYC verified customers: {sum(1 for c in customers if c['kyc_verified'])}")

    print("\n✓ All datasets generated successfully!")


if __name__ == "__main__":
    save_datasets()
