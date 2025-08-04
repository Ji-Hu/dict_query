from typing import List, Dict, Any
import copy

# TODO support items :  nested field, $exists, $regex, limit, sort


def get_nested_value(doc: Dict[str, Any], dotted_key: str) -> Any:
    keys = dotted_key.split(".")
    try:
        for k in keys:
            doc = doc[k]
        return doc
    except (KeyError, TypeError):
        return None

def matches(doc: Dict[str, Any], query: Dict[str, Any]) -> bool:
    for key, cond in query.items():
        if key == "$or":
            return any(matches(doc, sub_q) for sub_q in cond)

        value = get_nested_value(doc, key)

        if isinstance(cond, dict):
            for op, expected in cond.items():
                if op == "$gt" and not (value > expected): return False
                if op == "$lt" and not (value < expected): return False
                if op == "$gte" and not (value >= expected): return False
                if op == "$lte" and not (value <= expected): return False
                if op == "$ne" and not (value != expected): return False
                if op == "$in" and not (value in expected): return False
        else:
            if value != cond:
                return False

    return True

class DictQuery:
    def __init__(self, data: List[Dict[str, Any]] = None):
        self.data = data if data is not None else []

    def find(self, query: Dict[str, Any]) -> List[Dict[str, Any]]:
        return [copy.deepcopy(doc) for doc in self.data if matches(doc, query)]

    def insert_one(self, new_doc : Dict[str, Any]) -> None:
        self.data.append(copy.deepcopy(new_doc))

    def insert_many(self, new_docs : List[Dict[str, Any]]) -> None:
        self.data.extend(copy.deepcopy(new_docs))

    def delete_many(self, query : List[Dict[str, Any]]) -> None:
        self.data = [doc for doc in self.data if not matches(doc, query)]

    # def update_many(self, query, update_context):
    #     for doc in self.data:
    #         if matches(doc, query):
    #             self._apply_update(doc, update_context)
    #
    # def _apply_update(self, doc, update_context):
    #     for op, updates in update_context.items():
    #         if op == "$set":
    #             for key, value in updates.items():
    #                 self._set_nested_value(doc, key, value)
    #
    # def _set_nested_value(self, doc, key, value):
    #     keys = key.split(".")
    #     for k in keys[:-1]:
    #         doc = doc.setdefault(k, {})
    #     doc[keys[-1]] = value

    def all(self) -> List[Dict[str, Any]]:
        return self.data