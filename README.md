# README: Install Docker and Docker Compose (Linux)
# Steps are summarized from the official Docker documentation. https://docs.docker.com/engine/install/ubuntu/

## 1. Uninstall Old Versions (if any)
```bash
for pkg in docker.io docker-doc docker-compose docker-compose-v2 podman-docker containerd runc; do sudo apt-get remove $pkg; done
```
 ## Setup Docker's APT Repository
```bash
# Add Docker's official GPG key:
sudo apt-get update
sudo apt-get install ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

# Add the repository to Apt sources:
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "${UBUNTU_CODENAME:-$VERSION_CODENAME}") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update
```
## 2. Install Docker Engine, Docker Compose, and Containerd
```bash 
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```
## 3. Verify Installation
```bash
sudo docker run hello-world
```

## Install Filebeat , Steps are available on the official Elastic documentation - https://www.elastic.co/docs/reference/beats/filebeat/filebeat-installation-configuration
```bash
curl -L -O https://artifacts.elastic.co/downloads/beats/filebeat/filebeat-9.0.0-amd64.deb
sudo dpkg -i filebeat-9.0.0-amd64.deb
```	
