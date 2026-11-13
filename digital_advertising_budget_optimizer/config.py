"""
Configuration and constants for Digital Advertising Budget Optimizer.
"""

from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
BENCHMARKS_DIR = DATA_DIR / "benchmarks"
DATABASE_DIR = BASE_DIR / "database"
DATABASE_PATH = DATABASE_DIR / "advertising.db"
SCHEMA_PATH = DATABASE_DIR / "schema.sql"
REPORTS_DIR = BASE_DIR / "reports"
DOCS_DIR = BASE_DIR / "docs"
DIAGRAMS_DIR = BASE_DIR / "diagrams"

# Ensure runtime directories exist
for p in [RAW_DATA_DIR, PROCESSED_DATA_DIR, BENCHMARKS_DIR, DATABASE_DIR, REPORTS_DIR, DIAGRAMS_DIR]:
    p.mkdir(parents=True, exist_ok=True)

# Domain Constants
PLATFORMS = ["Facebook", "Instagram", "Google", "TikTok", "YouTube"]

CAMPAIGNS = [
    "Summer Mega Sale",
    "Brand Awareness 2026",
    "Lead Gen Blitz",
    "Retargeting Tier 1",
    "App Install Push",
    "Influencer Collab Promo",
    "Flash Weekend Deals",
    "Product Launch Alpha",
]

CITIES = ["Karachi", "Lahore", "Islamabad", "Rawalpindi", "Faisalabad", "Multan", "Peshawar"]

DEVICES = ["Mobile", "Desktop", "Tablet"]

GENDERS = ["Male", "Female", "Other"]

AGE_GROUPS = ["18-24", "25-34", "35-44", "45-54", "55+"]

DEFAULT_BUDGET = 1_000_000.0  # Rs. 1,000,000 PKR

# Expected historical performance benchmarks per platform (used for realistic data generation)
PLATFORM_PROFILES = {
    "Google": {
        "ctr_mean": 3.8, "ctr_std": 0.8,
        "cpc_mean": 18.0, "cpc_std": 3.5,
        "cvr_mean": 4.5, "cvr_std": 0.9,
        "roas_mean": 3.6, "roas_std": 0.6,
    },
    "Instagram": {
        "ctr_mean": 2.6, "ctr_std": 0.5,
        "cpc_mean": 12.0, "cpc_std": 2.5,
        "cvr_mean": 3.2, "cvr_std": 0.7,
        "roas_mean": 3.1, "roas_std": 0.5,
    },
    "Facebook": {
        "ctr_mean": 2.1, "ctr_std": 0.4,
        "cpc_mean": 9.5,  "cpc_std": 2.0,
        "cvr_mean": 2.8, "cvr_std": 0.6,
        "roas_mean": 2.7, "roas_std": 0.4,
    },
    "YouTube": {
        "ctr_mean": 1.4, "ctr_std": 0.3,
        "cpc_mean": 14.0, "cpc_std": 3.0,
        "cvr_mean": 2.2, "cvr_std": 0.5,
        "roas_mean": 2.4, "roas_std": 0.5,
    },
    "TikTok": {
        "ctr_mean": 3.2, "ctr_std": 0.7,
        "cpc_mean": 6.5,  "cpc_std": 1.5,
        "cvr_mean": 2.0, "cvr_std": 0.6,
        "roas_mean": 2.2, "roas_std": 0.6,
    },
}

REQUIRED_COLUMNS = [
    "date",
    "campaign",
    "platform",
    "impressions",
    "clicks",
    "spend",
    "conversions",
    "revenue",
    "age",
    "gender",
    "city",
    "device",
]

