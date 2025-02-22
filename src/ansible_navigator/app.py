"""Base class for apps (actions)."""
import logging

from copy import deepcopy
from typing import List
from typing import Pattern
from typing import Tuple
from typing import Union

from ansible_navigator.actions import kegexes

from .app_public import AppPublic

from .configuration_subsystem import ApplicationConfiguration
from .configuration_subsystem import Constants as C

from .initialization import parse_and_update

from .steps import Steps

from .ui_framework import Interaction
from .ui_framework import ui
from .ui_framework import warning_notification

from .utils import LogMessage
from .utils import ExitMessage


class App:
    # pylint: disable=too-few-public-methods
    # pylint: disable=too-many-instance-attributes
    """Base class for apps (actions)."""

    def __init__(self, args: ApplicationConfiguration, name: str, logger_name: str = __name__):
        """Initialize the App class.

        :param args: The current application configuration
        :param name: The name of the action inheriting this
        :param logger_name: The name for the logger
        """
        self._logger = logging.getLogger(logger_name)

        self._args: ApplicationConfiguration = self._copy_args(args)
        self._calling_app: AppPublic
        self._interaction: Interaction
        self._name = name
        self._previous_filter: Union[Pattern, None]
        self._previous_scroll: int
        self.stdout: List = []
        self.steps = Steps()

    @staticmethod
    def _action_match(entry: str) -> Union[Tuple[str, ui.Action], Tuple[None, None]]:
        """Attempt to match the user input against the regex provided by each action.

        :param entry: the user input
        :return: The name and matching action or not
        """
        for kegex in kegexes():
            match = kegex.kegex.match(entry)
            if match:
                return kegex.name, ui.Action(match=match, value=entry)
        return None, None

    @property
    def app(self) -> AppPublic:
        """Limit the scope of what is carried between actions.

        This will be passed to other actions to limit the scope of
        what can be mutated internally.

        :return: An instance of AppPublic for the current instance of the action
        :raises AttributeError: If the args have not been initialized
        """
        if self._args:
            return AppPublic(
                args=self._args,
                name=self._name,
                rerun=self.rerun,
                stdout=self.stdout,
                steps=self.steps,
                update=self.update,
                write_artifact=self.write_artifact,
            )
        raise AttributeError("app passed without args initialized")

    def no_interactive_mode(self, interaction: Interaction, app: AppPublic) -> None:
        # pylint: disable=unused-argument
        """Show a warning notification that the user interactive mode is not supported."""
        warning = warning_notification(
            messages=[
                f"The '{self._name}' subcommand is not available while using interactive mode.",
                "[HINT] Start an additional instance of ansible-navigator"
                + " in a new terminal with mode 'stdout'.",
                f"      e.g. 'ansible-navigator {self._name} --mode stdout",
            ]
        )
        interaction.ui.show(warning)

    @staticmethod
    def _copy_args(args: ApplicationConfiguration) -> ApplicationConfiguration:
        """Deepcopy the args.

        Note: Unmount the collection doc cache (CDC) first
        the CDC will get mounted if the child needs it
        in parse and update

        :param args: the current application configuration
        :return: A copy of the current application configuration
        """
        args.internals.collection_doc_cache = C.NOT_SET
        return deepcopy(args)

    def _prepare_to_run(self, app: AppPublic, interaction: Interaction) -> None:
        """Prepare for action run.

        An action can call this to prior to running. This
        will set the scroll to zero and store the state
        of the UI so it can be restored later.

        :param app: The instance of the action
        :param interaction: The current interaction from the UI
        """
        self._calling_app = app
        self._interaction = interaction
        self._interaction.ui.scroll(0)
        self._previous_scroll = interaction.ui.scroll()
        self._previous_filter = interaction.ui.menu_filter()

    def _prepare_to_exit(self, interaction: Interaction) -> None:
        """Prepare for action exit.

        An action can call this after running to clean up and
        restore the state of the UI prior to the action being
        invoked.

        :param interaction: The current interaction from the UI
        """
        interaction.ui.scroll(self._previous_scroll)
        interaction.ui.menu_filter(self._previous_filter)
        interaction.ui.scroll(0)

    def rerun(self) -> None:
        """Rerun the action.

        Defined in the child class if necessary.
        """

    def update(self) -> None:
        """Update the action.

        Defined in child if necessary
        """

    def _update_args(
        self, params: List, apply_previous_cli_entries: C = C.ALL, attach_cdc: bool = False
    ) -> None:
        """Update the current args.

        Pass the params through the configuration subsystem
        log messages and exit_messages as warnings since most will result in a form
        while the exit_messages would have cause a sys.exit(1) from the CLI
        each action should handle them in a manner that does not exit the TUI

        :param params: a sys.argv like list of parameters
        :param apply_previous_cli_entries: Should previous params from the CLI be applied
        :param attach_cdc: Should the collection doc cache be attached to the args.internals
        """
        messages: List[LogMessage]
        exit_messages: List[ExitMessage]

        messages, exit_messages = parse_and_update(
            params=params,
            apply_previous_cli_entries=apply_previous_cli_entries,
            args=self._args,
            attach_cdc=attach_cdc,
        )

        for message in messages:
            self._logger.log(level=message.level, msg=message.message)

        for exit_msg in exit_messages:
            if exit_msg.level == logging.ERROR:
                self._logger.warning(msg=exit_msg.message)
            else:
                self._logger.log(level=exit_msg.level, msg=exit_msg.message)

    def write_artifact(self, filename: str) -> None:
        """Write an artifact file.

        This will likely only be used by the run action.
        Defined in child if necessary

        :param filename: The filename to write to
        """
