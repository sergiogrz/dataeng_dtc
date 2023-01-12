# Terraform setup

## What is Terraform

[HashiCorp Terraform](https://developer.hashicorp.com/terraform/intro) is an infrastructure as code (IaC) tool that lets you define both cloud and on-prem resources in human-readable configuration files that you can version, reuse, and share. You can then use a consistent workflow to provision and manage all of your infrastructure throughout its lifecycle. Terraform can manage low-level components like compute, storage, and networking resources, as well as high-level components like DNS entries and SaaS features.

**Some advantages:**
* Terraform can manage infrastructure on multiple cloud platforms.
* The human-readable configuration language helps you write infrastructure code quickly.
* Terraform's state allows you to track resource changes throughout your deployments.
* You can commit your configurations to version control to safely collaborate on infrastructure.


## Creating a GCP infrastructure with Terraform

### Structure inside [terraform](https://github.com/sergiogrz/dataeng_dtc/tree/main/week1_basics_n_setup/terraform_gcp/terraform) directory:
* `main.tf`.
* `variables.tf`.
* Optional: `resources.tf`, `output.tf`.
* `.tfstate` (automatically created after `terraform apply` operation).

### Declarations

See [Terraform Language Documentation](https://developer.hashicorp.com/terraform/language).

* `terraform`: configure basic Terraform settings to provision your infrastructure.
   * `required_version`: minimum Terraform version to apply to your configuration.
   * `backend`: stores Terraform's "state" snapshots, to map real-world resources to your configuration.
      * `local`: stores state file locally as `terraform.tfstate`.
   * `required_providers`: specifies the providers required by the current module.
* `provider`:
   * adds a set of resource types and/or data sources that Terraform can manage.
   * the [Terraform Registry](https://registry.terraform.io/) is the main directory of publicly available providers from most major infrastructure platforms.
* `resource`
  * blocks to define components of your infrastructure.
  * project modules/resources: google_storage_bucket, google_bigquery_dataset.
* `variable` & `locals`
  * runtime arguments and constants


### Execution

**Steps:**
1. `terraform init`: 
    * Initializes and configures the backend, installs plugins/providers and checks out an existing configuration from a version control.
2. `terraform plan`:
    * Matches/previews local changes against a remote state and proposes an Execution Plan.
3. `terraform apply`: 
    * Asks for approval to the proposed plan and applies changes to the Cloud.
4. `terraform destroy`
    * Removes your stack from the Cloud.

```bash
# Refresh service-account's auth-token for this session
gcloud auth application-default login

# Initialize state file (.tfstate)
terraform init
```
```bash
# Check changes to new infra plan
terraform plan -var="project=<your-gcp-project-id>"
```
```bash
# Create new infra
terraform apply -var="project=<your-gcp-project-id>"
```
```bash
# Delete infra after your work, to avoid costs on any running services
terraform destroy
```
