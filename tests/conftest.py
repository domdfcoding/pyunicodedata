# stdlib
import importlib

# this package
import pyunicodedata._unicode_numeric
import pyunicodedata._unicodetype_db
import pyunicodedata._unicodetype_index

importlib.reload(pyunicodedata)
importlib.reload(pyunicodedata._c_unicodedata)
importlib.reload(pyunicodedata._unicode_numeric)
importlib.reload(pyunicodedata._unicodetype_db)
importlib.reload(pyunicodedata._unicodetype_index)

pyunicodedata.install_patch()
