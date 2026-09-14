"""
Compatibility custom node pack providing core string and primitive nodes introduced
in newer ComfyUI (v0.3.x+) for older base images.
Includes: StringConcatenate, RegexReplace, PrimitiveBoolean, PrimitiveFloat, PrimitiveInt,
PrimitiveString, StringCompare, StringContains, StringLength.
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
}

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]
