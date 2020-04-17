import os
import logging

logging.basicConfig(format="%(levelname)s: %(message)s")
log = logging.getLogger("gcp_hashicorp_packer_reaper")
log.setLevel(os.getenv("LOG_LEVEL", "INFO"))
