# Setting up the environment on a cloud VM

In case we have problems setting the environment locally, we can follow these instructions to set it on Google Cloud instead.

**Steps:**
1. Enable Compute Engine API.
2. Generate SSH keys.
3. Create a VM instance.
4. Connect to the VM via SSH.
    * 4.1. Connect to the VM via SSH config file.
    * 4.2. Configure VSCode to access the VM.
5. Configure VM.
    * 5.1. Update package index.
    * 5.2. Install Anaconda distribution.
    * 5.3. Install Docker.
    * 5.4. Install Docker Compose.
    * 5.5. Install Terraform.
6. Transfer files between local and VM.

## 1. Enable Compute Engine API

Enable [Compute Engine API](https://console.cloud.google.com/apis/library/compute.googleapis.com).


## 2. Generate SSH keys

* [Create SSH keys instructions](https://cloud.google.com/compute/docs/connect/create-ssh-keys)
    + `ssh-keygen` generates a private key and a public key in `~/.ssh`.
* Upload the public key to GCP, from GCP console: `Compute Engine > Metadata > SSH KEYS > ADD SSH KEY`. Copy the key we've previously generated (`cat <KEY>.pub`), paste it and save it.


## 3. Create a VM instance

* `Compute Engine > VM instances > CREATE INSTANCE`.
* Set configuration for the VM instance:
    + Name.
    + Region/Zone.
    + Machine configuration: recommended: *E2 series* / *e2-standard-4* instance (4 vCPUs, 16GB RAM).
    + Boot disk: *Ubuntu 20.04 LTS* / Size: 30GB.
    * Leave default values for the other fields and click on *Create*.

## 4. Connect to the VM via SSH

```bash
ssh -i ~/.ssh/<PRIVATE_KEY_NAME> <VM_USERNAME>@<VM_EXTERNAL_IP>
```
Where:
* <PRIVATE_KEY_NAME>: name of the SSH key that we generated previously.
* <VM_USERNAME>: username we used to generate the SSH keys.
* <VM_EXTERNAL_IP>: external IP of the VM that we created.


### 4.1. Connect to the VM via SSH config file

We can also connect by using a `config` file, so that we do not have to remember all this information and we use the VM instance name that we have set when creating it.

Create a `config` file for configuring SSH. It must be readable and writable only by the user and not accesible by others ([source](https://linuxize.com/post/using-the-ssh-config-file/)).

```bash
touch ~/.ssh/config
chmod 600 ~/.ssh/config
```

Add the information to the `config` file:

```config
Host <VM_INSTANCE_NAME>
    HostName <VM_EXTERNAL_IP>
    User <VM_USERNAME>
    IdentityFile ~/.ssh/<PRIVATE_KEY_NAME>
```
<VM_INSTANCE_NAME>: name we have set for the VM instance when we created it.

Now we can connect to the VM by running:

```bash
ssh <VM_INSTANCE_NAME>
```

### 4.2. Configure VSCode to access the VM
We can access the VM via VSCode and take advantage of its usability.
* In **VSCode**, install `Remote - SSH` extension.
* Click on `Open a remote window` button in the bottom left corner of VSCode console.
* Connect to host. Since we have our VM configuration in a `config` file, the name of the VM will directly appear, so we can click on it and a new VSCode window will show up, which will be connected with the VM via SSH.
* Setup port forwarding to local machine: we can forward ports to our local machine from VSCode `PORTS` tab. This way we could connect the VM with our local Postgres (port 5432), pgAdmin (port 8080) or jupyter (port 8888).

## 5. Configure VM

Google Cloud SDK is already installed in the VM (check `gcloud --version`).

### 5.1. Update package index

```bash
sudo apt-get update && sudo apt-get -y upgrade
```

### 5.2. Install Anaconda distribution

Download and install Anaconda in the VM:

```bash
wget https://repo.anaconda.com/archive/Anaconda3-2022.10-Linux-x86_64.sh
bash Anaconda3-2022.10-Linux-x86_64.sh

```

Reload .bashrc (`source ~/.bashrc`) and check installation (for example, with `conda --version`).

### 5.3. Install Docker

Download and install Docker:

```bash
sudo apt-get install docker.io
```

Change settings to be able to install Docker without sudo ([source](https://github.com/sindresorhus/guides/blob/main/docker-without-sudo.md)):
1. Add the docker group if it does not exist yet.
```bash
sudo groupadd docker
```
2. Add the current user to the docker group.
```bash
sudo gpasswd -a $USER docker
```
3. Restart the docker daemon.
```bash
sudo service docker restart
```
4. Log out and log back in so that your group membership is re-evaluated.
5. Check the installation was done correctly (`docker run hello-world`)

### 5.4. Install Docker Compose

1. Create a folder for binary files for your VM user and cd into it.
```bash
mkdir ~/bin && cd ~/bin
```
2. Go to https://github.com/docker/compose/releases and copy the URL for the `docker-compose-linux-x86_64` binary for its latest version.
3. Download the file in the `bin` folder.
```bash
wget https://github.com/docker/compose/releases/download/v2.15.1/docker-compose-linux-x86_64 -O docker-compose
```
4. Make the binary executable.
```bash
chmod +x docker-compose
```
5. To make it executable from any directory, we need to add it to the PATH variable. cd back into the home folder (`cd ~`) and edit the `.bashrc` file (`nano .bashrc`). Add the `bin` directory to the PATH:
```
export PATH="${HOME}/bin:${PATH}"
```
6. Reload .bashrc (`source ~/.bashrc`) and check installation (`docker-compose --version`).


### 5.5. Install Terraform

1. Download the binary file from [Terraform website](https://developer.hashicorp.com/terraform/downloads) in the `bin` directory.

```bash
wget https://releases.hashicorp.com/terraform/1.3.7/terraform_1.3.7_linux_amd64.zip
```
2. Unzip the file.
```bash
sudo apt-get install unzip
unzip terraform_1.3.7_linux_amd64.zip
rm terraform_1.3.7_linux_amd64.zip

```
3. Check installation: `terraform --version`.

## 6. Transfer files between local and VM

Download a file:

```bash
# From your local machine
scp <VM_INSTANCE_NAME>:path/to/remote/file path/to/local/file
```

Upload a file:
```bash
# From your local machine
scp path/to/local/file <VM_INSTANCE_NAME>:path/to/remote/file
```