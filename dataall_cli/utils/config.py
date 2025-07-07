"""data.all cli config helper functions.

Source repository: TODO
Documentation: TODO

"""

import logging
import os
from pathlib import Path
from typing import Any, Dict, cast

import yaml
from dataall_core.auth import AuthorizationClass
from dataall_core.profile import Profile, save_profile

logger = logging.getLogger(__name__)


def load_config(config_path: str) -> dict[Any, Any]:
    """Retrieve data.all config use ENV variable [dataall_config_path] to override default file location.

    :return: retrieved config from the file.
    """
    logger.info(f"Get config from {config_path}")
    if os.path.isfile(config_path):
        with open(config_path) as file:
            config = yaml.full_load(file)
            logger.debug(f"Retrieved config: {config}")
            return cast(dict[Any, Any], config)
    else:
        return {}


def save_config(
    profile: str,
    auth_type: str,
    params_dict: Dict[str, Any],
    config_path: Path,
) -> None:
    """Save Config Functions.

    :param profile: profile to save
    :param auth_type: auth type for the user
    :param params_dict: dict of profile params for the user
    :param config_path: path to config to store params
    """
    config = {f"{profile}": params_dict}

    # Init Profile
    p = Profile(profile_name=profile, **config[profile])

    # Save Profile
    save_profile(p, config_path)

    # Get Tokens
    auth_class = next(
        (
            cls
            for cls in AuthorizationClass.__subclasses__()
            if cls.__name__ == auth_type
        ),
        None,
    )
    if auth_class:
        auth_instance = auth_class(p)
        auth_instance.get_jwt_token()
    else:
        logger.error(f"No AuthorizationClass subclass found with name '{auth_type}'")
