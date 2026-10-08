import json
from kafka import KafkaConsumer
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import ASYNCHRONOUS

# 1. InfluxDB Configuration (Matches your docker-compose.yml)
INFLUX_URL = "http://localhost:8086"
INFLUX_TOKEN = "super-secret-smartline-token"
INFLUX_ORG = "smartline-360"
INFLUX_BUCKET = "smartline_kpis"

client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)
write_api = client.write_api(write_options=ASYNCHRONOUS)

# 2. Kafka Configuration
consumer = KafkaConsumer(
    'production-events',
    bootstrap_servers=['127.0.0.1:9092'],
    auto_offset_reset='latest', # Start reading incoming messages immediately
    value_deserializer=lambda m: m.decode('utf-8')
)

print(f"Connected! Listening to Redpanda and writing to InfluxDB ({INFLUX_BUCKET})...")

# 3. The Continuous Streaming Loop
for message in consumer:
    try:
        # Node-RED stringified the JSON, so we parse it back into a Python dictionary
        payload = json.loads(message.value)
        
        # 4. Build the Time-Series Data Point
        # We index the data using the PLC timestamp, NOT the Kafka arrival time
        point = Point(payload["metric"]) \
            .tag("station", payload["station"]) \
            .field("value", float(payload["value"])) \
            .time(payload["timestamp"]) 
        
        # 5. Write to InfluxDB
        write_api.write(bucket=INFLUX_BUCKET, org=INFLUX_ORG, record=point)
        
        print(f"✓ Stored {payload['metric']}: {payload['value']} at {payload['timestamp']}")

    except Exception as e:
        print("\n" + "="*40)
        print(f"❌ DATABASE WRITE FAILED!")
        print(f"Error Reason: {e}")
        print(f"Raw Data Received: {message.value}")
        print("="*40 + "\n")