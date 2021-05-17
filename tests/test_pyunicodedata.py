""" Tests for the unicodedata module.

    Written by Marc-Andre Lemburg (mal@lemburg.com).

    (c) Copyright CNRI, All Rights Reserved. NO WARRANTY.

"""

# stdlib
import hashlib
import sys
import unicodedata
import unittest
from test.support import requires_resource, script_helper

# this package
import pyunicodedata


class UnicodeMethodsTest(unittest.TestCase):

	# update this, if the database changes
	expectedchecksum = "fbdf8106a3c7c242086b0a9efa03ad4d30d5b85d"

	@unittest.expectedFailure
	@requires_resource("cpu")
	def test_method_checksum(self):
		h = hashlib.sha1()
		for i in range(sys.maxunicode + 1):
			char = chr(i)
			data = [
					# Predicates (single char)
					"01"[char.isalnum()],
					"01"[char.isalpha()],
					"01"[char.isdecimal()],
					"01"[char.isdigit()],
					"01"[char.islower()],
					"01"[char.isnumeric()],
					"01"[char.isspace()],
					"01"[char.istitle()],
					"01"[char.isupper()],

					# Predicates (multiple chars)
					"01"[(char + "abc").isalnum()],
					"01"[(char + "abc").isalpha()],
					"01"[(char + "123").isdecimal()],
					"01"[(char + "123").isdigit()],
					"01"[(char + "abc").islower()],
					"01"[(char + "123").isnumeric()],
					"01"[(char + " \t").isspace()],
					"01"[(char + "abc").istitle()],
					"01"[(char + "ABC").isupper()],

					# Mappings (single char)
					char.lower(),
					char.upper(),
					char.title(),

					# Mappings (multiple chars)
					(char + "abc").lower(),
					(char + "ABC").upper(),
					(char + "abc").title(),
					(char + "ABC").title(),
					]
			h.update(''.join(data).encode("utf-8", "surrogatepass"))
		result = h.hexdigest()
		self.assertEqual(result, self.expectedchecksum)


class UnicodeDatabaseTest(unittest.TestCase):
	db = pyunicodedata


class UnicodeFunctionsTest(UnicodeDatabaseTest):

	# Update this if the database changes. Make sure to do a full rebuild
	# (e.g. 'make distclean && make') to get the correct checksum.
	expectedchecksum = "d1e37a2854df60ac607b47b51189b9bf1b54bfdb"

	@unittest.expectedFailure
	@requires_resource("cpu")
	def test_function_checksum(self):
		h = hashlib.sha1()

		for i in range(sys.maxunicode + 1):
			char = chr(i)
			data = [
					# Properties
					format(self.db.digit(char, -1), ".12g"),
					format(self.db.numeric(char, -1), ".12g"),
					format(self.db.decimal(char, -1), ".12g"),
					unicodedata.category(char),
					unicodedata.bidirectional(char),
					unicodedata.decomposition(char),
					str(unicodedata.mirrored(char)),
					str(unicodedata.combining(char)),
					]
			h.update(''.join(data).encode("ascii"))
		result = h.hexdigest()
		self.assertEqual(result, self.expectedchecksum)

	def test_digit(self):
		self.assertEqual(self.db.digit('A', None), None)
		self.assertEqual(self.db.digit('9'), 9)
		self.assertEqual(self.db.digit('⅛', None), None)
		self.assertEqual(self.db.digit('⑨'), 9)
		self.assertEqual(self.db.digit('𠀀', None), None)
		self.assertEqual(self.db.digit('𝟽'), 7)

		self.assertRaises(TypeError, self.db.digit)
		self.assertRaises(TypeError, self.db.digit, "xx")
		self.assertRaises(ValueError, self.db.digit, 'x')

	def test_numeric(self):
		self.assertEqual(self.db.numeric('A', None), None)
		self.assertEqual(self.db.numeric('9'), 9)
		self.assertEqual(self.db.numeric('⅛'), 0.125)
		self.assertEqual(self.db.numeric('⑨'), 9.0)
		self.assertEqual(self.db.numeric('꘧'), 7.0)
		self.assertEqual(self.db.numeric('𠀀', None), None)
		self.assertEqual(self.db.numeric('𐄪'), 9000)

		self.assertRaises(TypeError, self.db.numeric)
		self.assertRaises(TypeError, self.db.numeric, "xx")
		self.assertRaises(ValueError, self.db.numeric, 'x')

	def test_decimal(self):
		self.assertEqual(self.db.decimal('A', None), None)
		self.assertEqual(self.db.decimal('9'), 9)
		self.assertEqual(self.db.decimal('⅛', None), None)
		self.assertEqual(self.db.decimal('⑨', None), None)
		self.assertEqual(self.db.decimal('𠀀', None), None)
		self.assertEqual(self.db.decimal('𝟽'), 7)

		self.assertRaises(TypeError, self.db.decimal)
		self.assertRaises(TypeError, self.db.decimal, "xx")
		self.assertRaises(ValueError, self.db.decimal, 'x')


class UnicodeMiscTest(UnicodeDatabaseTest):

	def test_failed_import_during_compiling(self):
		# Issue 4367
		# Decoding \N escapes requires the unicodedata module. If it can't be
		# imported, we shouldn't segfault.

		# This program should raise a SyntaxError in the eval.
		code = "import sys;" \
            "sys.modules['unicodedata'] = None;" \
            """eval("'\\\\N{SOFT HYPHEN}'")"""
		# We use a separate process because the unicodedata module may already
		# have been loaded in this process.
		result = script_helper.assert_python_failure("-c", code)
		error = "SyntaxError: (unicode error) \\N escapes not supported " \
            "(can't load unicodedata module)"
		self.assertIn(error, result.err.decode("ascii"))

	def test_decimal_numeric_consistent(self):
		# Test that decimal and numeric are consistent,
		# i.e. if a character has a decimal value,
		# its numeric value should be the same.
		count = 0
		for i in range(0x10000):
			c = chr(i)
			dec = self.db.decimal(c, -1)
			if dec != -1:
				self.assertEqual(dec, self.db.numeric(c))
				count += 1
		self.assertTrue(count >= 10)  # should have tested at least the ASCII digits

	def test_digit_numeric_consistent(self):
		# Test that digit and numeric are consistent,
		# i.e. if a character has a digit value,
		# its numeric value should be the same.
		count = 0
		for i in range(0x10000):
			c = chr(i)
			dec = self.db.digit(c, -1)
			if dec != -1:
				self.assertEqual(dec, self.db.numeric(c))
				count += 1
		self.assertTrue(count >= 10)  # should have tested at least the ASCII digits

	def test_ucd_510(self):
		# stdlib
		import unicodedata

		# In UCD 5.1.0, a mirrored property changed wrt. UCD 3.2.0
		self.assertTrue(unicodedata.mirrored('༺'))
		self.assertTrue(not unicodedata.ucd_3_2_0.mirrored('༺'))
		# Also, we now have two ways of representing
		# the upper-case mapping: as delta, or as absolute value
		self.assertTrue('a'.upper() == 'A')
		self.assertTrue('ᵹ'.upper() == 'Ᵹ')
		self.assertTrue('.'.upper() == '.')

	def test_bug_5828(self):
		self.assertEqual('ᵹ'.lower(), 'ᵹ')
		# Only U+0000 should have U+0000 as its upper/lower/titlecase variant
		self.assertEqual([
				c for c in range(sys.maxunicode + 1) if '\x00' in chr(c).lower() + chr(c).upper() + chr(c).title()
				], [0])

	def test_bug_4971(self):
		# LETTER DZ WITH CARON: DZ, Dz, dz
		self.assertEqual('Ǆ'.title(), 'ǅ')
		self.assertEqual('ǅ'.title(), 'ǅ')
		self.assertEqual('ǆ'.title(), 'ǅ')

	def test_linebreak_7643(self):
		for i in range(0x10000):
			lines = (chr(i) + 'A').splitlines()
			if i in (0x0a, 0x0b, 0x0c, 0x0d, 0x85, 0x1c, 0x1d, 0x1e, 0x2028, 0x2029):
				self.assertEqual(len(lines), 2, r"\u%.4x should be a linebreak" % i)
			else:
				self.assertEqual(len(lines), 1, r"\u%.4x should not be a linebreak" % i)


if __name__ == "__main__":
	unittest.main()
