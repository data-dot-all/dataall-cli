"""CLI for data.all."""

import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

import click
from dataall_core.dataall_client import DataallClient
from dataall_core.profile import CONFIG_PATH

from dataall_cli.bind_commands import bind
from dataall_cli.utils import discover_from_frontend, save_config

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


AUTH_TYPES = ["CognitoAuth", "CustomAuth", "OidcBrowserAuth"]
DEFAULT_REDIRECT_URI = "http://localhost:8765/callback"
DEFAULT_FALLBACK_REDIRECT_URI = "http://localhost:8766/callback"
DEFAULT_SCOPES = "openid offline_access"
DISCOVERED = "dataall_discovered"

DOMAIN_PROMPT = "Enter data.all's domain URL (e.g. https://<DOMAIN>.com)"
IDP_PROMPT = "Enter data.all Identity Provider Domain (e.g. https://<IdP-DOMAIN>.com)"
ISSUER_PROMPT = (
    "Enter OIDC issuer URL (e.g. https://<ORG>.okta.com/oauth2/<AUTH-SERVER-ID>)"
)
SECRET_PROMPT = "Enter IdP client secret (if applicable)"
AUTH_SERVER_PROMPT = "Enter IdP custom auth server (if applicable)"
FRONT_PAGE_PROMPT = (
    "Enter data.all front page URL (leave empty to type the values yourself)"
)


class AuthScopedOption(click.Option):
    """Option whose prompt depends on ``--auth_type``.

    ``scoped`` maps an auth type to ``{"prompt": text, "default": value}``. A spec
    without ``prompt`` uses its default silently; auth types not listed get ``None``.
    Values discovered from ``--dataall_url`` are used without prompting.
    """

    def __init__(
        self, *args: Any, scoped: Dict[str, Dict[str, Any]], **kwargs: Any
    ) -> None:
        self.scoped = scoped
        kwargs.setdefault("prompt", True)
        super().__init__(*args, **kwargs)

    def prompt_for_value(self, ctx: click.Context) -> Any:
        """Return the value for the active auth type, prompting only when needed."""
        discovered = ctx.meta.get(DISCOVERED, {})
        if self.name in discovered:
            return discovered[self.name]
        spec = self.scoped.get(str(ctx.params.get("auth_type")))
        if spec is None:
            return None
        if "prompt" not in spec:
            return spec.get("default")
        return click.prompt(
            spec["prompt"],
            default=spec.get("default"),
            type=self.type,
            value_proc=lambda x: self.process_value(ctx, x),
        )


def _discover(
    ctx: click.Context, _param: click.Parameter, value: Optional[str]
) -> Optional[str]:
    if not value:
        return value
    try:
        found = discover_from_frontend(value)
    except Exception as e:
        click.echo(f"Could not read settings from {value}: {e}", err=True)
        found = {}
    parsed = urlparse(value)
    found["frontend_url"] = f"{parsed.scheme}://{parsed.netloc}"
    for key, item in found.items():
        click.echo(f"Discovered {key}: {item}", err=True)
    ctx.meta[DISCOVERED] = found
    if "auth_type" not in ctx.params:
        ctx.default_map = {**(ctx.default_map or {}), "auth_type": "OidcBrowserAuth"}
    return value


def _for(auth_types: List[str], **spec: Any) -> Dict[str, Dict[str, Any]]:
    return {auth_type: dict(spec) for auth_type in auth_types}


@dataall_cli.command()
@click.option(
    "--auth_type",
    type=click.Choice(AUTH_TYPES),
    default="CognitoAuth",
    prompt="Select authentication type",
    help="Authentication type: Cognito, Custom (username/password) or OIDC browser login",
)
@click.option(
    "--dataall_url",
    cls=AuthScopedOption,
    expose_value=False,
    callback=_discover,
    scoped={"OidcBrowserAuth": {"prompt": FRONT_PAGE_PROMPT, "default": ""}},
    help="data.all front page URL; reads the IdP issuer, client id and API endpoint from it",
)
@click.option(
    "--client_id",
    cls=AuthScopedOption,
    required=True,
    scoped=_for(AUTH_TYPES, prompt="Enter data.all app client id"),
    help="data.all app client id",
)
@click.option(
    "--api_endpoint_url",
    cls=AuthScopedOption,
    required=True,
    scoped=_for(AUTH_TYPES, prompt="Enter data.all API endpoint url"),
    help="data.all API endpoint url",
)
@click.option(
    "--redirect_uri",
    cls=AuthScopedOption,
    required=True,
    scoped={
        **_for(["CognitoAuth", "CustomAuth"], prompt=DOMAIN_PROMPT),
        "OidcBrowserAuth": {"default": DEFAULT_REDIRECT_URI},
    },
    help="OAuth redirect URI: the data.all domain URL, or the loopback URI registered for the CLI",
)
@click.option(
    "--idp_domain_url",
    cls=AuthScopedOption,
    required=True,
    scoped={
        **_for(["CognitoAuth", "CustomAuth"], prompt=IDP_PROMPT),
        "OidcBrowserAuth": {"prompt": ISSUER_PROMPT},
    },
    help="Identity provider domain, or the OIDC issuer URL for browser login",
)
@click.option(
    "--client_secret",
    cls=AuthScopedOption,
    required=False,
    scoped=_for(["CognitoAuth", "CustomAuth"], prompt=SECRET_PROMPT, default=""),
    help="IdP client secret, if the app has one",
)
@click.option(
    "--auth_server",
    cls=AuthScopedOption,
    required=False,
    scoped=_for(
        ["CognitoAuth", "CustomAuth"], prompt=AUTH_SERVER_PROMPT, default="default"
    ),
    help="identity provider's custom authorization server used to get well-known openid config",
)
@click.option(
    "--scopes",
    cls=AuthScopedOption,
    required=False,
    scoped={"OidcBrowserAuth": {"default": DEFAULT_SCOPES}},
    help="OIDC scopes for browser login; use 'openid' if the IdP rejects offline_access",
)
@click.option(
    "--frontend_url",
    cls=AuthScopedOption,
    required=False,
    scoped={
        "OidcBrowserAuth": {"prompt": "Enter data.all front page URL", "default": ""}
    },
    help="data.all UI URL sent as Origin header; some deployments only accept API calls carrying it",
)
@click.option(
    "--fallback_redirect_uri",
    default=DEFAULT_FALLBACK_REDIRECT_URI,
    help="second loopback URI tried when the first port is busy (browser login)",
)
@click.option(
    "--profile",
    prompt="Enter data.all profile name",
    default="default",
    help="profile name for dataall_cli configured user",
)
def configure(
    auth_type: str,
    client_id: str,
    api_endpoint_url: str,
    redirect_uri: str,
    idp_domain_url: str,
    client_secret: Optional[str],
    auth_server: Optional[str],
    scopes: Optional[str],
    frontend_url: Optional[str],
    fallback_redirect_uri: str,
    profile: str,
) -> None:
    """Configure data.all client for a given user, use profile to setup multiple user profiles."""
    click.echo("Configuring data.all CLI...", err=True)

    try:
        profile_params_dict: Dict[str, Any] = {
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
        if auth_type == "OidcBrowserAuth":
            profile_params_dict.update(
                {"scopes": scopes, "fallback_redirect_uri": fallback_redirect_uri}
            )
        if frontend_url:
            profile_params_dict["frontend_url"] = frontend_url.rstrip("/")
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
