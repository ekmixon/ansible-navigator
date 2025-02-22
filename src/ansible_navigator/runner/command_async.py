"""Implementation of the asynchronous invocation of ``ansible-runner``.

Herewith lies the ability to invoke ``ansible-runner`` in an async fashion.
A queue is provided and ``ansible-runner`` uses ``pexpect`` to parse
standard out and error from the command run and populates the
queue with messages.
"""

from queue import Queue
from ansible_runner import run_command_async  # type: ignore[import]

from .command_base import CommandBase


class CommandAsync(CommandBase):
    # pylint: disable=too-few-public-methods
    # pylint: disable=too-many-instance-attributes
    """A wrapper for the asynchronous runner."""

    def __init__(self, executable_cmd: str, queue: Queue, **kwargs):
        """Initialize the arguments for the ``run_command_async`` interface of ``ansible-runner``.

        For common arguments refer to the documentation of the ``CommandBase`` class.

        :param executable_cmd: The command to be invoked.
        :param queue: The queue to post events from ``ansible-runner``.
        """
        self._eventq = None
        self._queue = queue
        super().__init__(executable_cmd, **kwargs)

    def _event_handler(self, event):
        self._logger.debug("ansible-runner event handle: %s", event)
        self._queue.put(event)

    def run(self):
        """Initiate the execution of the runner command in async mode"""
        self.generate_run_command_args()
        self._runner_args.update({"event_handler": self._event_handler})
        thread, self.ansible_runner_instance = run_command_async(**self._runner_args)
        self.status = "running"
        return thread
