import logging
import os, sys
from datetime import timedelta

import google.auth
from durations import Duration
from flask import Flask, jsonify, url_for
from flask_restful import reqparse

from gcp_hashicorp_packer_reaper.gcp import GlobalOptions
from gcp_hashicorp_packer_reaper.logger import log
from gcp_hashicorp_packer_reaper.reaper import (
    delete_expired_instances,
    list_packer_instances,
    stop_expired_instances,
)

options = None

app = Flask(__name__)

parser = reqparse.RequestParser()
parser.add_argument("older_than", type=Duration, default=Duration("2h"))
parser.add_argument("dry_run", type=bool, default=True)


@app.route("/")
def index():
    return jsonify(
        {
            "list": url_for("do_list", _external=True),
            "stop": url_for("do_stop", _external=True),
            "delete": url_for("do_delete", _external=True),
        }
    )


@app.route("/list")
def do_list():
    return do("list")


@app.route("/stop")
def do_stop():
    return do("stop")


@app.route("/delete")
def do_delete():
    return do("delete")


def do(operation: str):
    operations = {
        "list": list_packer_instances,
        "stop": stop_expired_instances,
        "delete": delete_expired_instances,
    }
    args = parser.parse_args()
    older_than = args.get("older_than")
    return jsonify(
        operations[operation](options, timedelta(seconds=older_than.to_seconds()))
    )


if __name__ == "__main__":
    credentials, project_id = google.auth.default()
    options = GlobalOptions(credentials=credentials, project=project_id, dry_run=False)

    if not project_id:
        log.error("No project id set")
        exit(1)

    # remove flask messagins.
    log = logging.getLogger("werkzeug")
    log.disabled = True
    sys.modules["flask.cli"].show_server_banner = lambda *x: None

    app.run(
        host="0.0.0.0",
        port=int(os.getenv("PORT", "8080")),
        debug=(os.getenv("LOG_LEVEL") == "DEBUG"),
    )
