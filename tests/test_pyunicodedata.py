""" Tests for the unicodedata module.

	Written by Marc-Andre Lemburg (mal@lemburg.com).

	(c) Copyright CNRI, All Rights Reserved. NO WARRANTY.

"""

# stdlib
import hashlib
import sys
import unicodedata
import unittest
from test.support import requires_resource, script_helper  # type: ignore[import]

# this package
import pyunicodedata


class UnicodeMethodsTest(unittest.TestCase):

	@requires_resource("cpu")
	def test_method_checksum(self):
		h = hashlib.sha1()  # nosec: B303
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

		if sys.version_info[:2] == (3, 8):
			self.assertEqual(result, "e728278035eb76cf92d86f07852266b0433f16a5")
		elif sys.version_info[:2] == (3, 11):
			self.assertEqual(result, "4739770dd4d0e5f1b1677accfc3552ed3c8ef326")
		elif sys.version_info[:2] == (3, 12):
			self.assertEqual(result, "e708c31c0d51f758adf475cb7201cf80917362be")
		elif sys.version_info[:2] >= (3, 13):
			# Update this from CPython if the database changes.
			self.assertEqual(result, "63aa77dcb36b0e1df082ee2a6071caeda7f0955e")
		elif sys.version_info[:2] >= (3, 9):
			self.assertEqual(result, "fbdf8106a3c7c242086b0a9efa03ad4d30d5b85d")


class UnicodeFunctionsTest(unittest.TestCase):

	@requires_resource("cpu")
	def test_function_checksum(self):
		h = hashlib.sha1()  # nosec: B303

		for i in range(sys.maxunicode + 1):
			char = chr(i)
			data = [
					# Properties
					format(pyunicodedata.digit(char, -1), ".12g"),
					format(pyunicodedata.numeric(char, -1), ".12g"),
					format(pyunicodedata.decimal(char, -1), ".12g"),
					unicodedata.category(char),
					unicodedata.bidirectional(char),
					unicodedata.decomposition(char),
					str(unicodedata.mirrored(char)),
					str(unicodedata.combining(char)),
					]
			h.update(''.join(data).encode("ascii"))
		result = h.hexdigest()

		if sys.version_info[:2] == (3, 8):
			self.assertEqual(result, "417249d799929ac756bac3faf9d5601bea36df57")
		elif sys.version_info[:2] == (3, 11):
			self.assertEqual(result, "63bc6ce2f302c7fcfc20c381f2790b550b92a870")
		elif sys.version_info[:2] == (3, 12):
			self.assertEqual(result, "e2b4d9c97d5f05a8bc8d50550145b5142354efc8")
		elif sys.version_info[:2] >= (3, 13):
			# Update this from CPython if the database changes.
			self.assertEqual(result, "53dc045369330865087e35f4808496ee84423e92")
		elif sys.version_info[:2] >= (3, 9):
			self.assertEqual(result, "d1e37a2854df60ac607b47b51189b9bf1b54bfdb")

	def test_digit(self):
		self.assertEqual(pyunicodedata.digit('A', None), None)
		self.assertEqual(pyunicodedata.digit('9'), 9)
		self.assertEqual(pyunicodedata.digit('⅛', None), None)
		self.assertEqual(pyunicodedata.digit('⑨'), 9)
		self.assertEqual(pyunicodedata.digit('𠀀', None), None)
		self.assertEqual(pyunicodedata.digit('𝟽'), 7)

		self.assertRaises(TypeError, pyunicodedata.digit)
		self.assertRaises(TypeError, pyunicodedata.digit, "xx")
		self.assertRaises(ValueError, pyunicodedata.digit, 'x')

	def test_numeric(self):
		self.assertEqual(pyunicodedata.numeric('A', None), None)
		self.assertEqual(pyunicodedata.numeric('9'), 9)
		self.assertEqual(pyunicodedata.numeric('⅛'), 0.125)
		self.assertEqual(pyunicodedata.numeric('⑨'), 9.0)
		self.assertEqual(pyunicodedata.numeric('꘧'), 7.0)
		self.assertEqual(pyunicodedata.numeric('𠀀', None), None)
		self.assertEqual(pyunicodedata.numeric('𐄪'), 9000)

		self.assertRaises(TypeError, pyunicodedata.numeric)
		self.assertRaises(TypeError, pyunicodedata.numeric, "xx")
		self.assertRaises(ValueError, pyunicodedata.numeric, 'x')

	def test_decimal(self):
		self.assertEqual(pyunicodedata.decimal('A', None), None)
		self.assertEqual(pyunicodedata.decimal('9'), 9)
		self.assertEqual(pyunicodedata.decimal('⅛', None), None)
		self.assertEqual(pyunicodedata.decimal('⑨', None), None)
		self.assertEqual(pyunicodedata.decimal('𠀀', None), None)
		self.assertEqual(pyunicodedata.decimal('𝟽'), 7)

		self.assertRaises(TypeError, pyunicodedata.decimal)
		self.assertRaises(TypeError, pyunicodedata.decimal, "xx")
		self.assertRaises(ValueError, pyunicodedata.decimal, 'x')


class UnicodeMiscTest(unittest.TestCase):

	def test_failed_import_during_compiling(self):
		# Issue 4367
		# Decoding \N escapes requires the unicodedata module. If it can't be
		# imported, we shouldn't segfault.

		# This program should raise a SyntaxError in the eval.
		code = "import sys;sys.modules['unicodedata'] = None;eval(\"'\\\\N{SOFT HYPHEN}'\")"
		# We use a separate process because the unicodedata module may already
		# have been loaded in this process.
		result = script_helper.assert_python_failure("-c", code)
		error = "SyntaxError: (unicode error) \\N escapes not supported (can't load unicodedata module)"
		self.assertIn(error, result.err.decode("ascii"))

	def test_decimal_numeric_consistent(self):
		# Test that decimal and numeric are consistent,
		# i.e. if a character has a decimal value,
		# its numeric value should be the same.
		count = 0
		for i in range(0x10000):
			c = chr(i)
			dec = pyunicodedata.decimal(c, -1)
			if dec != -1:
				self.assertEqual(dec, pyunicodedata.numeric(c))
				count += 1
		self.assertTrue(count >= 10)  # should have tested at least the ASCII digits

	def test_digit_numeric_consistent(self):
		# Test that digit and numeric are consistent,
		# i.e. if a character has a digit value,
		# its numeric value should be the same.
		count = 0
		for i in range(0x10000):
			c = chr(i)
			dec = pyunicodedata.digit(c, -1)
			if dec != -1:
				self.assertEqual(dec, pyunicodedata.numeric(c))
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
