""" Tests for the unicodedata module.

    Written by Marc-Andre Lemburg (mal@lemburg.com).

    (c) Copyright CNRI, All Rights Reserved. NO WARRANTY.

"""

# stdlib
import hashlib
import sys
import unicodedata
import unittest
from http.client import HTTPException
from test.support import cpython_only, open_urlresource, requires_resource, script_helper


class UnicodeMethodsTest(unittest.TestCase):

	# update this, if the database changes
	expectedchecksum = "fbdf8106a3c7c242086b0a9efa03ad4d30d5b85d"

	@unittest.expectedFailure
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
		self.assertEqual(result, self.expectedchecksum)


class UnicodeDatabaseTest(unittest.TestCase):
	db = unicodedata


class UnicodeFunctionsTest(UnicodeDatabaseTest):

	# Update this if the database changes. Make sure to do a full rebuild
	# (e.g. 'make distclean && make') to get the correct checksum.
	expectedchecksum = "d1e37a2854df60ac607b47b51189b9bf1b54bfdb"

	@unittest.expectedFailure
	@requires_resource("cpu")
	def test_function_checksum(self):
		h = hashlib.sha1()  # nosec: B303

		for i in range(sys.maxunicode + 1):
			char = chr(i)
			data = [
					# Properties
					format(self.db.digit(char, -1), ".12g"),
					format(self.db.numeric(char, -1), ".12g"),
					format(self.db.decimal(char, -1), ".12g"),
					self.db.category(char),
					self.db.bidirectional(char),
					self.db.decomposition(char),
					str(self.db.mirrored(char)),
					str(self.db.combining(char)),
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

	def test_category(self):
		self.assertEqual(self.db.category('\ufffe'), "Cn")
		self.assertEqual(self.db.category('a'), "Ll")
		self.assertEqual(self.db.category('A'), "Lu")
		self.assertEqual(self.db.category('𠀀'), "Lo")
		self.assertEqual(self.db.category('𐄪'), "No")

		self.assertRaises(TypeError, self.db.category)
		self.assertRaises(TypeError, self.db.category, "xx")

	def test_bidirectional(self):
		self.assertEqual(self.db.bidirectional('\ufffe'), '')
		self.assertEqual(self.db.bidirectional(' '), "WS")
		self.assertEqual(self.db.bidirectional('A'), 'L')
		self.assertEqual(self.db.bidirectional('𠀀'), 'L')

		self.assertRaises(TypeError, self.db.bidirectional)
		self.assertRaises(TypeError, self.db.bidirectional, "xx")

	def test_decomposition(self):
		self.assertEqual(self.db.decomposition('\ufffe'), '')
		self.assertEqual(self.db.decomposition('¼'), "<fraction> 0031 2044 0034")

		self.assertRaises(TypeError, self.db.decomposition)
		self.assertRaises(TypeError, self.db.decomposition, "xx")

	def test_mirrored(self):
		self.assertEqual(self.db.mirrored('\ufffe'), 0)
		self.assertEqual(self.db.mirrored('a'), 0)
		self.assertEqual(self.db.mirrored('∁'), 1)
		self.assertEqual(self.db.mirrored('𠀀'), 0)

		self.assertRaises(TypeError, self.db.mirrored)
		self.assertRaises(TypeError, self.db.mirrored, "xx")

	def test_combining(self):
		self.assertEqual(self.db.combining('\ufffe'), 0)
		self.assertEqual(self.db.combining('a'), 0)
		self.assertEqual(self.db.combining('⃡'), 230)
		self.assertEqual(self.db.combining('𠀀'), 0)

		self.assertRaises(TypeError, self.db.combining)
		self.assertRaises(TypeError, self.db.combining, "xx")

	def test_pr29(self):
		# https://www.unicode.org/review/pr-29.html
		# See issues #1054943 and #10254.
		composed = ("େ̀ା", "ᄀ̀ᅡ", "Li̍t-sṳ́", "मार्क ज़" + "ुकेरबर्ग", "किर्गिज़" + "स्तान")
		for text in composed:
			self.assertEqual(self.db.normalize("NFC", text), text)

	def test_issue10254(self):
		# Crash reported in #10254
		a = "C̸" * 20 + "Ç"
		b = "C̸" * 20 + 'Ç'
		self.assertEqual(self.db.normalize("NFC", a), b)

	def test_issue29456(self):
		# Fix #29456
		u1176_str_a = "ᄀᅶᆨ"
		u1176_str_b = "ᄀᅶᆨ"
		u11a7_str_a = "기ᆧ"
		u11a7_str_b = "기ᆧ"
		u11c3_str_a = "기ᇃ"
		u11c3_str_b = "기ᇃ"
		self.assertEqual(self.db.normalize("NFC", u1176_str_a), u1176_str_b)
		self.assertEqual(self.db.normalize("NFC", u11a7_str_a), u11a7_str_b)
		self.assertEqual(self.db.normalize("NFC", u11c3_str_a), u11c3_str_b)

	def test_east_asian_width(self):
		eaw = self.db.east_asian_width
		self.assertRaises(TypeError, eaw, b'a')
		self.assertRaises(TypeError, eaw, bytearray())
		self.assertRaises(TypeError, eaw, '')
		self.assertRaises(TypeError, eaw, "ra")
		self.assertEqual(eaw('\x1e'), 'N')
		self.assertEqual(eaw(' '), "Na")
		self.assertEqual(eaw('좔'), 'W')
		self.assertEqual(eaw('ｦ'), 'H')
		self.assertEqual(eaw('？'), 'F')
		self.assertEqual(eaw('‐'), 'A')
		self.assertEqual(eaw('𠀀'), 'W')

	def test_east_asian_width_9_0_changes(self):
		self.assertEqual(self.db.ucd_3_2_0.east_asian_width('⌚'), 'N')
		self.assertEqual(self.db.east_asian_width('⌚'), 'W')


class UnicodeMiscTest(UnicodeDatabaseTest):

	@cpython_only
	def test_disallow_instantiation(self):
		# Ensure that the type disallows instantiation (bpo-43916)
		self.assertRaises(TypeError, unicodedata.UCD)

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

	def test_bug_1704793(self):
		self.assertEqual(self.db.lookup("GOTHIC LETTER FAIHU"), '𐍆')

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


class NormalizationTest(unittest.TestCase):

	@staticmethod
	def check_version(testfile):
		hdr = testfile.readline()
		return unicodedata.unidata_version in hdr

	@staticmethod
	def unistr(data):
		data = [int(x, 16) for x in data.split(' ')]
		return ''.join([chr(x) for x in data])

	@requires_resource("network")
	def test_normalization(self):
		TESTDATAFILE = "NormalizationTest.txt"
		TESTDATAURL = f"http://www.pythontest.net/unicode/{unicodedata.unidata_version}/{TESTDATAFILE}"

		# Hit the exception early
		try:
			testdata = open_urlresource(TESTDATAURL, encoding="utf-8", check=self.check_version)
		except PermissionError:
			self.skipTest(f"Permission error when downloading {TESTDATAURL} " f"into the test data directory")
		except (OSError, HTTPException):
			self.fail(f"Could not retrieve {TESTDATAURL}")

		with testdata:
			self.run_normalization_tests(testdata)

	def run_normalization_tests(self, testdata):
		part = None
		part1_data = {}

		def NFC(str):
			return unicodedata.normalize("NFC", str)

		def NFKC(str):
			return unicodedata.normalize("NFKC", str)

		def NFD(str):
			return unicodedata.normalize("NFD", str)

		def NFKD(str):
			return unicodedata.normalize("NFKD", str)

		for line in testdata:
			if '#' in line:
				line = line.split('#')[0]
			line = line.strip()
			if not line:
				continue
			if line.startswith("@Part"):
				part = line.split()[0]
				continue
			c1, c2, c3, c4, c5 = [self.unistr(x) for x in line.split(';')[:-1]]

			# Perform tests
			self.assertTrue(c2 == NFC(c1) == NFC(c2) == NFC(c3), line)
			self.assertTrue(c4 == NFC(c4) == NFC(c5), line)
			self.assertTrue(c3 == NFD(c1) == NFD(c2) == NFD(c3), line)
			self.assertTrue(c5 == NFD(c4) == NFD(c5), line)
			self.assertTrue(c4 == NFKC(c1) == NFKC(c2) == NFKC(c3) == NFKC(c4) == NFKC(c5), line)
			self.assertTrue(c5 == NFKD(c1) == NFKD(c2) == NFKD(c3) == NFKD(c4) == NFKD(c5), line)

			self.assertTrue(unicodedata.is_normalized("NFC", c2))
			self.assertTrue(unicodedata.is_normalized("NFC", c4))

			self.assertTrue(unicodedata.is_normalized("NFD", c3))
			self.assertTrue(unicodedata.is_normalized("NFD", c5))

			self.assertTrue(unicodedata.is_normalized("NFKC", c4))
			self.assertTrue(unicodedata.is_normalized("NFKD", c5))

			# Record part 1 data
			if part == "@Part1":
				part1_data[c1] = 1

		# Perform tests for all other data
		for c in range(sys.maxunicode + 1):
			X = chr(c)
			if X in part1_data:
				continue
			self.assertTrue(X == NFC(X) == NFD(X) == NFKC(X) == NFKD(X), c)

	def test_edge_cases(self):
		self.assertRaises(TypeError, unicodedata.normalize)
		self.assertRaises(ValueError, unicodedata.normalize, "unknown", "xx")
		self.assertEqual(unicodedata.normalize("NFKC", ''), '')

	def test_bug_834676(self):
		# Check for bug 834676
		unicodedata.normalize("NFC", "한글")


if __name__ == "__main__":
	unittest.main()
