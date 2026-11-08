-- ============================================================================
-- flood-ews: TimescaleDB Initialization Schema & Hyderabad Seed Data
-- ============================================================================

-- 1. Enable TimescaleDB Extension if available
DO $$
BEGIN
    CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;
EXCEPTION WHEN OTHERS THEN
    RAISE NOTICE 'TimescaleDB extension not available, falling back to standard relational tables';
END $$;

-- 2. Nodes Table
CREATE TABLE IF NOT EXISTS nodes (
    id VARCHAR(32) PRIMARY KEY,
    name VARCHAR(128) NOT NULL,
    lat DOUBLE PRECISION NOT NULL,
    lon DOUBLE PRECISION NOT NULL,
    ward VARCHAR(64) NOT NULL,
    mount_height_cm DOUBLE PRECISION NOT NULL DEFAULT 200.0,
    capacity_cm DOUBLE PRECISION NOT NULL DEFAULT 180.0,
    status VARCHAR(16) NOT NULL DEFAULT 'offline',
    last_seen TIMESTAMPTZ,
    current_gate_deg INT NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 3. Telemetry Readings Table (Hypertable)
CREATE TABLE IF NOT EXISTS readings (
    time TIMESTAMPTZ NOT NULL,
    node_id VARCHAR(32) NOT NULL REFERENCES nodes(id) ON DELETE CASCADE,
    depth_cm DOUBLE PRECISION NOT NULL,
    rain_mm_h DOUBLE PRECISION NOT NULL,
    gate_deg INT NOT NULL DEFAULT 0,
    rssi INT NOT NULL DEFAULT -70
);

-- Index for time-series queries
CREATE INDEX IF NOT EXISTS idx_readings_node_time ON readings (node_id, time DESC);

-- Convert readings to hypertable if TimescaleDB extension is active
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'timescaledb') THEN
        PERFORM create_hypertable('readings', 'time', if_not_exists => TRUE);
        RAISE NOTICE 'Successfully created hypertable for readings.';
    END IF;
END $$;

-- 4. Continuous Aggregate: 5-minute telemetry summary (TimescaleDB)
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'timescaledb') THEN
        IF NOT EXISTS (SELECT 1 FROM pg_matviews WHERE matviewname = 'readings_5min') THEN
            CREATE MATERIALIZED VIEW readings_5min
            WITH (timescaledb.continuous) AS
            SELECT
                time_bucket('5 minutes', time) AS bucket,
                node_id,
                avg(depth_cm) AS avg_depth_cm,
                max(depth_cm) AS max_depth_cm,
                min(depth_cm) AS min_depth_cm,
                avg(rain_mm_h) AS avg_rain_mm_h,
                max(rain_mm_h) AS max_rain_mm_h,
                count(*) AS sample_count
            FROM readings
            GROUP BY bucket, node_id
            WITH NO DATA;

            PERFORM add_continuous_aggregate_policy('readings_5min',
                start_offset => INTERVAL '2 hours',
                end_offset => INTERVAL '5 minutes',
                schedule_interval => INTERVAL '5 minutes',
                if_not_exists => TRUE
            );
        END IF;

        -- 30-Day Retention Policy
        PERFORM add_retention_policy('readings', INTERVAL '30 days', if_not_exists => TRUE);
        RAISE NOTICE 'Configured 5-minute continuous aggregate and 30-day retention policy.';
    END IF;
EXCEPTION WHEN OTHERS THEN
    RAISE NOTICE 'Skipping Timescale continuous aggregate / retention setup: %', SQLERRM;
END $$;

-- 5. Shelters Table
CREATE TABLE IF NOT EXISTS shelters (
    id VARCHAR(32) PRIMARY KEY,
    name VARCHAR(128) NOT NULL,
    lat DOUBLE PRECISION NOT NULL,
    lon DOUBLE PRECISION NOT NULL,
    capacity INT NOT NULL DEFAULT 200,
    current_occupancy INT NOT NULL DEFAULT 0,
    ward VARCHAR(64) NOT NULL,
    contact_phone VARCHAR(32) DEFAULT '+91-40-23456789'
);

-- 6. Subscribers Table
CREATE TABLE IF NOT EXISTS subscribers (
    id SERIAL PRIMARY KEY,
    phone VARCHAR(32) UNIQUE NOT NULL,
    name VARCHAR(128) NOT NULL,
    ward VARCHAR(64) NOT NULL,
    language VARCHAR(8) NOT NULL DEFAULT 'en', -- en, te, hi
    opted_in BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 7. Alerts Table
CREATE TABLE IF NOT EXISTS alerts (
    id SERIAL PRIMARY KEY,
    node_id VARCHAR(32) NOT NULL REFERENCES nodes(id) ON DELETE CASCADE,
    level VARCHAR(16) NOT NULL, -- WATCH, WARNING, CRITICAL
    message TEXT NOT NULL,
    channel VARCHAR(16) NOT NULL DEFAULT 'sms', -- sms, whatsapp, broadcast
    sent_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    recipients_count INT NOT NULL DEFAULT 0
);

-- 8. Gate Audit Logs Table
CREATE TABLE IF NOT EXISTS gate_audit_logs (
    id SERIAL PRIMARY KEY,
    node_id VARCHAR(32) NOT NULL REFERENCES nodes(id) ON DELETE CASCADE,
    gate_angle INT NOT NULL,
    reason VARCHAR(128) NOT NULL,
    triggered_by VARCHAR(64) NOT NULL, -- 'automation:warning', 'operator:web', 'local_failsafe'
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ============================================================================
-- SEED DATA (Hyderabad Musi River Basin Flood Flashpoints)
-- ============================================================================

-- Seed 6 Drainage Sensor Nodes
INSERT INTO nodes (id, name, lat, lon, ward, mount_height_cm, capacity_cm, status, last_seen, current_gate_deg)
VALUES
    ('drain-01', 'Moosarambagh Bridge', 17.3705, 78.5080, 'Amberpet', 200.0, 180.0, 'online', NOW(), 0),
    ('drain-02', 'Chaderghat Causeway', 17.3789, 78.4902, 'Malakpet', 220.0, 200.0, 'online', NOW(), 0),
    ('drain-03', 'Amberpet Nallah', 17.3912, 78.5201, 'Amberpet', 180.0, 150.0, 'online', NOW(), 0),
    ('drain-04', 'Afzalgunj Siphon', 17.3734, 78.4776, 'Charminar', 210.0, 190.0, 'online', NOW(), 0),
    ('drain-05', 'Purana Pul Culvert', 17.3621, 78.4590, 'Goshamahal', 190.0, 160.0, 'online', NOW(), 0),
    ('drain-06', 'Malakpet Railway Underpass', 17.3750, 78.4985, 'Malakpet', 230.0, 210.0, 'online', NOW(), 0)
ON CONFLICT (id) DO UPDATE SET
    name = EXCLUDED.name,
    lat = EXCLUDED.lat,
    lon = EXCLUDED.lon,
    ward = EXCLUDED.ward,
    mount_height_cm = EXCLUDED.mount_height_cm,
    capacity_cm = EXCLUDED.capacity_cm;

-- Seed 4 Disaster Relief Shelters
INSERT INTO shelters (id, name, lat, lon, capacity, current_occupancy, ward, contact_phone)
VALUES
    ('shelter-01', 'Amberpet Indoor Stadium Relief Camp', 17.3980, 78.5150, 450, 42, 'Amberpet', '+91-40-27401122'),
    ('shelter-02', 'Nimboliadda Community Hall', 17.3820, 78.4950, 250, 15, 'Malakpet', '+91-40-24552233'),
    ('shelter-03', 'Chaderghat Govt High School Shelter', 17.3760, 78.4870, 300, 20, 'Malakpet', '+91-40-24754455'),
    ('shelter-04', 'City Model High School & Relief Centre', 17.3680, 78.4680, 350, 30, 'Charminar', '+91-40-24526677')
ON CONFLICT (id) DO UPDATE SET
    name = EXCLUDED.name,
    lat = EXCLUDED.lat,
    lon = EXCLUDED.lon,
    capacity = EXCLUDED.capacity,
    ward = EXCLUDED.ward;

-- Seed 5 Multilingual Subscribers
INSERT INTO subscribers (phone, name, ward, language, opted_in)
VALUES
    ('+919876543210', 'Ramesh Kumar', 'Amberpet', 'te', TRUE),
    ('+919876543211', 'Sunita Sharma', 'Malakpet', 'hi', TRUE),
    ('+919876543212', 'Mohammed Abdul', 'Charminar', 'en', TRUE),
    ('+919876543213', 'Lakshmi Reddy', 'Amberpet', 'te', TRUE),
    ('+919876543214', 'Vikram Singh', 'Goshamahal', 'hi', TRUE)
ON CONFLICT (phone) DO UPDATE SET
    name = EXCLUDED.name,
    ward = EXCLUDED.ward,
    language = EXCLUDED.language,
    opted_in = EXCLUDED.opted_in;

-- Seed initial baseline readings for each node (for instant sparklines)
INSERT INTO readings (time, node_id, depth_cm, rain_mm_h, gate_deg, rssi)
SELECT
    NOW() - (i || ' minutes')::INTERVAL,
    n.id,
    ROUND((n.capacity_cm * 0.22 + (SIN(i * 0.5) * 4.0))::NUMERIC, 1),
    ROUND((5.0 + (COS(i * 0.3) * 3.0))::NUMERIC, 1),
    0,
    -65
FROM nodes n
CROSS JOIN generate_series(0, 180, 5) AS i;
