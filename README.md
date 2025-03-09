# task2_cloud_function_hc
this repository for task2_cloud_function_health check 


# Create a Cloud Function for Health Check Monitoring

## Goal 

- Monitor Cloud SQL replication lag, connection count, Cloud Run readiness probe, and external connectivity.
- If any metric fails 4 times in a row, trigger a disaster alert via Pub/Sub.
- Alert notifications via Cloud Monitoring


## Create a Pub/Sub topic for disaster alerts.

- Deploy a Cloud Function to monitor health metrics.
- Schedule the Cloud Function to run every 30 seconds.
- Set up log-based metrics and alerts.



# Step 1: Enable Required APIs

- Before setting up any resources, we must enable the required GCP services

```bash
gcloud services enable cloudfunctions.googleapis.com \
    pubsub.googleapis.com \
    logging.googleapis.com \
    cloudscheduler.googleapis.com \
    monitoring.googleapis.com
```

   ## Explanation:

   - cloudfunctions.googleapis.com → Enables Cloud Functions.
   - pubsub.googleapis.com → Enables Pub/Sub messaging.
   - logging.googleapis.com → Enables Cloud Logging.
   - cloudscheduler.googleapis.com → Enables scheduled jobs (to run Cloud Function every 30 seconds).
   - monitoring.googleapis.com → Enables Cloud Monitoring.


     ![alt text](image-1.png)



# Step 2 : Create a Pub/Sub Topic for Disaster Alerts 



- We need a Pub/Sub topic where the Cloud Function will publish alerts when a disaster is detected.

- Open Cloud Shell and run:

```bash
gcloud pubsub topics create disaster-alert
```

   ## Explanation:

   - This creates a Pub/Sub topic named disaster-alert, which will be used to send alerts when a failure occurs


     ![alt text](image-2.png)


   - Confirm by running below command:

```bash  
gcloud pubsub topics list
```

   ![alt text](image-3.png)


  - You should see disaster-alert in the output.

   
    ![alt text](image-4.png)








