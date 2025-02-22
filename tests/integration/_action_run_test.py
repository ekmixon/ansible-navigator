"""directly run an action for testing"""
import os
import re
import sys
import tempfile

from copy import deepcopy

from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple

from ansible_navigator.app_public import AppPublic
from ansible_navigator.configuration_subsystem import Constants as C
from ansible_navigator.configuration_subsystem import NavigatorConfiguration
from ansible_navigator.ui_framework.ui import Action as Ui_action
from ansible_navigator.ui_framework.ui import Interaction
from ansible_navigator.ui_framework.ui import Ui
from ansible_navigator.steps import Steps


class ActionRunTest:
    # pylint: disable=too-many-instance-attributes
    # pylint: disable=too-many-arguments
    """Directly run an action."""

    def __init__(
        self,
        action_name,
        container_engine: Optional[str] = None,
        container_options: Optional[List] = None,
        execution_environment: Optional[str] = None,
        execution_environment_image: Optional[str] = None,
        host_cwd: Optional[List] = None,
        set_environment_variable: Optional[Dict] = None,
        pass_environment_variable: Optional[List] = None,
        private_data_dir: Optional[str] = None,
        rotate_artifacts: Optional[int] = None,
        timeout: Optional[int] = None,
    ) -> None:
        self._action_name = action_name
        self._container_engine = container_engine
        self._container_options = container_options
        self._execution_environment = execution_environment
        self._execution_environment_image = execution_environment_image
        self._set_environment_variable = set_environment_variable
        self._pass_environment_variable = pass_environment_variable
        self._host_cwd = host_cwd
        self._private_data_dir = private_data_dir
        self._rotate_artifacts = rotate_artifacts
        self._timeout = timeout
        self._app_args = {
            "container_engine": self._container_engine,
            "container_options": self._container_options,
            "execution_environment": self._execution_environment,
            "execution_environment_image": self._execution_environment_image,
            "set_environment_variable": self._set_environment_variable,
            "pass_environment_variable": self._pass_environment_variable,
            "ansible_runner_artifact_dir": self._private_data_dir,
            "ansible_runner_rotate_artifacts_count": self._rotate_artifacts,
            "ansible_runner_timeout": self._timeout,
        }
        self._app_action = __import__(
            f"ansible_navigator.actions.{self._action_name}", globals(), fromlist=["Action"]
        )

    def callable_pass_one_arg(self, value=0):
        """a do nothing callable"""

    def callable_pass(self, **kwargs):
        """a do nothing callable"""

    def run_action_interactive(self) -> Any:
        """run the action
        The return type is set to Any here since not all actions
        have the same signature, the corresponding integration test
        will be using the action internals for asserts
        """
        self._app_args.update({"mode": "interactive"})
        args = deepcopy(NavigatorConfiguration)
        for argument, value in self._app_args.items():
            args.entry(argument).value.current = value
            args.entry(argument).value.source = C.USER_CFG

        action = self._app_action.Action(args=args)
        steps = Steps()
        app = AppPublic(
            args=args,
            name="test_app",
            rerun=self.callable_pass,
            stdout=[],
            steps=steps,
            update=self.callable_pass,
            write_artifact=self.callable_pass,
        )

        user_interface = Ui(
            clear=self.callable_pass,
            menu_filter=self.callable_pass_one_arg,
            scroll=self.callable_pass_one_arg,
            show=self.callable_pass,
            update_status=self.callable_pass,
            xform=self.callable_pass,
        )
        match = re.match(self._app_action.Action.KEGEX, self._action_name)
        if not match:
            raise ValueError

        ui_action = Ui_action(match=match, value=self._action_name)
        interaction = Interaction(name="test", ui=user_interface, action=ui_action)

        # run the action
        action.run(interaction=interaction, app=app)

        return action

    def run_action_stdout(self, **kwargs) -> Tuple[int, str, str]:
        # pylint: disable=too-many-locals
        """run the action"""
        self._app_args.update({"mode": "stdout"})
        self._app_args.update(kwargs)
        args = deepcopy(NavigatorConfiguration)
        for argument, value in self._app_args.items():
            args.entry(argument).value.current = value
            args.entry(argument).value.source = C.USER_CFG

        action = self._app_action.Action(args=args)

        # get a TTY, runner/docker requires it
        _mtty, stty = os.openpty()

        # preserve current ``stdin``, ``stdout``, ``stderr``
        __stdin__ = sys.stdin
        __stdout__ = sys.stdout
        __stderr__ = sys.stderr

        # ``pytest`` pseudo ``stdin`` doesn't ``fileno()``, use original
        sys.stdin = stty  # type: ignore

        # set ``stderr`` and ``stdout`` to file descriptors
        with tempfile.TemporaryFile() as sys_stdout, tempfile.TemporaryFile() as sys_stderr:
            sys.stdout = sys_stdout  # type: ignore
            sys.stderr = sys_stderr  # type: ignore

            # run the action
            return_code = action.run_stdout()

            # restore ``stdin``
            sys.stdin = __stdin__

            # read and restore ``stdout``
            sys.stdout.seek(0)
            stdout = sys.stdout.read().decode()  # type: ignore
            sys.stdout = __stdout__

            # read and restore ``stderr``
            sys.stderr.seek(0)
            stderr = sys.stderr.read().decode()  # type: ignore
            sys.stderr = __stderr__

        return return_code, stdout, stderr
