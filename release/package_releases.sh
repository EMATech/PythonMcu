#!/bin/bash

# ----------------------------------------------------------------------------
#
#  PythonMcu
#  =========
#  Mackie Host Controller written in Python
#
#  Copyright (c) 2011 Martin Zuther (http://www.mzuther.de/)
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#  Thank you for using free software!
#
# ----------------------------------------------------------------------------

PYTHON_MCU_VERSION="1.07"

PYTHON_MCU_SOURCE_DIR="../src"
PYTHON_MCU_DOCUMENTATION_DIR="../doc"

function create_new_archive
{
	echo "  Creating folder \"$1\"..."
	echo "  Copying files to \"$1\"..."
	mkdir -p "$1"
	echo
}

function compress_new_archive
{
	echo
	echo "  Creating archive \"$1\"..."
	echo

	if [ "$3" = "bzip2" ]; then
		tar --create --bzip2 --verbose --file "$1" "$2"/* | gawk ' { print "    adding: " $1 } '
	elif [ "$3" = "zip" ]; then
		zip --recurse-paths "$1" "$2"/* | gawk ' { print "  " $0 } '
	fi

	echo
	echo "  Removing folder \"$2\"..."

	rm -r "$2"/

	echo "  Done."
	echo
}

echo


PYTHON_MCU_ARCHIVE_DIR="PythonMcu_$PYTHON_MCU_VERSION"

create_new_archive "$PYTHON_MCU_ARCHIVE_DIR"

cp "../README.markdown" "$PYTHON_MCU_ARCHIVE_DIR/README"

mkdir -p "$PYTHON_MCU_ARCHIVE_DIR/doc"
cp "$PYTHON_MCU_DOCUMENTATION_DIR/CONTRIBUTORS" "$PYTHON_MCU_ARCHIVE_DIR/doc"
cp "$PYTHON_MCU_DOCUMENTATION_DIR/Controllers.pdf" "$PYTHON_MCU_ARCHIVE_DIR/doc"
cp "$PYTHON_MCU_DOCUMENTATION_DIR/PythonMcu.pdf" "$PYTHON_MCU_ARCHIVE_DIR/doc"
cp "$PYTHON_MCU_DOCUMENTATION_DIR/HISTORY" "$PYTHON_MCU_ARCHIVE_DIR/doc"
cp "$PYTHON_MCU_DOCUMENTATION_DIR/LICENSE" "$PYTHON_MCU_ARCHIVE_DIR/doc"

cp --recursive  "$PYTHON_MCU_SOURCE_DIR" "$PYTHON_MCU_ARCHIVE_DIR"
find "$PYTHON_MCU_ARCHIVE_DIR/" -iname '*.pyc' -execdir rm {} \;

compress_new_archive "$PYTHON_MCU_ARCHIVE_DIR.zip" "$PYTHON_MCU_ARCHIVE_DIR" "zip"
