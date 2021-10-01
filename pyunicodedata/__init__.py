#!/usr/bin/env python3
#
#  __init__.py
"""
Pure-python implementation of some unicodedata functions.
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

# stdlib
import unicodedata

# this package
from pyunicodedata._c_unicodedata import Py_UNICODE_TODECIMAL, Py_UNICODE_TODIGIT, Py_UNICODE_TONUMERIC

__author__: str = "Dominic Davis-Foster"
__license__: str = "PSF"
__version__: str = "0.0.0"
__email__: str = "dominic@davis-foster.co.uk"

__all__ = ["decimal", "digit", "numeric"]

MISSING = object()


def decimal(chr: str, default=MISSING):  # noqa: A002  # pylint: disable=redefined-builtin
	"""
	Returns the decimal value assigned to the character chr as integer.

	If no such value is defined, default is returned, or, if not given, ValueError is raised.

	:param chr:
	:param default:
	"""

	# TODO: get_old_record

	rc: int = Py_UNICODE_TODECIMAL(chr)
	if rc < 0:
		if default is MISSING:
			raise ValueError("not a decimal")
		else:
			return default

	return rc


def digit(chr: str, default=MISSING):  # noqa: A002  # pylint: disable=redefined-builtin
	"""
	Returns the digit value assigned to the character chr as integer.

	If no such value is defined, default is returned, or, if not given, ValueError is raised.

	:param chr:
	:param default:
	"""

	rc: int = Py_UNICODE_TODIGIT(chr)
	if rc < 0:
		if default is MISSING:
			raise ValueError("not a digit")
		else:
			return default

	return rc


def numeric(chr: str, default=MISSING):  # noqa: A002  # pylint: disable=redefined-builtin
	"""
	Returns the numeric value assigned to the character chr as float.

	If no such value is defined, default is returned, or, if not given, ValueError is raised.

	:param chr:
	:param default:
	"""

	# TODO: get_old_record

	rc: float = Py_UNICODE_TONUMERIC(chr)
	if rc == -1.0:
		if default is MISSING:
			raise ValueError("not a numeric character")
		else:
			return default

	return rc


# combining
# east asian width
# mirrored
# decomposition
# is_normalized


def install_patch():
	if not hasattr(unicodedata, "decimal"):
		unicodedata.decimal = decimal

	if not hasattr(unicodedata, "digit"):
		unicodedata.digit = digit

	if not hasattr(unicodedata, "numeric"):
		unicodedata.numeric = numeric
