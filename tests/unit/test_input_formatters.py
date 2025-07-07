import os
from pathlib import Path

import pytest

from dataall_cli.bind_commands import _structure_input_dict

PROFILE_CONFIG = os.path.join(
    Path(__file__).parents[1], "profile_config", "config.yaml"
)
os.environ["dataall_config_path"] = PROFILE_CONFIG


flattened_args_1 = {"shareUri": (None, "shareUri"), "filter": (None, "filter")}

exepcted_args_1 = {
    "shareUri": ("String", None, True),
    "filter": ("ShareableObjectFilter", None, False),
}

flattened_args_2 = {
    "label": (None, "input.label"),
    "organizationUri": (None, "input.organizationUri"),
    "environmentUri": (None, "input.environmentUri"),
    "description": (None, "input.description"),
    "tags": (None, "input.tags"),
    "owner": (None, "input.owner"),
    "topics": (None, "input.topics"),
    "SamlAdminGroupName": (None, "input.SamlAdminGroupName"),
    "businessOwnerEmail": (None, "input.businessOwnerEmail"),
    "businessOwnerDelegationEmails": (None, "input.businessOwnerDelegationEmails"),
    "confidentiality": (None, "input.confidentiality"),
    "stewards": (None, "input.stewards"),
    "autoApprovalEnabled": (None, "input.autoApprovalEnabled"),
    "filter": (None, "filter"),
    "tables_filter": (None, "tables_filter"),
    "locations_filter": (None, "locations_filter"),
    "shares_filter": (None, "shares_filter"),
    "projectUri": (None, "projectUri"),
    "environmentUri_1": (None, "environmentUri"),
}

expected_args_2 = {
    "input": {
        "label": "String",
        "organizationUri": "String",
        "environmentUri": "String",
        "description": "String",
        "tags": "List",
        "owner": "String",
        "topics": "List",
        "SamlAdminGroupName": "String",
        "businessOwnerEmail": "String",
        "businessOwnerDelegationEmails": "String",
        "confidentiality": "String",
        "stewards": "String",
        "autoApprovalEnabled": "Boolean",
    },
    "filter": ("EnvironmentFilter", None, False),
    "tables_filter": ("DatasetTableFilter", None, False),
    "locations_filter": ("DatasetStorageLocationFilter", None, False),
    "shares_filter": ("ShareObjectFilter", None, False),
    "projectUri": ("String", None, False),
    "environmentUri": ("String", None, False),
}

flattened_args_3 = {
    "datasetUri": (None, "datasetUri"),
    "itemUri": (None, "itemUri"),
    "itemType": (None, "itemType"),
    "input": (None, "input"),
    "filter": (None, "filter"),
}

expected_args_3 = {
    "datasetUri": "String",
    "input": {
        "environmentUri": "String",
        "groupUri": "String",
        "principalId": "String",
        "principalType": "String",
        "requestPurpose": "String",
        "attachMissingPolicies": "Boolean",
    },
}

cli_args_3 = {
    "profile": "TestUser",
    "dataseturi": "URI",
    "input": '{"environmentUri": "URI", "groupUri": "TestGroup", "principalId": "TestGroup", "principalType": "Group", "requestPurpose": "Created by data.all CLI", "attachMissingPolicies": true}',
}

flattened_args_4 = {
    "datasetUri": (None, "datasetUri"),
    "itemUri": (None, "itemUri"),
    "itemType": (None, "itemType"),
    "input": (None, "input"),
    "filter": (None, "filter"),
}

expected_args_4 = {}

cli_args_4 = {"dataseturi": None, "input": None}


def getshape(d):
    if isinstance(d, dict):
        return {k: getshape(d[k]) for k in d}
    else:
        return None


@pytest.mark.parametrize(
    "input_args",
    [(flattened_args_1, exepcted_args_1), (flattened_args_2, expected_args_2)],
)
def test_structure_input_dict(input_args):
    flattened, expected = input_args
    cli_args = {}
    for k, v in flattened.items():
        cli_args[k.lower()] = "testvalue"
    inputs = _structure_input_dict(flattened, cli_args)

    assert getshape(inputs) == getshape(expected)


@pytest.mark.parametrize(
    "input_args",
    [
        (flattened_args_3, expected_args_3, cli_args_3),
        (flattened_args_4, expected_args_4, cli_args_4),
    ],
)
def test_nested_json_structure_input_dict(input_args):
    flattened, expected, cli_args = input_args
    inputs = _structure_input_dict(flattened, cli_args)

    assert getshape(inputs) == getshape(expected)
