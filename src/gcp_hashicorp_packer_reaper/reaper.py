from datetime import timedelta
from typing import List

import humanize

from gcp_hashicorp_packer_reaper.gcp import GlobalOptions, Instance
from gcp_hashicorp_packer_reaper.logger import log


def list_packer_instances(options: GlobalOptions, older_than: timedelta = None) -> List:
    result = Instance.list(options)
    result = list(
        filter(
            lambda i: i.description == "New instance created by Packer"
            and i.name.startswith("packer-")
            and (not older_than or i.time_since_launch > older_than),
            result,
        )
    )
    return result


def stop_expired_instances(options: GlobalOptions, older_than: timedelta) -> list:
    count = 0
    instances = list(
        filter(
            lambda i: i.status == "RUNNING", list_packer_instances(options, older_than)
        )
    )
    for instance in instances:
        log.info(
            "stopping %s in %s created %s",
            instance,
            options.project,
            humanize.naturaltime(instance.time_since_launch),
        )
        count = count + 1
        if not options.dry_run:
            instance.stop()
    log.info(f"total of {len(instances)} running instances stopped")
    return instances


def delete_expired_instances(options: GlobalOptions, older_than: timedelta):

    instances = list(
        filter(
            lambda i: i.status in ["RUNNING", "STOPPED", "TERMINATED"],
            list_packer_instances(options, older_than),
        )
    )
    for instance in instances:
        log.info(
            "deleting %s in %s created %s",
            instance,
            options.project,
            humanize.naturaltime(instance.time_since_launch),
        )
        if not options.dry_run:
            instance.delete()
    log.info(f"total of {len(instances)} instances deleted")
    return instances
