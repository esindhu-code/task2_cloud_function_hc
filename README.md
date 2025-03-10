# task2_cloud_function_hc
this repository for task2_cloud_function_health check 


# Create a Cloud Function for Health Check Monitoring

## Goal 

- Monitor Cloud SQL replication lag, connection count, Cloud Run readiness probe, and external connectivity.
- If any metric fails 4 times in a row, trigger a disaster alert via Pub/Sub.
- Alert notifications via Cloud Monitoring



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





![image](https://github.com/user-attachments/assets/0df04146-493f-4c27-9fb2-8d4a7026f396)





# Successfully deployed cloud function


![image](https://github.com/user-attachments/assets/473a7d8b-4cd6-4bcc-b966-3d9e0889c3f6)



![image](https://github.com/user-attachments/assets/efc28fd4-974d-449b-b524-90332fb7cf47)



![image](https://github.com/user-attachments/assets/58f6be0d-ddbd-4ef1-8ab6-f0f1bd690905)










# Step 5  Schedule the Function to Run Every 30 Seconds 


## 5.1 : Create a Cloud Scheduler Job

-  Google Cloud Scheduler will invoke the Cloud Function every 30 seconds.

  ``` bash

gcloud scheduler jobs create http monitor-job \  # Creates a Cloud Scheduler job named 'monitor-job'
    --schedule "*/30 * * * *" \  # Runs every 30 minutes (Cron format)
    --uri "https://us-central1-dev-project-449909.cloudfunctions.net/consecutive_failure_monitor" \  # URL of the Cloud Function to trigger
    --http-method GET \  # Uses an HTTP GET request to call the function
    --time-zone "UTC" \  # Sets the time zone to UTC
    --location "us-central1"  # Specifies the region where the job will run


``` 

- This runs the function every 30 seconds

      

![image](https://github.com/user-attachments/assets/f5504120-8af6-4693-b8be-682797613ded)



- Now, your Cloud Function will be automatically triggered every 30 minutes

- If you need to check logs or verify execution, you can run:

 ```bash

  gcloud scheduler jobs describe monitor-job --location "us-central1"

```


![image](https://github.com/user-attachments/assets/6f5faa53-0d9e-4160-ad22-a4650ef249eb)


- or check logs in Cloud Logging:


```bash

gcloud logging read "resource.type=cloud_scheduler_job AND resource.labels.job_id=monitor-job" --limit 10

```









# Validation :

### Test Your Function (Publicly Accessible)


```bash
curl -X POST https://us-central1-dev-project-449909.cloudfunctions.net/consecutive_failure_monitor

```

![image](https://github.com/user-attachments/assets/8b7eeef2-5fa6-4348-9284-b12a493bfba2)


- If successful, it should return OK with status 200.
- If there's an issue, it will return Error: <message> with status 500.

### check logs:

``` bash

gcloud functions logs read consecutive_failure_monitor --region=us-central1

```

- This will show whether the function is properly detecting failures and publishing messages to Pub/Sub.


### Logs 

```bash

sravan_kumarp92@cloudshell:~/gcp-health-monitoring (dev-project-449909)$ gcloud functions logs read consecutive_failure_monitor --region=us-central1
LEVEL: Iumarp92@cloudshell:~/gcp-health-monitoring (dev-project-449909)$ gcloud functions logs read consecutive_failure_monitor --region=us-central1
NAME: consecutive-failure-monitor
EXECUTION_ID: 
TIME_UTC: 2025-03-09 21:16:50.851
LOG: 

LEVEL: I
NAME: consecutive-failure-monitor
EXECUTION_ID: 
TIME_UTC: 2025-03-09 21:16:16.195
LOG: 

LEVEL: I
NAME: consecutive-failure-monitor
EXECUTION_ID: 
TIME_UTC: 2025-03-09 21:15:28.000
LOG: Default STARTUP TCP probe succeeded after 1 attempt for container "worker" on port 8080.

LEVEL: I
NAME: consecutive-failure-monitor
EXECUTION_ID: 
TIME_UTC: 2025-03-09 21:15:26.077
LOG: 

LEVEL: 
NAME: consecutive-failure-monitor
EXECUTION_ID: 
TIME_UTC: 2025-03-09 20:51:05.292
LOG: E0000 00:00:1741553465.293242       1 init.cc:232] grpc_wait_for_shutdown_with_timeout() timed out.

LEVEL: 
NAME: consecutive-failure-monitor
EXECUTION_ID: 
TIME_UTC: 2025-03-09 20:51:05.292
LOG: WARNING: All log messages before absl::InitializeLog() is called are written to STDERR

LEVEL: 
NAME: consecutive-failure-monitor
EXECUTION_ID: 
TIME_UTC: 2025-03-09 20:51:01.804
LOG: E0000 00:00:1741553461.804403      13 init.cc:232] grpc_wait_for_shutdown_with_timeout() timed out.

LEVEL: 
NAME: consecutive-failure-monitor
EXECUTION_ID: 
TIME_UTC: 2025-03-09 20:51:01.804
LOG: WARNING: All log messages before absl::InitializeLog() is called are written to STDERR

LEVEL: I
NAME: consecutive-failure-monitor
EXECUTION_ID: 
TIME_UTC: 2025-03-09 20:35:57.390
LOG: Default STARTUP TCP probe succeeded after 1 attempt for container "worker" on port 8080.

LEVEL: E
NAME: consecutive-failure-monitor
EXECUTION_ID: 
TIME_UTC: 2025-03-09 20:15:46.055
LOG: Default STARTUP TCP probe failed 1 time consecutively for container "worker" on port 8080. The instance was not started.

LEVEL: WARNING
NAME: consecutive-failure-monitor
EXECUTION_ID: 
TIME_UTC: 2025-03-09 20:15:45.944
LOG: Container called exit(1).

LEVEL: E
NAME: consecutive-failure-monitor
EXECUTION_ID: 
TIME_UTC: 2025-03-09 20:15:45.314
LOG: Traceback (most recent call last):
  File "/layers/google.python.pip/pip/bin/functions-framework", line 8, in <module>
    sys.exit(_cli())
  File "/layers/google.python.pip/pip/lib/python3.10/site-packages/click/core.py", line 1161, in __call__
    return self.main(*args, **kwargs)
  File "/layers/google.python.pip/pip/lib/python3.10/site-packages/click/core.py", line 1082, in main
    rv = self.invoke(ctx)
  File "/layers/google.python.pip/pip/lib/python3.10/site-packages/click/core.py", line 1443, in invoke
    return ctx.invoke(self.callback, **ctx.params)
  File "/layers/google.python.pip/pip/lib/python3.10/site-packages/click/core.py", line 788, in invoke
    return __callback(*args, **kwargs)
  File "/layers/google.python.pip/pip/lib/python3.10/site-packages/functions_framework/_cli.py", line 36, in _cli
    app = create_app(target, source, signature_type)
  File "/layers/google.python.pip/pip/lib/python3.10/site-packages/functions_framework/__init__.py", line 395, in create_app
    raise e from None
  File "/layers/google.python.pip/pip/lib/python3.10/site-packages/functions_framework/__init__.py", line 376, in create_app
    spec.loader.exec_module(source_module)
  File "<frozen importlib._bootstrap_external>", line 883, in exec_module
  File "<frozen importlib._bootstrap>", line 241, in _call_with_frames_removed
  File "/workspace/main.py", line 18, in <module>
    publisher = pubsub_v1.PublisherClient()
NameError: name 'pubsub_v1' is not defined

LEVEL: E
NAME: consecutive-failure-monitor
EXECUTION_ID: 
TIME_UTC: 2025-03-09 20:07:39.878
LOG: Default STARTUP TCP probe failed 1 time consecutively for container "worker" on port 8080. The instance was not started.

LEVEL: WARNING
NAME: consecutive-failure-monitor
EXECUTION_ID: 
TIME_UTC: 2025-03-09 20:07:39.767
LOG: Container called exit(1).

LEVEL: E
NAME: consecutive-failure-monitor
EXECUTION_ID: 
TIME_UTC: 2025-03-09 20:07:39.334
LOG: Traceback (most recent call last):
  File "/layers/google.python.pip/pip/bin/functions-framework", line 8, in <module>
    sys.exit(_cli())
  File "/layers/google.python.pip/pip/lib/python3.10/site-packages/click/core.py", line 1161, in __call__
    return self.main(*args, **kwargs)
  File "/layers/google.python.pip/pip/lib/python3.10/site-packages/click/core.py", line 1082, in main
    rv = self.invoke(ctx)
  File "/layers/google.python.pip/pip/lib/python3.10/site-packages/click/core.py", line 1443, in invoke
    return ctx.invoke(self.callback, **ctx.params)
  File "/layers/google.python.pip/pip/lib/python3.10/site-packages/click/core.py", line 788, in invoke
    return __callback(*args, **kwargs)
  File "/layers/google.python.pip/pip/lib/python3.10/site-packages/functions_framework/_cli.py", line 36, in _cli
    app = create_app(target, source, signature_type)
  File "/layers/google.python.pip/pip/lib/python3.10/site-packages/functions_framework/__init__.py", line 395, in create_app
    raise e from None
  File "/layers/google.python.pip/pip/lib/python3.10/site-packages/functions_framework/__init__.py", line 376, in create_app
    spec.loader.exec_module(source_module)
  File "<frozen importlib._bootstrap_external>", line 883, in exec_module
  File "<frozen importlib._bootstrap>", line 241, in _call_with_frames_removed
  File "/workspace/main.py", line 18, in <module>
    publisher = pubsub_v1.PublisherClient()
NameError: name 'pubsub_v1' is not defined

LEVEL: E
NAME: consecutive-failure-monitor
EXECUTION_ID: 
TIME_UTC: 2025-03-09 20:03:37.251
LOG: Default STARTUP TCP probe failed 1 time consecutively for container "worker" on port 8080. The instance was not started.

LEVEL: WARNING
NAME: consecutive-failure-monitor
EXECUTION_ID: 
TIME_UTC: 2025-03-09 20:03:37.167
LOG: Container called exit(1).

LEVEL: E
NAME: consecutive-failure-monitor
EXECUTION_ID: 
TIME_UTC: 2025-03-09 20:03:36.178
LOG: Traceback (most recent call last):
  File "/layers/google.python.pip/pip/bin/functions-framework", line 8, in <module>
    sys.exit(_cli())
  File "/layers/google.python.pip/pip/lib/python3.10/site-packages/click/core.py", line 1161, in __call__
    return self.main(*args, **kwargs)
  File "/layers/google.python.pip/pip/lib/python3.10/site-packages/click/core.py", line 1082, in main
    rv = self.invoke(ctx)
  File "/layers/google.python.pip/pip/lib/python3.10/site-packages/click/core.py", line 1443, in invoke
    return ctx.invoke(self.callback, **ctx.params)
  File "/layers/google.python.pip/pip/lib/python3.10/site-packages/click/core.py", line 788, in invoke
    return __callback(*args, **kwargs)
  File "/layers/google.python.pip/pip/lib/python3.10/site-packages/functions_framework/_cli.py", line 36, in _cli
    app = create_app(target, source, signature_type)
  File "/layers/google.python.pip/pip/lib/python3.10/site-packages/functions_framework/__init__.py", line 395, in create_app
    raise e from None
  File "/layers/google.python.pip/pip/lib/python3.10/site-packages/functions_framework/__init__.py", line 376, in create_app
    spec.loader.exec_module(source_module)
  File "<frozen importlib._bootstrap_external>", line 883, in exec_module
  File "<frozen importlib._bootstrap>", line 241, in _call_with_frames_removed
  File "/workspace/main.py", line 18, in <module>
    publisher = pubsub_v1.PublisherClient()
NameError: name 'pubsub_v1' is not defined

LEVEL: E
NAME: consecutive-failure-monitor
EXECUTION_ID: 
TIME_UTC: 2025-03-09 19:50:07.645
LOG: Default STARTUP TCP probe failed 1 time consecutively for container "worker" on port 8080. The instance was not started.

LEVEL: WARNING
NAME: consecutive-failure-monitor
EXECUTION_ID: 
TIME_UTC: 2025-03-09 19:50:07.568
LOG: Container called exit(1).
sravan_kumarp92@cloudshell:~/gcp-health-monitoring (dev-project-449909)$


```


or 

```bash

gcloud functions logs read consecutive_failure_monitor --limit=50

```


- Understanding the Output:

- If logs are displayed:

- Look for "Published disaster alert to Pub/Sub" → This confirms the function detected a disaster condition.
- Look for "OK" → Confirms the function successfully returned a 200 response.



```bash

sravan_kumarp92@cloudshell:~/gcp-health-monitoring (dev-project-449909)$ gcloud functions logs read consecutive_failure_monitor --limit=50
LEVEL: 
NAME: consecutive-failure-monitor
EXECUTION_ID: 
TIME_UTC: 2025-03-09 22:15:15.398
LOG: E0000 00:00:1741558515.399004       1 init.cc:232] grpc_wait_for_shutdown_with_timeout() timed out.

LEVEL: 
NAME: consecutive-failure-monitor
EXECUTION_ID: 
TIME_UTC: 2025-03-09 22:15:15.398
LOG: WARNING: All log messages before absl::InitializeLog() is called are written to STDERR

LEVEL: 
NAME: consecutive-failure-monitor
EXECUTION_ID: 
TIME_UTC: 2025-03-09 22:15:11.890
LOG: E0000 00:00:1741558511.890263      13 init.cc:232] grpc_wait_for_shutdown_with_timeout() timed out.

LEVEL: 
NAME: consecutive-failure-monitor
EXECUTION_ID: 
TIME_UTC: 2025-03-09 22:15:11.890
LOG: WARNING: All log messages before absl::InitializeLog() is called are written to STDERR

LEVEL: I
NAME: consecutive-failure-monitor
EXECUTION_ID: 
TIME_UTC: 2025-03-09 22:00:01.302
LOG: 

LEVEL: I
NAME: consecutive-failure-monitor
EXECUTION_ID: 
TIME_UTC: 2025-03-09 21:47:05.703
LOG: 

LEVEL: I
NAME: consecutive-failure-monitor
EXECUTION_ID: 
TIME_UTC: 2025-03-09 21:46:59.114
LOG: Default STARTUP TCP probe succeeded after 1 attempt for container "worker" on port 8080.

LEVEL: I
NAME: consecutive-failure-monitor
EXECUTION_ID: 
TIME_UTC: 2025-03-09 21:46:57.405
LOG: 

LEVEL: 
NAME: consecutive-failure-monitor
EXECUTION_ID: 
TIME_UTC: 2025-03-09 21:32:05.291
LOG: E0000 00:00:1741555925.291768       1 init.cc:232] grpc_wait_for_shutdown_with_timeout() timed out.

LEVEL: 
NAME: consecutive-failure-monitor
EXECUTION_ID: 
TIME_UTC: 2025-03-09 21:32:05.291
LOG: WARNING: All log messages before absl::InitializeLog() is called are written to STDERR

LEVEL: 
NAME: consecutive-failure-monitor
EXECUTION_ID: 
TIME_UTC: 2025-03-09 21:32:01.797
LOG: E0000 00:00:1741555921.797433      13 init.cc:232] grpc_wait_for_shutdown_with_timeout() timed out.

LEVEL: 
NAME: consecutive-failure-monitor
EXECUTION_ID: 
TIME_UTC: 2025-03-09 21:32:01.797
LOG: WARNING: All log messages before absl::InitializeLog() is called are written to STDERR

LEVEL: I
NAME: consecutive-failure-monitor
EXECUTION_ID: 
TIME_UTC: 2025-03-09 21:16:50.851
LOG: 

LEVEL: I
NAME: consecutive-failure-monitor
EXECUTION_ID: 
TIME_UTC: 2025-03-09 21:16:16.195
LOG: 

LEVEL: I
NAME: consecutive-failure-monitor
EXECUTION_ID: 
TIME_UTC: 2025-03-09 21:15:28.000
LOG: Default STARTUP TCP probe succeeded after 1 attempt for container "worker" on port 8080.

LEVEL: I
NAME: consecutive-failure-monitor
EXECUTION_ID: 
TIME_UTC: 2025-03-09 21:15:26.077
LOG: 

LEVEL: 
NAME: consecutive-failure-monitor
EXECUTION_ID: 
TIME_UTC: 2025-03-09 20:51:05.292
LOG: E0000 00:00:1741553465.293242       1 init.cc:232] grpc_wait_for_shutdown_with_timeout() timed out.

LEVEL: 
NAME: consecutive-failure-monitor
EXECUTION_ID: 
TIME_UTC: 2025-03-09 20:51:05.292
LOG: WARNING: All log messages before absl::InitializeLog() is called are written to STDERR

LEVEL: 
NAME: consecutive-failure-monitor
EXECUTION_ID: 
TIME_UTC: 2025-03-09 20:51:01.804
LOG: E0000 00:00:1741553461.804403      13 init.cc:232] grpc_wait_for_shutdown_with_timeout() timed out.

LEVEL: 
NAME: consecutive-failure-monitor
EXECUTION_ID: 
TIME_UTC: 2025-03-09 20:51:01.804
LOG: WARNING: All log messages before absl::InitializeLog() is called are written to STDERR

LEVEL: I
NAME: consecutive-failure-monitor
EXECUTION_ID: 
TIME_UTC: 2025-03-09 20:35:57.390
LOG: Default STARTUP TCP probe succeeded after 1 attempt for container "worker" on port 8080.

LEVEL: E
NAME: consecutive-failure-monitor
EXECUTION_ID: 
TIME_UTC: 2025-03-09 20:15:46.055
LOG: Default STARTUP TCP probe failed 1 time consecutively for container "worker" on port 8080. The instance was not started.

LEVEL: WARNING
NAME: consecutive-failure-monitor
EXECUTION_ID: 
TIME_UTC: 2025-03-09 20:15:45.944
LOG: Container called exit(1).

LEVEL: E
NAME: consecutive-failure-monitor
EXECUTION_ID: 
TIME_UTC: 2025-03-09 20:15:45.314
LOG: Traceback (most recent call last):
  File "/layers/google.python.pip/pip/bin/functions-framework", line 8, in <module>
    sys.exit(_cli())
  File "/layers/google.python.pip/pip/lib/python3.10/site-packages/click/core.py", line 1161, in __call__
    return self.main(*args, **kwargs)
  File "/layers/google.python.pip/pip/lib/python3.10/site-packages/click/core.py", line 1082, in main
    rv = self.invoke(ctx)
  File "/layers/google.python.pip/pip/lib/python3.10/site-packages/click/core.py", line 1443, in invoke
    return ctx.invoke(self.callback, **ctx.params)
  File "/layers/google.python.pip/pip/lib/python3.10/site-packages/click/core.py", line 788, in invoke
    return __callback(*args, **kwargs)
  File "/layers/google.python.pip/pip/lib/python3.10/site-packages/functions_framework/_cli.py", line 36, in _cli
    app = create_app(target, source, signature_type)
  File "/layers/google.python.pip/pip/lib/python3.10/site-packages/functions_framework/__init__.py", line 395, in create_app
    raise e from None
  File "/layers/google.python.pip/pip/lib/python3.10/site-packages/functions_framework/__init__.py", line 376, in create_app
    spec.loader.exec_module(source_module)
  File "<frozen importlib._bootstrap_external>", line 883, in exec_module
  File "<frozen importlib._bootstrap>", line 241, in _call_with_frames_removed
  File "/workspace/main.py", line 18, in <module>
    publisher = pubsub_v1.PublisherClient()
NameError: name 'pubsub_v1' is not defined

LEVEL: E
NAME: consecutive-failure-monitor
EXECUTION_ID: 
TIME_UTC: 2025-03-09 20:07:39.878
LOG: Default STARTUP TCP probe failed 1 time consecutively for container "worker" on port 8080. The instance was not started.

LEVEL: WARNING
NAME: consecutive-failure-monitor
EXECUTION_ID: 
TIME_UTC: 2025-03-09 20:07:39.767
LOG: Container called exit(1).

LEVEL: E
NAME: consecutive-failure-monitor
EXECUTION_ID: 
TIME_UTC: 2025-03-09 20:07:39.334
LOG: Traceback (most recent call last):
  File "/layers/google.python.pip/pip/bin/functions-framework", line 8, in <module>
    sys.exit(_cli())
  File "/layers/google.python.pip/pip/lib/python3.10/site-packages/click/core.py", line 1161, in __call__
    return self.main(*args, **kwargs)
  File "/layers/google.python.pip/pip/lib/python3.10/site-packages/click/core.py", line 1082, in main
    rv = self.invoke(ctx)
  File "/layers/google.python.pip/pip/lib/python3.10/site-packages/click/core.py", line 1443, in invoke
    return ctx.invoke(self.callback, **ctx.params)
  File "/layers/google.python.pip/pip/lib/python3.10/site-packages/click/core.py", line 788, in invoke
    return __callback(*args, **kwargs)
  File "/layers/google.python.pip/pip/lib/python3.10/site-packages/functions_framework/_cli.py", line 36, in _cli
    app = create_app(target, source, signature_type)
  File "/layers/google.python.pip/pip/lib/python3.10/site-packages/functions_framework/__init__.py", line 395, in create_app
    raise e from None
  File "/layers/google.python.pip/pip/lib/python3.10/site-packages/functions_framework/__init__.py", line 376, in create_app
    spec.loader.exec_module(source_module)
  File "<frozen importlib._bootstrap_external>", line 883, in exec_module
  File "<frozen importlib._bootstrap>", line 241, in _call_with_frames_removed
  File "/workspace/main.py", line 18, in <module>
    publisher = pubsub_v1.PublisherClient()
NameError: name 'pubsub_v1' is not defined

LEVEL: E
NAME: consecutive-failure-monitor
EXECUTION_ID: 
TIME_UTC: 2025-03-09 20:03:37.251
LOG: Default STARTUP TCP probe failed 1 time consecutively for container "worker" on port 8080. The instance was not started.

LEVEL: WARNING
NAME: consecutive-failure-monitor
EXECUTION_ID: 
TIME_UTC: 2025-03-09 20:03:37.167
LOG: Container called exit(1).

LEVEL: E
NAME: consecutive-failure-monitor
EXECUTION_ID: 
TIME_UTC: 2025-03-09 20:03:36.178
LOG: Traceback (most recent call last):
  File "/layers/google.python.pip/pip/bin/functions-framework", line 8, in <module>
    sys.exit(_cli())
  File "/layers/google.python.pip/pip/lib/python3.10/site-packages/click/core.py", line 1161, in __call__
    return self.main(*args, **kwargs)
  File "/layers/google.python.pip/pip/lib/python3.10/site-packages/click/core.py", line 1082, in main
    rv = self.invoke(ctx)
  File "/layers/google.python.pip/pip/lib/python3.10/site-packages/click/core.py", line 1443, in invoke
    return ctx.invoke(self.callback, **ctx.params)
  File "/layers/google.python.pip/pip/lib/python3.10/site-packages/click/core.py", line 788, in invoke
    return __callback(*args, **kwargs)
  File "/layers/google.python.pip/pip/lib/python3.10/site-packages/functions_framework/_cli.py", line 36, in _cli
    app = create_app(target, source, signature_type)
  File "/layers/google.python.pip/pip/lib/python3.10/site-packages/functions_framework/__init__.py", line 395, in create_app
    raise e from None
  File "/layers/google.python.pip/pip/lib/python3.10/site-packages/functions_framework/__init__.py", line 376, in create_app
    spec.loader.exec_module(source_module)
  File "<frozen importlib._bootstrap_external>", line 883, in exec_module
  File "<frozen importlib._bootstrap>", line 241, in _call_with_frames_removed
  File "/workspace/main.py", line 18, in <module>
    publisher = pubsub_v1.PublisherClient()
NameError: name 'pubsub_v1' is not defined

LEVEL: E
NAME: consecutive-failure-monitor
EXECUTION_ID: 
TIME_UTC: 2025-03-09 19:50:07.645
LOG: Default STARTUP TCP probe failed 1 time consecutively for container "worker" on port 8080. The instance was not started.

LEVEL: WARNING
NAME: consecutive-failure-monitor
EXECUTION_ID: 
TIME_UTC: 2025-03-09 19:50:07.568
LOG: Container called exit(1).

LEVEL: E
NAME: consecutive-failure-monitor
EXECUTION_ID: 
TIME_UTC: 2025-03-09 19:50:07.031
LOG: Traceback (most recent call last):
  File "/layers/google.python.pip/pip/bin/functions-framework", line 8, in <module>
    sys.exit(_cli())
  File "/layers/google.python.pip/pip/lib/python3.10/site-packages/click/core.py", line 1161, in __call__
    return self.main(*args, **kwargs)
  File "/layers/google.python.pip/pip/lib/python3.10/site-packages/click/core.py", line 1082, in main
    rv = self.invoke(ctx)
  File "/layers/google.python.pip/pip/lib/python3.10/site-packages/click/core.py", line 1443, in invoke
    return ctx.invoke(self.callback, **ctx.params)
  File "/layers/google.python.pip/pip/lib/python3.10/site-packages/click/core.py", line 788, in invoke
    return __callback(*args, **kwargs)
  File "/layers/google.python.pip/pip/lib/python3.10/site-packages/functions_framework/_cli.py", line 36, in _cli
    app = create_app(target, source, signature_type)
  File "/layers/google.python.pip/pip/lib/python3.10/site-packages/functions_framework/__init__.py", line 395, in create_app
    raise e from None
  File "/layers/google.python.pip/pip/lib/python3.10/site-packages/functions_framework/__init__.py", line 376, in create_app
    spec.loader.exec_module(source_module)
  File "<frozen importlib._bootstrap_external>", line 883, in exec_module
  File "<frozen importlib._bootstrap>", line 241, in _call_with_frames_removed
  File "/workspace/main.py", line 18, in <module>
    publisher = pubsub_v1.PublisherClient()
NameError: name 'pubsub_v1' is not defined

LEVEL: 
NAME: consecutive-failure-monitor
EXECUTION_ID: 
TIME_UTC: 2025-03-09 11:27:24.289
LOG: E0000 00:00:1741519644.290213       1 init.cc:232] grpc_wait_for_shutdown_with_timeout() timed out.

LEVEL: 
NAME: consecutive-failure-monitor
EXECUTION_ID: 
TIME_UTC: 2025-03-09 11:27:24.289
LOG: WARNING: All log messages before absl::InitializeLog() is called are written to STDERR

LEVEL: 
NAME: consecutive-failure-monitor
EXECUTION_ID: 
TIME_UTC: 2025-03-09 11:27:20.987
LOG: E0000 00:00:1741519640.988410      13 init.cc:232] grpc_wait_for_shutdown_with_timeout() timed out.

LEVEL: 
NAME: consecutive-failure-monitor
EXECUTION_ID: 
TIME_UTC: 2025-03-09 11:27:20.987
LOG: WARNING: All log messages before absl::InitializeLog() is called are written to STDERR

LEVEL: 
NAME: consecutive-failure-monitor
EXECUTION_ID: vxZadM61JZ6d
TIME_UTC: 2025-03-09 11:12:11.427
LOG: Published disaster alert to Pub/Sub: Disaster in primary region detected!

LEVEL: I
NAME: consecutive-failure-monitor
EXECUTION_ID: 
TIME_UTC: 2025-03-09 11:12:11.423
LOG: 

LEVEL: I
NAME: consecutive-failure-monitor
EXECUTION_ID: 
TIME_UTC: 2025-03-09 11:12:09.962
LOG: 

LEVEL: I
NAME: consecutive-failure-monitor
EXECUTION_ID: 
TIME_UTC: 2025-03-09 11:12:07.060
LOG: 

LEVEL: I
NAME: consecutive-failure-monitor
EXECUTION_ID: 
TIME_UTC: 2025-03-09 11:12:02.357
LOG: 

LEVEL: I
NAME: consecutive-failure-monitor
EXECUTION_ID: 
TIME_UTC: 2025-03-09 11:12:00.269
LOG: 

LEVEL: 
NAME: consecutive-failure-monitor
EXECUTION_ID: n5uriIIlzLOR
TIME_UTC: 2025-03-09 11:11:57.204
LOG: Published disaster alert to Pub/Sub: Disaster in primary region detected!

LEVEL: I
NAME: consecutive-failure-monitor
EXECUTION_ID: 
TIME_UTC: 2025-03-09 11:11:57.197
LOG: 

LEVEL: 
NAME: consecutive-failure-monitor
EXECUTION_ID: PtlSoh3ZKaXL
TIME_UTC: 2025-03-09 11:11:53.954
LOG: Published disaster alert to Pub/Sub: Disaster in primary region detected!

LEVEL: I
NAME: consecutive-failure-monitor
EXECUTION_ID: 
TIME_UTC: 2025-03-09 11:11:53.949
LOG: 

LEVEL: 
NAME: consecutive-failure-monitor
EXECUTION_ID: hLHno607Tqdj
TIME_UTC: 2025-03-09 11:11:50.479
LOG: Published disaster alert to Pub/Sub: Disaster in primary region detected!

LEVEL: I
NAME: consecutive-failure-monitor
EXECUTION_ID: 
TIME_UTC: 2025-03-09 11:11:50.473
LOG: 

LEVEL: 
NAME: consecutive-failure-monitor
EXECUTION_ID: 6bTVgmEHnZGC
TIME_UTC: 2025-03-09 11:11:47.892
LOG: Published disaster alert to Pub/Sub: Disaster in primary region detected!
sravan_kumarp92@cloudshell:~/gcp-health-monitoring (dev-project-449909)$ 

```




### Check Pub/Sub Messages (If Disaster Alert Triggered)

- If your function should publish messages to Pub/Sub, verify if messages are being sent:

```bash

  gcloud pubsub subscriptions pull projects/dev-project-449909/subscriptions/YOUR_SUBSCRIPTION_NAME --auto-ack

```

 - Replace YOUR_SUBSCRIPTION_NAME with your actual Pub/Sub subscription.



![image](https://github.com/user-attachments/assets/ba186e33-d33a-4f2d-8ea0-75d65f84db18)




# Commands:

```bash

   74  ls -lrth
   75  cd gcp-health-monitoring/
   76  clear
   77  ls -lrth
   78  vi main.py
   79  cat main.py 
   80  cleart
   81  touch requirements.txt
   82  ls -lrth
   83  rm requirements.txt 
   84  clear
   85  to
   86  touch requirements.txt
   87  ls -lrth
   88  vi requirements.txt 
   89  cat requirements.txt 
   90  vi requirements.txt 
   91  cat requirements.txt 
   92  gcloud functions deploy consecutive-failure-monitor     --runtime python310     --trigger-http     --allow-unauthenticated     --set-env-vars PUBSUB_TOPIC=disaster-alert     --region us-central1
   93  vi requirements.txt 
   94  pip list | grep functions-framework
   95  pip install functions-framework
   96  pip list | grep functions-framework
   97  gcloud functions deploy consecutive-failure-monitor     --project dev-project-449909     --runtime python310     --trigger-http     --allow-unauthenticated     --set-env-vars PUBSUB_TOPIC=disaster-alert     --region us-central1
   98  vi main.py 
   99  gcloud functions deploy consecutive-failure-monitor     --project dev-project-449909     --runtime python310     --trigger-http     --allow-unauthenticated     --set-env-vars PUBSUB_TOPIC=disaster-alert     --region us-central1
  100  cat main.py 
  101  cat requirements.txt 
  102  functions-framework --target=consecutive_failure_monitor --port=8080
  103  ls
  104  functions-framework --target=consecutive_failure_monitor --port=8080 --debug
  105  pip show functions-framework
  106  gcloud functions delete consecutive-failure-monitor --region=us-central1
  107  gcloud functions deploy consecutive-failure-monitor     --project dev-project-449909     --runtime python310     --trigger-http     --allow-unauthenticated     --set-env-vars PUBSUB_TOPIC=disaster-alert     --region us-central1     --entry-point=consecutive_failure_monitor
  108  vi main.py 
  109  pip install -r requirements.txt --upgrade
  110  pip show functions-framework
  111  functions-framework --target=consecutive_failure_monitor --port=8080
  112  ls -l ~/gcp-health-monitoring
  113  grep "def consecutive_failure_monitor" ~/gcp-health-monitoring/main.py
  114  python3 -c "import main; print(dir(main))"
  115  vi main.py 
  116  cat main.py 
  117  vi main.py 
  118  cat main.py 
  119  gcloud functions deploy consecutive_failure_monitor   --runtime python311   --trigger-http   --allow-unauthenticated   --region=us-central1
  120  ls -lrth
  121  cat requirements.txt 
  122  cd _
  123  cd __pycache__
  124  ls
  125  cd ..
  126  ls -lrth
  127  cd __pycache__
  128  ls -lrth
  129  cat main.cpython-312.pyc 
  130  cd ..
  131  ls -lrth
  132  cd __pycache__
  133  ls -lrth
  134  history
```





# NOTE: Validation can be done in multiple ways, so we need to understand the concept














# Main troubleshooting  

after getting code 3 error 


 ```bash
    pip list | grep functions-framework
    pip install functions-framework
    pip list | grep functions-framework
   
    pip install -r requirements.txt --upgrade
    pip show functions-framework
 ```
    then deploy cloud function 

