"""Some simple tests for exec command and param generation."""

from typing import List
from typing import NamedTuple

import pytest

from ansible_navigator.actions.exec import _generate_command


class CommandTestData(NamedTuple):
    """The artifact files test data object."""

    name: str
    command: str
    shell: bool
    result_command: str
    result_params: List


def id_from_data(test_value):
    """Return the name from the test data object.

    :param test_value: The value from which the test id will be extracted
    :returns: The test id
    """
    return f" {test_value.name} "


command_test_data = [
    CommandTestData(
        name="With shell simple",
        command="echo foo",
        shell=True,
        result_command="/bin/bash",
        result_params=["-c", "echo foo"],
    ),
    CommandTestData(
        name="Without shell simple",
        command="echo foo",
        shell=False,
        result_command="echo",
        result_params=["foo"],
    ),
    CommandTestData(
        name="With shell complex",
        command="ansible-vault encrypt_string --vault-password-file"
        + " a_password_file 'foobar' --name 'the_secret'",
        shell=True,
        result_command="/bin/bash",
        result_params=[
            "-c",
            "ansible-vault encrypt_string --vault-password-file"
            + " a_password_file 'foobar' --name 'the_secret'",
        ],
    ),
    CommandTestData(
        name="Without shell complex",
        command="ansible-vault encrypt_string --vault-password-file"
        + " a_password_file 'foobar' --name 'the secret'",
        shell=False,
        result_command="ansible-vault",
        result_params=[
            "encrypt_string",
            "--vault-password-file",
            "a_password_file",
            "foobar",
            "--name",
            "the secret",
        ],
    ),
]


@pytest.mark.parametrize("cmd_test_data", command_test_data, ids=id_from_data)
def test_artifact_path(cmd_test_data: CommandTestData):
    """Test the generation of the command and params.

    :param cmd_test_data: The test data
    """
    command, additional_params = _generate_command(
        exec_command=cmd_test_data.command,
        exec_shell=cmd_test_data.shell,
    )
    comment = command_test_data, command, additional_params
    assert command == cmd_test_data.result_command, comment
    assert additional_params == cmd_test_data.result_params, comment
