"""
Compatibility custom node pack providing core string and primitive nodes introduced
in newer ComfyUI (v0.3.x+) for older base images.
Includes: StringConcatenate, RegexReplace, PrimitiveBoolean, PrimitiveFloat, PrimitiveInt,
PrimitiveString, StringCompare, StringContains, StringLength, WidgetToString.
"""

import re


class StringConcatenate:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "string_a": ("STRING", {"default": "", "multiline": True}),
                "string_b": ("STRING", {"default": "", "multiline": True}),
                "delimiter": ("STRING", {"default": "", "multiline": False}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("STRING",)
    FUNCTION = "concatenate"
    CATEGORY = "utils"

    def concatenate(self, string_a="", string_b="", delimiter=""):
        str_a = "" if string_a is None else str(string_a)
        str_b = "" if string_b is None else str(string_b)
        delim = "" if delimiter is None else str(delimiter)
        return (f"{str_a}{delim}{str_b}",)


class RegexReplace:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "string": ("STRING", {"default": "", "multiline": True}),
                "regex_pattern": ("STRING", {"default": ""}),
                "replace": ("STRING", {"default": ""}),
                "case_insensitive": ("BOOLEAN", {"default": True}),
                "multiline": ("BOOLEAN", {"default": False}),
                "dotall": ("BOOLEAN", {"default": False}),
                "count": ("INT", {"default": 0, "min": 0, "max": 100000}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("STRING",)
    FUNCTION = "regex_replace"
    CATEGORY = "utils"

    def regex_replace(
        self,
        string="",
        regex_pattern="",
        replace="",
        case_insensitive=True,
        multiline=False,
        dotall=False,
        count=0,
    ):
        if not string:
            return ("",)
        if not regex_pattern:
            return (string,)

        flags = 0
        if case_insensitive:
            flags |= re.IGNORECASE
        if multiline:
            flags |= re.MULTILINE
        if dotall:
            flags |= re.DOTALL

        try:
            result = re.sub(regex_pattern, replace, string, count=count, flags=flags)
        except Exception:
            result = string
        return (result,)


class PrimitiveBoolean:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "value": ("BOOLEAN", {"default": False}),
            }
        }

    RETURN_TYPES = ("BOOLEAN",)
    RETURN_NAMES = ("BOOLEAN",)
    FUNCTION = "get_value"
    CATEGORY = "utils"

    def get_value(self, value=False):
        return (bool(value),)


class PrimitiveFloat:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "value": (
                    "FLOAT",
                    {"default": 0.0, "min": -1000000.0, "max": 1000000.0, "step": 0.01},
                ),
            }
        }

    RETURN_TYPES = ("FLOAT",)
    RETURN_NAMES = ("FLOAT",)
    FUNCTION = "get_value"
    CATEGORY = "utils"

    def get_value(self, value=0.0):
        return (float(value),)


class PrimitiveInt:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "value": (
                    "INT",
                    {"default": 0, "min": -1000000, "max": 1000000, "step": 1},
                ),
            }
        }

    RETURN_TYPES = ("INT",)
    RETURN_NAMES = ("INT",)
    FUNCTION = "get_value"
    CATEGORY = "utils"

    def get_value(self, value=0):
        return (int(value),)


class PrimitiveString:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "value": ("STRING", {"default": "", "multiline": True}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("STRING",)
    FUNCTION = "get_value"
    CATEGORY = "utils"

    def get_value(self, value=""):
        return (str(value),)


class StringCompare:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "string_a": ("STRING", {"default": "", "multiline": True}),
                "string_b": ("STRING", {"default": "", "multiline": True}),
                "case_sensitive": ("BOOLEAN", {"default": True}),
            }
        }

    RETURN_TYPES = ("BOOLEAN",)
    RETURN_NAMES = ("BOOLEAN",)
    FUNCTION = "compare"
    CATEGORY = "utils"

    def compare(self, string_a="", string_b="", case_sensitive=True):
        if not case_sensitive:
            return (str(string_a).lower() == str(string_b).lower(),)
        return (str(string_a) == str(string_b),)


class StringContains:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "string": ("STRING", {"default": "", "multiline": True}),
                "substring": ("STRING", {"default": ""}),
                "case_sensitive": ("BOOLEAN", {"default": True}),
            }
        }

    RETURN_TYPES = ("BOOLEAN",)
    RETURN_NAMES = ("BOOLEAN",)
    FUNCTION = "contains"
    CATEGORY = "utils"

    def contains(self, string="", substring="", case_sensitive=True):
        if not case_sensitive:
            return (str(substring).lower() in str(string).lower(),)
        return (str(substring) in str(string),)


class StringLength:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "string": ("STRING", {"default": "", "multiline": True}),
            }
        }

    RETURN_TYPES = ("INT",)
    RETURN_NAMES = ("INT",)
    FUNCTION = "length"
    CATEGORY = "utils"

    def length(self, string=""):
        return (len(str(string)),)


class WidgetToString:
    """Reads a widget value from another node and returns it as a STRING.

    Originally provided by comfyui-custom-scripts; this shim preserves
    compatibility with workflows that reference the node.

    The ``prompt`` hidden input contains the full workflow graph at execution
    time, keyed by node id (string).  Each node entry has an ``inputs`` dict
    whose keys are widget / input names.  We look up the requested node and
    widget name, then format the value as a string.
    """

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "id": ("INT", {"default": 0, "min": 0, "max": 0x7FFFFFFF}),
                "widget_name": ("STRING", {"default": ""}),
                "return_all": ("BOOLEAN", {"default": False}),
            },
            "optional": {
                "node_title": ("STRING", {"default": ""}),
                "allowed_float_decimals": (
                    "INT",
                    {"default": 2, "min": 0, "max": 10},
                ),
            },
            "hidden": {
                "prompt": "PROMPT",
                "extra_pnginfo": "EXTRA_PNGINFO",
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("STRING",)
    OUTPUT_IS_LIST = (True,)
    FUNCTION = "get_widget_value"
    CATEGORY = "utils"

    def get_widget_value(
        self,
        id,
        widget_name,
        return_all=False,
        node_title="",
        allowed_float_decimals=2,
        prompt=None,
        extra_pnginfo=None,
    ):
        if prompt is None:
            return (["<prompt unavailable>"],)

        # ``id`` is an int but prompt keys are strings
        node_data = prompt.get(str(id))
        if node_data is None:
            return ([f"<node {id} not found>"],)

        inputs = node_data.get("inputs", {})

        if return_all:
            # Return every widget value as a comma-separated string
            values = []
            for k, v in inputs.items():
                if isinstance(v, list) and len(v) == 2 and isinstance(v[0], str):
                    # This is a linked input (node_id, slot) — skip it
                    continue
                values.append(self._format(v, allowed_float_decimals))
            return (values if values else [""],)

        value = inputs.get(widget_name)
        if value is None:
            return ([f"<widget '{widget_name}' not found in node {id}>"],)

        return ([self._format(value, allowed_float_decimals)],)

    @staticmethod
    def _format(value, decimals):
        if isinstance(value, float):
            return f"{value:.{decimals}f}"
        return str(value)


NODE_CLASS_MAPPINGS = {
    "StringConcatenate": StringConcatenate,
    "RegexReplace": RegexReplace,
    "PrimitiveBoolean": PrimitiveBoolean,
    "PrimitiveFloat": PrimitiveFloat,
    "PrimitiveInt": PrimitiveInt,
    "PrimitiveString": PrimitiveString,
    "StringCompare": StringCompare,
    "StringContains": StringContains,
    "StringLength": StringLength,
    "WidgetToString": WidgetToString,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "StringConcatenate": "Concatenate (String)",
    "RegexReplace": "Regex Replace",
    "PrimitiveBoolean": "Primitive Boolean",
    "PrimitiveFloat": "Primitive Float",
    "PrimitiveInt": "Primitive Int",
    "PrimitiveString": "Primitive String",
    "StringCompare": "String Compare",
    "StringContains": "String Contains",
    "StringLength": "String Length",
    "WidgetToString": "Widget To String",
}

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]
