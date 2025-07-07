import os
from pathlib import Path

import pytest
import yaml
from atomicfile import AtomicFile

from dataall_cli.utils import load_config, save_config

PROFILE_CONFIG = os.path.join(
    Path(__file__).parents[1], "profile_config", "config.yaml"
)
os.environ["dataall_config_path"] = PROFILE_CONFIG


@pytest.fixture(scope="module", autouse=True)
def clean_profile_configs():
    os.makedirs(os.path.dirname(PROFILE_CONFIG), exist_ok=True)
    with AtomicFile(PROFILE_CONFIG, "w") as file:
        yaml.dump({}, file)


@pytest.fixture(scope="function")
def base_profile_params():
    return {
        "api_endpoint_url": "XXXXXXXXXXXXXXXX",
        "username": "XXXXXXXX",
        "password": "XXXXXXXX",
        "client_id": "client_id",
        "redirect_uri": "XXXXXXXXXXXXXXXX",
        "idp_domain_url": "XXXXXXXXXXXXXXXX",
        "config_type": "SECRET",
    }


@pytest.fixture(scope="function")
def custom_profile_params():
    return {
        "session_token_endpoint": "XXXXXXXXXXXXXXXX",
    }


@pytest.fixture(scope="function", autouse=True)
def mocked_get_jwt_token(mocker):
    mocker.patch(
        "dataall_core.auth.AuthorizationClass.get_jwt_token", return_value="token"
    )
    yield


def test_save_config(
    base_profile_params,
):
    auth_type = "CognitoAuth"
    profile = "default"
    base_profile_params["auth_type"] = auth_type

    save_config(
        profile=profile,
        auth_type=auth_type,
        params_dict=base_profile_params,
        config_path=PROFILE_CONFIG,
    )

    config = load_config(PROFILE_CONFIG)
    assert len(config[profile])


def test_save_config_custom(base_profile_params, custom_profile_params):
    auth_type = "CustomAuth"
    profile = "default"
    base_profile_params["auth_type"] = auth_type
    base_profile_params.update(custom_profile_params)
    save_config(
        profile=profile,
        auth_type=auth_type,
        params_dict=base_profile_params,
        config_path=PROFILE_CONFIG,
    )

    config = load_config(PROFILE_CONFIG)
    assert config[profile]["session_token_endpoint"]


def test_load_config():
    config = load_config(PROFILE_CONFIG)
    assert config
    assert len(config) == 1


def test_load_config_dne():
    config = load_config(
        os.path.join(Path(__file__).parents[1], "profile_config", "config_dne.yaml")
    )
    assert config == {}


def test_load_config_bad_path():
    with pytest.raises(Exception):
        load_config(Path(__file__))
