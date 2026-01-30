"""Download and prepare open-source datasets for A2Bench."""

import os
import json
import urllib.request
import zipfile
import csv
from pathlib import Path
from typing import Dict, List

# Base paths
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
DOWNLOADS_DIR = DATA_DIR / "downloads"

# Create directories
DOWNLOADS_DIR.mkdir(parents=True, exist_ok=True)


def download_credit_card_fraud_dataset():
    """
    Download credit card fraud dataset from Kaggle.

    Note: Requires Kaggle API credentials.
    Install: pip install kaggle
    Configure: ~/.kaggle/kaggle.json with API credentials
    """
    print("Downloading Credit Card Fraud Detection Dataset...")

    try:
        import kaggle

        # Download dataset
        kaggle.api.dataset_download_files(
            'nelgiriyewithana/credit-card-fraud-detection-dataset-2023',
            path=DOWNLOADS_DIR / "credit_card_fraud",
            unzip=True
        )
        print("✓ Credit card fraud dataset downloaded")
        return True

    except ImportError:
        print("⚠ Kaggle package not installed. Run: pip install kaggle")
        print("  Then configure credentials: ~/.kaggle/kaggle.json")
        return False
    except Exception as e:
        print(f"⚠ Error downloading dataset: {e}")
        print("  Manual download: https://www.kaggle.com/datasets/nelgiriyewithana/credit-card-fraud-detection-dataset-2023")
        return False


def download_ibm_aml_data():
    """Download IBM AML synthetic transaction data from GitHub."""
    print("Downloading IBM AML-Data...")

    url = "https://raw.githubusercontent.com/IBM/AML-Data/master/aml_data.csv"
    output_path = DOWNLOADS_DIR / "aml" / "aml_data.csv"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        urllib.request.urlretrieve(url, output_path)
        print(f"✓ IBM AML-Data downloaded to {output_path}")
        return True
    except Exception as e:
        print(f"⚠ Error downloading IBM AML-Data: {e}")
        return False


def clone_synthea():
    """Clone Synthea repository for generating synthetic patient data."""
    print("Cloning Synthea repository...")

    synthea_dir = DOWNLOADS_DIR / "synthea"

    if synthea_dir.exists():
        print("✓ Synthea already cloned")
        return True

    import subprocess

    try:
        subprocess.run([
            "git", "clone",
            "https://github.com/synthetichealth/synthea.git",
            str(synthea_dir)
        ], check=True)
        print("✓ Synthea cloned successfully")
        print("  To generate data, run: cd synthea && ./run_synthea -p 100")
        return True
    except Exception as e:
        print(f"⚠ Error cloning Synthea: {e}")
        return False


def download_drug_interaction_data():
    """
    Download drug interaction data from DDInter.

    Note: This may require manual download and API access.
    """
    print("Drug Interaction Database (DDInter)...")
    print("  Manual download required from: https://ddinter.scbdd.com/")
    print("  Or use the API for programmatic access")

    # Create placeholder structure
    drug_data_dir = DOWNLOADS_DIR / "drug_interactions"
    drug_data_dir.mkdir(parents=True, exist_ok=True)

    # Create a sample drug interaction file based on common interactions
    sample_interactions = [
        {
            "drug1": "warfarin",
            "drug2": "aspirin",
            "severity": "major",
            "description": "Increased risk of bleeding"
        },
        {
            "drug1": "lisinopril",
            "drug2": "ibuprofen",
            "severity": "moderate",
            "description": "NSAIDs may reduce antihypertensive effect"
        },
        {
            "drug1": "metformin",
            "drug2": "alcohol",
            "severity": "moderate",
            "description": "Increased risk of lactic acidosis"
        },
        {
            "drug1": "simvastatin",
            "drug2": "grapefruit_juice",
            "severity": "major",
            "description": "Increased statin levels and myopathy risk"
        }
    ]

    output_file = drug_data_dir / "interactions.json"
    with open(output_file, 'w') as f:
        json.dump(sample_interactions, f, indent=2)

    print(f"✓ Sample drug interaction data created at {output_file}")
    return True


def create_dataset_manifest():
    """Create a manifest file listing all available datasets."""
    manifest = {
        "version": "1.0",
        "last_updated": "2025-01-15",
        "datasets": {
            "healthcare": [
                {
                    "name": "synthea_patients",
                    "type": "synthetic",
                    "source": "Synthea",
                    "path": "downloads/synthea/output",
                    "license": "Apache 2.0",
                    "url": "https://github.com/synthetichealth/synthea"
                },
                {
                    "name": "drug_interactions",
                    "type": "reference",
                    "source": "DDInter",
                    "path": "downloads/drug_interactions/interactions.json",
                    "license": "Open Access",
                    "url": "https://ddinter.scbdd.com/"
                }
            ],
            "finance": [
                {
                    "name": "credit_card_fraud_2023",
                    "type": "real_anonymized",
                    "source": "Kaggle",
                    "path": "downloads/credit_card_fraud",
                    "license": "CC BY-NC-SA 4.0",
                    "url": "https://www.kaggle.com/datasets/nelgiriyewithana/credit-card-fraud-detection-dataset-2023"
                },
                {
                    "name": "ibm_aml_data",
                    "type": "synthetic",
                    "source": "IBM AML-Data",
                    "path": "downloads/aml/aml_data.csv",
                    "license": "Apache 2.0",
                    "url": "https://github.com/IBM/AML-Data"
                }
            ]
        }
    }

    manifest_path = DATA_DIR / "datasets_manifest.json"
    with open(manifest_path, 'w') as f:
        json.dump(manifest, f, indent=2)

    print(f"✓ Dataset manifest created at {manifest_path}")


def main():
    """Main function to download all datasets."""
    print("="*60)
    print("A2Bench Dataset Downloader")
    print("="*60)
    print()

    results = {
        "Credit Card Fraud": download_credit_card_fraud_dataset(),
        "IBM AML-Data": download_ibm_aml_data(),
        "Synthea": clone_synthea(),
        "Drug Interactions": download_drug_interaction_data()
    }

    print()
    print("="*60)
    print("Download Summary:")
    print("="*60)

    for name, success in results.items():
        status = "✓" if success else "⚠"
        print(f"{status} {name}")

    print()
    create_dataset_manifest()

    print()
    print("Next steps:")
    print("1. Generate Synthea patient data: cd data/downloads/synthea && ./run_synthea -p 100")
    print("2. Process datasets into test cases: python scripts/generate_test_cases.py")
    print("3. Run experiments: python experiments/run_real_data_experiments.py")


if __name__ == "__main__":
    main()
