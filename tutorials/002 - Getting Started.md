
# 2 - Getting Started

## How does dataall_cli handle data.all user credentials and profiles?

Dataall's CLI requires user profile information to be stored either in a local file or in AWS Secrets Manager. The user information required includes:

- auth_type: `CognitoAuth`, `CustomAuth` or `OidcBrowserAuth` (browser login, no password)
- client_id: The App Client ID
- api_endpoint_url: The URL data.all API Gateway Endpoint 
- redirect_uri: The data.all domain URL (for `OidcBrowserAuth`: the loopback URI registered for the CLI, default `http://localhost:8765/callback`)
- idp_domain_url: The Identity Providers URL (for `OidcBrowserAuth`: the OIDC issuer URL)
- client_secret (optional): The client secret used for the data.all App Client
- auth_server (optional, used for CustomAuth): The Custom Authorization Server used if applicable
- session_token_endpoint (optional, required for CustomAuth): The Identity Provider API endpoint to retrieve session tokens
- scopes (optional, OidcBrowserAuth): OIDC scopes, default `openid offline_access`
- fallback_redirect_uri (optional, OidcBrowserAuth): second loopback URI tried when the first port is busy
- frontend_url (optional): the data.all UI URL, sent as `Origin` and `Referer` headers; required where the API only accepts calls carrying the UI origin
- profile:  The Profile Name

Data.all's SDK uses the profile information to fetch and save tokens from the data.all application. 

By default the user information is provided at `~/.dataall/config.yaml` and the token information is saved at `~/.dataall/credentials.yaml`

If a valid token or refresh token exists for the given user, that will be used to fetch a new token and authenticate the profile. Otherwise, the user will be prompted for username and password when running an API request and the fetched tokens will be saved. With `OidcBrowserAuth` the CLI opens the identity provider's login page in the browser instead.


### Configuring your first data.all User profile

Below is an example of what a configured user profile typically looks like in `~/.dataall/config.yaml`:

```
TestCognitoProfile:
  auth_type: CognitoAuth
  client_id: testclient
  api_endpoint_url: https://API_GATEWAY_URL/prod
  redirect_uri: https://DATAALL_DOMAIN_URL
  idp_domain_url: https://IDP_DOMAIN_URL
```

### Configuring a Custom Auth User

If your data.all application is using custom auth, below is an example of a custom auth user configuration in `~/.dataall/config.yaml`: 
```
TestCustomProfile:
  auth_type: CustomAuth
  client_id: testclient
  client_secret: testsecret
  api_endpoint_url: https://API_GATEWAY_URL/prod
  redirect_uri: https://DATAALL_DOMAIN_URL
  idp_domain_url: https://IDP_DOMAIN_URL
  session_token_endpoint: testtokenendpoint
```


### Configuring a browser login (OIDC + PKCE, e.g. Okta)

`OidcBrowserAuth` signs in the way the data.all web app does: the CLI opens your browser on the identity provider, receives the authorization code on a loopback redirect URI and exchanges it with PKCE. Tokens are refreshed silently while the refresh token is valid.

Prerequisites on the identity provider app (public client with PKCE, Authorization Code + Refresh Token grants):

- register `http://localhost:8765/callback` and `http://localhost:8766/callback` as sign-in redirect URIs (Okta matches them exactly, port included)
- enable the Device Authorization grant if the CLI is also used on hosts without a browser (SSH sessions)
- if the authorization server policy does not allow the `offline_access` scope, the CLI falls back to `openid` and you log in again when the access token expires (about hourly); set `scopes: openid` in the profile to skip the rejected first attempt

The quickest way to configure it is to point the CLI at the data.all front page; the issuer, client id and API endpoint are read from the deployed app and the page URL is kept as `frontend_url`:

```bash
dataall_cli configure --profile okta --auth_type OidcBrowserAuth --dataall_url https://DATAALL_DOMAIN_URL
```

The resulting profile in `~/.dataall/config.yaml`:

```
okta:
  auth_type: OidcBrowserAuth
  client_id: testclient
  api_endpoint_url: https://API_GATEWAY_URL/prod
  redirect_uri: http://localhost:8765/callback
  fallback_redirect_uri: http://localhost:8766/callback
  idp_domain_url: https://IDP_DOMAIN_URL/oauth2/AUTH_SERVER_ID
  scopes: openid offline_access
  frontend_url: https://DATAALL_DOMAIN_URL
```

On a host without a browser (or with `DATAALL_DEVICE_LOGIN=1`) the CLI prints an activation URL and a short code instead; open the URL in any browser, enter the code and sign in.

### Specifying your user profile

Once you have configured your user profile appropriately, you can begin running data.all API requests via the SDK using your configured profile(s) such as:

  ```bash
  dataall_cli list_organizations --profile TestCustomProfile

  dataall_cli list_datasets --profile TestCognitoProfile
  ```

  By default, a profile of name `default` is used if none if provided


## Additional Configuration Options

### Specifying a separate Config YAML paths

If you would rather store your user information in a separate file, you can set an environment variable `dataall_config_path` to specify where to save/fetch a given profile provided:

```bash
export dataall_config_path=~/PATH/TO/NEW/PROFILE.yaml

dataall_cli configure --profile NewProfile # Will save profile to above dataall_config_path

...

dataall_cli list_organizations --profile NewProfile # Will fetch profile from above dataall_config_path
```

Additionally, you can specify a separate env variable `dataall_creds_path` to save `credentials.yaml` to a different path when configuring a new User Profile via `dataall_cli configure` command (default is `~/.dataall/credentials.yaml`)
