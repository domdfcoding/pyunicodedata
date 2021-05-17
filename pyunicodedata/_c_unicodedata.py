#!/usr/bin/env python3
#
#  _c_unicode.py
"""
Parts of unicodedata based on CPython C source code.
"""
#
#  Based on CPython.
#  Licensed under the Python Software Foundation License Version 2.
#  Copyright © 2001-2020 Python Software Foundation. All rights reserved.
#  Copyright © 2000 BeOpen.com. All rights reserved.
#  Copyright © 1995-2000 Corporation for National Research Initiatives. All rights reserved.
#  Copyright © 1991-1995 Stichting Mathematisch Centrum. All rights reserved.
#
#  See the LICENSE file for details.
#

# this package
from ._unicode_numeric import numeric_items
from ._unicodetype_db import data
from ._unicodetype_index import index

ALPHA_MASK = 0x01
DECIMAL_MASK = 0x02
DIGIT_MASK = 0x04
LOWER_MASK = 0x08
LINEBREAK_MASK = 0x10
SPACE_MASK = 0x20
TITLE_MASK = 0x40
UPPER_MASK = 0x80
XID_START_MASK = 0x100
XID_CONTINUE_MASK = 0x200
PRINTABLE_MASK = 0x400
NUMERIC_MASK = 0x800
CASE_IGNORABLE_MASK = 0x1000
CASED_MASK = 0x2000
EXTENDED_CASE_MASK = 0x4000


def _PyUnicode_IsTitlecase(ch):
	"""
	Returns 1 for Unicode characters having the category 'Lt', 0 otherwise.

	:param ch:
	:return:
	"""

	record = data[index[ord(ch)]]
	upper, lower, title, decimal, digit, flags = record
	return flags & TITLE_MASK != 0


def _PyUnicode_IsXidStart(ch):
	"""
	Returns 1 for Unicode characters having the XID_Start property, 0 otherwise.

	:param ch:
	:return:
	"""

	record = data[index[ord(ch)]]
	upper, lower, title, decimal, digit, flags = record
	return flags & XID_START_MASK != 0


def _PyUnicode_IsXidContinue(ch):
	"""
	Returns 1 for Unicode characters having the XID_Continue property, 0 otherwise.

	:param ch:
	:return:
	"""

	record = data[index[ord(ch)]]
	upper, lower, title, decimal, digit, flags = record

	return flags & XID_CONTINUE_MASK != 0


def _PyUnicode_ToDecimalDigit(ch):
	"""
	Returns the integer decimal (0-9) for Unicode characters having this property, -1 otherwise.

	:param ch:
	:return:
	"""

	record = data[index[ord(ch)]]
	upper, lower, title, decimal, digit, flags = record

	if flags & DECIMAL_MASK:
		return decimal
	else:
		return -1


def _PyUnicode_IsDecimalDigit(ch):
	"""

	:param ch:
	:return:
	"""

	if _PyUnicode_ToDecimalDigit(ch) < 0:
		return 0
	return 1


def _PyUnicode_ToDigit(ch):
	"""
	Returns the integer digit (0-9) for Unicode characters having this property, -1 otherwise

	:param ch:
	:return:
	"""

	record = data[index[ord(ch)]]
	upper, lower, title, decimal, digit, flags = record

	if flags & DIGIT_MASK:
		return digit
	else:
		return -1


def _PyUnicode_IsDigit(ch):
	"""

	:param ch:
	:return:
	"""

	if _PyUnicode_ToDigit(ch) < 0:
		return 0
	return 1


def _PyUnicode_IsNumeric(ch):
	"""
	Returns the numeric value as double for Unicode characters having this property, -1.0 otherwise.

	:param ch:
	:return:
	"""

	record = data[index[ord(ch)]]
	upper, lower, title, decimal, digit, flags = record
	return flags & NUMERIC_MASK != 0


def _PyUnicode_ToNumeric(ch: str):
	"""
	Returns the numeric value as double for Unicode characters having this property, -1.0 otherwise.
	"""

	for value, codepoints in numeric_items.items():
		if ord(ch) in codepoints:
			return eval(value)

	return -1.0


def _PyUnicode_IsPrintable(ch):
	"""
	Returns 1 for Unicode characters to be hex-escaped when repr()ed, 0 otherwise.

	All characters except those characters defined in the Unicode character
	database as following categories are considered printable.
	  * Cc (Other, Control)
	  * Cf (Other, Format)
	  * Cs (Other, Surrogate)
	  * Co (Other, Private Use)
	  * Cn (Other, Not Assigned)
	  * Zl Separator, Line ('\u2028', LINE SEPARATOR)
	  * Zp Separator, Paragraph ('\u2029', PARAGRAPH SEPARATOR)
	  * Zs (Separator, Space) other than ASCII space('\x20').

	:param ch:
	:return:
	"""

	record = data[index[ord(ch)]]
	upper, lower, title, decimal, digit, flags = record
	return flags & PRINTABLE_MASK != 0


def _PyUnicode_IsLowercase(ch):
	"""
	Returns 1 for Unicode characters having the category 'Ll', 0 otherwise.

	:param ch:
	:return:
	"""

	record = data[index[ord(ch)]]
	upper, lower, title, decimal, digit, flags = record
	return flags & LOWER_MASK != 0


def _PyUnicode_IsUppercase(ch):
	"""
	Returns 1 for Unicode characters having the category 'Lu', 0 otherwise.

	:param ch:
	:return:
	"""

	record = data[index[ord(ch)]]
	upper, lower, title, decimal, digit, flags = record
	return flags & UPPER_MASK != 0


# def Py_UNICODE_ISSPACE(ch):
# 	if ord(ch) < 128:
# 		return _Py_ascii_whitespace[ch]
# 	return _PyUnicode_IsWhitespace(ch)

Py_UNICODE_ISLOWER = _PyUnicode_IsLowercase
Py_UNICODE_ISUPPER = _PyUnicode_IsUppercase
Py_UNICODE_ISTITLE = _PyUnicode_IsTitlecase
# Py_UNICODE_ISLINEBREAK = _PyUnicode_IsLinebreak

# Py_UNICODE_TOLOWER = _PyUnicode_ToLowercase
# Py_UNICODE_TOUPPER = _PyUnicode_ToUppercase
# Py_UNICODE_TOTITLE = _PyUnicode_ToTitlecase

Py_UNICODE_ISDECIMAL = _PyUnicode_IsDecimalDigit
Py_UNICODE_ISDIGIT = _PyUnicode_IsDigit
Py_UNICODE_ISNUMERIC = _PyUnicode_IsNumeric
Py_UNICODE_ISPRINTABLE = _PyUnicode_IsPrintable

Py_UNICODE_TODECIMAL = _PyUnicode_ToDecimalDigit
Py_UNICODE_TODIGIT = _PyUnicode_ToDigit
Py_UNICODE_TONUMERIC = _PyUnicode_ToNumeric
