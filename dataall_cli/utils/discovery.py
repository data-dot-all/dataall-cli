"""Discover CLI settings from a deployed data.all front page."""

import re
from typing import Dict
from urllib.parse import urljoin, urlparse

import httpx

BUNDLE_PATTERN = re.compile(r'src="([^"]*static/js/main\.[^"]+\.js)"')
VALUE_PATTERN = re.compile(r'(REACT_APP_[A-Z_]+):"([^"]*)"')
API_SUFFIX = "/graphql/api"


def frontend_origin(dataall_url: str) -> str:
    """Return ``scheme://host`` of a data.all URL."""
    parsed = urlparse(dataall_url)
    return f"{parsed.scheme}://{parsed.netloc}"


def discover_from_frontend(dataall_url: str) -> Dict[str, str]:
    """Read the auth type, identity provider, client id and API endpoint from the front page bundle.

    Returns ``frontend_url`` plus whichever values were found.
    """
    found = {"frontend_url": frontend_origin(dataall_url)}
    base = dataall_url.rstrip("/") + "/"
    index = httpx.get(base, follow_redirects=True, timeout=30)
    index.raise_for_status()
    match = BUNDLE_PATTERN.search(index.text)
    if not match:
        return found
    bundle = httpx.get(urljoin(base, match.group(1)), follow_redirects=True, timeout=60)
    bundle.raise_for_status()
    values = dict(VALUE_PATTERN.findall(bundle.text))

    if values.get("REACT_APP_CUSTOM_AUTH") and values.get("REACT_APP_CUSTOM_AUTH_URL"):
        found["auth_type"] = "OidcBrowserAuth"
        found["idp_domain_url"] = values["REACT_APP_CUSTOM_AUTH_URL"]
        if values.get("REACT_APP_CUSTOM_AUTH_CLIENT_ID"):
            found["client_id"] = values["REACT_APP_CUSTOM_AUTH_CLIENT_ID"]
    elif values.get("REACT_APP_COGNITO_APP_CLIENT_ID"):
        found["auth_type"] = "CognitoAuth"
        found["client_id"] = values["REACT_APP_COGNITO_APP_CLIENT_ID"]
        domain = values.get("REACT_APP_COGNITO_DOMAIN", "")
        if domain:
            found["idp_domain_url"] = domain if "://" in domain else f"https://{domain}"
        if values.get("REACT_APP_COGNITO_REDIRECT_SIGNIN"):
            found["redirect_uri"] = values["REACT_APP_COGNITO_REDIRECT_SIGNIN"]
    api = values.get("REACT_APP_GRAPHQL_API", "")
    if api:
        found["api_endpoint_url"] = (
            api[: -len(API_SUFFIX)] if api.endswith(API_SUFFIX) else api
        )
    return found
