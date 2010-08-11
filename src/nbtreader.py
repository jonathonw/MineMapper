#! /usr/bin/python

# MineMapper - A Minecraft Infinite Map Generator
# Copyright (C) 2010  Jonathon Williams
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

__author__="Jonathon"
__date__ ="$Aug 10, 2010 6:59:14 PM$"

import struct
import gzip

from encodings import utf_8
from pprint import PrettyPrinter

class TagType:
    END = 0
    BYTE = 1
    SHORT = 2
    INT = 3
    LONG = 4 #long is actually long long (64-bits)
    FLOAT = 5
    DOUBLE = 6
    BYTE_ARRAY = 7
    STRING = 8
    LIST = 9
    COMPOUND = 10

class InvalidTagError(Exception):
    def __init__(self, tagType):
        self.tagType = tagType

    def __str__(self):
        return str(self.tagType)


class NbtReader:
    """
    Reads an NBT file and produces a python object hierarchy (using the appropriate
    equivalent python types, such as dictionaries for Compounds and lists for Lists)
    from it.
    """
    
    def __init__(self, file):
        """
        Constructs a new NBT reader from the specified file.  File should be a python
        file-like object; the NBTReader will handle decoding the Gzipped file.
        """
        self.file = gzip.GzipFile(fileobj=file)
        pass

   
    def readNbt(self):
        """
        Begins reading an NBT file.  There should be a single named tag at the
        root of the file, all other tags at the root level will be ignored.

        According to Notch's specification, we should only accept a Compound
        here, but we can accept any named tag as a root element for flexibility
        reasons.
        """
        return self.readNamedTag()

    def readNamedTag(self):
        """
        Reads an arbitrary named tag.  Returns a tuple:  (name, value).
        """
        #get the tag type (a byte)
        type = self.readByte()
        if type == TagType.END:
            return ("", None)
        else:
            #get the name (a string)
            name = self.readString()
            #and now get the actual data
            data = self.readTag(type)

            return (name, data)

    
    def readTag(self, type):
        """
        Reads an arbitrary tag of type 'type' and returns its value.
        """
        if type == TagType.BYTE:
            return self.readByte()
        elif type == TagType.SHORT:
            return self.readShort()
        elif type == TagType.INT:
            return self.readInt()
        elif type == TagType.LONG:
            return self.readLong()
        elif type == TagType.FLOAT:
            return self.readFloat()
        elif type == TagType.DOUBLE:
            return self.readDouble()
        elif type == TagType.BYTE_ARRAY:
            return self.readByteArray()
        elif type == TagType.STRING:
            return self.readString()
        elif type == TagType.LIST:
            return self.readList()
        elif type == TagType.COMPOUND:
            return self.readCompound()
        else:
            raise InvalidTagError(type)

    
    def readByte(self):
        """
        Reads a single (signed) byte from the input file.
        """
        byteString = self.file.read(1)
        # This odd (item, ) syntax is necessary because unpacks returns a tuple;
        # we want this function to return just the one byte.
        (byteData, ) = struct.unpack(">b", byteString)
        return byteData

    
    def readShort(self):
        """
        Reads a (signed) short from the input file.
        """
        shortString = self.file.read(2)
        (shortData, ) = struct.unpack(">h", shortString)
        return shortData

    def readInt(self):
        """
        Reads a (signed) int from the input file.
        """
        intString = self.file.read(4)
        (intData, ) = struct.unpack(">i", intString)
        return intData

    def readLong(self):
        """
        Reads a (signed) long from the input file.
        """
        longString = self.file.read(8)
        (longData, ) = struct.unpack(">q", longString)
        return longData

    def readFloat(self):
        """
        Reads a (signed) float from the input file.
        """
        floatString = self.file.read(4)
        (floatData, ) = struct.unpack(">f", floatString)
        return floatData

    def readDouble(self):
        """
        Reads a (signed) double from the input file.
        """
        doubleString = self.file.read(8)
        (doubleData, ) = struct.unpack(">d", doubleString)
        return doubleData

    def readByteArray(self):
        """
        Reads a byte array from the input file.

        A byte array is composed of an integer designating the lengh of the
        array, followed by the specified number of bytes.

        Returns a native Python list corresponding to the array which was read.
        """
        length = self.readInt()
        array = [ ]
        for i in range(length):
            array.append(self.readByte())

        return array

    
    def readString(self):
        """
        Reads a string from the input file.

        A string is composed of a short designating the length in bytes, followed
        by a *UTF-8* string of the specified length.

        Returns a unicode string (Python 'unicode') corresponding to the string
        which was read.
        """
        length = self.readShort()
        str = self.file.read(length)
        (unicodestr, lengthConsumed) = utf_8.decode(str)
        return unicodestr

    def readList(self):
        """
        Reads a list from the input file.

        A list is composed of a byte designating the type of all objects in the
        list, an integer designating the number of elements in the list, and the
        indicated number of instances of the specified type.

        Returns a native Python list corresponding to the list which was read.
        """
        type = self.readByte()
        length = self.readInt()

        array = [ ]
        for i in range(length):
            array.append(self.readTag(type))

        return array

    def readCompound(self):
        """
        Reads a compound object from the input file.

        A Compound is composed of a sequence of named tags, terminated by an
        unnamed tag of type TagType.END .  Order is not preserved in a Compound,
        and keys may only occur once per compound (they may reoccur in other
        Compound objects).

        Returns a native Python dictionary corresponding to the Compound which
        was read.
        """
        compoundData = {}
        reachedEnd = False
        while not reachedEnd:
            (name, value) = self.readNamedTag()
            if (name, value) != ("", None):
                compoundData[name] = value
            else:
                #Reached end tag; end the look
                reachedEnd = True

        return compoundData

if __name__ == "__main__":
    #Test function: read one of the test input files provided and print it out
    with open("testData/bigtest.nbt", "rb") as f:
        reader = NbtReader(f)
        result = reader.readNbt()
        pprinter = PrettyPrinter()
        pprinter.pprint(result)