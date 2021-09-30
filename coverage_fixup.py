"""
Convert absolute filenames in ``.coverage`` files from one base directory to another.
"""

# stdlib
import os
import sqlite3
import sys
from pathlib import PurePosixPath, PureWindowsPath

# 3rd party
from domdf_python_tools.paths import PathPlus


def main():

	for path in ('.', os.getcwd()):
		if path in sys.path:
			sys.path.remove(path)

	# this package
	import pyunicodedata

	old_base = PathPlus(pyunicodedata.__file__).parent
	print(old_base)
	new_base = f"./{pyunicodedata.__name__}"

	conn = sqlite3.connect(".coverage")
	c = conn.cursor()

	for (idx, filename) in c.execute("SELECT * FROM file").fetchall():

		if filename.startswith(str(old_base)):
			print(idx, filename, end='')

			try:
				new_base_p = PurePosixPath(new_base)
				new_filename_p = PureWindowsPath(filename).relative_to(PureWindowsPath(old_base))
				new_filename = str(new_base_p / new_filename_p)

				print(" ->", new_filename, end='')
				c.execute("UPDATE file SET path=? WHERE id=?", (new_filename, idx))
			finally:
				print()

		elif filename.startswith(pyunicodedata.__name__):
			print(idx, filename)
		elif filename.startswith(str(PathPlus.cwd() / pyunicodedata.__name__)):
			print(idx, filename)
		else:
			c.execute("DELETE FROM file WHERE id=?", (idx, ))
			continue

	conn.commit()
	conn.close()


if __name__ == "__main__":
	sys.exit(main())
