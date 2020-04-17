# AWS Hashicorp Packer Reaper
Hashicorp Packer is a great tool for building Google Compute Engine Images. However, sometimes the virtual machine running packer
is not stopped. This utility stops or terminated all virtual machines with the name tag 'Packer Builder'

You can use it as a command line utility or install it as an Cloud Run service and stop the spend , NoOps style!

## install the packer reaper
to install the packer reaper, type:

```sh
pip install gcp-hashicorp-packer-reaper
```

## show running packer instances
To show running packer instances:
```sh
$ gcp-hashicorp-packer-reaper list
packer-5e99d4f2-b5a5-e9e0-b763-cd5102ae7e73 launched 7 minutes ago in your-project - europe-west4-c - RUNNING
INFO: 1 packer builder instances found
```

## stop running packer instances
To stop running packer instances older than 2 hours:
```sh
$ gcp-hashicorp-packer-reaper stop --older-than 2h

INFO: stopping packer-5e99d4f2-b5a5-e9e0-b763-cd5102ae7e73 in your-project created 3 hours ago
INFO: total of 1 running instances stopped
```

## delete running packer instances
To terminate stopped and running packer instances older than 24 hours:
```sh
gcp-hashicorp-packer-reaper --verbose delete --older-than 24h

INFO: deleting packer-5e99d4f2-b5a5-e9e0-b763-cd5102ae7e73 in your-project created 2 days ago
INFO: total of 1 instances deleted
```

## deploy the packer reaper
To deploy the packer reaper as a service in your project, type:

```sh
git clone https://github.com/binxio/gcp-hashicorp-packer-reaper.git
cd gcp-hashicorp-packer-reaper

PROJECT=$(gcloud config get-value project)
make USERNAME=$PROJECT snapshot

cd terraform
terraform init
vi erterraform apply -var project=$PROJECT -auto-approve
```
This will install the packer reaper in your GCP project and run every hour, and delete
instances older than 24 hours. You can change the schedule and the action to meet your requirements.

