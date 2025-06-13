#!/bin/bash
# Usage: ./setup_replication_swapped.sh

# Load environment variables
source .env

# Configuration - SWAPPED setup
REPL_USER="replication_user"
REPL_PASSWORD="secure_password"
SRC_DB="$DB_NAME"               # Django DB (now source)
SRC_HOST="$DB_HOST"             # Django DB host
DEST_DB="taxi_analytics"        # Analytics DB (now destination)
DEST_HOST="localhost"           # Analytics DB host
PUBLICATION="taxi_pub"
SUBSCRIPTION="taxi_sub"
POSTGRES_USER="postgres"   

# Step 1: Configure Source (Django DB)
echo "Configuring source database ($SRC_DB)..."

psql -U $POSTGRES_USER -h $SRC_HOST -d $SRC_HOST <<EOF
-- Enable logical replication if not already enabled
ALTER SYSTEM SET wal_level = logical;
SELECT pg_reload_conf();

-- Create replication user if not exists
DO \$$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = '$REPL_USER') THEN
    CREATE ROLE $REPL_USER WITH REPLICATION LOGIN PASSWORD '$REPL_PASSWORD';
  END IF;
END
\$$;

-- Grant necessary permissions
GRANT CONNECT ON DATABASE $SRC_DB TO $REPL_USER;
GRANT USAGE ON SCHEMA public TO $REPL_USER;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO $REPL_USER;
GRANT SELECT ON ALL TABLES IN SCHEMA your_app TO $REPL_USER;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO $REPL_USER;
ALTER DEFAULT PRIVILEGES IN SCHEMA your_app GRANT SELECT ON TABLES TO $REPL_USER;

-- Create publication for TaxiOrder table
DROP PUBLICATION IF EXISTS $PUBLICATION;
CREATE PUBLICATION $PUBLICATION FOR TABLE your_app_taxiorder;
EOF

# Step 2: Set up Destination (Analytics DB)
echo "Configuring destination database ($DEST_DB)..."

psql -U $POSTGRES_USER -h $DEST_HOST -d $DEST_DB <<EOF
-- Ensure PostGIS is available
CREATE EXTENSION IF NOT EXISTS postgis;

-- Create subscription to source
DROP SUBSCRIPTION IF EXISTS $SUBSCRIPTION;
CREATE SUBSCRIPTION $SUBSCRIPTION
CONNECTION 'host=$SRC_HOST dbname=$SRC_DB user=$REPL_USER password=$REPL_PASSWORD'
PUBLICATION $PUBLICATION;

-- Create transformation view (Option 4.A)
CREATE OR REPLACE VIEW transformed_taxi_orders AS
SELECT 
    o.id::text AS vendor_id,
    o.pickup_datetime AS tpep_pickup_datetime,
    o.dropoff_datetime AS tpep_dropoff_datetime,
    o.passenger_count,
    o.trip_distance_km AS trip_distance,
    ST_Transform(o.pickup_coords::geometry, 4326) AS pickup_location,
    CASE WHEN o.status = 'DONE' THEN 1 ELSE 0 END AS rate_code_id,
    CASE o.payment_type
        WHEN 0 THEN 'credit_card'
        WHEN 1 THEN 'cash'
        ELSE 'other'
    END AS payment_type,
    o.extra,
    o.total AS total_amount
FROM your_app_taxiorder o;
EOF

# Step 3: Verification
echo "Verifying replication..."

psql -U $POSTGRES_USER -h $DEST_HOST -d $DEST_DB <<EOF
-- Check subscription status
SELECT * FROM pg_stat_subscription;

-- Compare record counts
SELECT 
    (SELECT count(*) FROM your_app_taxiorder) AS source_count,
    (SELECT count(*) FROM transformed_taxi_orders) AS transformed_count;
EOF

echo "Setup complete! Access transformed data using: SELECT * FROM transformed_taxi_orders;"