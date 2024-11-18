import random
import time
import datetime
import requests
from collections import defaultdict
import math
import os
from dotenv import load_dotenv
from opentelemetry.proto.logs.v1 import logs_pb2
from opentelemetry.proto.common.v1 import common_pb2
from opentelemetry.proto.resource.v1 import resource_pb2

# Load environment variables from .env file
load_dotenv()

class ACMETravelLogGenerator:
    def __init__(self, instance_id, api_key):
        self.instance_id = instance_id
        self.api_key = api_key
        self.start_time = time.time()
        self.error_count = defaultdict(int)
        self.otlp_url = os.getenv('OTLP_ENDPOINT', 'https://otlp-gateway-prod-us-central-0.grafana.net/otlp/v1/logs')

    def get_timestamp_ns(self):
        """Return current timestamp in nanoseconds"""
        return int(time.time() * 1e9)

    def format_timestamp(self):
        """Return current timestamp in ISO 8601 format"""
        return datetime.datetime.now().isoformat()

    def escape_logfmt_value(self, value):
        """Escape special characters in logfmt values"""
        if isinstance(value, (int, float)):
            return str(value)
        value = str(value)
        if ' ' in value or '"' in value or '=' in value:
            return f'"{value.replace('"', '\\"')}"'
        return value

    def to_logfmt(self, attributes):
        """Convert attributes dictionary to logfmt format"""
        return ' '.join(f"{k}={self.escape_logfmt_value(v)}" for k, v in attributes.items())

    def create_key_value(self, key, value):
        """Helper function to create KeyValue protobuf message"""
        kv = common_pb2.KeyValue()
        kv.key = key
        
        if isinstance(value, str):
            kv.value.string_value = value
        elif isinstance(value, int):
            kv.value.int_value = value
        elif isinstance(value, float):
            kv.value.double_value = value
        elif isinstance(value, bool):
            kv.value.bool_value = value
            
        return kv

    def create_resource_logs(self, log_records):
        """Create OTLP-formatted ResourceLogs using protobuf"""
        resource_logs = logs_pb2.ResourceLogs()
        
        resource = resource_pb2.Resource()
        attributes = [
            ("service.name", "acmetravel-backend"),
            ("service.version", "1.0.0"),
            ("deployment.environment", "demo")
        ]
        
        for key, value in attributes:
            resource.attributes.append(self.create_key_value(key, value))
        
        scope_logs = logs_pb2.ScopeLogs()
        scope = common_pb2.InstrumentationScope()
        scope.name = "acmetravel-backend"
        scope.version = "1.0.0"
        scope_logs.scope.CopyFrom(scope)
        
        for record in log_records:
            scope_logs.log_records.append(record)
        
        resource_logs.resource.CopyFrom(resource)
        resource_logs.scope_logs.append(scope_logs)
        
        return resource_logs

    def generate_normal_logs(self):
        actions = [
            "SearchRequest", "HotelDetails", "RoomAvailability",
            "PriceCalculation", "BookingAttempt", "PaymentProcessing",
            "EmailNotification", "UserAuthentication"
        ]
        
        status_codes = [200, 201, 204, 206, 302]
        response_times = range(50, 500)
        
        action = random.choice(actions)
        status = random.choice(status_codes)
        response_time = random.choice(response_times)
        user_id = str(random.randint(1000, 9999))
        session_id = f"sess_{random.randint(10000, 99999)}"
        request_id = f"req_{random.randint(100000, 999999)}"

        context_details = {
            "SearchRequest": {"location": "New York", "check_in": "2024-03-15", "check_out": "2024-03-20", "guests": 2, "rooms": 1, "price_range": "100-300"},
            "HotelDetails": {"hotel_id": f"HTL{random.randint(1000,9999)}", "include_amenities": True, "include_room_types": True},
            "RoomAvailability": {"dates": "2024-03-15_to_2024-03-20", "room_types": "standard,deluxe", "meal_plan": "breakfast_included"},
            "PriceCalculation": {"tax_rate": 8.5, "resort_fee": 25, "nights": 5, "base_price": random.randint(100, 300)},
            "BookingAttempt": {"reservation_id": f"RSV{random.randint(10000,99999)}", "payment_method": "credit_card", "special_requests": "late_checkout"},
            "PaymentProcessing": {"amount": random.randint(200,1000), "transaction_id": f"TXN{random.randint(100000,999999)}"},
            "EmailNotification": {"template": "booking_confirmation", "includes": "itinerary,check_in_instructions,policies"},
            "UserAuthentication": {"account_type": "premium", "auth_method": "2FA"}
        }

        attributes = {
            "timestamp": self.format_timestamp(),
            "level": "info",
            "component": "api",
            "action": action,
            "status_code": status,
            "response_time_ms": response_time,
            "user_id": user_id,
            "request_id": request_id,
            "session_id": session_id
        }
        
        # Add context details to attributes
        attributes.update(context_details[action])

        log_record = logs_pb2.LogRecord()
        log_record.time_unix_nano = self.get_timestamp_ns()
        log_record.severity_number = logs_pb2.SEVERITY_NUMBER_INFO
        log_record.severity_text = "info"
        
        # Create logfmt message
        log_record.body.string_value = self.to_logfmt(attributes)
        
        # Add attributes
        for key, value in attributes.items():
            log_record.attributes.append(self.create_key_value(key, str(value)))
        
        return log_record

    def generate_minor_error_logs(self):
        errors = [
            ("database", {
                "error": "connection_pool_exhausted",
                "query": "SELECT * FROM bookings WHERE status = 'pending'",
                "pool_size": random.randint(20, 50),
                "active_connections": random.randint(15, 45),
                "waiting_queries": random.randint(5, 20)
            }),
            ("rate-limiter", {
                "error": "rate_limit_exceeded",
                "ip_address": f"192.168.{random.randint(1,255)}.{random.randint(1,255)}",
                "current_rate": random.randint(100, 500),
                "limit": 100,
                "cooldown_seconds": random.randint(30, 120)
            }),
            ("cache", {
                "error": "cache_invalidation_failed",
                "region": random.choice(["us-east-1", "eu-west-1", "ap-southeast-2"]),
                "cluster": f"cache-cluster-{random.randint(1,5)}",
                "affected_keys": random.randint(50, 200)
            })
        ]
        
        component, error_context = random.choice(errors)
        severity = random.choice([
            (logs_pb2.SEVERITY_NUMBER_ERROR, "error"),
            (logs_pb2.SEVERITY_NUMBER_WARN, "warn")
        ])

        attributes = {
            "timestamp": self.format_timestamp(),
            "level": severity[1],
            "component": component
        }
        attributes.update(error_context)

        log_record = logs_pb2.LogRecord()
        log_record.time_unix_nano = self.get_timestamp_ns()
        log_record.severity_number = severity[0]
        log_record.severity_text = severity[1]
        
        # Create logfmt message
        log_record.body.string_value = self.to_logfmt(attributes)
        
        # Add attributes
        for key, value in attributes.items():
            log_record.attributes.append(self.create_key_value(key, str(value)))
        
        return log_record

    def generate_escalating_error(self, minutes_elapsed):
        db_metrics = {
            "timestamp": self.format_timestamp(),
            "level": "error",
            "component": "database",
            "error": "critical_performance_degradation",
            "instance": "replica-3",
            "active_connections": random.randint(95, 100),
            "connection_timeout_ms": random.randint(1000, 5000),
            "dead_locks_detected": random.randint(1, 5),
            "query_queue_depth": random.randint(50, 200),
            "memory_usage_percent": random.randint(85, 95),
            "disk_queue_depth": random.randint(10, 30),
            "replication_lag_seconds": random.randint(30, 120),
            "impact": "increased_latency_and_failures",
            "mitigation": "scaling_up_connection_pool,clearing_query_cache"
        }

        log_record = logs_pb2.LogRecord()
        log_record.time_unix_nano = self.get_timestamp_ns()
        log_record.severity_number = logs_pb2.SEVERITY_NUMBER_ERROR
        log_record.severity_text = "error"
        
        # Create logfmt message
        log_record.body.string_value = self.to_logfmt(db_metrics)
        
        # Add attributes
        for key, value in db_metrics.items():
            log_record.attributes.append(self.create_key_value(key, str(value)))
        
        return log_record

    def calculate_error_frequency(self, minutes_elapsed):
        cycle_minutes = minutes_elapsed % 5
        return math.ceil(2 ** (cycle_minutes / 2 - 2))

    def send_to_otlp(self, log_records):
        headers = {
            'Content-Type': 'application/x-protobuf',
            'Authorization': f'Bearer {self.instance_id}:{self.api_key}',
        }

        logs_data = logs_pb2.LogsData()
        resource_logs = self.create_resource_logs(log_records)
        logs_data.resource_logs.append(resource_logs)
        
        payload = logs_data.SerializeToString()

        try:
            response = requests.post(
                self.otlp_url,
                headers=headers,
                data=payload,
                timeout=10
            )
            if response.status_code not in [200, 204]:
                print(f"Error sending logs: {response.status_code} - {response.text}")
            return response.status_code in [200, 204]
        except Exception as e:
            print(f"Exception sending logs: {e}")
            return False

    def run(self):
        print("Starting log generator (running indefinitely)...")
        while True:
            current_time = time.time()
            minutes_elapsed = (current_time - self.start_time) / 60

            log_records = []
                
            if random.random() < 0.7:
                log_records.append(self.generate_normal_logs())
            
            if random.random() < 0.2:
                log_records.append(self.generate_minor_error_logs())
            
            if random.random() < 0.1:
                error_frequency = self.calculate_error_frequency(minutes_elapsed)
                for _ in range(error_frequency):
                    log_records.append(self.generate_escalating_error(minutes_elapsed))
            
            if log_records:
                self.send_to_otlp(log_records)
            
            time.sleep(random.uniform(0.1, 0.5))

if __name__ == "__main__":
    # Get Grafana Cloud configuration from environment variables
    instance_id = os.getenv('GRAFANA_INSTANCE_ID')
    api_key = os.getenv('GRAFANA_API_KEY')

    if not instance_id or not api_key:
        print("Error: Environment variables GRAFANA_INSTANCE_ID and GRAFANA_API_KEY must be set")
        print("Example usage:")
        print("export GRAFANA_INSTANCE_ID='your-instance-id'")
        print("export GRAFANA_API_KEY='your-api-key'")
        print("export OTLP_ENDPOINT='your-otlp-endpoint' # Optional - defaults to Grafana Cloud endpoint")
        exit(1)
    
    generator = ACMETravelLogGenerator(instance_id, api_key)
    generator.run()
