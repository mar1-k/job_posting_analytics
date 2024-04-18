import os
import re

# Function to validate GCP project name
def is_valid_project_name(project):
    # Project name must start with a letter followed by up to 30 lowercase letters, digits, or hyphens
    return re.match("^[a-z]([-a-z0-9]{0,29}[a-z0-9])?$", project) is not None

# Function to validate file path
def is_valid_file_path(path):
    return os.path.exists(path) and os.path.isfile(path)

# Function to create variables.tf file
def create_variables_tf(credentials, project, region, zone, location, gcs_storage_class, bq_dataset, network, subnetwork):
    with open("variables.tf", "w") as f:
        f.write(f'''variable "credentials" {{
  description = "My Credentials"
  default     = "{credentials}"
}}

variable "project" {{
  description = "Project"
  default     = "{project}"
}}

variable "region" {{
  description = "Your project region"
  default     = "{region}"
  type        = string
}}

variable "zone" {{
  description = "Your project zone"
  default     = "{zone}"
  type        = string
}}

variable "location" {{
  description = "Project Location"
  default     = "{location}"
}}

variable "gcs_storage_class" {{
  description = "Bucket Storage Class"
  default     = "{gcs_storage_class}"
}}

variable "bq_dataset" {{
  description = "Big Query Dataset"
  default     = "{bq_dataset}"
  type        = string
}}

variable "network" {{
  description = "Network for instances/cluster"
  default     = "{network}"
  type        = string
}}

variable "subnetwork" {{
  description = "Subnetwork for instances/cluster"
  default     = "{subnetwork}"
  type        = string
}}
''')

# Main function
def main():
    # Prompt user for input
    credentials = input("Enter the path to your credentials file: ")

    # Validate file path
    while not is_valid_file_path(credentials):
        print("Invalid file path.")
        credentials = input("Enter the path to your credentials file again: ")

    project = input("Enter your project name: ")

    # Validate project name
    while not is_valid_project_name(project):
        print("Invalid project name. Project name must start with a letter followed by up to 30 lowercase letters, digits, or hyphens.")
        project = input("Enter your project name again: ")

    # Default values for other variables
    region = "us-central1"
    zone = "us-central1-a"
    location = "US"
    gcs_storage_class = "STANDARD"
    bq_dataset = "job_posting_analytics_dataset"
    network = "default"
    subnetwork = "job-posting-analytics-subnetwork"

    # Create variables.tf file
    create_variables_tf(credentials, project, region, zone, location, gcs_storage_class, bq_dataset, network, subnetwork)

    # Display generated variables.tf content
    with open("variables.tf", "r") as f:
        print("\nGenerated variables.tf content:\n")
        print(f.read())

    # Prompt user to confirm
    confirmation = input("\nAre the provided defaults okay? (yes/no): ").lower()
    if confirmation != "yes":
        print("Exiting. Please provide correct values and run the script again.")
        os.remove("variables.tf")  # Remove the variables.tf file if confirmation is not yes

# Execute the main function
if __name__ == "__main__":
    main()
