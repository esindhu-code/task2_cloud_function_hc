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


   ![image](https://github.com/user-attachments/assets/c4531bed-9977-4eeb-b553-247f23b35e97)




# Step 2 : Create a Pub/Sub Topic for Disaster Alerts 



- We need a Pub/Sub topic where the Cloud Function will publish alerts when a disaster is detected.

- Open Cloud Shell and run:

```bash
gcloud pubsub topics create disaster-alert
```

   ## Explanation:

   - This creates a Pub/Sub topic named disaster-alert, which will be used to send alerts when a failure occurs


    ![image](https://github.com/user-attachments/assets/c685cef4-fc56-4568-9550-620222388d77)



   - Confirm by running below command:

```bash  
gcloud pubsub topics list
```

  ![image](https://github.com/user-attachments/assets/045a7303-d558-4058-b296-621018f0cac0)



  - You should see disaster-alert in the output.


![image](https://github.com/user-attachments/assets/cabe4bc6-18bf-45a7-ad7a-736e932ab865)



# Step 3 : Create a Pub/Sub Subscription


- Run this command to create a subscription for the disaster-alert topic:

  ```bash  
gcloud pubsub subscriptions create disaster-alert-sub \
    --topic=disaster-alert
```


## Explanation:
   - disaster-alert-sub → This is the subscription name (you can choose a different name).
   - --topic=disaster-alert → This subscribes to the disaster-alert topic, which the Cloud Function will publish alerts to.


![image](https://github.com/user-attachments/assets/215ce22a-3cff-41f7-9e37-370aac5bb4bf)



  - Verify the subscription was created successfully:

  ```bash 
gcloud pubsub subscriptions list
```

![image](https://github.com/user-attachments/assets/3cae19b8-d842-4de4-8dff-b2c262ea4f0a)


   - You should see disaster-alert-sub in the list.


![image](https://github.com/user-attachments/assets/4566baec-4b11-47c2-aa4d-5c6fccc54d04)





# Step 4 : Create a Cloud Function to Monitor Health.


   ## The Cloud Function will:
  - Run every 30 seconds.
  - Check Cloud SQL replication lag, connection count, Cloud Run readiness probe, and external connectivity.
  - Maintain failure counters (track consecutive failures).
  - Publish an alert to Pub/Sub if any metric fails 4 times in a row.


  ## step 4.1 : Create a Python File (main.py)

 - Create a working directory and navigate into it.

```bash 
   mkdir gcp-health-monitoring
   cd gcp-health-monitoring
```

![image](https://github.com/user-attachments/assets/f1f87136-80c0-46e6-9c28-142fd78161fc)


- Create main.py:

```bash
  touch main.py
```


![image](https://github.com/user-attachments/assets/3cbb7466-49f6-42af-9876-1d9631d82e4b)


```bash
  vi main.py
```


![image](https://github.com/user-attachments/assets/8f43b640-8b24-4d64-9a37-7eab9f5bdec0)



## Step 4.2 : Create a requirements.txt File

- create file using touch command

```bash
touch requirements.txt
```


![image](https://github.com/user-attachments/assets/59c4e056-38e7-4fa4-aac3-5ff34fe377f0)



- Add these dependencies:


  ```bash
  vi requirements.txt
```


```bash
functions-framework
google-cloud-logging
google-cloud-pubsub
```



![image](https://github.com/user-attachments/assets/0bb6ad4f-e292-40d2-be74-0bd1ba83dc1c)



# Step 5 : Deploy the Cloud Function

```bash
gcloud functions deploy consecutive-failure-monitor \
    --runtime python310 \
    --trigger-http \
    --allow-unauthenticated \
    --set-env-vars PUBSUB_TOPIC=disaster-alert \
    --region us-central1
```


or 

```bash
gcloud functions deploy consecutive-failure-monitor \
    --project YOUR_PROJECT_ID \
    --runtime python310 \
    --trigger-http \
    --allow-unauthenticated \
    --set-env-vars PUBSUB_TOPIC=disaster-alert \
    --region us-central1
```


## Explanation:


- --project YOUR_PROJECT_ID → Ensures deployment happens in the correct GCP project.
- --runtime python310 → Specifies the runtime as Python 3.10.
- --trigger-http → Configures the function to be triggered via HTTP requests.
- --allow-unauthenticated → Allows anyone to access the function without authentication. (Remove this for restricted access.)
- --set-env-vars PUBSUB_TOPIC=disaster-alert → Sets environment variables required by the function.
- --region us-central1 → Deploys the function in the us-central1 region.


## Note : Do You Need to Specify Port 8080?
- No, Cloud Functions (Gen 2) automatically assign a port when deployed. You don't need to mention 8080 explicitly unless you're running it locally.



## Error

![image](https://github.com/user-attachments/assets/3f3d9c55-b614-455d-bad6-a6772d38e912)


- Your Cloud Function (Gen 2) failed to start due to a container health check issue. The error message says:

"The user-provided container failed to start and listen on the port defined provided by the PORT=8080 environment variable within the allocated timeout."


## Possible Causes & Fixes


### Ensure Your Function Listens on the Correct Port
- Cloud Run (Gen 2) expects the function to listen on the $PORT environment variable (usually 8080).
But Cloud Functions (Gen 2) automatically maps HTTP functions to the correct port, so you do not need to set a port manually.
### Fix:
- Make sure your function does not manually set a port and only relies on functions_framework.

### Missing functions_framework Dependency
- Your function must have functions_framework installed.

- Check if your requirements.txt file includes:

```bash
functions-framework
google-cloud-logging
google-cloud-pubsub
```

## Note : All requirements are included, so below screenshots are the troubleshooting steps. 

# OR 

## directly use the app.py code  

## Note : in app.py code just change 


# Before: 

```bash

import functions_framework
import google.cloud.logging
import google.cloud.pubsub_v1
import os
import time

# Load environment variables
PROJECT_ID = os.environ.get("PROJECT_ID", "dev-project-449909")
PUBSUB_TOPIC = os.environ.get("PUBSUB_TOPIC", "disaster-alert")
REPLICATION_LAG_THRESHOLD = int(os.environ.get("REPLICATION_LAG_THRESHOLD", 30))
CONNECTION_COUNT_THRESHOLD = int(os.environ.get("CONNECTION_COUNT_THRESHOLD", 1))
READINESS_PROBE_THRESHOLD = int(os.environ.get("READINESS_PROBE_THRESHOLD", 1))
EXTERNAL_PING_THRESHOLD = int(os.environ.get("EXTERNAL_PING_THRESHOLD", 1))

```

## After:

```bash

import functions_framework
import google.cloud.logging
from google.cloud import pubsub_v1  #  Corrected import
import os
import time

# Load environment variables
PROJECT_ID = os.environ.get("GCP_PROJECT", "dev-project-449909")  #  Fixed environment variable name
PUBSUB_TOPIC = os.environ.get("PUBSUB_TOPIC", "disaster-alert")
REPLICATION_LAG_THRESHOLD = int(os.environ.get("REPLICATION_LAG_THRESHOLD", 30))
CONNECTION_COUNT_THRESHOLD = int(os.environ.get("CONNECTION_COUNT_THRESHOLD", 1))
READINESS_PROBE_THRESHOLD = int(os.environ.get("READINESS_PROBE_THRESHOLD", 1))
EXTERNAL_PING_THRESHOLD = int(os.environ.get("EXTERNAL_PING_THRESHOLD", 1))

```




![image](https://github.com/user-attachments/assets/997f30fb-0eff-45da-a171-0e998a6ba1fb)



![image](https://github.com/user-attachments/assets/20f2c54e-b2e3-4408-a89d-6c43d8069d55)


![image](https://github.com/user-attachments/assets/d02eff5b-2c35-4e22-b6c0-f52d85b5361a)

![image](https://github.com/user-attachments/assets/866a289b-b859-43f5-ae66-a2332b6789ba)



![image](https://github.com/user-attachments/assets/d6d84f51-1621-4018-8e14-c5addc40f880)



![image](https://github.com/user-attachments/assets/d486719f-9bcf-4e5c-990e-fab02417972d)



![image](https://github.com/user-attachments/assets/5add60fb-39e2-4331-93f9-770da7160dc2)



![image](https://github.com/user-attachments/assets/63a22400-8081-414a-a64a-5414ecd0d86a)





# Successfully deployed cloud fucntion 


![image](https://github.com/user-attachments/assets/473a7d8b-4cd6-4bcc-b966-3d9e0889c3f6)



![image](https://github.com/user-attachments/assets/efc28fd4-974d-449b-b524-90332fb7cf47)














