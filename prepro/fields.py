"""Editable form of block property values, for the Blender model editor.

Each block property is shown with one widget, chosen from its catalog
binding (`widget`). A value is split into the plain slots the widget edits
(`to_slots`) and assembled back from them (`from_slots`). Nothing here uses
`bpy`, so the conversions are tested with plain Python.

Slots:
    text          numbers and expressions, a comma-separated vector, text or JSON
    integer       a label
    flag          'UNSET', 'YES' or 'NO'
    choice        a choice, as text
    pos_type      'null', 'eye', 'vector', 'matrix', 'diag', 'sym', 'axes', or a choice
    first_axis, second_axis, first_vector, second_vector, reference
"""

from __future__ import annotations

import json

POSITION_TYPES = ("null", "eye", "vector", "matrix", "diag", "sym", "axes")
POSITION_LENGTHS = {"vector": 3, "matrix": 9, "diag": 3, "sym": 6}
REFERENCES = ("", "global", "node", "local", "other position", "other orientation",
              "other node")


def widget(name: str, binding: dict, default) -> str:
    """The widget that edits a property: label, expr, vector, flag, choice, text,
    position or json."""
    if name == "label":
        return "label"
    form = binding.get("form")
    if binding.get("auto"):
        return {"expr": "expr", "flag": "flag", "choice": "choice", "text": "text",
                "choice_or_expr": "expr", "position": "position"}.get(form, "json")
    if form == "value":
        return ("vector" if isinstance(default, list) else
                "json" if isinstance(default, dict) else "expr")
    if form in ("position", "node_position", "diag"):
        return "vector"
    if form in ("choice", "input_option"):
        return "choice"
    if form in ("text", "optional_text"):
        return "text"
    if form == "optional_bool":
        return "flag"
    if form == "orientation_axes":
        return "position"
    if form == "status_triplet":
        return "vector"
    return "json"


def choices(binding: dict, kind: str) -> list[str]:
    """The texts a choice or position widget offers; '' means unset."""
    if kind == "position":
        if binding.get("form") == "orientation_axes":
            return ["eye", "axes"]
        return list(POSITION_TYPES) + [str(c) for c in binding.get("choices", ())]
    unset = [""] if binding.get("optional") or binding.get("form") == "optional_text" else []
    return unset + [str(choice) for choice in binding.get("choices", ())]


def _number_text(value) -> str:
    if isinstance(value, dict) and set(value) == {"expr"}:
        return value["expr"]
    if value is None:
        return ""
    return value if isinstance(value, str) else json.dumps(value)


def _number(text: str):
    text = text.strip()
    if not text:
        return None
    try:
        value = json.loads(text)
    except ValueError:
        return {"expr": text}
    if type(value) in (int, float):
        return value
    return {"expr": text}


def split(text: str) -> list[str]:
    """Split comma-separated items, keeping the commas inside parentheses."""
    items, depth, start = [], 0, 0
    for index, char in enumerate(text):
        if char in "([":
            depth += 1
        elif char in ")]":
            depth -= 1
        elif char == "," and depth == 0:
            items.append(text[start:index].strip())
            start = index + 1
    last = text[start:].strip()
    if last or items:
        items.append(last)
    return items


def _vector_text(values) -> str:
    return ", ".join(_number_text(value) for value in values)


def _is_raw(value) -> bool:
    return isinstance(value, dict) and set(value) == {"raw"}


def to_slots(kind: str, binding: dict, value) -> dict:
    """The widget slots showing `value`."""
    if _is_raw(value) and kind != "json":
        return {"text": json.dumps(value), "raw": True}
    if kind == "label":
        return {"integer": int(value)}
    if kind == "expr":
        return {"text": _number_text(value)}
    if kind == "vector":
        if binding.get("form") == "status_triplet":
            return {"text": ", ".join(value)}
        return {"text": _vector_text(value)}
    if kind == "flag":
        return {"flag": "UNSET" if value is None else "YES" if value else "NO"}
    if kind == "choice":
        return {"choice": "" if value is None else str(value)}
    if kind == "text":
        return {"text": value or ""}
    if kind == "position":
        if binding.get("form") == "orientation_axes":
            value = {"type": value["mode"], "first_axis": value["first_axis"],
                     "first_vector": value["first_vector"], "second_axis": value["second_axis"],
                     "second_vector": value["second_vector"]}
        if value is None:
            return {"pos_type": "", "reference": ""}
        if not isinstance(value, dict):
            return {"pos_type": str(value), "reference": ""}
        slots = {"pos_type": value["type"], "reference": value.get("reference") or "",
                 "text": _vector_text(value.get("values", []))}
        if "first_axis" in value:
            second = value["second_vector"]
            slots.update(first_axis=value["first_axis"], second_axis=value["second_axis"],
                         first_vector=_vector_text(value["first_vector"]),
                         second_vector=second if second == "guess" else _vector_text(second))
        return slots
    return {"text": json.dumps(value)}


def from_slots(kind: str, binding: dict, slots: dict):
    """The value the widget slots hold."""
    if slots.get("raw") or (kind != "json" and slots.get("text", "").lstrip().startswith('{"raw"')):
        return json.loads(slots["text"])
    if kind == "label":
        return int(slots["integer"])
    if kind == "expr":
        text = slots.get("text", "")
        if binding.get("form") == "choice_or_expr" and text.strip() in [
                str(c) for c in binding.get("choices", ())]:
            return next(c for c in binding["choices"] if str(c) == text.strip())
        return _number(text)
    if kind == "vector":
        if binding.get("form") == "status_triplet":
            return split(slots.get("text", ""))
        return [_number(item) for item in split(slots.get("text", ""))]
    if kind == "flag":
        return {"UNSET": None, "YES": True, "NO": False}[slots["flag"]]
    if kind == "choice":
        text = slots.get("choice", "")
        if text == "":
            return None
        return next((c for c in binding.get("choices", ()) if str(c) == text), text)
    if kind == "text":
        text = slots.get("text", "")
        if text == "" and (binding.get("optional") or binding.get("form") == "optional_text"):
            return None
        return text
    if kind == "position":
        kind_ = slots.get("pos_type", "")
        if kind_ == "":
            return None
        if kind_ not in POSITION_TYPES:
            return next((c for c in binding.get("choices", ()) if str(c) == kind_), kind_)
        value: dict = {"type": kind_}
        if kind_ in POSITION_LENGTHS:
            value["values"] = [_number(item) for item in split(slots.get("text", ""))]
        if kind_ == "axes" or binding.get("form") == "orientation_axes":
            second = slots.get("second_vector", "").strip()
            value.update(first_axis=int(slots.get("first_axis", 1)),
                         first_vector=[_number(item) for item in
                                       split(slots.get("first_vector", ""))],
                         second_axis=int(slots.get("second_axis", 2)),
                         second_vector=second if second == "guess" else
                         [_number(item) for item in split(second)])
        if binding.get("form") == "orientation_axes":
            return {"mode": kind_, "first_axis": value["first_axis"],
                    "first_vector": value["first_vector"], "second_axis": value["second_axis"],
                    "second_vector": value["second_vector"]}
        if slots.get("reference"):
            value["reference"] = slots["reference"]
        return value
    text = slots.get("text", "").strip()
    return json.loads(text) if text else None
