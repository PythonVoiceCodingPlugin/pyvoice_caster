import json
import os
import sys
import time
from tempfile import gettempdir
from uuid import uuid4


def is_linux():
    return sys.platform.startswith("linux")


from dragonfly import Key

# How old a request file needs to be before we declare it stale and are willing
# to remove it
STALE_TIMEOUT_MS = 60000

# The amount of time to wait for application to perform a command, in seconds
RPC_COMMAND_TIMEOUT_SECONDS = 3.0

# When doing exponential back off waiting for the application to perform a command, how
# long to sleep the first time
MINIMUM_SLEEP_TIME_SECONDS = 0.0005

# Indicates whether a pre-phrase signal was emitted during the course of the
# current phrase
did_emit_pre_phrase_signal = False


class NotSet(object):
    def __repr__(self):
        return "<argument not set>"


class NoFileServerException(Exception):
    pass


def write_json_exclusive(path, body):
    """Writes jsonified object to file, failing if the file already exists

    Args:
        path: The path of the file to write
        body: The object to convert to json and write
    """
    with open(path, "w") as out_file:
        out_file.write(json.dumps(body))


class Request:
    def __init__(self, command_id, args, wait_for_finish, return_command_output, uuid):
        self.command_id = command_id
        self.args = args
        self.wait_for_finish = wait_for_finish
        self.return_command_output = return_command_output
        self.uuid = uuid

    def to_dict(self):
        return {
            "commandId": self.command_id,
            "args": self.args,
            "waitForFinish": self.wait_for_finish,
            "returnCommandOutput": self.return_command_output,
            "uuid": self.uuid,
        }


def write_request(request, path):
    """Converts the given request to json and writes it to the file, failing if
    the file already exists unless it is stale, in which case it replaces it

    Args:
        request: The request to serialize
        path: The path to write to

    Raises:
        Exception: If another process has an active request file
    """
    try:
        write_json_exclusive(path, request.to_dict())
        request_file_exists = False
    except OSError:
        request_file_exists = True

    if request_file_exists:
        handle_existing_request_file(path)
        write_json_exclusive(path, request.to_dict())


def handle_existing_request_file(path):
    stats = os.stat(path)

    modified_time_ms = stats.st_mtime_ns / 1e6
    current_time_ms = time.time() * 1e3
    time_difference_ms = abs(modified_time_ms - current_time_ms)

    if time_difference_ms < STALE_TIMEOUT_MS:
        raise Exception(
            "Found recent request file; another Talon process is probably running"
        )
    else:
        print("Removing stale request file")
        robust_unlink(path)


def run_command(command_id, *args, **kwargs):
    """Runs a command, using the command server if available

    Args:
        command_id: The ID of the command to run.
        args: The arguments to the command.
        kwargs:
          wait_for_finish (bool, optional): Whether to wait for the command to finish before returning. Defaults to False.
          return_command_output (bool, optional): Whether to return the output of the command. Defaults to False.

    Raises:
        Exception: If there is an issue with the file-based communication, or
        application raises an exception

    Returns:
        Object: The response from the command, if requested.
    """
    print(command_id, args, kwargs)
    wait_for_finish = kwargs.get("wait_for_finish", False)
    return_command_output = kwargs.get("return_command_output", False)

    # NB: This is a hack to work around the fact that talon doesn't support
    # variable argument lists
    args = [x for x in args if x is not NotSet]

    communication_dir_path = get_communication_dir_path()

    if not os.path.exists(communication_dir_path):
        if args or return_command_output:
            raise Exception("Must use command-server extension for advanced commands")
        raise NoFileServerException("Communication directory not found")

    request_path = os.path.join(communication_dir_path, "request.json")
    response_path = os.path.join(communication_dir_path, "response.json")

    # Generate uuid that will be mirrored back to us by command server for
    # sanity checking
    uuid = str(uuid4())
    print("uuid", uuid)
    print("args", args)
    print("request_path", request_path)
    request = Request(
        command_id=command_id,
        args=args,
        wait_for_finish=wait_for_finish,
        return_command_output=return_command_output,
        uuid=uuid,
    )

    # First, write the request to the request file, which makes us the sole
    # owner because all other processes will try to open it with 'x'
    write_request(request, request_path)

    # We clear the response file if it does exist, though it shouldn't
    if os.path.exists(response_path):
        print("WARNING: Found old response file")
        robust_unlink(response_path)

    # Then, perform keystroke telling the application to execute the command in the
    # request file.  Because only the active application instance will accept
    # keypresses, we can be sure that the active application instance will be the
    # one to execute the command.
    Actions.trigger_command_server_command_execution()  # Commented as it's not clear where Actions is defined

    # try:
    #     decoded_contents = read_json_with_timeout(response_path)
    # finally:
    #     # NB: We remove the response file first because we want to do this while we
    #     # still own the request file
    #     robust_unlink(response_path)
    #     robust_unlink(request_path)

    # if decoded_contents["uuid"] != uuid:
    #     raise Exception("uuids did not match")

    # for warning in decoded_contents["warnings"]:
    #     print("WARNING:", warning)

    # if decoded_contents["error"] is not None:
    #     raise Exception(decoded_contents["error"])

    # time.sleep(0.025)

    # return decoded_contents["returnValue"]


def get_communication_dir_path():
    """Returns the directory that is used by the command-server for communication

    Returns:
        str: The path to the communication dir
    """
    suffix = ""

    # NB: We don't suffix on Windows because the temp dir is user-specific
    # anyway
    if hasattr(os, "getuid"):
        suffix = "-{}".format(os.getuid())

    return os.path.join(gettempdir(), "{}{}".format("vscode-command-server", suffix))


def robust_unlink(path):
    """Unlink the given file if it exists, and if we're on Windows and it is
    currently in use, just rename it

    Args:
        path: The path to unlink
    """
    try:
        os.unlink(path)
    except OSError as e:
        if hasattr(e, "winerror") and e.winerror == 32:
            graveyard_dir = os.path.join(get_communication_dir_path(), "graveyard")
            os.makedirs(graveyard_dir, exist_ok=True)
            graveyard_path = os.path.join(graveyard_dir, str(uuid4()))
            print(
                "WARNING: File {} was in use when we tried to delete it; "
                "moving to graveyard at path {}".format(path, graveyard_path)
            )
            os.rename(path, graveyard_path)
        else:
            raise e


def read_json_with_timeout(path):
    """Repeatedly tries to read a json object from the given path, waiting
    until there is a trailing new line indicating that the write is complete

    Args:
        path: The path to read from

    Raises:
        Exception: If we timeout waiting for a response

    Returns:
        Any: The json-decoded contents of the file
    """
    timeout_time = time.perf_counter() + RPC_COMMAND_TIMEOUT_SECONDS
    sleep_time = MINIMUM_SLEEP_TIME_SECONDS
    while True:
        try:
            with open(path, "r") as f:
                raw_text = f.read()

            if raw_text.endswith("\n"):
                break
        except FileNotFoundError:
            # If not found, keep waiting
            pass

        time.sleep(sleep_time)

        time_left = timeout_time - time.perf_counter()

        if time_left < 0:
            raise Exception("Timed out waiting for response")

        # NB: We use the minimum sleep time here to ensure that we don't spin with
        # small sleeps due to clock slip
        sleep_time = max(min(sleep_time * 2, time_left), MINIMUM_SLEEP_TIME_SECONDS)

    return json.loads(raw_text)


class Actions(object):
    @staticmethod
    def run_rpc_command(
        command_id, arg1=NotSet, arg2=NotSet, arg3=NotSet, arg4=NotSet, arg5=NotSet
    ):
        """Execute command via RPC."""
        run_command(
            command_id,
            arg1,
            arg2,
            arg3,
            arg4,
            arg5,
        )

    @staticmethod
    def run_rpc_command_and_wait(
        command_id, arg1=NotSet, arg2=NotSet, arg3=NotSet, arg4=NotSet, arg5=NotSet
    ):
        """Execute command via application command server and wait for the command to finish."""
        run_command(
            command_id,
            arg1,
            arg2,
            arg3,
            arg4,
            arg5,
            wait_for_finish=True,
        )

    @staticmethod
    def run_rpc_command_get(
        command_id, arg1=NotSet, arg2=NotSet, arg3=NotSet, arg4=NotSet, arg5=NotSet
    ):
        """Execute command via application command server and return command output."""
        return run_command(
            command_id,
            arg1,
            arg2,
            arg3,
            arg4,
            arg5,
            return_command_output=True,
        )

    @staticmethod
    def command_server_directory():
        """Return the directory of the command server"""
        return "vscode-command-server"

    @staticmethod
    def trigger_command_server_command_execution():
        """Issue keystroke to trigger the command server to execute the command that
        was written to the file. For internal use only"""
        if is_linux:
            Key("csa-p").execute()
        else:
            Key("cs-f17").execute()

    @staticmethod
    def emit_pre_phrase_signal():
        """
        If in an application supporting the command client, returns True
        and touches a file to indicate that a phrase is beginning execution.
        Otherwise does nothing and returns False.
        """
        # termx88: not implemented, to be ever True
        return False

    @staticmethod
    def did_emit_pre_phrase_signal():
        """Indicates whether the pre-phrase signal was emitted at the start of this phrase"""
        # NB: This action is used by cursorless; please don't delete it :)
        return did_emit_pre_phrase_signal
