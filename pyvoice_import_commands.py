from dragonfly import *

try:
    from pyvoice_caster.action_classes import (LspExecute, SublimeCommand,
                                               VSCodeCommand)
    from pyvoice_caster.caster_standard_imports import *
    from pyvoice_caster.dict_lists import dynamic_list, dynamic_list_reference
except ImportError:
    from caster_user_content.rules.pyvoice_caster.action_classes import (
        LspExecute, SublimeCommand, VSCodeCommand)
    from caster_user_content.rules.pyvoice_caster.caster_standard_imports import *
    from caster_user_content.rules.pyvoice_caster.dict_lists import (
        dynamic_list, dynamic_list_reference)


def insert_pyvoice_qualified(importable):
    t = ".".join([importable["module"], importable["name"]])
    Text('"{}"'.format(t)).execute()


class PyvoiceImport(MappingRule):
    pronunciation = "pie voice import"

    mapping = {
        "import <importable>": R(
            LspExecute(
                "add_import",
                lambda importable: ["$file_uri", importable],
            ),
            rdescript="Add import statement single step",
        ),
        "from  <importable>": R(
            LspExecute(
                "from_import",
                lambda importable: [importable],
            ),
            rdescript="Deeper from import statement part one of a double step processs",
        ),
        "import <subsymbol>": R(
            LspExecute("add_import", lambda subsymbol: ["$file_uri", subsymbol]),
            rdescript="Deeper From import statement part two",
        ),
        "from  <importable> [fuzzy] import  [<every>] [<name>]": R(
            LspExecute(
                "from_import_fuzzy",
                lambda importable, every, name: [
                    "$file_uri",
                    importable,
                    str(name),
                    every,
                ],
            ),
            rdescript="From ",
        ),
        "get spoken": R(
            LspExecute("get_spoken", ["$file_uri", "$position"]),
            rdescript="Shorthand for getting spoken information without waiting for the listener on the editor",
        ),
        "qualified <importable>": R(Function(insert_pyvoice_qualified)),
    }
    extras = [
        dynamic_list_reference("importable"),
        dynamic_list_reference("subsymbol"),
        Literal("every", "every", True, False),
        Dictation("name", default=""),
    ]
    defaults = {}


# ---------------------------------------------------------------------------


def get_rule():
    return PyvoiceImport, RuleDetails(name="pie voice import")
