-- Digital Advertising Budget Optimizer Database Schema
-- Normalized SQLite relational schema

PRAGMA foreign_keys = ON;

-- Dimension: Platforms
CREATE TABLE IF NOT EXISTS platforms (
    platform_id INTEGER PRIMARY KEY AUTOINCREMENT,
    platform_name TEXT NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Dimension: Campaigns
CREATE TABLE IF NOT EXISTS campaigns (
    campaign_id INTEGER PRIMARY KEY AUTOINCREMENT,
    campaign_name TEXT NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Dimension: Cities
CREATE TABLE IF NOT EXISTS cities (
    city_id INTEGER PRIMARY KEY AUTOINCREMENT,
    city_name TEXT NOT NULL UNIQUE
);

-- Dimension: Devices
CREATE TABLE IF NOT EXISTS devices (
    device_id INTEGER PRIMARY KEY AUTOINCREMENT,
    device_name TEXT NOT NULL UNIQUE
);

-- Fact: Advertising Records
CREATE TABLE IF NOT EXISTS advertising_records (
    record_id INTEGER PRIMARY KEY AUTOINCREMENT,
    record_date TEXT NOT NULL,
    campaign_id INTEGER NOT NULL,
    platform_id INTEGER NOT NULL,
    city_id INTEGER NOT NULL,
    device_id INTEGER NOT NULL,
    age_group TEXT NOT NULL,
    gender TEXT NOT NULL,
    impressions INTEGER NOT NULL CHECK(impressions >= 0),
    clicks INTEGER NOT NULL CHECK(clicks >= 0 AND clicks <= impressions),
    spend REAL NOT NULL CHECK(spend >= 0.0),
    conversions INTEGER NOT NULL CHECK(conversions >= 0 AND conversions <= clicks),
    revenue REAL NOT NULL CHECK(revenue >= 0.0),
    FOREIGN KEY (campaign_id) REFERENCES campaigns(campaign_id),
    FOREIGN KEY (platform_id) REFERENCES platforms(platform_id),
    FOREIGN KEY (city_id) REFERENCES cities(city_id),
    FOREIGN KEY (device_id) REFERENCES devices(device_id)
);

-- Indexes for high-performance aggregations
CREATE INDEX IF NOT EXISTS idx_adv_platform ON advertising_records(platform_id);
CREATE INDEX IF NOT EXISTS idx_adv_campaign ON advertising_records(campaign_id);
CREATE INDEX IF NOT EXISTS idx_adv_date ON advertising_records(record_date);
CREATE INDEX IF NOT EXISTS idx_adv_city ON advertising_records(city_id);

-- Operational: Benchmark Results
CREATE TABLE IF NOT EXISTS benchmark_results (
    benchmark_id INTEGER PRIMARY KEY AUTOINCREMENT,
    executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    dataset_size INTEGER NOT NULL,
    engine TEXT NOT NULL,
    execution_time_sec REAL NOT NULL,
    throughput_rps REAL NOT NULL,
    memory_mb REAL,
    status TEXT NOT NULL,
    notes TEXT
);

-- Operational: Budget Recommendations
CREATE TABLE IF NOT EXISTS budget_recommendations (
    recommendation_id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    total_budget REAL NOT NULL,
    strategy TEXT NOT NULL,
    platform TEXT NOT NULL,
    allocated_percentage REAL NOT NULL,
    allocated_amount REAL NOT NULL,
    expected_conversions REAL,
    expected_revenue REAL,
    expected_roas REAL,
    rationale TEXT
);

-- Analytical View for Reporting
CREATE VIEW IF NOT EXISTS v_platform_summary AS
SELECT 
    p.platform_name,
    COUNT(a.record_id) AS total_records,
    SUM(a.impressions) AS total_impressions,
    SUM(a.clicks) AS total_clicks,
    SUM(a.spend) AS total_spend,
    SUM(a.conversions) AS total_conversions,
    SUM(a.revenue) AS total_revenue,
    CASE WHEN SUM(a.impressions) > 0 THEN (SUM(a.clicks) * 100.0 / SUM(a.impressions)) ELSE 0.0 END AS ctr,
    CASE WHEN SUM(a.clicks) > 0 THEN (SUM(a.spend) * 1.0 / SUM(a.clicks)) ELSE 0.0 END AS cpc,
    CASE WHEN SUM(a.conversions) > 0 THEN (SUM(a.spend) * 1.0 / SUM(a.conversions)) ELSE 0.0 END AS cpa,
    CASE WHEN SUM(a.clicks) > 0 THEN (SUM(a.conversions) * 100.0 / SUM(a.clicks)) ELSE 0.0 END AS conversion_rate,
    CASE WHEN SUM(a.spend) > 0 THEN (SUM(a.revenue) * 1.0 / SUM(a.spend)) ELSE 0.0 END AS roas
FROM advertising_records a
JOIN platforms p ON a.platform_id = p.platform_id
GROUP BY p.platform_name;

