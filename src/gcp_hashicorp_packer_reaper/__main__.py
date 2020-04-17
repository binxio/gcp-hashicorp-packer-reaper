import os
from collections import namedtuple
import google.auth


import click
import humanize
from gcp_hashicorp_packer_reaper.click_argument_types import Duration
from datetime import timedelta
from gcp_hashicorp_packer_reaper.gcp import list_projects
from gcp_hashicorp_packer_reaper.logger import log
from gcp_hashicorp_packer_reaper.reaper import (
    stop_expired_instances,
    delete_expired_instances,
    list_packer_instances,
    GlobalOptions,
)


@click.group()
@click.option("--dry-run", is_flag=True, default=False, help="do not change anything")
@click.option("--verbose", is_flag=True, default=False, help="output")
@click.option("--project", help="to delete from")
@click.pass_context
def main(ctx, dry_run, project, verbose):
    """
    stop or delete dangling packer instances.
    """
    log.setLevel(os.getenv("LOG_LEVEL", "DEBUG" if verbose else "INFO"))
    credentials, project_id = google.auth.default()

    if not project:
        project = project_id
        if not project_id:
            log.error("no default project set and --project is missing")
            exit(1)
        log.debug("using default project %s", project)

    ctx.obj = GlobalOptions(credentials=credentials, project=project, dry_run=dry_run)


@main.command(help="packer builder instances")
@click.option(
    "--older-than", type=Duration(), required=True, help="period since launched"
)
@click.pass_context
def stop(ctx, older_than):
    stop_expired_instances(ctx.obj, older_than=timedelta(seconds=older_than.seconds))


@main.command(help="packer builder instances")
@click.option(
    "--older-than", type=Duration(), required=True, help="period since launched"
)
@click.pass_context
def delete(ctx, older_than: Duration):
    delete_expired_instances(ctx.obj, older_than=timedelta(seconds=older_than.seconds))


@main.command(help="packer builder instances")
@click.pass_context
def list(ctx):
    instances = list_packer_instances(ctx.obj)
    for i in instances:
        print(
            f"{i} launched {humanize.naturaltime(i.time_since_launch)} in {i.project} - {i.zone} - {i.status}"
        )
    log.info(f"{len(instances)} packer builder instances found")


if __name__ == "__main__":
    main()
