# Database Design & Schema Specification
## SQLite Relational Architecture for Advertising Analytics

### 1. Architectural Philosophy
The database adheres strictly to Third Normal Form (3NF) and Kimball dimensional modeling principles:
- Normalizes high-cardinality descriptive dimensions (platforms, campaigns, cities, devices) to eliminate string redundancy.
- Retains numerical metrics (impressions, clicks, spend, conversions, revenue) in a high-efficiency fact table.
- Enforces relational foreign keys, CHECK constraints, and B-Tree indexes on join and filter columns.

### 2. Table Specifications

#### A. Dimension: `platforms`
- `platform_id` INTEGER PRIMARY KEY AUTOINCREMENT
- `platform_name` TEXT NOT NULL UNIQUE (Facebook, Instagram, Google, TikTok, YouTube)
- `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP

#### B. Dimension: `campaigns`
- `campaign_id` INTEGER PRIMARY KEY AUTOINCREMENT
- `campaign_name` TEXT NOT NULL UNIQUE
- `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP

#### C. Dimension: `cities`
- `city_id` INTEGER PRIMARY KEY AUTOINCREMENT
- `city_name` TEXT NOT NULL UNIQUE (Karachi, Lahore, Islamabad, etc.)

#### D. Dimension: `devices`
- `device_id` INTEGER PRIMARY KEY AUTOINCREMENT
- `device_name` TEXT NOT NULL UNIQUE (Mobile, Desktop, Tablet)

#### E. Fact Table: `advertising_records`
- `record_id` INTEGER PRIMARY KEY AUTOINCREMENT
- `record_date` TEXT NOT NULL
- `campaign_id` INTEGER NOT NULL REFERENCES campaigns(campaign_id)
- `platform_id` INTEGER NOT NULL REFERENCES platforms(platform_id)
- `city_id` INTEGER NOT NULL REFERENCES cities(city_id)
- `device_id` INTEGER NOT NULL REFERENCES devices(device_id)
- `age_group` TEXT NOT NULL
- `gender` TEXT NOT NULL
- `impressions` INTEGER NOT NULL CHECK(impressions >= 0)
- `clicks` INTEGER NOT NULL CHECK(clicks >= 0 AND clicks <= impressions)
- `spend` REAL NOT NULL CHECK(spend >= 0.0)
- `conversions` INTEGER NOT NULL CHECK(conversions >= 0 AND conversions <= clicks)
- `revenue` REAL NOT NULL CHECK(revenue >= 0.0)

#### F. Indexes for Performance
- `idx_adv_platform` ON `advertising_records(platform_id)`
- `idx_adv_campaign` ON `advertising_records(campaign_id)`
- `idx_adv_date` ON `advertising_records(record_date)`
- `idx_adv_city` ON `advertising_records(city_id)`

#### G. Analytical View: `v_platform_summary`
Precomputed aggregation computing total records, spend, revenue, CTR, CPC, CPA, CVR, and ROAS directly in SQLite engine.

