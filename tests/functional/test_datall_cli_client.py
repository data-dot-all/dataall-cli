import itertools
import json
import os
import tempfile

import pytest
import yaml
from atomicfile import AtomicFile
from click.testing import CliRunner
from dataall_core.profile import Profile, get_profile

PROFILE_CONFIG = os.path.join(os.path.join(tempfile.mkdtemp(), "config.yaml"))
os.environ["dataall_config_path"] = PROFILE_CONFIG

from dataall_cli.cli import commands, configure, dataall_cli  # noqa: E402


@pytest.fixture(scope="module", autouse=True)
def clean_profile_configs():
    os.makedirs(os.path.dirname(PROFILE_CONFIG), exist_ok=True)
    with AtomicFile(PROFILE_CONFIG, "w") as file:
        yaml.dump({}, file)


@pytest.fixture(scope="module")
def runner():
    yield CliRunner()


@pytest.fixture
def mock_execute(mocker):
    mocker.patch("dataall_core.base_client.BaseClient.execute", return_value={})
    yield


@pytest.fixture
def mock_http_execute(mocker):
    mocker.patch("dataall_core.base_client.BaseClient._execute", return_value={})
    yield


@pytest.fixture(scope="function")
def mocked_get_jwt_token(mocker):
    mocker.patch(
        "dataall_core.auth.AuthorizationClass.get_jwt_token", return_value="token"
    )
    yield


def test_cli_help_option(runner):
    result = runner.invoke(dataall_cli, ["--help"])
    assert result.exit_code == 0

    lines = list(map(str.strip, result.output.splitlines()))
    lines.append("configure")

    for operation_name, _ in commands.items():
        assert operation_name in lines

    assert result.exit_code == 0


@pytest.mark.parametrize(
    "profile_input",
    (
        [
            (
                "TestCognitoProfile",
                "CognitoAuth\ntestclient\ntestAPIURL\ntestdataallURL\ntestIdPURL\n\n\nTestCognitoProfile\nTestUser\nPassword1!\nPassword1!\n",
            ),
            (
                "TestCustomProfile",
                "CustomAuth\ntestclient\ntestAPIURL\ntestdataallURL\ntestIdPURL\n\nauth_server\nTestCustomProfile\nTokenendpoint\nTestUser\nPassword1!\nPassword1!\n",
            ),
            (
                "TestOidcProfile",
                "OidcBrowserAuth\n\ntestclient\ntestAPIURL\ntestIdPURL\n\nTestOidcProfile\n",
            ),
        ]
    ),
)
def test_cli_configure_option(runner, profile_input, mocked_get_jwt_token):
    result = runner.invoke(configure, input=profile_input[1])
    assert result.exit_code == 0
    final_output = result.output.splitlines()[-1]
    assert final_output == "data.all CLI configured successfully."

    profile = get_profile(profile=profile_input[0], config_path=PROFILE_CONFIG)
    assert isinstance(profile, Profile)


def test_cli_configure_oidc_browser_defaults(runner, mocked_get_jwt_token):
    result = runner.invoke(
        configure,
        input="OidcBrowserAuth\n\ntestclient\ntestAPIURL\nhttps://idp/oauth2/aus1\n\nTestOidcDefaults\n",
    )
    assert result.exit_code == 0

    profile = get_profile(profile="TestOidcDefaults", config_path=PROFILE_CONFIG)
    assert profile.auth_type == "OidcBrowserAuth"
    assert profile.idp_domain_url == "https://idp/oauth2/aus1"
    assert profile.redirect_uri == "http://localhost:8765/callback"
    assert profile.fallback_redirect_uri == "http://localhost:8766/callback"
    assert profile.scopes == "openid offline_access"
    assert profile.client_secret is None
    assert profile.session_token_endpoint is None
    assert profile.frontend_url is None


def test_cli_configure_from_dataall_url(runner, mocked_get_jwt_token, mocker):
    mocker.patch(
        "dataall_cli.cli.discover_from_frontend",
        return_value={
            "idp_domain_url": "https://idp/oauth2/aus1",
            "client_id": "0oaCLIENT",
            "api_endpoint_url": "https://api/prod",
        },
    )
    result = runner.invoke(
        configure,
        ["--dataall_url", "https://dataall.example.com", "--profile", "TestDiscovered"],
        input="\n",
    )
    assert result.exit_code == 0
    assert "Discovered client_id: 0oaCLIENT" in result.output

    profile = get_profile(profile="TestDiscovered", config_path=PROFILE_CONFIG)
    assert profile.auth_type == "OidcBrowserAuth"
    assert profile.client_id == "0oaCLIENT"
    assert profile.api_endpoint_url == "https://api/prod"
    assert profile.idp_domain_url == "https://idp/oauth2/aus1"
    assert profile.redirect_uri == "http://localhost:8765/callback"
    assert profile.frontend_url == "https://dataall.example.com"


def test_cli_configure_prompts_for_front_page(runner, mocked_get_jwt_token, mocker):
    mocker.patch(
        "dataall_cli.cli.discover_from_frontend",
        return_value={
            "idp_domain_url": "https://idp/oauth2/aus1",
            "client_id": "0oaCLIENT",
            "api_endpoint_url": "https://api/prod",
        },
    )
    result = runner.invoke(
        configure, input="OidcBrowserAuth\nhttps://dataall.example.com\nTestPrompted\n"
    )
    assert result.exit_code == 0
    assert "Enter data.all app client id" not in result.output
    assert "Discovered client_id: 0oaCLIENT" in result.output

    profile = get_profile(profile="TestPrompted", config_path=PROFILE_CONFIG)
    assert profile.client_id == "0oaCLIENT"
    assert profile.frontend_url == "https://dataall.example.com"


def test_cli_configure_dataall_url_unreachable_prompts(
    runner, mocked_get_jwt_token, mocker
):
    mocker.patch("dataall_cli.cli.discover_from_frontend", side_effect=OSError("boom"))
    result = runner.invoke(
        configure,
        [
            "--dataall_url",
            "https://dataall.example.com",
            "--profile",
            "TestUnreachable",
        ],
        input="\ntestclient\ntestAPIURL\nhttps://idp/oauth2/aus1\n",
    )
    assert result.exit_code == 0
    assert "Could not read settings" in result.output
    profile = get_profile(profile="TestUnreachable", config_path=PROFILE_CONFIG)
    assert profile.client_id == "testclient"
    assert profile.frontend_url == "https://dataall.example.com"


def test_cli_configure_cognito_has_no_oidc_fields(runner, mocked_get_jwt_token):
    result = runner.invoke(
        configure,
        input="CognitoAuth\ntestclient\ntestAPIURL\ntestdataallURL\ntestIdPURL\n\n\nTestCognitoPlain\n",
    )
    assert result.exit_code == 0
    with open(PROFILE_CONFIG) as file:
        saved = yaml.safe_load(file)["TestCognitoPlain"]
    assert "scopes" not in saved
    assert "fallback_redirect_uri" not in saved
    assert "frontend_url" not in saved
    assert saved["client_secret"] == ""


def test_cli_configure_frontend_url_flag_any_auth_type(runner, mocked_get_jwt_token):
    result = runner.invoke(
        configure,
        [
            "--frontend_url",
            "https://dataall.example.com/",
            "--profile",
            "TestCognitoOrigin",
        ],
        input="CognitoAuth\ntestclient\ntestAPIURL\ntestdataallURL\ntestIdPURL\n\n\n",
    )
    assert result.exit_code == 0
    profile = get_profile(profile="TestCognitoOrigin", config_path=PROFILE_CONFIG)
    assert profile.frontend_url == "https://dataall.example.com"


def test_cli_commands(runner, mock_execute, mocked_get_jwt_token, N=10):
    result = runner.invoke(
        configure,
        input="CustomAuth\ntestclient\ntestAPIURL\ntestdataallURL\ntestIdPURL\n\nauth_server\nTestCustomProfile\nTokenendpoint\nTestUser\nPassword1!\nPassword1!\n",
    )
    for operation_name, op_details in dict(
        itertools.islice(commands.items(), N)
    ).items():
        result = runner.invoke(
            dataall_cli,
            [operation_name, "--profile", "TestCustomProfile"],
        )
        assert result.exit_code == 0
        assert result.output.splitlines()[-1] == "{}"


def test_cli_commands_custom_header(runner, mock_execute, mocked_get_jwt_token, N=1):
    result = runner.invoke(
        configure,
        input="CustomAuth\ntestclient\ntestAPIURL\ntestdataallURL\ntestIdPURL\n\nauth_server\nTestCustomProfile\nTokenendpoint\nTestUser\nPassword1!\nPassword1!\n",
    )

    # Set env variable to use custom header
    os.environ["dataall_custom_headers_json"] = json.dumps(
        {"X-Custom-Header": "custom-value"}
    )

    for operation_name, op_details in dict(
        itertools.islice(commands.items(), N)
    ).items():
        result = runner.invoke(
            dataall_cli,
            [operation_name, "--profile", "TestCustomProfile"],
        )
        assert result.exit_code == 0
        assert result.output.splitlines()[-1] == "{}"

    # Clean up and delete env variable
    del os.environ["dataall_custom_headers_json"]


def test_cli_commands_custom_header_invalid(
    runner, mock_execute, mocked_get_jwt_token, N=1
):
    result = runner.invoke(
        configure,
        input="CustomAuth\ntestclient\ntestAPIURL\ntestdataallURL\ntestIdPURL\n\nauth_server\nTestCustomProfile\nTokenendpoint\nTestUser\nPassword1!\nPassword1!\n",
    )

    # Set env variable to use custom header
    os.environ["dataall_custom_headers_json"] = (
        '{ "X-Custom-Header": "test", "X-Custom-Header-2": 25 '
    )

    for operation_name, op_details in dict(
        itertools.islice(commands.items(), N)
    ).items():
        result = runner.invoke(
            dataall_cli,
            [operation_name, "--profile", "TestCustomProfile"],
        )
        assert result.exit_code == 0
        assert result.output.splitlines()[-1] == "{}"

    # Clean up and delete env variable
    del os.environ["dataall_custom_headers_json"]


def test_cli_commands_default_profile_dne(runner):
    op_name = list(commands.keys())[0]
    result = runner.invoke(dataall_cli, [op_name])
    assert result.exit_code == 1


def test_cli_configure_help_does_not_prompt(runner):
    result = runner.invoke(configure, ["--help"])
    assert result.exit_code == 0
    assert "Usage:" in result.output
    assert "Select authentication type" not in result.output


def test_cli_configure_dataall_url_after_other_options(
    runner, mocked_get_jwt_token, mocker
):
    mocker.patch(
        "dataall_cli.cli.discover_from_frontend",
        return_value={
            "idp_domain_url": "https://idp/oauth2/aus1",
            "client_id": "0oaCLIENT",
            "api_endpoint_url": "https://api/prod",
        },
    )
    result = runner.invoke(
        configure,
        [
            "--profile",
            "TestDiscoveredLate",
            "--auth_type",
            "OidcBrowserAuth",
            "--dataall_url",
            "https://dataall.example.com",
        ],
    )
    assert result.exit_code == 0
    profile = get_profile(profile="TestDiscoveredLate", config_path=PROFILE_CONFIG)
    assert profile.client_id == "0oaCLIENT"
    assert profile.idp_domain_url == "https://idp/oauth2/aus1"
