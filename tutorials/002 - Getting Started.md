
# 2 - Getting Started

## How does dataall_cli handle data.all user credentials and profiles?

Dataall's CLI requires user profile information to be stored either in a local file or in AWS Secrets Manager. The user information required includes:

- auth_type: Either `CognitoAuth` or `CustomAuth`
- client_id: The App Client ID
- api_endpoint_url: The URL data.all API Gateway Endpoint 
- redirect_uri: The data.all domain URL
- idp_domain_url: The Identity Providers URL
- client_secret (optional): The client secret used for the data.all App Client
- auth_server (optional, used for CustomAuth): The Custom Authorization Server used if applicable
- session_token_endpoint (optional, required for CustomAuth): The Identity Provider API endpoint to retrieve session tokens
- profile:  The Profile Name

Data.all's SDK uses the profile information to fetch and save tokens from the data.all application. 

By default the user information is provided at `~/.dataall/config.yaml` and the token information is saved at `~/.dataall/credentials.yaml`

If a valid token or refresh token exists for the given user, that will be used to fetch a new token and authenticate the profile. Otherwise, the user will be prompted for username and password when running an API request and the fetched tokens will be saved.


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
