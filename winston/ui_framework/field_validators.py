""" predefined form field validators
"""
from collections.abc import Iterable

import os
from typing import Any
from typing import List
from typing import NamedTuple
from typing import Union
from .sentinals import unknown
from .sentinals import Unknown


class Validation(NamedTuple):
    """the response from a validation"""

    value: Any
    error_msg: str


class FieldValidators:
    """a box in which validators are put"""

    @staticmethod
    def all_true(response: List = [], hint: bool = False) -> Union[Validation, str]:
        # pylint: disable=dangerous-default-value
        """validate all in list are true"""
        msg = "Please ensure all values are true"
        if hint:
            return msg
        value = response
        if all(v is True for v in value):
            msg = ""
        return Validation(value=value, error_msg=msg)

    @staticmethod
    def file_path(text: str = "", hint=False) -> Union[Validation, str]:
        """validate that a file path is a real file"""
        msg = "Please enter a valid file path"
        if hint:
            return msg
        value = os.path.abspath(os.path.expanduser(text))
        if os.path.exists(value) and os.path.isfile(value):
            msg = ""
        else:
            value = text
        return Validation(value=value, error_msg=msg)

    @staticmethod
    def one_of(choices: List = [], text: str = "", hint: bool = False) -> Union[Validation, str]:
        # pylint: disable=dangerous-default-value
        """validate that some text is one of choices"""
        if choices:
            choices_str = f"{', '.join(choices[:-1])} or {choices[-1]}"
        else:
            choices_str = ""
        msg = f"Please enter {choices_str}"
        value = text
        if hint:
            return msg
        try:
            value = choices[[c.lower() for c in choices].index(text.lower())]
            msg = ""
        except ValueError:
            pass
        return Validation(value=value, error_msg=msg)

    @staticmethod
    def none(text="", hint: bool = False) -> Union[Validation, str]:
        """no validation"""
        if hint:
            return "Please provide a value (optional)"
        return Validation(value=text, error_msg="")

    @staticmethod
    def some_of_or_none(
        choices: Union[Unknown, List] = unknown,
        min_selected: Union[Unknown, int] = unknown,
        max_selected: Union[Unknown, int] = unknown,
        hint: bool = False,
    ) -> Union[Validation, str]:
        """validation for a checkbox"""
        if min_selected == max_selected:
            word = "entry" if min_selected == 1 else "entries"
            msg = f"Please select {str(min_selected)} {word}"
        else:
            msg = f"Please select between {min_selected} and "
            word = str(max_selected) if max_selected != -1 else "all"
            msg += f"{word} entries"

        if hint:
            return msg
        if (
            isinstance(min_selected, int)
            and isinstance(max_selected, int)
            and isinstance(choices, Iterable)
        ):
            checked = len([choice for choice in choices if choice.checked])
            if max_selected >= checked >= min_selected:
                msg = ""

            return Validation(value=choices, error_msg=msg)
        raise TypeError

    @staticmethod
    def something(text: str = "", hint: bool = False) -> Union[Validation, str]:
        """validate that the text is not an empty string"""
        msg = "Please provide a value (required)"
        if hint:
            return msg
        if text:
            msg = ""
        return Validation(value=text, error_msg=msg)

    @staticmethod
    def yes_no(text: str = "", hint: bool = False) -> Union[Validation, str]:
        """yes or no"""
        msg = "Please enter yes or no"
        value = text
        if hint:
            return msg
        if text:
            if text[0] == "y":
                value = "yes"
                msg = ""
            elif text[0] == "n":
                value = "no"
                msg = ""
        return Validation(value=value, error_msg=msg)

    @staticmethod
    def true_false(text: str = "", hint: bool = False) -> Union[Validation, str]:
        """true or false"""
        msg = "Please enter true or false"
        if hint:
            return msg
        if text:
            if text[0].lower() == "t":
                value = True
                msg = ""
                return Validation(value=value, error_msg=msg)

            if text[0].lower() == "f":
                value = False
                msg = ""
                return Validation(value=value, error_msg=msg)
        return Validation(value=text, error_msg=msg)
