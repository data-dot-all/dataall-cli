
# 3 - Running a CLI Command

## Running a CLI Command

To run an SDK command it is as simple as writing your data.all cli command in a bash shell, specifying whatever additional parameters and profile for the given command.

For instance:
```bash
dataall_cli list_organizations --profile TestCustomProfile
```


### Listing Supported Commands

To get a list of all support commands you can pass the `--help` flag:

```bash
dataall_cli --help

```


## Listing Supported Input Arguments

To get a list of all support input parameters for a given command you can pass the `--help` flag for that command:

```bash
dataall_cli list_organization --help

```


## Specifying a New Schema Version 

By default, data.all uses the latest schema present in the the dataall_core PyPi repositories library, under path `dataall_core/dataall_core/schema/v2_6.json`.

Each one of the schemas listed in the `schema/` directory are the GraphQL Schema files generated from that version of data.all (a.k.a the value of the release tag of the version). 

To specify a separate schema version to use, you can export a new environment variable `dataall_schema_version` before running a CLI command, for example:

```bash

export dataall_schema_version=v2_5

dataall_cli list_organization
```


## Specifying a New Schema Path 

Going further, if you want to provide your own GraphQL schema specific to your data.all application you can do that as well. 

To specify a separate GraphQL schema to use, you can export a new environment variable `dataall_schema_path` before running a CLI command so that you can point the DataallClient to load a GraphQL schema that is custom to you deployment, for example:

```bash

export dataall_schema_path=/Path/To/Custom/dataall/schema.json

dataall_cli custom_command
```