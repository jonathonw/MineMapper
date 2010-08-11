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
    def __init__(self, file):
        self.file = gzip.GzipFile(fileobj=file)
        pass

    def readNbt(self):
        return self.readNamedTag()

    def readNamedTag(self):
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

    '''
    Reads an arbitrary tag of type 'type' and returns its value.
    '''
    def readTag(self, type):
        
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
        byteString = self.file.read(1)
        # This odd (item, ) syntax is necessary because unpacks returns a tuple;
        # we want this function to return just the one byte.
        (byteData, ) = struct.unpack(">b", byteString)
        return byteData

    def readShort(self):
        shortString = self.file.read(2)
        (shortData, ) = struct.unpack(">h", shortString)
        return shortData

    def readInt(self):
        intString = self.file.read(4)
        (intData, ) = struct.unpack(">i", intString)
        return intData

    def readLong(self):
        longString = self.file.read(8)
        (longData, ) = struct.unpack(">q", longString)
        return longData

    def readFloat(self):
        floatString = self.file.read(4)
        (floatData, ) = struct.unpack(">f", floatString)
        return floatData

    def readDouble(self):
        doubleString = self.file.read(8)
        (doubleData, ) = struct.unpack(">d", doubleString)
        return doubleData

    def readByteArray(self):
        length = self.readInt()
        array = [ ]
        for i in range(length):
            array.append(self.readByte())

        return array

    """
    Reads a string, which is composed of a short indicating the length in
    bytes, followed by a *UTF-8* string.
    """
    def readString(self):
        length = self.readShort()
        str = self.file.read(length)
        unicodestr = utf_8.decode(str)
        return unicodestr

    def readList(self):
        type = self.readByte()
        length = self.readInt()

        array = [ ]
        for i in range(length):
            array.append(self.readTag(type))

        return array

    def readCompound(self):
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
    with open("bigtest.nbt", "rb") as f:
        reader = NbtReader(f)
        result = reader.readNbt()
        pprinter = PrettyPrinter()
        pprinter.pprint(result)
