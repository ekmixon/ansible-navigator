"""Jump to one action."""
import os

from typing import TYPE_CHECKING

from ansible_navigator.actions import kegexes
from ansible_navigator.actions import run_action

from .app import App
from .configuration_subsystem import ApplicationConfiguration
from .steps import Steps
from .ui_framework import Interaction
from .ui_framework import UIConfig
from .ui_framework import UserInterface

if TYPE_CHECKING:
    from _curses import _CursesWindow  # pylint: disable=no-name-in-module

    Window = _CursesWindow
else:
    from typing import Any

    Window = Any

DEFAULT_REFRESH = 100
DEFAULT_COLORS = "terminal_colors.json"
THEME = "dark_vs.json"


class ActionRunner(App):

    # pylint: disable=too-few-public-methods
    # pylint: disable=too-many-instance-attributes
    """A single action runner."""

    def __init__(self, args: ApplicationConfiguration) -> None:
        """Initialize the ActionRunner class.

        :param args: The current application configuration
        """
        super().__init__(args, name="action_runner")
        self._ui: UserInterface
        self.steps: Steps = Steps()

    def initialize_ui(self, refresh: int) -> None:
        """Initialize the user interface.

        :param refresh: The refresh for the UI
        :type refresh: int
        """
        share_directory = self._args.internals.share_directory
        theme_dir = os.path.join(share_directory, "themes")

        config = UIConfig(
            color=self._args.display_color,
            colors_initialized=False,
            grammar_dir=os.path.join(share_directory, "grammar"),
            osc4=self._args.osc4,
            terminal_colors_path=os.path.join(theme_dir, DEFAULT_COLORS),
            theme_path=os.path.join(theme_dir, THEME),
        )

        self._ui = UserInterface(
            screen_miny=3,
            kegexes=kegexes,
            refresh=refresh,
            ui_config=config,
        )

    def run(self, _screen: Window) -> None:
        # pylint: disable=protected-access
        """Run the app.

        Initialize the UI.
        Create an interaction based on the app name from the current settings.
        Run the action, passing the interaction.

        :param _screen: The screen instance from the curses wrapper call
        """
        self.initialize_ui(DEFAULT_REFRESH)
        name, action = self._action_match(self._args.app)
        if name and action:
            interaction = Interaction(
                name=name, action=action, menu=None, content=None, ui=self._ui._ui
            )
            self._run_app(interaction)

    def _run_app(self, initial_interaction: Interaction) -> None:
        """Enter the endless app loop.

        :param initial_interaction: The initial interaction for app start
        """
        while True:
            if not self.steps:
                self.steps.append(initial_interaction)

            if isinstance(self.steps.current, Interaction):
                interaction = run_action(self.steps.current.name, self.app, self.steps.current)
            if interaction is None:
                self.steps.back_one()
                if not self.steps:
                    break
            elif interaction.name == "quit":
                break
            else:
                self.steps.append(interaction)
