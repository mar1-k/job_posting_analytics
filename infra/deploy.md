# Deployment

Here are the step-by-step instructions for getting started with this project. I provide the GCP instructions from the Web Console perspective, but you are absolutely welcome to use the CLI or whichever preferred method. 

### Step 0: Clone the Repo and Make sure Terraform is Installed

- Clone this repo to the system where you will be running Terraform from
- Ensure Terraform is installed on your system and that you can use terraform commands

### Step 1: Create a new GCP Project

- Create the GCP project where Terraform will be building everything in

### Step 2: Create a Terraform Service Account

- Go to https://console.cloud.google.com/iam-admin/serviceaccounts within your newly created project and create a new service account for Terraform
- Grant the account the Owner role

  ![image](https://github.com/mar1-k/job_posting_analytics/assets/14811869/347ac50e-c620-4f64-974b-7642cb2031e1)
  ![image](https://github.com/mar1-k/job_posting_analytics/assets/14811869/0bca09ca-98c1-4333-b7fc-d56b47ab7d7d)


### Step 3: Create a Service Account Key

- From the console, click on your newly created service account and navigate to the "KEYS" tab
- Click on "Add Key" to Create a key file for this service account
- Save the key file somewhere safe and accessible on the system that you will be using Terraform from

![image](https://github.com/mar1-k/job_posting_analytics/assets/14811869/436e33f1-4182-4b29-9c89-df3e28dbe309)

### Step 4: Enable Necessary APIs

Terraform will need the following GCP APIs enabled for this project, please enable them in your project

- https://console.developers.google.com/apis/api/iam.googleapis.com/
- https://console.developers.google.com/apis/api/bigquery.googleapis.com/
- https://console.developers.google.com/apis/api/dataproc.googleapis.com/
- https://console.developers.google.com/apis/api/run.googleapis.com/
- https://console.cloud.google.com/marketplace/product/google/compute.googleapis.com
- https://console.cloud.google.com/marketplace/product/google/cloudresourcemanager.googleapis.com

### Step 5: Setup Terraform Variables file

- Navigate to the Terraform folder of this project and ensure that the Terraform variables file `variables.tf` has the correct project name and GCP key file path information
- You may use the provided python script `initialize_variables.py` to make it easier:

![image](https://github.com/mar1-k/job_posting_analytics/assets/14811869/12a33a2e-012e-41e8-a7bb-6644103f14fb)

### Step 6: Terraform init and apply

- While in the Terraform folder of this project run `terraform init` and then `terraform apply`
- Review the Terraform plan and type `yes` if everything looks good, you should see `Plan: 18 to add, 0 to change, 0 to destroy.`
- This may take around 6-8 minutes to finish

![image](https://github.com/mar1-k/job_posting_analytics/assets/14811869/42240d21-e28a-4ffc-ab8e-7e72a3708983)
![image](https://github.com/mar1-k/job_posting_analytics/assets/14811869/c8fad342-559a-461f-bc29-b6bea0b60227)

- NOTE: Occasionly you may see an error like`│ Error: Error creating Dataproc cluster: googleapi: Error 400: Permissions are missing for the default service account '123456789-compute@developer.gserviceaccount.com', missing permissions: [storage.buckets.get, storage.objects.create, storage.objects.delete, storage.objects.get, storage.objects.list, storage.objects.update] on the temp_bucket 'projects/_/buckets/dataproc-temp-us-central1-588255356668-gkbyykuh'. This usually happens when a custom resource (ex: custom staging bucket) or a user-managed VM Service account has been provided and the default/user-managed service account hasn't been granted enough permissions on the resource. See https://cloud.google.com/dataproc/docs/concepts/configuring-clusters/service-accounts#VM_service_account...`
- If you see this error, it is due to permissions in GCP occasionly taking a little longer than usual to apply, simply run terraform apply again a minute later and it should work just fine. I put a 90 second sleep in Terraform to alleviate this problem.

### Step 7: Wait for the Data Pipeline to Finish Running

Once Terraform has finished deploying everything to GCP, it will take about another 15-20 minutes for the Airflow VM to set itself up and go through the whole pipeline. At this point, you are welcome to setup SSH to the Airflow VM instance, tunnel port 8080 and watch the DAGs run. Alternatively, you can just monitor the DataProc jobs for the creation of the main PySpark job. 

- Note that the streamlit dashboard app will be accessible. However, you will get errors due to the data not existing in BigQuery just yet
- To SSH to the Airflow VM, use the IP provided from the `airflow_vm_ip` Terraform output and the method shown in https://www.youtube.com/watch?v=ae-CV2KfoN0&list=PL3MmuxUbc_hJed7dXYoJw8DoCuVHhGEQb
- Here is an example command of me SSHing to the VM and tunneling port 8080 to my local machine: `ssh -i ~/.ssh/<your key> -L 8080:localhost:8080 <your-username>@<your_airflow_vm_ip_here>`
- The credentials for the Airflow GUI are `admin` and `airflow`
- You may use the URL provided from the `dataproc_cluster_jobs_url` to monitor for the PySpark job, note that there will be no jobs there until the data pipeline gets to the point where it submits the job. Also note that for cost saving reasons, I have Airflow delete the dataproc cluster once it is done succesfully using it, so you won't be able to see anything at the URL if you get to it too late.

![image](https://github.com/mar1-k/job_posting_analytics/assets/14811869/de5faf3a-e231-4978-b01f-2d4429c6522b)
![image](https://github.com/mar1-k/job_posting_analytics/assets/14811869/ba241fa8-59ae-4875-95d0-f30d6300e762)
![image](https://github.com/mar1-k/job_posting_analytics/assets/14811869/4dfb516b-e19e-4a10-802a-bfa79475046e)
![image](https://github.com/mar1-k/job_posting_analytics/assets/14811869/4ca02b4e-0c43-4765-8886-49f01648adf3)



### Step 8: Enjoy the Dashboard!

Once the pipeline has completed running, you may use the dashboard link provided from the terraform `dashboard_url` output to access the dashboard app to your heart's content. 

### Step 9: Clean up

- Run `terraform destroy`
- Delete the Terraform service account
- Delete the GCP Project

