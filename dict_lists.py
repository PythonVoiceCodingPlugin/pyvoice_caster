from dragonfly import DictList, DictListRef

try:
    from pyvoice_caster.rpc import add_method
except ImportError:
    from caster_user_content.rules.pyvoice_caster.rpc import add_method

__all__ = [
    "dynamic_list",
    "dynamic_list_reference",
]

lists = {}


def dynamic_list(name, *args, **kwargs):
    if name not in lists:
        lists[name] = DictList(name, *args, **kwargs)
    return lists[name]


def dynamic_list_reference(reference_name, name=None, *args, **kwargs):
    if name is None:
        name = reference_name
    return DictListRef(name, dynamic_list(name, *args, **kwargs))


@add_method()
def enhance_spoken(list_name, data):
    print("Enhancing: ", list_name, len(data), data[0])
    with lists[list_name]:
        lists[list_name].set({x["spoken"]: x for x in data})
    return True
