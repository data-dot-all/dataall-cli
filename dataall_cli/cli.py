"""CLI for data.all."""

import json
import logging
import os
from pathlib import Path

import click
from dataall_core.dataall_client import DataallClient
from dataall_core.profile import CONFIG_PATH

from dataall_cli.bind_commands import bind
from dataall_cli.utils import save_config

DA_CONFIG_PATH = os.getenv("dataall_config_path", CONFIG_PATH)
CREDS_PATH = os.getenv("dataall_creds_path", None)
SCHEMA_PATH = os.getenv("dataall_schema_path", None)
SCHEMA_VERSION = os.getenv("dataall_schema_version", None)
DA_CUSTOM_HEADERS_JSON: str = os.getenv("dataall_custom_headers_json", "{}")

logger = logging.getLogger(__name__)

try:
    custom_headers = json.loads(DA_CUSTOM_HEADERS_JSON)
except ValueError:
    logger.info(
        f"Invalid custom headers json string: {DA_CUSTOM_HEADERS_JSON}. Using default headers..."
    )
    custom_headers = {}

da = DataallClient(schema_path=SCHEMA_PATH, schema_version=SCHEMA_VERSION)
default_client = da.client(config_path=DA_CONFIG_PATH, custom_headers=custom_headers)
commands = da.op_dict


@click.group(name="dataall_cli", invoke_without_command=True)
def dataall_cli() -> None:
    """data.all cli groups."""
    click.echo("Executing dataall_cli.", err=True)
    pass


bind(
    dataall_cli=dataall_cli,
    commands=commands,
    config_path=DA_CONFIG_PATH,
    schema_path=SCHEMA_PATH,
    schema_version=SCHEMA_VERSION,
    custom_headers=custom_headers,
)


@dataall_cli.command()
@click.option(
    "--auth_type",
    type=click.Choice(["CognitoAuth", "CustomAuth"]),
    default="CognitoAuth",
    prompt="Select authentication type",
    help="Authentication type: Cognito or Custom",
)
@click.option(
    "--client_id",
    required=True,
    prompt="Enter data.all app client id",
    help="data.all app client id",
)
@click.option(
    "--api_endpoint_url",
    required=True,
    prompt="Enter data.all API endpoint url",
    help="data.all API endpoint url",
)
@click.option(
    "--redirect_uri",
    required=True,
    prompt="Enter data.all's domain URL (e.g. https://<DOMAIN>.com)",
    help="data.all domain URL",
)
@click.option(
    "--idp_domain_url",
    required=True,
    prompt="Enter data.all Identity Provider Domain (e.g. https://<IdP-DOMAIN>.com)",
    help="data.all IdP domain URL",
)
@click.option(
    "--client_secret",
    required=False,
    prompt="Enter IdP client secret (if applicable)",
    default="",
    help="profile name for dataall_cli configured user",
)
@click.option(
    "--auth_server",
    prompt="Enter IdP custom auth server (if applicable)",
    default="default",
    help="identity provider's custom authorization server used to get well-known openid config",
)
@click.option(
    "--profile",
    prompt="Enter data.all profile name",
    default="default",
    help="profile name for dataall_cli configured user",
)
def configure(
    client_id: str,
    api_endpoint_url: str,
    auth_type: str,
    redirect_uri: str,
    idp_domain_url: str,
    client_secret: str,
    auth_server: str,
    profile: str,
) -> None:
    """Configure data.all client for a given user, use profile to setup multiple user profiles."""
    click.echo("Configuring data.all CLI...", err=True)

    try:
        profile_params_dict = {
            "client_id": client_id,
            "api_endpoint_url": api_endpoint_url,
            "auth_type": auth_type,
            "idp_domain_url": idp_domain_url,
            "redirect_uri": redirect_uri,
            "client_secret": client_secret,
        }
        if auth_type == "CustomAuth":
            session_token_endpoint = click.prompt("Enter session token endpoint")
            profile_params_dict.update(
                {
                    "auth_server": auth_server,
                    "session_token_endpoint": session_token_endpoint,
                }
            )
        if CREDS_PATH:
            profile_params_dict.update(
                {
                    "creds_path": str(CREDS_PATH),
                }
            )
        save_config(
            profile=profile,
            auth_type=auth_type,
            params_dict=profile_params_dict,
            config_path=Path(DA_CONFIG_PATH),
        )
        click.echo("data.all CLI configured successfully.", err=True)
    except Exception as e:
        click.echo(f"An error occurred: {e}", err=True)
