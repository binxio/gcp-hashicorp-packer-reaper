import re
from collections import namedtuple
from datetime import datetime, timedelta
from typing import List
from uuid import uuid4

from dateutil import parser
from googleapiclient import discovery
from pytz import UTC
from gcp_hashicorp_packer_reaper.logger import log

GlobalOptions = namedtuple("GlobalOptions", ["credentials", "project", "dry_run"])


class Project(dict):
    def __init__(self, p, api):
        self.update(p)
        self.api = api

    @property
    def id(self):
        return self["projectId"]

    @property
    def name(self):
        return self["name"]

    def __str__(self):
        return self.id


class Instance(dict):
    def __init__(self, i, compute):
        self.update(i)
        self.compute = compute

    @property
    def id(self):
        return self["id"]

    @property
    def tags(self) -> List[str]:
        return self.get("tags", {}).get("items", [])

    @property
    def name(self):
        return self["name"]

    @property
    def description(self):
        return self["description"]

    @property
    def creation_time(self):
        return parser.isoparse(self["creationTimestamp"])

    @property
    def time_since_launch(self) -> timedelta:
        return UTC.localize(datetime.utcnow()) - self.creation_time

    @property
    def status(self):
        return self["status"]

    @property
    def zone(self):
        return self["zone"].split("/")[-1]

    def __str__(self):
        return self.name

    @property
    def project(self):
        m = re.fullmatch(
            r"^https://www.googleapis.com/compute/[^/]*/projects/(?P<project>[^/]*)/.*",
            self["selfLink"],
        )
        assert m, f"selfLink '{self['selfLink']}' is not from compute engine"
        return m.group("project")

    def stop(self):
        request_id = str(uuid4())
        response = (
            self.compute.instances()
            .stop(
                project=self.project,
                zone=self.zone,
                instance=self.id,
                requestId=request_id,
            )
            .execute()
        )
        return response

    def delete(self):
        request_id = str(uuid4())
        response = (
            self.compute.instances()
            .delete(
                project=self.project,
                zone=self.zone,
                instance=self.id,
                requestId=request_id,
            )
            .execute()
        )
        return response

    @staticmethod
    def list(options: GlobalOptions) -> List["Instance"]:
        result = []
        compute = discovery.build(
            "compute", "v1", cache_discovery=False, credentials=options.credentials
        )
        response = compute.instances().aggregatedList(project=options.project).execute()
        for zone, r in response.get("items", {}).items():
            result.extend(map(lambda i: Instance(i, compute), r.get("instances", [])))
        return result


def list_projects(options: GlobalOptions) -> List[Project]:
    api = discovery.build(
        "cloudresourcemanager",
        "v1",
        cache_discovery=False,
        credentials=options.credentials,
    )
    try:
        return map(
            lambda p: Project(p, api),
            api.projects().list().execute().get("projects", []),
        )
    except Exception as e:
        log.debug("failed to list all projects, %s", e)
        return [options.project_id] if options.project_id else []
