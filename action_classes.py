from dragonfly.actions.action_base import ActionBase, ActionError
try:
    from pyvoice_caster.functional_utils import evaluate_function
    from pyvoice_caster.sublime_client import send_sublime
    from pyvoice_caster.vscode_client import run_command
except ImportError:
    from caster_user_content.rules.pyvoice_caster.functional_utils import evaluate_function
    from caster_user_content.rules.pyvoice_caster.sublime_client import send_sublime
    from caster_user_content.rules.pyvoice_caster.vscode_client import run_command

__all__ = [
    "SublimeCommand",
]


class SublimeCommand(ActionBase):
    def __init__(self, command="", parameters={}, extra=None, synchronous=True):
        super(SublimeCommand, self).__init__()
        if not isinstance(parameters, dict) and not callable(parameters):
            raise TypeError("In SublimeCommand parameters must be a dict or a callable")
        if not isinstance(command, str) and not callable(command):
            raise TypeError("In SublimeCommand command must be a string")
        self.parameters = parameters
        self.command = command
        self.synchronous = synchronous

    def _execute(self, data):
        if isinstance(self.parameters, dict):
            p = self.parameters
        else:
            p = evaluate_function(self.parameters, data)
        send_sublime(self.command, p)


class VSCodeCommand(ActionBase):
    def __init__(self, command="", parameters=[], extra=None, synchronous=True):
        super(VSCodeCommand, self).__init__()
        if not isinstance(parameters, list) and not callable(parameters):
            raise TypeError("In VSCodeCommand parameters must be a list or a callable")
        if not isinstance(command, str) and not callable(command):
            raise TypeError("In VSCodeCommand command must be a string")
        self.parameters = parameters
        self.command = command
        self.synchronous = synchronous

    def _execute(self, data):
        if isinstance(self.parameters, list):
            p = self.parameters
        else:
            p = evaluate_function(self.parameters, data)
        run_command(self.command, *p)


# context action
from dragonfly import *

# ContextAction(
#     default=Key("c-y"),
#     actions=[
#         # Use cs-z for rstudio
#         (AppContext(executable="rstudio"), Key("cs-z")),
#     ],
# )


# def lsp_execute(
#     command_name="", session_name="", command_args=[], extra=None, synchronous=True
# ):
#     return C


class LspExecute(ActionBase):
    def __init__(
        self,
        command_name="",
        command_args=[],
        session_name="LSP-pyvoice",
        extra=None,
        synchronous=True,
    ):
        if not isinstance(command_name, str) and not callable(command_name):
            raise TypeError("In LspExecute command_name must be a string")
        if not isinstance(session_name, str) and not callable(session_name):
            raise TypeError("In LspExecute session_name must be a string")
        if not isinstance(command_args, list) and not callable(command_args):
            raise TypeError("In LspExecute command_args must be a list")
        self.command_name = command_name
        self.session_name = session_name
        self.command_args = command_args
        self.synchronous = synchronous

    def _execute(self, data):
        if isinstance(self.command_args, list):
            p = self.command_args
        else:
            p = evaluate_function(self.command_args, data)
        action = ContextAction(
            default=SublimeCommand(
                "lsp_execute",
                {
                    "command_name": self.command_name,
                    "session_name": self.session_name,
                    "command_args": p,
                },
                synchronous=self.synchronous,
            ),
            actions=[
                (
                    AppContext(executable="code", title="Visual Studio Code"),
                    VSCodeCommand(
                        "pyvoice.lsp_execute",
                        [self.command_name, p],
                        synchronous=self.synchronous,
                    ),
                ),
            ],
        )
        action.execute(data)
