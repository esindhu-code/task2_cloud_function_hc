import functions_framework
import google.cloud.logging
import google.cloud.pubsub_v1
import os
import time


# Environment variables (set in Cloud Function configuration)

PROJECT_ID = os.environ.get("PROJECT_ID", "dev-project-449909")
PUBSUB_TOPIC = os.environ.get("PUBSUB_TOPIC", "disaster-alert")
REPLICATION_LAG_THRESHOLD = int(os.environ.get("REPLICATION_LAG_THRESHOLD", 30))
CONNECTION_COUNT_THRESHOLD = int(os.environ.get("CONNECTION_COUNT_THRESHOLD", 1))
READINESS_PROBE_THRESHOLD = int(os.environ.get("READINESS_PROBE_THRESHOLD", 1))
EXTERNAL_PING_THRESHOLD = int(os.environ.get("EXTERNAL_PING_THRESHOLD", 1))

 
# Initialize logging and Pub/Sub

logging_client = google.cloud.logging.Client()
logger = logging_client.logger("consecutive-failure-monitor")
publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path(PROJECT_ID, PUBSUB_TOPIC)


# Initialize failure counters (in memory; reset on cold start)

failure_counters = {
    "replication_lag": 0,
    "connection_count": 0,
    "readiness_probe": 0,
    "external_ping": 0,
}

# Dummy metric check functions (replace with actual logic)

def check_replication_lag():
 # Replace with your Cloud SQL replication lag check
    lag = time.time() % 60  # Example: Simulate varying lag
    return lag > REPLICATION_LAG_THRESHOLD


def check_connection_count():
# Replace with your Cloud SQL connection count check
    count = time.time() % 5   # Example: Simulate varying connection count
    return count < CONNECTION_COUNT_THRESHOLD


def check_readiness_probe():
 # Replace with your Cloud Run readiness probe check
    return time.time() % 10 > READINESS_PROBE_THRESHOLD  # Simulated readiness probe failure


def check_external_ping():
 # Replace with your external ping check
    return time.time() % 15 > EXTERNAL_PING_THRESHOLD  # Simulated external ping failure

# Cloud Function triggered via HTTP request
@functions_framework.http
def consecutive_failure_monitor(request):
    try:
        # Check metrics
        replication_lag_failed = check_replication_lag()
        connection_count_failed = check_connection_count()
        readiness_probe_failed = check_readiness_probe()
        external_ping_failed = check_external_ping()

         # Update failure counters
        if replication_lag_failed:
            failure_counters["replication_lag"] += 1
        else:
            failure_counters["replication_lag"] = 0

        if connection_count_failed:
            failure_counters["connection_count"] += 1
        else:
            failure_counters["connection_count"] = 0

        if readiness_probe_failed:
            failure_counters["readiness_probe"] += 1
        else:
            failure_counters["readiness_probe"] = 0

        if external_ping_failed:
            failure_counters["external_ping"] += 1
        else:
            failure_counters["external_ping"] = 0

         # Check for disaster condition (4 consecutive failures)
        disaster_condition = (
            failure_counters["replication_lag"] >= 4
            or failure_counters["connection_count"] >= 4
            or failure_counters["readiness_probe"] >= 4
            or failure_counters["external_ping"] >= 4
        )

        # Log the results
        logger.log_struct(
            {
                "replication_lag_failed": replication_lag_failed,
                "connection_count_failed": connection_count_failed,
                "readiness_probe_failed": readiness_probe_failed,
                "external_ping_failed": external_ping_failed,
                "failure_counters": failure_counters,
                "disaster_condition": disaster_condition,
            },
            severity="INFO",
        )

         # Publish disaster alert if needed
        if disaster_condition:
            message = "Disaster in primary region detected!"
            data = message.encode("utf-8")
            publisher.publish(topic_path, data)
            logger.log_text(f"Published disaster alert to Pub/Sub: {message}", severity="CRITICAL")

        return "OK", 200

    except Exception as e:
        logger.log_text(f"Error: {e}", severity="ERROR")
        return f"Error: {e}", 500
