terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "5.6.0"
    }
  }
}

provider "google" {
  credentials = file(var.credentials)
  project     = var.project
  region      = var.region
}

data "google_project" "project" {
}

resource "google_compute_subnetwork" "job-posting-analytics-subnetwork" {
  name          = var.subnetwork
  region        = var.region
  network       = var.network
  ip_cidr_range = "192.168.0.0/16"
  project       = var.project

  private_ip_google_access = true # Enable Private Google Access on subnetwork for DataProc
}

#Need this firewall rule to allow internal access
resource "google_compute_firewall" "internal_allow_192_168" {
  name    = "allow-internal-192-168"
  network = var.network

  allow {
    protocol = "all"
  }

  source_ranges = ["192.168.0.0/16"]
}

resource "google_storage_bucket" "job-posting-analytics-bucket" {
  name     = "${var.project}-storage-bucket"
  location = var.region
  force_destroy = true
  uniform_bucket_level_access = true

  lifecycle_rule {
    action {
      type = "Delete"
    }
    condition {
      age = 30 # days
    }
  }
}

resource "google_bigquery_dataset" "bq_dataset" {
  dataset_id = var.bq_dataset
  project    = var.project
  location   = var.region
  delete_contents_on_destroy = true
}

resource "google_compute_firewall" "allow-internet-outbound" {
  name    = "allow-internet-outbound"
  network = var.network
  direction = "EGRESS"

  # Allow outbound traffic to all destinations on port 443 (HTTPS) and port 80 (HTTP)
  allow {
    protocol = "tcp"
    ports    = ["443", "80"]
  }

  # Apply the firewall rule only to the specified instance
  target_tags = ["allow-internet-outbound"]
}

resource "google_service_account" "svc-airflow" {
	account_id = "svc-airflow"
	display_name = "Airflow service account"
}

resource "google_project_iam_binding" "svc-airflow_editor" {
  project = var.project
  role    = "roles/editor"  # This grants editor permissions to the airflow service account

  members = [
    "serviceAccount:${google_service_account.svc-airflow.email}"
  ]
}

resource "google_service_account_key" "svc-airflow-key" {
	service_account_id = google_service_account.svc-airflow.email
	public_key_type = "TYPE_X509_PEM_FILE"
}

locals {
  svc-airflow_key = ("${base64decode(google_service_account_key.svc-airflow-key.private_key)}")
  sensitive = true
}

resource "google_compute_instance" "airflow_vm_instance" {
  depends_on = [google_dataproc_cluster.mulitnode_spark_cluster, google_storage_bucket.job-posting-analytics-bucket, google_compute_subnetwork.job-posting-analytics-subnetwork, google_compute_firewall.internal_allow_192_168, google_compute_firewall.allow-internet-outbound]
  name                      = "job-posting-analytics-airflow-instance"
  machine_type              = "e2-standard-4"
  zone = var.zone
  allow_stopping_for_update = false

  service_account {
    email  = "${data.google_project.project.number}-compute@developer.gserviceaccount.com"
    scopes = ["cloud-platform"]
  }

  boot_disk {
    initialize_params {
      image = "ubuntu-os-cloud/ubuntu-2004-lts"
      size  = 50
    }
  }

  tags = ["allow-internet-outbound"]
  network_interface {
      subnetwork = google_compute_subnetwork.job-posting-analytics-subnetwork.self_link
      access_config {
      }
    }

  metadata_startup_script = <<-EOT
  #!/bin/bash
  
  # Create a directory for the repository on the boot disk
  mkdir -p /home/job_posting_analytics

  
  # Clone the GitHub repository into the persistent directory
  git clone https://github.com/mar1-k/job_posting_analytics /home/job_posting_analytics
  
  # Change to the repository directory
  cd /home/job_posting_analytics/infra/airflow

  #Create the config,logs and jobs directories
  mkdir config
  mkdir data
  mkdir logs
  mkdir jobs
  mkdir jobs/pyspark
  
  # Write svc account key to a JSON file on the VM
  echo '${local.svc-airflow_key}' > ./config/gcp_key.json

  # Write necessary GCP environment variables:
  cat <<EOF > ./config/gcp_env_variables.sh
  export PROJECT_ID="${var.project}"
  export BUCKET_NAME="${google_storage_bucket.job-posting-analytics-bucket.name}"
  export CLUSTER_NAME="${google_dataproc_cluster.mulitnode_spark_cluster.name}"
  export BIGQUERY_DATASET="${var.bq_dataset}"
  export REGION="${var.region}"
  EOF

  # Run setup script
  bash setup.sh
  EOT

}

#Permissions for compute service account in order for Dataproc to work. Also grant bigQuery job user to be able to query dataset
resource "google_project_iam_binding" "dataproc_compute_service_account_roles" {
  project = var.project
  for_each = toset([
    "roles/storage.admin",
    "roles/dataproc.admin",
    "roles/dataproc.worker",
    "roles/bigquery.dataViewer",
    "roles/bigquery.jobUser"
  ])
  role = each.value
  members = [
    "serviceAccount:${data.google_project.project.number}-compute@developer.gserviceaccount.com"
  ]
}

#Need a time sleep for permissions to apply to the compute service account for dataproc provisioning 
resource "time_sleep" "wait_60_seconds" {
  create_duration = "60s"
}

resource "google_dataproc_cluster" "mulitnode_spark_cluster" {
  depends_on = [time_sleep.wait_60_seconds, google_project_iam_binding.dataproc_compute_service_account_roles, google_compute_firewall.internal_allow_192_168]
  name   = "job-posting-analytics-multinode-spark-cluster"
  region = var.region

  cluster_config {
    staging_bucket = google_storage_bucket.job-posting-analytics-bucket.name

    gce_cluster_config {
      internal_ip_only = "true" # Set to true to use private IPs only
      subnetwork       = google_compute_subnetwork.job-posting-analytics-subnetwork.self_link
      zone             = var.zone

      shielded_instance_config {
        enable_secure_boot = true
        enable_integrity_monitoring = true
        enable_vtpm = true
      }
    }

    master_config {
      num_instances = 1
      machine_type  = "e2-standard-4"

      disk_config {
        boot_disk_type    = "pd-ssd"
        boot_disk_size_gb = 30
      }
    }

    worker_config {
      num_instances = 2
      machine_type  = "e2-standard-4"

      disk_config {
        boot_disk_size_gb = 30
      }
    }

    software_config {
      image_version = "2.2-debian12"

      override_properties = {
        "dataproc:dataproc.allow.zero.workers" = "true"
      }

      optional_components = ["JUPYTER"]
    }

    endpoint_config {
      enable_http_port_access = "true"
    }
  }
}

resource "google_cloud_run_service" "streamlit-dashboard" {
  name     = "streamlit-dashboard"
  location = var.region

  template {
    spec {
      containers {
        image = "docker.io/marw1/job_posting_analytics:job_posting_analytics_streamlit_app"
        env {
          name  = "DATABASE_NAME"
          value = var.bq_dataset
        }
        ports {
          container_port = 8501
        }
      }
    }
  }

  traffic {
    percent         = 100
    latest_revision = true
  }

  metadata {
    annotations = {
      "run.googleapis.com/ingress" = "all"
    }
  }
}

resource "google_cloud_run_service_iam_binding" "streamlit-dashboard-invoker" {
  location = google_cloud_run_service.streamlit-dashboard.location
  service  = google_cloud_run_service.streamlit-dashboard.name
  role     = "roles/run.invoker"
  members = [
    "allUsers"
  ]
}

# Print out dataproc cluster URL and Dashboard URL, and Airflow VM IP (For debugging)

output "airflow_vm_ip"{
  value = google_compute_instance.airflow_vm_instance.network_interface[0].access_config[0].nat_ip
}

output "dataproc_cluster_jobs_url" {
  value = "https://console.cloud.google.com/dataproc/clusters/${google_dataproc_cluster.mulitnode_spark_cluster.name}/jobs?region=${var.region}&project=${var.project}"
}

output "dashboard_url" {
  value = google_cloud_run_service.streamlit-dashboard.status[0].url
}

