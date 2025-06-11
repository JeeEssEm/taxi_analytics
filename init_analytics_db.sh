#!/bin/bash

dataset=nyc-yellow-taxi-trip-data
dataset_dir=$dataset
table=nyc_yellow_taxi_trip

echo "Downloading dataset $dataset..."

curl -L --skip-existing -o "$dataset.zip" \
  https://www.kaggle.com/api/v1/datasets/download/elemento/nyc-yellow-taxi-trip-data

echo "Extracting dataset to $dataset_dir"
unzip -n $dataset.zip -d $dataset_dir

echo "Enter database name: "
read database

sudo -u postgres psql -d $database -c "CREATE EXTENSION IF NOT EXISTS postgis"
sudo -u postgres psql -d $database -c \
"CREATE TABLE IF NOT EXISTS $table (
    vendor_id TEXT,
    tpep_pickup_datetime TIMESTAMP,
    tpep_dropoff_datetime TIMESTAMP,
    passenger_count INTEGER,
    trip_distance NUMERIC,
    pickup_longitude NUMERIC,
    pickup_latitude NUMERIC,
    pickup_location GEOMETRY(POINT, 4326),  
    rate_code_id INTEGER,
    store_and_fwd_flag TEXT,
    dropoff_longitude NUMERIC,
    dropoff_latitude NUMERIC,
    dropoff_location GEOMETRY(POINT, 4326), 
    payment_type TEXT,
    fare_amount NUMERIC,
    extra NUMERIC,
    mta_tax NUMERIC,
    tip_amount NUMERIC,
    tolls_amount NUMERIC,
    improvement_surcharge NUMERIC,
    total_amount NUMERIC
);"

filelist=$(ls $dataset_dir)
for filename in ${filelist[@]}; do
    sudo -u postgres psql -d $database -c \
        "\copy $table (
        vendor_id,
        tpep_pickup_datetime,
        tpep_dropoff_datetime,
        passenger_count,
        trip_distance,
        pickup_longitude,
        pickup_latitude,
        rate_code_id,
        store_and_fwd_flag,
        dropoff_longitude,
        dropoff_latitude,
        payment_type,
        fare_amount,
        extra,
        mta_tax,
        tip_amount,
        tolls_amount,
        improvement_surcharge,
        total_amount
    )
    FROM '$dataset_dir/$filename' 
    WITH (FORMAT CSV, HEADER true, NULL '')"
done

sudo -u postgres psql -d $database -c \
"UPDATE $table
SET pickup_location = ST_SetSRID(ST_MakePoint(pickup_longitude, pickup_latitude), 4326)
WHERE pickup_longitude IS NOT NULL AND pickup_latitude IS NOT NULL"

sudo -u postgres psql -d $database -c \
"UPDATE $table
SET pickup_location = ST_SetSRID(ST_MakePoint(pickup_longitude, pickup_latitude), 4326)
WHERE pickup_longitude IS NOT NULL AND pickup_latitude IS NOT NULL"
