try:
    from pyvoice_caster.caster_standard_imports import *
    from pyvoice_caster.dict_lists import dynamic_list_reference
except ImportError:
    from caster_user_content.rules.pyvoice_caster.caster_standard_imports import *
    from caster_user_content.rules.pyvoice_caster.dict_lists import \
        dynamic_list_reference


def insert_text(expression):
    value = expression["value"]
    if value[-1] == ")":
        Text(value).execute()
        Key("left").execute()
    else:
        Text(value).execute()


class PyVoiceCcr(MergeRule):
    pronunciation = "pie voice C C R"

    mapping = {
        "<expression>": R(Function(insert_text)),
    }
    extras = [
        dynamic_list_reference("expression"),
    ]
    defaults = {}


# ---------------------------------------------------------------------------


def get_rule():
    return PyVoiceCcr, RuleDetails(ccrtype=CCRType.GLOBAL)
