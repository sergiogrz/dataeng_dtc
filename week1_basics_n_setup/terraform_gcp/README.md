# Terraform and GCP

## What is Terraform

[HashiCorp Terraform](https://developer.hashicorp.com/terraform/intro) is an infrastructure as code tool that lets you define both cloud and on-prem resources in human-readable configuration files that you can version, reuse, and share. You can then use a consistent workflow to provision and manage all of your infrastructure throughout its lifecycle. Terraform can manage low-level components like compute, storage, and networking resources, as well as high-level components like DNS entries and SaaS features.

## Local setup for Terraform and GCP

### Terraform

[Terraform client installation](https://developer.hashicorp.com/terraform/downloads)  

### GCP

Project ID: nomadic-grid-374211  

For this course, we'll use a free version (upto EUR 300 credits). 

1. Create an account with your Google email ID. 
2. Setup a [project](https://console.cloud.google.com/) and note down the "Project ID" (we'll use this later when deploying infra with TF).
3. Setup [service account & authentication](https://cloud.google.com/docs/authentication/getting-started) for this project
    * Grant `Viewer` role to begin with.
    * Download service-account-keys (.json) for auth.
4. Download [SDK](https://cloud.google.com/sdk/docs/quickstart) for local setup.
5. Set environment variable to point to your downloaded GCP keys:
   ```shell
   export GOOGLE_APPLICATION_CREDENTIALS="<path/to/your/service-account-authkeys>.json"
   
   # Refresh token/session, and verify authentication
   gcloud auth application-default login
   ```

#### Project infrastucture modules in GCP

* Google Cloud Storage (GCS): Data Lake.
* BigQuery: Data Warehouse.

**Setup for access:**  
1. [IAM (Identity and Access Management) Roles](https://cloud.google.com/storage/docs/access-control/iam-roles) for service account:
   * Go to the [*IAM* section](https://console.cloud.google.com/iam-admin/iam) of *IAM & Admin*.
   * Click the *Edit principal* icon for your service account.
   * Add these roles in addition to *Viewer* : ***Storage Admin*** + ***Storage Object Admin*** + ***BigQuery Admin***.
   
2. Enable these APIs for your project:
   * [Identity and Access Management (IAM) API](https://console.cloud.google.com/apis/library/iam.googleapis.com)
   * [IAM Service Account Credentials API](https://console.cloud.google.com/apis/library/iamcredentials.googleapis.com)
