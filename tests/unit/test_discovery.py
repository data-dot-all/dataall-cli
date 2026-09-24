import httpx
import pytest

from dataall_cli.utils import discover_from_frontend

FRONT = "https://dataall.example.com"
INDEX = (
    "<!doctype html><html><head><title>data.all</title>"
    '<script defer="defer" src="/static/js/main.aaa1de7c.js"></script></head>'
    '<body><div id="root"></div></body></html>'
)
BUNDLE = (
    'REACT_APP_GRAPHQL_API:"https://api.example.com/prod/graphql/api",'
    'REACT_APP_CUSTOM_AUTH:"okta",'
    'REACT_APP_CUSTOM_AUTH_URL:"https://idp.example.com/oauth2/aus1",'
    'REACT_APP_CUSTOM_AUTH_CLIENT_ID:"0oaCLIENT",'
    'REACT_APP_CUSTOM_AUTH_SCOPES:"openid"'
)


def serve(mocker, pages):
    def fake_get(url, **kwargs):
        status, text = pages.get(url, (404, ""))
        return httpx.Response(status, text=text, request=httpx.Request("GET", url))

    mocker.patch("dataall_cli.utils.discovery.httpx.get", side_effect=fake_get)


def test_discover_all_values(mocker):
    serve(
        mocker,
        {
            f"{FRONT}/": (200, INDEX),
            f"{FRONT}/static/js/main.aaa1de7c.js": (200, BUNDLE),
        },
    )
    assert discover_from_frontend(FRONT) == {
        "idp_domain_url": "https://idp.example.com/oauth2/aus1",
        "client_id": "0oaCLIENT",
        "api_endpoint_url": "https://api.example.com/prod",
    }


def test_discover_partial_bundle(mocker):
    serve(
        mocker,
        {
            f"{FRONT}/": (200, INDEX),
            f"{FRONT}/static/js/main.aaa1de7c.js": (
                200,
                'REACT_APP_CUSTOM_AUTH_CLIENT_ID:"0oaCLIENT"',
            ),
        },
    )
    assert discover_from_frontend(f"{FRONT}/") == {"client_id": "0oaCLIENT"}


def test_discover_without_bundle(mocker):
    serve(mocker, {f"{FRONT}/": (200, "<html><body>maintenance</body></html>")})
    assert discover_from_frontend(FRONT) == {}


def test_discover_http_error(mocker):
    serve(mocker, {})
    with pytest.raises(httpx.HTTPStatusError):
        discover_from_frontend(FRONT)
