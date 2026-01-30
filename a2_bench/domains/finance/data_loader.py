"""Data loader for real Kaggle credit card fraud dataset."""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import random


class CreditCardDataLoader:
    """Loads and manages real credit card fraud dataset from Kaggle."""

    def __init__(self, data_path: Optional[str] = None):
        """Initialize data loader.

        Args:
            data_path: Path to creditcard_2023.csv file
        """
        if data_path is None:
            # Default path
            data_path = Path(__file__).parent.parent.parent.parent / "data" / "downloads" / "credit_card_fraud_2023" / "creditcard_2023.csv"

        self.data_path = Path(data_path)
        self.df = None
        self._load_data()

    def _load_data(self):
        """Load credit card dataset."""
        if not self.data_path.exists():
            raise FileNotFoundError(
                f"Credit card dataset not found at {self.data_path}. "
                f"Please run scripts/download_real_datasets.py first."
            )

        print(f"Loading credit card dataset from {self.data_path}...")
        # Load only first 50k rows for faster processing
        self.df = pd.read_csv(self.data_path, nrows=50000)
        print(f"Loaded {len(self.df)} transactions ({self.df['Class'].sum()} fraudulent)")

    def get_random_transaction(
        self,
        min_amount: float = 10.0,
        max_amount: float = 10000.0,
        fraud: Optional[bool] = None
    ) -> Dict:
        """Get a random transaction from the dataset.

        Args:
            min_amount: Minimum transaction amount
            max_amount: Maximum transaction amount
            fraud: If True, return fraudulent transaction; if False, return normal; if None, random

        Returns:
            Transaction dict with features and metadata
        """
        # Filter by amount
        filtered = self.df[
            (self.df['Amount'] >= min_amount) &
            (self.df['Amount'] <= max_amount)
        ]

        # Filter by fraud label if specified
        if fraud is not None:
            filtered = filtered[filtered['Class'] == (1 if fraud else 0)]

        if len(filtered) == 0:
            # Fallback: just get any transaction
            filtered = self.df

        # Sample one transaction
        row = filtered.sample(n=1).iloc[0]

        return {
            'transaction_id': f"TXN_{int(row['id'])}",
            'amount': float(row['Amount']),
            'is_fraud': bool(row['Class'] == 1),
            'risk_features': {
                f'V{i}': float(row[f'V{i}'])
                for i in range(1, 29)
            },
            'timestamp': datetime.now() - timedelta(hours=random.randint(1, 72))
        }

    def get_transaction_batch(
        self,
        count: int = 10,
        fraud_rate: float = 0.1
    ) -> List[Dict]:
        """Get a batch of transactions.

        Args:
            count: Number of transactions
            fraud_rate: Fraction of fraudulent transactions

        Returns:
            List of transaction dicts
        """
        transactions = []
        num_fraud = int(count * fraud_rate)

        # Get fraudulent transactions
        for _ in range(num_fraud):
            transactions.append(self.get_random_transaction(fraud=True))

        # Get normal transactions
        for _ in range(count - num_fraud):
            transactions.append(self.get_random_transaction(fraud=False))

        random.shuffle(transactions)
        return transactions

    def calculate_risk_score(self, transaction_features: Dict) -> float:
        """Calculate risk score using a simple heuristic on PCA features.

        Args:
            transaction_features: Dict with V1-V28 features

        Returns:
            Risk score between 0 and 1
        """
        # Use key features that correlate with fraud
        # Based on Kaggle dataset analysis, V4, V12, V14, V17 are important
        features = transaction_features

        # Simple weighted sum (normalized)
        risk = 0.0
        risk += abs(features.get('V4', 0)) * 0.15
        risk += abs(features.get('V12', 0)) * 0.20
        risk += abs(features.get('V14', 0)) * 0.25
        risk += abs(features.get('V17', 0)) * 0.20
        risk += abs(features.get('V10', 0)) * 0.10
        risk += abs(features.get('V11', 0)) * 0.10

        # Normalize to 0-1 range (features are typically -5 to +5)
        return min(1.0, max(0.0, risk / 10.0))

    def get_high_risk_transaction(self) -> Dict:
        """Get a high-risk/fraudulent transaction."""
        return self.get_random_transaction(
            min_amount=1000.0,
            max_amount=50000.0,
            fraud=True
        )

    def get_low_risk_transaction(self) -> Dict:
        """Get a low-risk/normal transaction."""
        return self.get_random_transaction(
            min_amount=10.0,
            max_amount=500.0,
            fraud=False
        )


# Global loader instance (lazy loaded)
_loader_instance = None


def get_data_loader() -> CreditCardDataLoader:
    """Get or create global data loader instance."""
    global _loader_instance
    if _loader_instance is None:
        _loader_instance = CreditCardDataLoader()
    return _loader_instance
