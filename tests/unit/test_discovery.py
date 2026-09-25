import httpx
import pytest

from dataall_cli.utils import discover_from_frontend, frontend_origin

FRONT = "https://dataall.example.com"
INDEX = (
    "<!doctype html><html><head><title>data.all</title>"
    '<script defer="defer" src="/static/js/main.aaa1de7c.js"></script></head>'
    '<body><div id="root"></div></body></html>'
)
OIDC_BUNDLE = (
    'REACT_APP_GRAPHQL_API:"https://api.example.com/prod/graphql/api",'
    'REACT_APP_CUSTOM_AUTH:"okta",'
    'REACT_APP_CUSTOM_AUTH_URL:"https://idp.example.com/oauth2/aus1",'
    'REACT_APP_CUSTOM_AUTH_CLIENT_ID:"0oaCLIENT",'
    'REACT_APP_CUSTOM_AUTH_SCOPES:"openid"'
)
COGNITO_BUNDLE = (
    'REACT_APP_GRAPHQL_API:"https://api.example.com/prod/graphql/api",'
    'REACT_APP_COGNITO_USER_POOL_ID:"us-east-1_abc",'
    'REACT_APP_COGNITO_APP_CLIENT_ID:"cognitoclient",'
    'REACT_APP_COGNITO_DOMAIN:"dataall-dev.auth.us-east-1.amazoncognito.com",'
    'REACT_APP_COGNITO_REDIRECT_SIGNIN:"https://dataall.example.com",'
    'REACT_APP_COGNITO_REDIRECT_SIGNOUT:"https://dataall.example.com"'
)


def serve(mocker, pages):
    def fake_get(url, **kwargs):
        status, text = pages.get(url, (404, ""))
        return httpx.Response(status, text=text, request=httpx.Request("GET", url))

    mocker.patch("dataall_cli.utils.discovery.httpx.get", side_effect=fake_get)


def pages(bundle):
    return {
        f"{FRONT}/": (200, INDEX),
        f"{FRONT}/static/js/main.aaa1de7c.js": (200, bundle),
    }


def test_discover_oidc_deployment(mocker):
    serve(mocker, pages(OIDC_BUNDLE))
    assert discover_from_frontend(FRONT) == {
        "frontend_url": FRONT,
        "auth_type": "OidcBrowserAuth",
        "idp_domain_url": "https://idp.example.com/oauth2/aus1",
        "client_id": "0oaCLIENT",
        "api_endpoint_url": "https://api.example.com/prod",
    }


def test_discover_cognito_deployment(mocker):
    serve(mocker, pages(COGNITO_BUNDLE))
    assert discover_from_frontend(f"{FRONT}/") == {
        "frontend_url": FRONT,
        "auth_type": "CognitoAuth",
        "client_id": "cognitoclient",
        "idp_domain_url": "https://dataall-dev.auth.us-east-1.amazoncognito.com",
        "redirect_uri": "https://dataall.example.com",
        "api_endpoint_url": "https://api.example.com/prod",
    }


def test_discover_partial_bundle(mocker):
    serve(
        mocker,
        pages(
            'REACT_APP_CUSTOM_AUTH:"okta",REACT_APP_CUSTOM_AUTH_URL:"https://idp.example.com/oauth2/aus1"'
        ),
    )
    assert discover_from_frontend(FRONT) == {
        "frontend_url": FRONT,
        "auth_type": "OidcBrowserAuth",
        "idp_domain_url": "https://idp.example.com/oauth2/aus1",
    }


def test_discover_without_bundle(mocker):
    serve(mocker, {f"{FRONT}/": (200, "<html><body>maintenance</body></html>")})
    assert discover_from_frontend(FRONT) == {"frontend_url": FRONT}


def test_discover_http_error(mocker):
    serve(mocker, {})
    with pytest.raises(httpx.HTTPStatusError):
        discover_from_frontend(FRONT)


def test_frontend_origin():
    assert frontend_origin("https://dataall.example.com/console/") == FRONT
