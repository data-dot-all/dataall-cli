"""Discover CLI settings from a deployed data.all front page."""

import re
from typing import Dict
from urllib.parse import urljoin

import httpx

BUNDLE_PATTERN = re.compile(r'src="([^"]*static/js/main\.[^"]+\.js)"')
BUNDLE_VALUES = {
    "idp_domain_url": "REACT_APP_CUSTOM_AUTH_URL",
    "client_id": "REACT_APP_CUSTOM_AUTH_CLIENT_ID",
    "api_endpoint_url": "REACT_APP_GRAPHQL_API",
}
API_SUFFIX = "/graphql/api"


def discover_from_frontend(dataall_url: str) -> Dict[str, str]:
    """Read the OIDC issuer, client id and API endpoint embedded in the front page bundle.

    Returns only the values that were found.
    """
    base = dataall_url.rstrip("/") + "/"
    index = httpx.get(base, follow_redirects=True, timeout=30)
    index.raise_for_status()
    match = BUNDLE_PATTERN.search(index.text)
    if not match:
        return {}
    bundle = httpx.get(urljoin(base, match.group(1)), follow_redirects=True, timeout=60)
    bundle.raise_for_status()

    found: Dict[str, str] = {}
    for key, name in BUNDLE_VALUES.items():
        value = re.search(rf'{name}:"([^"]+)"', bundle.text)
        if value:
            found[key] = value.group(1)
    api = found.get("api_endpoint_url", "")
    if api.endswith(API_SUFFIX):
        found["api_endpoint_url"] = api[: -len(API_SUFFIX)]
    return found
