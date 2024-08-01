""" Tests for the unicodedata module.

	Written by Marc-Andre Lemburg (mal@lemburg.com).

	(c) Copyright CNRI, All Rights Reserved. NO WARRANTY.

"""

# stdlib
import hashlib
import sys
import test.support  # type: ignore[import]
import unicodedata
import unittest
import urllib.parse
import urllib.request
from http.client import HTTPException

# 3rd party
from domdf_python_tools.paths import TemporaryPathPlus


class UnicodeMethodsTest(unittest.TestCase):

	@test.support.requires_resource("cpu")
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

	@test.support.requires_resource("cpu")
	def test_function_checksum(self):
		h = hashlib.sha1()  # nosec: B303

		for i in range(sys.maxunicode + 1):
			char = chr(i)
			data = [
					# Properties
					format(unicodedata.digit(char, -1), ".12g"),
					format(unicodedata.numeric(char, -1), ".12g"),
					format(unicodedata.decimal(char, -1), ".12g"),
					unicodedata.category(char),
					unicodedata.bidirectional(char),
					unicodedata.decomposition(char),
					str(unicodedata.mirrored(char)),
					str(unicodedata.combining(char)),
					]
			h.update(''.join(data).encode("ascii"))
		result = h.hexdigest()

		if sys.version_info[:2] == (3, 8):
			self.assertEqual(result, "4bcbf9df344114b1ebc95b904f4352dd250dff7e")
		elif sys.version_info[:2] == (3, 11):
			self.assertEqual(result, "98d602e1f69d5c5bb8a5910c40bbbad4e18e8370")
		elif sys.version_info[:2] == (3, 12):
			self.assertEqual(result, "42d326b3db43e0984ae6a6db02b51f4cc45f4364")
		elif sys.version_info[:2] >= (3, 13):
			# Update this from CPython if the database changes.
			self.assertEqual(result, "f578eba167fdb18d559b029fcef2b3ed98c64f13")
		elif sys.version_info[:2] >= (3, 9):
			self.assertEqual(result, "d1e37a2854df60ac607b47b51189b9bf1b54bfdb")

	def test_digit(self):
		self.assertEqual(unicodedata.digit('A', None), None)
		self.assertEqual(unicodedata.digit('9'), 9)
		self.assertEqual(unicodedata.digit('⅛', None), None)
		self.assertEqual(unicodedata.digit('⑨'), 9)
		self.assertEqual(unicodedata.digit('𠀀', None), None)
		self.assertEqual(unicodedata.digit('𝟽'), 7)

		self.assertRaises(TypeError, unicodedata.digit)
		self.assertRaises(TypeError, unicodedata.digit, "xx")
		self.assertRaises(ValueError, unicodedata.digit, 'x')

	def test_numeric(self):
		self.assertEqual(unicodedata.numeric('A', None), None)
		self.assertEqual(unicodedata.numeric('9'), 9)
		self.assertEqual(unicodedata.numeric('⅛'), 0.125)
		self.assertEqual(unicodedata.numeric('⑨'), 9.0)
		self.assertEqual(unicodedata.numeric('꘧'), 7.0)
		self.assertEqual(unicodedata.numeric('𠀀', None), None)
		self.assertEqual(unicodedata.numeric('𐄪'), 9000)

		self.assertRaises(TypeError, unicodedata.numeric)
		self.assertRaises(TypeError, unicodedata.numeric, "xx")
		self.assertRaises(ValueError, unicodedata.numeric, 'x')

	def test_decimal(self):
		self.assertEqual(unicodedata.decimal('A', None), None)
		self.assertEqual(unicodedata.decimal('9'), 9)
		self.assertEqual(unicodedata.decimal('⅛', None), None)
		self.assertEqual(unicodedata.decimal('⑨', None), None)
		self.assertEqual(unicodedata.decimal('𠀀', None), None)
		self.assertEqual(unicodedata.decimal('𝟽'), 7)

		self.assertRaises(TypeError, unicodedata.decimal)
		self.assertRaises(TypeError, unicodedata.decimal, "xx")
		self.assertRaises(ValueError, unicodedata.decimal, 'x')

	def test_category(self):
		self.assertEqual(unicodedata.category('\ufffe'), "Cn")
		self.assertEqual(unicodedata.category('a'), "Ll")
		self.assertEqual(unicodedata.category('A'), "Lu")
		self.assertEqual(unicodedata.category('𠀀'), "Lo")
		self.assertEqual(unicodedata.category('𐄪'), "No")

		self.assertRaises(TypeError, unicodedata.category)
		self.assertRaises(TypeError, unicodedata.category, "xx")

	def test_bidirectional(self):
		self.assertEqual(unicodedata.bidirectional('\ufffe'), '')
		self.assertEqual(unicodedata.bidirectional(' '), "WS")
		self.assertEqual(unicodedata.bidirectional('A'), 'L')
		self.assertEqual(unicodedata.bidirectional('𠀀'), 'L')

		self.assertRaises(TypeError, unicodedata.bidirectional)
		self.assertRaises(TypeError, unicodedata.bidirectional, "xx")

	def test_decomposition(self):
		self.assertEqual(unicodedata.decomposition('\ufffe'), '')
		self.assertEqual(unicodedata.decomposition('¼'), "<fraction> 0031 2044 0034")

		self.assertRaises(TypeError, unicodedata.decomposition)
		self.assertRaises(TypeError, unicodedata.decomposition, "xx")

	def test_mirrored(self):
		self.assertEqual(unicodedata.mirrored('\ufffe'), 0)
		self.assertEqual(unicodedata.mirrored('a'), 0)
		self.assertEqual(unicodedata.mirrored('∁'), 1)
		self.assertEqual(unicodedata.mirrored('𠀀'), 0)

		self.assertRaises(TypeError, unicodedata.mirrored)
		self.assertRaises(TypeError, unicodedata.mirrored, "xx")

	def test_combining(self):
		self.assertEqual(unicodedata.combining('\ufffe'), 0)
		self.assertEqual(unicodedata.combining('a'), 0)
		self.assertEqual(unicodedata.combining('⃡'), 230)
		self.assertEqual(unicodedata.combining('𠀀'), 0)

		self.assertRaises(TypeError, unicodedata.combining)
		self.assertRaises(TypeError, unicodedata.combining, "xx")

	def test_pr29(self):
		# https://www.unicode.org/review/pr-29.html
		# See issues #1054943 and #10254.
		composed = ("େ̀ା", "ᄀ̀ᅡ", "Li̍t-sṳ́", "मार्क ज़" + "ुकेरबर्ग", "किर्गिज़" + "स्तान")
		for text in composed:
			self.assertEqual(unicodedata.normalize("NFC", text), text)

	def test_issue10254(self):
		# Crash reported in #10254
		a = "C̸" * 20 + "Ç"
		b = "C̸" * 20 + 'Ç'
		self.assertEqual(unicodedata.normalize("NFC", a), b)

	def test_issue29456(self):
		# Fix #29456
		u1176_str_a = "ᄀᅶᆨ"
		u1176_str_b = "ᄀᅶᆨ"
		u11a7_str_a = "기ᆧ"
		u11a7_str_b = "기ᆧ"
		u11c3_str_a = "기ᇃ"
		u11c3_str_b = "기ᇃ"
		self.assertEqual(unicodedata.normalize("NFC", u1176_str_a), u1176_str_b)
		self.assertEqual(unicodedata.normalize("NFC", u11a7_str_a), u11a7_str_b)
		self.assertEqual(unicodedata.normalize("NFC", u11c3_str_a), u11c3_str_b)

	def test_east_asian_width(self):
		eaw = unicodedata.east_asian_width
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
		self.assertEqual(unicodedata.ucd_3_2_0.east_asian_width('⌚'), 'N')
		self.assertEqual(unicodedata.east_asian_width('⌚'), 'W')


class UnicodeMiscTest(unittest.TestCase):

	@test.support.cpython_only
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
		result = test.support.script_helper.assert_python_failure("-c", code)
		error = "SyntaxError: (unicode error) \\N escapes not supported (can't load unicodedata module)"
		self.assertIn(error, result.err.decode("ascii"))

	def test_decimal_numeric_consistent(self):
		# Test that decimal and numeric are consistent,
		# i.e. if a character has a decimal value,
		# its numeric value should be the same.
		count = 0
		for i in range(0x10000):
			c = chr(i)
			dec = unicodedata.decimal(c, -1)
			if dec != -1:
				self.assertEqual(dec, unicodedata.numeric(c))
				count += 1
		self.assertTrue(count >= 10)  # should have tested at least the ASCII digits

	def test_digit_numeric_consistent(self):
		# Test that digit and numeric are consistent,
		# i.e. if a character has a digit value,
		# its numeric value should be the same.
		count = 0
		for i in range(0x10000):
			c = chr(i)
			dec = unicodedata.digit(c, -1)
			if dec != -1:
				self.assertEqual(dec, unicodedata.numeric(c))
				count += 1
		self.assertTrue(count >= 10)  # should have tested at least the ASCII digits

	def test_bug_1704793(self):
		self.assertEqual(unicodedata.lookup("GOTHIC LETTER FAIHU"), '𐍆')

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

	@test.support.requires_resource("network")
	def test_normalization(self):
		TESTDATAFILE = "NormalizationTest.txt"
		TESTDATAURL = f"http://www.pythontest.net/unicode/{unicodedata.unidata_version}/{TESTDATAFILE}"

		# Hit the exception early
		try:
			url = TESTDATAURL
			filename = urllib.parse.urlparse(url)[2].split('/')[-1]  # '/': it's URL!

			with TemporaryPathPlus() as tmpdir:
				fn = tmpdir / filename

				# Verify the requirement before downloading the file
				test.support.requires("urlfetch")
				print(f'\tfetching {url} ...')

				with urllib.request.build_opener().open(url, timeout=15) as f:
					with fn.open("wb") as out:
						s = f.read()
						while s:
							out.write(s)
							s = f.read()

				with fn.open() as f:
					if self.check_version(f):
						f.seek(0)
						self.run_normalization_tests(f)
						return

				raise test.support.TestFailed(f'invalid resource {fn!r}')

		except PermissionError:
			self.skipTest(f"Permission error when downloading {TESTDATAURL} "
							f"into the test data directory")
		except (OSError, HTTPException):
			self.fail(f"Could not retrieve {TESTDATAURL}")

	def run_normalization_tests(self, testdata):
		part = None
		part1_data = {}

		def NFC(string):
			return unicodedata.normalize("NFC", string)

		def NFKC(string):
			return unicodedata.normalize("NFKC", string)

		def NFD(string):
			return unicodedata.normalize("NFD", string)

		def NFKD(string):
			return unicodedata.normalize("NFKD", string)

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
