"""Functions to Bind Dataall Commands to core functions."""

import json
import logging
from typing import Any, Callable, Dict, Optional

import click
from dataall_core.dataall_client import DataallClient

logger = logging.getLogger(__name__)


def _structure_input_dict(
    flattened: dict[str, Any], cli_args: dict[str, Any], sep: str = "."
) -> dict[str, Any]:
    reconstructed: dict[str, Any] = {}
    for key, parent in flattened.items():
        if key.lower() in cli_args.keys():
            if parent[1] and cli_args[key.lower()]:
                # Try JSON Loads for Dict Input
                try:
                    cli_args[key.lower()] = json.loads(cli_args[key.lower()])
                except json.JSONDecodeError:
                    pass
                parent_keys = parent[1].split(sep)
                parent_dict = reconstructed
                for pk in parent_keys[:-1]:
                    parent_dict = parent_dict.setdefault(pk, {})
                parent_dict[parent_keys[-1]] = cli_args[key.lower()]

    return reconstructed


def _bind_function(
    fn_name: str,
    operation_details: dict[str, Any],
    config_path: str,
    schema_path: Optional[str],
    schema_version: Optional[str],
    custom_headers: Dict[str, Any] = {},
) -> Callable[..., None]:
    name = operation_details["operation_name"]
    operation_details["input_args"]
    flatten_input_args = operation_details["flatten_input_args"]

    def func(**kwargs: Any) -> None:
        logger.debug("I am the '{}' command".format(name))
        da_client = DataallClient(
            schema_path=schema_path, schema_version=schema_version
        ).client(
            profile=kwargs.get("profile", "default"),
            config_path=config_path,
            custom_headers=custom_headers,
        )
        input_dict = {}
        try:
            input_dict = _structure_input_dict(flatten_input_args, kwargs)
        except Exception as e:
            raise Exception(f"Invalid Input: {e}")
        response = getattr(da_client, fn_name)(**input_dict)
        click.echo(json.dumps(response))

    # Add Click Options
    for key in flatten_input_args.keys():
        desc = flatten_input_args[key][0]
        func = click.option(f"--{key}", default=None, help=desc)(func)
    func = click.option("--profile", default="default", help="data.all profile name")(
        func
    )

    # Add Click Func Name
    func.__name__ = fn_name
    return func


# IMPORTANT: Bind each CLI command name to its respective function
def bind(
    dataall_cli: click.Group,
    commands: Dict[str, Any],
    config_path: str,
    schema_path: Optional[str],
    schema_version: Optional[str],
    custom_headers: Dict[str, Any] = {},
) -> None:
    """
    Bind CLI commands to their respective functions.

    Args:
        dataall_cli (click.Group): The main CLI group.
        commands (Dict[str, Any]): A dictionary containing the command details.
        config_path (str): The path to the configuration file.

    Returns
    -------
        None
    """
    for operation_name, operation_details in commands.items():
        f = _bind_function(
            operation_name,
            operation_details,
            config_path,
            schema_path,
            schema_version,
            custom_headers,
        )
        dataall_cli.command(name=operation_name)(f)
