import json
import os
import platform
import subprocess


def validate_subl():
    if platform.system() == "Windows":
        candidates = [
            "subl",
            r"C:\Program Files\Sublime Text\subl",
            r"C:\Program Files\Sublime Text 3\subl",
            r"C:\Program Files (x86)\Sublime Text 3\subl",
            r"C:\Program Files (x86)\Sublime Text\subl",
        ]
    elif platform.system() == "Darwin":
        candidates = [
            "subl",
            "/Applications/Sublime Text.app/Contents/SharedSupport/bin/subl",
        ]
    else:
        candidates = ["subl"]
    for candidate in candidates:
        try:
            subprocess.check_call(
                [candidate, "-h"], stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            return candidate
        except Exception as e:
            continue
    else:
        raise ValueError(
            "subl not found. Please follow instructions https://www.sublimetext.com/docs/command_line.html"
        )


subl = validate_subl()


def send_sublime(c, data):
    print("send_sublime", c, json.dumps(data))
    command = [subl, "-b", "--command", c + " " + json.dumps(data)]
    # Adopted from https://dragonfly2.readthedocs.io/en/latest/_modules/dragonfly/actions/action_cmd.html#RunCommand
    import subprocess

    # Suppress showing the new CMD.exe window on Windows.
    startupinfo = None
    if os.name == "nt":
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

    ret_code = subprocess.call(command, startupinfo=startupinfo)
    return ret_code


# def send_snippet(contents, **kw):
#     """primitive to transmit the snippet to be inserted
#     This only takes care of sending the raw snippet text and parameters
#     not generating it or doing the bookkeeping for the variance system

#     Args:
#         contents (str): the contents/text of this snippet to be inserted
#         **kw: the raw snippet parameters passed as keyword arguments

#     """
#     if not isinstance(contents, str):
#         raise TypeError("contents must be a string instead received ", contents)
#     try:
#         json.dumps(kw)
#     except:
#         raise TypeError(
#             "snippet parameters must be json serializable, instead received", kw
#         )
#     kw["contents"] = contents
#     send_sublime("insert_snippet", kw)


# def send_quick_panel(items):
#     """displaying a list of choices in the quick panel and executed different action depending
#     on what the user chose

#     Args:
#         items (TYPE): an iterable of tuples representing a choice and consisting of three parts
#             - caption (str): the text displayed to the user
#             - command (str): the name of the command to execute, if this item is chosen
#             - args (dict): the parameters to pass to the command, must be json serializable

#     """
#     result = []
#     for caption, command, args in items:
#         if not isinstance(caption, str):
#             raise TypeError("caption must be a string instead received ", caption)
#         if not isinstance(command, str):
#             raise TypeError("command must be a string instead received ", command)
#         if not isinstance(args, dict):
#             raise TypeError("args must be a dict instead received ", args)
#         try:
#             json.dumps(args)
#         except:
#             raise TypeError("args must be json serializable, received ", args)
#         result.append(dict(caption=caption, command=command, args=args))
#     send_sublime("quick_panel", dict(items=result))
