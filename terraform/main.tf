terraform {
  required_version = ">= 0.12"
}

variable project {
  type = string
}

variable region {
  type    = string
  default = "europe-west1"
}

provider google {
  project = var.project
  region  = var.region
}

data google_project current {
  provider = google
}

resource "google_cloud_run_service" "packer-reaper" {
  name     = "gcp-hashicorp-packer-reaper"
  location = var.region

  template {
    spec {
      service_account_name = google_service_account.packer-reaper.email
      containers {
        image = "gcr.io/${data.google_project.current.project_id}/gcp-hashicorp-packer-reaper:latest"
      }
    }
  }
  timeouts {
    create = "10m"
  }
  depends_on = [google_project_service.run]
  project    = data.google_project.current.project_id
}

output "reaper-url" {
  value = "${google_cloud_run_service.packer-reaper.status[0].url}"
}

resource "google_service_account" "packer-reaper" {
  display_name = "Hashicorp Packer reaper"
  account_id   = "packer-reaper"
  project      = data.google_project.current.project_id
}

resource "google_project_iam_member" "packer-reaper-compute-engine" {
  role    = "roles/compute.instanceAdmin" # way too much permission, but could not find a smaller one.
  member  = "serviceAccount:${google_service_account.packer-reaper.email}"
  project = data.google_project.current.project_id
}

resource "google_cloud_scheduler_job" "packer-reaper" {
  name        = "packer-reaper"
  description = "invoke every hour"
  schedule    = "*/1 * * * *"

  http_target {
    http_method = "GET"
    uri         = "${google_cloud_run_service.packer-reaper.status[0].url}/delete?dry_run=false&older_than=2h"
    oidc_token {
      service_account_email = google_service_account.scheduler.email
    }
  }
  depends_on = [google_project_service.cloudscheduler]
  project    = data.google_project.current.project_id
}

resource "google_service_account" "scheduler" {
  display_name = "Google Cloud Scheduler invoker"
  account_id   = "scheduler"
  project      = data.google_project.current.project_id
}

resource "google_cloud_run_service_iam_binding" "reaper-run-invoker" {
  role = "roles/run.invoker"
  members = ["serviceAccount:${google_service_account.scheduler.email}",
  "user:mark.van.holsteijn@gmail.com"]

  service  = google_cloud_run_service.packer-reaper.name
  location = google_cloud_run_service.packer-reaper.location
  project  = data.google_project.current.project_id
}

resource "google_project_service" "run" {
  service            = "run.googleapis.com"
  disable_on_destroy = false
  project            = data.google_project.current.project_id
}

resource "google_project_service" "cloudscheduler" {
  service            = "cloudscheduler.googleapis.com"
  disable_on_destroy = false
  project            = data.google_project.current.project_id
}

resource "google_project_service" "appengine" {
  service            = "appengine.googleapis.com"
  disable_on_destroy = false
  project            = data.google_project.current.project_id
}
