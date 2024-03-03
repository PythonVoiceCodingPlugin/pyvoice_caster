import datetime
import logging

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

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

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
    start = datetime.datetime.now()
    with lists[list_name]:
        lists[list_name].set({x["spoken"]: x for x in data})
    end = datetime.datetime.now()
    logger.info(
        "Enhanced list %s with %s items over %s seconds (%s until %s)",
        list_name,
        len(data),
        (end - start).total_seconds(),
        start,
        end
    )
    logger.debug(
        "Sample item: %s",
        data[0] if data else None,
    )
    return True
