# © 2023 Amazon Web Services, Inc. or its affiliates. All Rights Reserved.
# This AWS Content is provided subject to the terms of the AWS Customer Agreement
# available at http://aws.amazon.com/agreement or other written agreement between
# Customer and either Amazon Web Services, Inc. or Amazon Web Services EMEA SARL or both.

"""Initial Module Data.all CLI.

Source repository: TODO
Documentation: TODO

"""

import logging
import os
import sys

from dataall_core.profile import CONFIG_PATH

from .__metadata__ import (  # noqa: F401
    __description__,
    __license__,
    __title__,
    __version__,
)

root_logger = logging.getLogger("dataall_cli")
root_logger.setLevel(os.environ.get("dataall_cli_loglevel", "INFO").upper())

handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(
    logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
)
root_logger.addHandler(handler)

DA_CONFIG_PATH = os.getenv("dataall_config_path", CONFIG_PATH)
CREDS_PATH = os.getenv("dataall_creds_path", None)
SCHEMA_PATH = os.getenv("dataall_schema_path", None)
SCHEMA_VERSION = os.getenv("dataall_schema_version", None)
