#!/usr/bin/env python
#  -*- coding: <utf-8> -*-

"""
This file is part of Spartacus project
Copyright (C) 2016  CSE

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License along
with this program; if not, write to the Free Software Foundation, Inc.,
51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
"""

import unittest
import struct
from ToolChain.Assembler.Parser.Parser import Parser

__author__ = "CSE"
__copyright__ = "Copyright 2015, CSE"
__credits__ = ["CSE"]
__license__ = "GPL"
__version__ = "2.0"
__maintainer__ = "CSE"
__status__ = "Dev"


class TestParser(unittest.TestCase):

    parser = Parser()

    def test_parse(self):
        """
        Tests the method:
        build(self, text)
        """

        self.parser.relativeAddressCounter = 0
        text = "MOV $B $C"
        instruction, relAddress, flag = self.parser.parse(text)
        self.assertEqual(instruction, bytes((0b10011011,)) + bytes((0b00010010,)))
        self.assertEqual(relAddress, 2)
        self.assertEqual(flag, 0)

        self.parser.relativeAddressCounter = 0
        text = ".dataAlpha test string  two  spaces\n"
        instruction, relAddress, flag = self.parser.parse(text)
        self.assertEqual(instruction, b'test string  two  spaces\x00')
        self.assertEqual(relAddress, 25)
        self.assertEqual(flag, 0)

        self.parser.relativeAddressCounter = 0
        text = ".global start"
        instruction, relAddress, flag = self.parser.parse(text)
        self.assertEqual(instruction, "START")
        self.assertEqual(relAddress, 0)
        self.assertEqual(flag, 2)

        self.parser.relativeAddressCounter = 0
        text = "start:"
        instruction, relAddress, flag = self.parser.parse(text)
        self.assertEqual(instruction, "START")
        self.assertEqual(relAddress, 0)
        self.assertEqual(flag, 1)

        self.parser.relativeAddressCounter = 0
        text = "MOV start $B"
        instruction, relAddress, flag = self.parser.parse(text)
        self.assertEqual(instruction, bytes((0b01100000,)) + b':START:' + bytes((0b00000001,)))
        self.assertEqual(relAddress, 6)
        self.assertEqual(flag, 0)

    def test_parseError(self):
        """
        Tests various errors for the method:
        build(self, text)
        """

        try:
            self.parser.parse("nothing good here")
        except ValueError:
            pass
        else:
            raise AssertionError("ValueError was not raised")

        try:
            self.parser.parse("MOV ;")
        except ValueError:
            pass
        else:
            raise AssertionError("ValueError was not raised")

        try:
            self.parser.parse(":START: ")
        except ValueError:
            pass
        else:
            raise AssertionError("ValueError was not raised")

    def test_findInstructionCodeIns(self):
        """
        Tests the method:
        _findInstructionCode(self, form, line, instruction)
        for instruction in STATE0 (Ins)
        """

        instruction = self.parser._findInstructionCode("Ins", ["ACTI"], b'')
        self.assertEqual(instruction, bytes((0b11110001,)))

        instruction = self.parser._findInstructionCode("Ins", ["DACTI"], b'')
        self.assertEqual(instruction, bytes((0b11110010,)))

        instruction = self.parser._findInstructionCode("Ins", ["HIRET"], b'')
        self.assertEqual(instruction, bytes((0b11110011,)))

        instruction = self.parser._findInstructionCode("Ins", ["NOP"], b'')
        self.assertEqual(instruction, bytes((0b11111111,)))

        instruction = self.parser._findInstructionCode("Ins", ["RET"], b'')
        self.assertEqual(instruction, bytes((0b11110000,)))

    def test_findInstructionCodeInsError(self):
        try:
            self.parser._findInstructionCode("Ins", ["error"], b'')
        except ValueError:
            pass
        else:
            raise AssertionError("ValueError was not raised")

        try:
            self.parser._findInstructionCode("InsReg", ["RET"], b'')
        except ValueError:
            pass
        else:
            raise AssertionError("ValueError was not raised")

    def test_findInstructionCodeInsReg(self):
        """
        Tests the method:
        _findInstructionCode(self, form, line, instruction)
        for instruction in STATE1 (InsReg)
        """

        instruction = self.parser._findInstructionCode("InsReg", ["CALL", "$B"], b'')
        self.assertEqual(instruction, bytes((0b01110010,)))

        instruction = self.parser._findInstructionCode("InsReg", ["INT", "$B"], b'')
        self.assertEqual(instruction, bytes((0b01110110,)))

        instruction = self.parser._findInstructionCode("InsReg", ["NOT", "$B"], b'')
        self.assertEqual(instruction, bytes((0b01110000,)))

        instruction = self.parser._findInstructionCode("InsReg", ["POP", "$C"], b'')
        self.assertEqual(instruction, bytes((0b01110100,)))

        instruction = self.parser._findInstructionCode("InsReg", ["PUSH", "$C"], b'')
        self.assertEqual(instruction, bytes((0b01110011,)))

        instruction = self.parser._findInstructionCode("InsReg", ["SIVR", "$B"], b'')
        self.assertEqual(instruction, bytes((0b01110101,)))

    def test_findInstructionCodeInsRegError(self):

        try:
            self.parser._findInstructionCode("InsReg", ["error"], b'')
        except ValueError:
            pass
        else:
            raise AssertionError("ValueError was not raised")

        try:
            self.parser._findInstructionCode("Ins", ["CALL"], b'')
        except ValueError:
            pass
        else:
            raise AssertionError("ValueError was not raised")

    def test_findInstructionCodeInsRegReg(self):
        """
        Tests the method:
        _findInstructionCode(self, form, line, instruction)
        for instruction in STATE2 (InsRegReg)
        """

        instruction = self.parser._findInstructionCode("InsRegReg", ["ADD", "$B", "$C"], b'')
        correctInstruction = 0b10010010
        self.assertEqual(instruction, bytes((correctInstruction,)))

        instruction = self.parser._findInstructionCode("InsRegReg", ["AND", "$B", "$C"], b'')
        correctInstruction = 0b10010111
        self.assertEqual(instruction, bytes((correctInstruction,)))

        instruction = self.parser._findInstructionCode("InsRegReg", ["CMP", "$B", "$C"], b'')
        correctInstruction = 0b10011010
        self.assertEqual(instruction, bytes((correctInstruction,)))

        instruction = self.parser._findInstructionCode("InsRegReg", ["DIV", "$B", "$C"], b'')
        correctInstruction = 0b10010101
        self.assertEqual(instruction, bytes((correctInstruction,)))

        instruction = self.parser._findInstructionCode("InsRegReg", ["MOV", "$C", "$B"], b'')
        correctInstruction = 0b10011011
        self.assertEqual(instruction, bytes((correctInstruction,)))

        instruction = self.parser._findInstructionCode("InsRegReg", ["MUL", "$C", "$B"], b'')
        correctInstruction = 0b10010100
        self.assertEqual(instruction, bytes((correctInstruction,)))

        instruction = self.parser._findInstructionCode("InsRegReg", ["OR", "$B", "$C"], b'')
        correctInstruction = 0b10011000
        self.assertEqual(instruction, bytes((correctInstruction,)))

        instruction = self.parser._findInstructionCode("InsRegReg", ["SHL", "$C", "$B"], b'')
        correctInstruction = 0b10010110
        self.assertEqual(instruction, bytes((correctInstruction,)))

        instruction = self.parser._findInstructionCode("InsRegReg", ["SHR", "$B", "$C"], b'')
        correctInstruction = 0b10011001
        self.assertEqual(instruction, bytes((correctInstruction,)))

        instruction = self.parser._findInstructionCode("InsRegReg", ["SUB", "$C", "$B"], b'')
        correctInstruction = 0b10010011
        self.assertEqual(instruction, bytes((correctInstruction,)))

        instruction = self.parser._findInstructionCode("InsRegReg", ["XOR", "$C", "$B"], b'')
        correctInstruction = 0b10010000
        self.assertEqual(instruction, bytes((correctInstruction,)))

    def test_findInstructionCodeInsRegRegError(self):

        try:
            self.parser._findInstructionCode("InsRegReg", ["error"], b'')
        except ValueError:
            pass
        else:
            raise AssertionError("ValueError was not raised")

        try:
            self.parser._findInstructionCode("InsReg", ["ADD"], b'')
        except ValueError:
            pass
        else:
            raise AssertionError("ValueError was not raised")

    def test_findInstructionCodeInsImm(self):
        """
        Tests the method:
        _findInstructionCode(self, form, line, instruction)
        for instruction in STATE3 (InsImm)
        """

        instruction = self.parser._findInstructionCode("InsImm", ["CALL", "#4"], b'')
        self.assertEqual(instruction, bytes((0b10000010,)))

        instruction = self.parser._findInstructionCode("InsImm", ["CALL", "function"], b'')
        self.assertEqual(instruction, bytes((0b10000010,)))

        instruction = self.parser._findInstructionCode("InsImm", ["INT", "#4"], b'')
        self.assertEqual(instruction, bytes((0b10000011,)))

        instruction = self.parser._findInstructionCode("InsImm", ["PUSH", "#4"], b'')
        self.assertEqual(instruction, bytes((0b10000001,)))

        instruction = self.parser._findInstructionCode("InsImm", ["PUSH", "label"], b'')
        self.assertEqual(instruction, bytes((0b10000001,)))

    def test_findInstructionCodeInsImmError(self):
        """
        Tests ValueErrors for the method:
        _findInstructionCode(self, form, line, instruction)
        for instruction in STATE3 (InsImm)
        """

        try:
            self.parser._findInstructionCode("InsImm", ["error"], b'')
        except ValueError:
            pass
        else:
            raise AssertionError("ValueError was not raised")

        try:
            self.parser._findInstructionCode("Ins", ["CALL"], b'')
        except ValueError:
            pass
        else:
            raise AssertionError("ValueError was not raised")

    def test_findInstructionCodeInsImmReg(self):
        """
        Tests the method:
        _findInstructionCode(self, form, line, instruction)
        for instruction in STATE4 (InsImmReg)
        """

        instruction = self.parser._findInstructionCode("InsImmReg", ["ADD", "#4", "$C"], b'')
        self.assertEqual(instruction, bytes((0b01100110,)))

        instruction = self.parser._findInstructionCode("InsImmReg", ["AND", "#4", "$C"], b'')
        self.assertEqual(instruction, bytes((0b01100001,)))

        instruction = self.parser._findInstructionCode("InsImmReg", ["CMP", "#4", "$C"], b'')
        self.assertEqual(instruction, bytes((0b01101000,)))

        instruction = self.parser._findInstructionCode("InsImmReg", ["MOV", "#4", "$B"], b'')
        self.assertEqual(instruction, bytes((0b01100000,)))

        instruction = self.parser._findInstructionCode("InsImmReg", ["MOV", "label", "$C"], b'')
        self.assertEqual(instruction, bytes((0b01100000,)))

        instruction = self.parser._findInstructionCode("InsImmReg", ["OR", "#4", "$C"], b'')
        self.assertEqual(instruction, bytes((0b01100010,)))

        instruction = self.parser._findInstructionCode("InsImmReg", ["SHL", "#4", "$B"], b'')
        self.assertEqual(instruction, bytes((0b01100101,)))

        instruction = self.parser._findInstructionCode("InsImmReg", ["SHR", "#4", "$B"], b'')
        self.assertEqual(instruction, bytes((0b01100100,)))

        instruction = self.parser._findInstructionCode("InsImmReg", ["SUB", "#4", "$B"], b'')
        self.assertEqual(instruction, bytes((0b01100111,)))

        instruction = self.parser._findInstructionCode("InsImmReg", ["XOR", "#4", "$B"], b'')
        self.assertEqual(instruction, bytes((0b01100011,)))

    def test_findInstructionCodeInsImmRegError(self):
        """
        Tests ValueErrors for the method:
        _findInstructionCode(self, form, line, instruction)
        for instruction in STATE4 (InsImmReg)
        """

        try:
            self.parser._findInstructionCode("InsImmReg", ["error"], b'')
        except ValueError:
            pass
        else:
            raise AssertionError("ValueError was not raised")

        try:
            self.parser._findInstructionCode("Ins", ["ADD"], b'')
        except ValueError:
            pass
        else:
            raise AssertionError("ValueError was not raised")

    def test_findInstructionCodeInsWidthImmImm(self):
        """
        Tests the method:
        _findInstructionCode(self, form, line, instruction)
        for instruction in STATE5 (InsWidthImmImm)
        """

        instruction = self.parser._findInstructionCode("InsWidthImmImm", ["MEMW", "[1]", "#4", "#6"], b'')
        self.assertEqual(instruction, bytes((0b00110000,)))

    def test_findInstructionCodeInsWidthImmImmError(self):
        """
        Tests ValueErrors for the method:
        _findInstructionCode(self, form, line, instruction)
        for instruction in STATE5 (InsWidthImmImm)
        """

        try:
            self.parser._findInstructionCode("InsWidthImmImm", ["error"], b'')
        except ValueError:
            pass
        else:
            raise AssertionError("ValueError was not raised")

        try:
            self.parser._findInstructionCode("Ins", ["MEMW"], b'')
        except ValueError:
            pass
        else:
            raise AssertionError("ValueError was not raised")

    def test_findInstructionCodeInsWidthImmReg(self):
        """
        Tests the method:
        _findInstructionCode(self, form, line, instruction)
        for instruction in STATE6 (InsWidthImmReg)
        """

        instruction = self.parser._findInstructionCode("InsWidthImmReg", ["MEMR", "[1]", "#4", "$C"], b'')
        self.assertEqual(instruction, bytes((0b00000001,)))

        instruction = self.parser._findInstructionCode("InsWidthImmReg", ["MEMW", "[1]", "#4", "$C"], b'')
        self.assertEqual(instruction, bytes((0b00000000,)))

    def test_findInstructionCodeInsWidthImmRegError(self):
        """
        Tests ValueErrors for the method:
        _findInstructionCode(self, form, line, instruction)
        for instruction in STATE6 (InsWidthImmReg)
        """

        try:
            self.parser._findInstructionCode("InsWidthImmReg", ["error"], b'')
        except ValueError:
            pass
        else:
            raise AssertionError("ValueError was not raised")

        try:
            self.parser._findInstructionCode("Ins", ["MEMW"], b'')
        except ValueError:
            pass
        else:
            raise AssertionError("ValueError was not raised")

    def test_findInstructionCodeInsWidthRegImm(self):
        """
        Tests the method:
        _findInstructionCode(self, form, line, instruction)
        for instruction in STATE7 (InsWidthRegImm)
        """

        instruction = self.parser._findInstructionCode("InsWidthRegImm", ["MEMW", "[1]", "$C", "#4"], b'')
        self.assertEqual(instruction, bytes((0b00100000,)))

    def test_findInstructionCodeInsWidthRegImmError(self):
        """
        Tests ValueErrors for the method:
        _findInstructionCode(self, form, line, instruction)
        for instruction in STATE7 (InsWidthRegImm)
        """

        try:
            self.parser._findInstructionCode("InsWidthRegImm", ["error"], b'')
        except ValueError:
            pass
        else:
            raise AssertionError("ValueError was not raised")

        try:
            self.parser._findInstructionCode("Ins", ["MEMW"], b'')
        except ValueError:
            pass
        else:
            raise AssertionError("ValueError was not raised")

    def test_findInstructionCodeInsWidthRegReg(self):
        """
        Tests the method:
         _findInstructionCode(self, form, line, instruction)
        for instruction in STATE8 (InsWidthRegReg)
        """

        instruction = self.parser._findInstructionCode("InsWidthRegReg", ["MEMR", "[1]", "$B", "$C"], b'')
        self.assertEqual(instruction, bytes((0b00010000,)))

        instruction = self.parser._findInstructionCode("InsWidthRegReg", ["MEMW", "[1]", "$C", "$B"], b'')
        self.assertEqual(instruction, bytes((0b00010001,)))

    def test_findInstructionCodeInsWidthRegRegError(self):
        """
        Tests ValueErrors for the method:
        _findInstructionCode(self, form, line, instruction)
        for instruction in STATE8 (InsWidthRegReg)
        """

        try:
            self.parser._findInstructionCode("InsWidthRegReg", ["error"], b'')
        except ValueError:
            pass
        else:
            raise AssertionError("ValueError was not raised")

        try:
            self.parser._findInstructionCode("InsWidthRegImm", ["MEMR"], b'')
        except ValueError:
            pass
        else:
            raise AssertionError("ValueError was not raised")

    def test_findInstructionCodeInsFlagImm(self):
        """
        Tests the method:
        _findInstructionCode(self, form, line, instruction)
        for instruction in STATE9 (InsFlagImm)
        """

        instruction = self.parser._findInstructionCode("InsFlagImm", ["JMP", "<>", "#4"], b'')
        self.assertEqual(instruction, bytes((0b01000001,)))

        instruction = self.parser._findInstructionCode("InsFlagImm", ["JMP", "$B", "label"], b'')
        self.assertEqual(instruction, bytes((0b01000001,)))

        instruction = self.parser._findInstructionCode("InsFlagImm", ["JMPR", "<>", "#4"], b'')
        self.assertEqual(instruction, bytes((0b01000000,)))

        instruction = self.parser._findInstructionCode("InsFlagImm", ["SFSTOR", "<L>", "#4"], b'')
        self.assertEqual(instruction, bytes((0b01000010,)))

    def test_findInstructionCodeInsFlagImmError(self):
        """
        Tests ValueErrors for the method:
        _findInstructionCode(self, form, line, instruction)
        for instruction in STATE9 (InsFlagImm)
        """

        try:
            self.parser._findInstructionCode("InsFlagImm", ["error"], b'')
        except ValueError:
            pass
        else:
            raise AssertionError("ValueError was not raised")

        try:
            self.parser._findInstructionCode("InsFlag", ["JMP"], b'')
        except ValueError:
            pass
        else:
            raise AssertionError("ValueError was not raised")

    def test_findInstructionCodeInsFlagReg(self):
        """
        Tests the method:
        _findInstructionCode(self, form, line, instruction)
        for instruction in STATE10 (InsFlagReg)
        """

        instruction = self.parser._findInstructionCode("InsFlagReg", ["JMP", "<>", "$C"], b'')
        self.assertEqual(instruction, bytes((0b01010001,)))

        instruction = self.parser._findInstructionCode("InsFlagReg", ["JMPR", "<>", "$C"], b'')
        self.assertEqual(instruction, bytes((0b01010000,)))

        instruction = self.parser._findInstructionCode("InsFlagReg", ["SFSTOR", "<E>", "$C"], b'')
        self.assertEqual(instruction, bytes((0b01010010,)))

    def test_findInstructionCodeInsFlagRegError(self):
        """
        Tests ValueErrors for the method:
        _findInstructionCode(self, form, line, instruction)
        for instruction in STATE10 (InsFlagReg)
        """

        try:
            self.parser._findInstructionCode("InsFlagReg", ["error"], b'')
        except ValueError:
            pass
        else:
            raise AssertionError("ValueError was not raised")

        try:
            self.parser._findInstructionCode("InsFlag", ["JMPR"], b'')
        except ValueError:
            pass
        else:
            raise AssertionError("ValueError was not raised")

    def test_definestateAndAddRelativeAddress(self):
        """
        Tests the method:
        _definestateAndAddRelativeAddress(self, form)
        """

        self.parser.relativeAddressCounter = 0

        form = self.parser._definestateAndAddRelativeAddress("Ins")
        self.assertEqual(form, "STATE0")
        self.assertEqual(self.parser.relativeAddressCounter, 1)

        form = self.parser._definestateAndAddRelativeAddress("InsReg")
        self.assertEqual(form, "STATE1")
        self.assertEqual(self.parser.relativeAddressCounter, 3)

        form = self.parser._definestateAndAddRelativeAddress("InsRegReg")
        self.assertEqual(form, "STATE2")
        self.assertEqual(self.parser.relativeAddressCounter, 5)

        form = self.parser._definestateAndAddRelativeAddress("InsImm")
        self.assertEqual(form, "STATE3")
        self.assertEqual(self.parser.relativeAddressCounter, 10)

        form = self.parser._definestateAndAddRelativeAddress("InsImmReg")
        self.assertEqual(form, "STATE4")
        self.assertEqual(self.parser.relativeAddressCounter, 16)

        form = self.parser._definestateAndAddRelativeAddress("InsWidthImmImm")
        self.assertEqual(form, "STATE5")
        self.assertEqual(self.parser.relativeAddressCounter, 26)

        form = self.parser._definestateAndAddRelativeAddress("InsWidthImmReg")
        self.assertEqual(form, "STATE6")
        self.assertEqual(self.parser.relativeAddressCounter, 32)

        form = self.parser._definestateAndAddRelativeAddress("InsWidthRegImm")
        self.assertEqual(form, "STATE7")
        self.assertEqual(self.parser.relativeAddressCounter, 38)

        form = self.parser._definestateAndAddRelativeAddress("InsWidthRegReg")
        self.assertEqual(form, "STATE8")
        self.assertEqual(self.parser.relativeAddressCounter, 41)

        form = self.parser._definestateAndAddRelativeAddress("InsFlagImm")
        self.assertEqual(form, "STATE9")
        self.assertEqual(self.parser.relativeAddressCounter, 47)

        form = self.parser._definestateAndAddRelativeAddress("InsFlagReg")
        self.assertEqual(form, "STATE10")
        self.assertEqual(self.parser.relativeAddressCounter, 49)

    def test_definestateAndAddRelativeAddressError(self):
            """
            Tests ValueErrors for the method:
            _definestateAndAddRelativeAddress(self, form)
            """

            try:
                self.parser._definestateAndAddRelativeAddress("InsFlag")
            except ValueError:
                pass
            else:
                raise AssertionError("ValueError was not raised")

    def test_evaluateIndicatorData(self):
        """
        Tests the method:
        _evaluateIndicatorData(self, text, dataIdentifier, line, instruction, labelFlag)
        """

        self.parser.relativeAddressCounter = 0

        text = ".DATAALPHA test\n"
        ins, flag = self.parser._evaluateIndicatorData(text, text.split()[0], text.split(), b'', 0)
        expectedOutput = b'test' + b'\x00'
        self.assertEqual(ins, expectedOutput)
        self.assertEqual(flag, 0)
        self.assertEqual(self.parser.relativeAddressCounter, 5)

        text = ".DATANUMERIC #50"
        expectedOutput = struct.pack(">I", int(text.split()[1][1:]))
        ins, flag = self.parser._evaluateIndicatorData(text, text.split()[0], text.split(), b'', 0)
        self.assertEqual(ins, expectedOutput)
        self.assertEqual(flag, 0)
        self.assertEqual(self.parser.relativeAddressCounter, 9)

        text = ".DATAMEMREF :start"
        expectedOutput = b':START:'
        ins, flag = self.parser._evaluateIndicatorData(text, text.split()[0], text.split(), b'', 0)
        self.assertEqual(ins, expectedOutput)
        self.assertEqual(flag, 0)
        self.assertEqual(self.parser.relativeAddressCounter, 13)

        text = ".DATAMEMREF start"
        expectedOutput = b':START:'
        ins, flag = self.parser._evaluateIndicatorData(text, text.split()[0], text.split(), b'', 0)
        self.assertEqual(ins, expectedOutput)
        self.assertEqual(flag, 0)
        self.assertEqual(self.parser.relativeAddressCounter, 17)

        text = ".GLOBAL start"
        expectedOutput = "START"
        ins, flag = self.parser._evaluateIndicatorData(text, text.split()[0], text.split(), b'', 0)
        self.assertEqual(ins, expectedOutput)
        self.assertEqual(flag, 2)

        text = "start:"
        expectedOutput = "START"
        ins, flag = self.parser._evaluateIndicatorData(text, text.split()[0], text.split(), b'', 0)
        self.assertEqual(ins, expectedOutput)
        self.assertEqual(flag, 1)

        text = ";test string for comment"
        expectedOutput = ""
        ins, flag = self.parser._evaluateIndicatorData(text, text.split()[0], text.split(), b'', 0)
        self.assertEqual(ins, expectedOutput)
        self.assertEqual(flag, 3)

    def test_evaluateIndicatorDataError(self):
            """
            Tests ValueErrors for the method:
            _evaluateIndicatorData(self, text, dataIdentifier, line, instruction, labelFlag)
            """

            text = "error"
            try:
                self.parser._evaluateIndicatorData(text, text.split()[0], text.split(), b'', 0)
            except ValueError:
                pass
            else:
                raise AssertionError("ValueError was not raised")

    def test_evaluateFormBasedOnArguments(self):
        """
        Tests the method:
        _evaluateFormBasedOnArguments(self, line, form, arglist)
        """

        text = "ACTI"
        form, arglist = self.parser._evaluateFormBasedOnArguments(text.split(), "Ins", [])
        self.assertEqual(form, "Ins")
        self.assertEqual(arglist, [])

        text = "INT $A"
        form, arglist = self.parser._evaluateFormBasedOnArguments(text.split(), "Ins", [])
        self.assertEqual(form, "InsReg")
        self.assertEqual(arglist, ["$A"])

        text = "ADD $C $B"
        form, arglist = self.parser._evaluateFormBasedOnArguments(text.split(), "Ins", [])
        self.assertEqual(form, "InsRegReg")
        self.assertEqual(arglist, ["$C", "$B"])

        text = "CALL label"
        form, arglist = self.parser._evaluateFormBasedOnArguments(text.split(), "Ins", [])
        self.assertEqual(form, "InsImm")
        self.assertEqual(arglist, ["label"])

        text = "MOV #4 $C"
        form, arglist = self.parser._evaluateFormBasedOnArguments(text.split(), "Ins", [])
        self.assertEqual(form, "InsImmReg")
        self.assertEqual(arglist, ["#4", "$C"])

        text = "MEMW [1] #4 #6"
        form, arglist = self.parser._evaluateFormBasedOnArguments(text.split(), "Ins", [])
        self.assertEqual(form, "InsWidthImmImm")
        self.assertEqual(arglist, ["[1]", "#4", "#6"])

        text = "MEMR [1] #4 $C"
        form, arglist = self.parser._evaluateFormBasedOnArguments(text.split(), "Ins", [])
        self.assertEqual(form, "InsWidthImmReg")
        self.assertEqual(arglist, ["[1]", "#4", "$C"])

        text = "MEMW [1] $C #4"
        form, arglist = self.parser._evaluateFormBasedOnArguments(text.split(), "Ins", [])
        self.assertEqual(form, "InsWidthRegImm")
        self.assertEqual(arglist, ["[1]", "$C", "#4"])

        text = "MEMR [1] $C $B"
        form, arglist = self.parser._evaluateFormBasedOnArguments(text.split(), "Ins", [])
        self.assertEqual(form, "InsWidthRegReg")
        self.assertEqual(arglist, ["[1]", "$C", "$B"])

        text = "JMP <E> #4"
        form, arglist = self.parser._evaluateFormBasedOnArguments(text.split(), "Ins", [])
        self.assertEqual(form, "InsFlagImm")
        self.assertEqual(arglist, ["<E>", "#4"])

        text = "JMP <LH> $C"
        form, arglist = self.parser._evaluateFormBasedOnArguments(text.split(), "Ins", [])
        self.assertEqual(form, "InsFlagReg")
        self.assertEqual(arglist, ["<LH>", "$C"])

    def test_evaluateFormBasedOnArgumentsError(self):
        """
        Tests ValueErrors for the method:
        _evaluateFormBasedOnArguments(self, line, form, arglist)
        """

        text = "Instruction with too many arguments"

        try:
            self.parser._evaluateFormBasedOnArguments(text.split(), "Ins", [])
        except ValueError:
            pass
        else:
            raise AssertionError("ValueError was not raised")

    def test_buildBinaryCodeACTI(self):
        """
        Tests the method:
        _buildBinaryCodeFromInstructionAndArguments(self, ins, state, arglist, instruction)
        for the ACTI instruction
        """

        text = "ACTI"
        ins = self.parser._findInstructionCode("Ins", ["ACTI"], b'')
        instruction = self.parser._buildBinaryCode(text.split()[0], "STATE0", [], ins)
        self.assertEqual(instruction, bytes((0b11110001,)))

    def test_buildBinaryCodeADD(self):
        """
        Tests the method:
        _buildBinaryCodeFromInstructionAndArguments(self, ins, state, arglist, instruction)
        for the ADD instruction
        """

        text = "ADD $B $C"
        arglist = text.split()[1:]
        ins = self.parser._findInstructionCode("InsRegReg", text.split(), b'')
        instruction = self.parser._buildBinaryCode(text.split()[0], "STATE2", arglist, ins)
        self.assertEqual(instruction, bytes((0b10010010,)) + bytes((0b00010010,)))

        text = "ADD #4 $B"
        arglist = text.split()[1:]
        ins = self.parser._findInstructionCode("InsImmReg", text.split(), b'')
        instruction = self.parser._buildBinaryCode(text.split()[0], "STATE4", arglist, ins)
        immediate = 4
        expectedOutput = bytes((0b01100110,)) + immediate.to_bytes(4, byteorder='big') + bytes((0b00000001,))
        self.assertEqual(instruction, expectedOutput)

    def test_buildBinaryCodeAND(self):
        """
        Tests the method:
        _buildBinaryCodeFromInstructionAndArguments(self, ins, state, arglist, instruction)
        for the AND instruction
        """

        text = "AND $B $C"
        arglist = text.split()[1:]
        ins = self.parser._findInstructionCode("InsRegReg", text.split(), b'')
        instruction = self.parser._buildBinaryCode(text.split()[0], "STATE2", arglist, ins)
        self.assertEqual(instruction, bytes((0b10010111,)) + bytes((0b00010010,)))

        text = "AND #4 $B"
        arglist = text.split()[1:]
        ins = self.parser._findInstructionCode("InsImmReg", text.split(), b'')
        instruction = self.parser._buildBinaryCode(text.split()[0], "STATE4", arglist, ins)
        immediate = 4
        expectedOutput = bytes((0b01100001,)) + immediate.to_bytes(4, byteorder='big') + bytes((0b00000001,))
        self.assertEqual(instruction, expectedOutput)

    def test_buildBinaryCodeCALL(self):
        """
        Tests the method:
        _buildBinaryCodeFromInstructionAndArguments(self, ins, state, arglist, instruction)
        for the CALL instruction
        """

        text = "CALL $B"
        arglist = text.split()[1:]
        ins = self.parser._findInstructionCode("InsReg", text.split(), b'')
        instruction = self.parser._buildBinaryCode(text.split()[0], "STATE1", arglist, ins)
        self.assertEqual(instruction, bytes((0b01110010,)) + bytes((0b00000001,)))

        text = "CALL #4"
        arglist = text.split()[1:]
        ins = self.parser._findInstructionCode("InsImm", text.split(), b'')
        instruction = self.parser._buildBinaryCode(text.split()[0], "STATE3", arglist, ins)
        immediate = 4
        expectedOutput = bytes((0b10000010,)) + immediate.to_bytes(4, byteorder='big')
        self.assertEqual(instruction, expectedOutput)

        text = "CALL label"
        arglist = text.split()[1:]
        ins = self.parser._findInstructionCode("InsImm", text.split(), b'')
        instruction = self.parser._buildBinaryCode(text.split()[0], "STATE3", arglist, ins)
        immediate = 4
        self.assertEqual(instruction, bytes((0b10000010,)) + b':label:')

    def test_buildBinaryCodeCMP(self):
        """
        Tests the method:
        _buildBinaryCodeFromInstructionAndArguments(self, ins, state, arglist, instruction)
        for the CMP instruction
        """

        text = "CMP $B $C"
        arglist = text.split()[1:]
        ins = self.parser._findInstructionCode("InsRegReg", text.split(), b'')
        instruction = self.parser._buildBinaryCode(text.split()[0], "STATE2", arglist, ins)
        self.assertEqual(instruction, bytes((0b10011010,)) + bytes((0b00010010,)))

        text = "CMP #4 $C"
        arglist = text.split()[1:]
        ins = self.parser._findInstructionCode("InsImmReg", text.split(), b'')
        instruction = self.parser._buildBinaryCode(text.split()[0], "STATE4", arglist, ins)
        immediate = 4
        expectedOutput = bytes((0b01101000,)) + immediate.to_bytes(4, byteorder='big') + bytes((0b00000010,))
        self.assertEqual(instruction, expectedOutput)

    def test_buildBinaryCodeDACTI(self):
        """
        Tests the method:
        _buildBinaryCodeFromInstructionAndArguments(self, ins, state, arglist, instruction)
        for the DACTI instruction
        """

        text = "DACTI"
        arglist = text.split()[1:]
        ins = self.parser._findInstructionCode("Ins", text.split(), b'')
        instruction = self.parser._buildBinaryCode(text.split()[0], "STATE0", arglist, ins)
        self.assertEqual(instruction, bytes((0b11110010,)))

    def test_buildBinaryCodeDIV(self):
        """
        Tests the method:
        _buildBinaryCodeFromInstructionAndArguments(self, ins, state, arglist, instruction)
        for the DIV instruction
        """

        text = "DIV $B $C"
        arglist = text.split()[1:]
        ins = self.parser._findInstructionCode("InsRegReg", text.split(), b'')
        instruction = self.parser._buildBinaryCode(text.split()[0], "STATE2", arglist, ins)
        self.assertEqual(instruction, bytes((0b10010101,)) + bytes((0b00010010,)))

    def test_buildBinaryCodeHIRET(self):
        """
        Tests the method:
        _buildBinaryCodeFromInstructionAndArguments(self, ins, state, arglist, instruction)
        for the HIRET instruction
        """

        text = "HIRET"
        arglist = text.split()[1:]
        ins = self.parser._findInstructionCode("Ins", text.split(), b'')
        instruction = self.parser._buildBinaryCode(text.split()[0], "STATE0", arglist, ins)
        self.assertEqual(instruction, bytes((0b11110011,)))

    def test_buildBinaryCodeINT(self):
        """
        Tests the method:
        _buildBinaryCodeFromInstructionAndArguments(self, ins, state, arglist, instruction)
        for the INT instruction
        """

        text = "INT $B"
        arglist = text.split()[1:]
        ins = self.parser._findInstructionCode("InsReg", text.split(), b'')
        instruction = self.parser._buildBinaryCode(text.split()[0], "STATE1", arglist, ins)
        self.assertEqual(instruction, bytes((0b01110110,)) + bytes((0b00000001,)))

        text = "INT #4"
        arglist = text.split()[1:]
        ins = self.parser._findInstructionCode("InsImm", text.split(), b'')
        instruction = self.parser._buildBinaryCode(text.split()[0], "STATE3", arglist, ins)
        immediate = 4
        expectedOutput = bytes((0b10000011,)) + immediate.to_bytes(4, byteorder='big')
        self.assertEqual(instruction, expectedOutput)

    def test_buildBinaryCodeJMP(self):
        """
        Tests the method:
        _buildBinaryCodeFromInstructionAndArguments(self, ins, state, arglist, instruction)
        for the JMP instruction
        """

        text = "JMP <> $B"
        arglist = text.split()[1:]
        ins = self.parser._findInstructionCode("InsFlagReg", text.split(), b'')
        instruction = self.parser._buildBinaryCode(text.split()[0], "STATE10", arglist, ins)
        self.assertEqual(instruction, bytes((0b01010001,)) + bytes((0b00000001,)))

        text = "JMP <> #4"
        arglist = text.split()[1:]
        ins = self.parser._findInstructionCode("InsFlagImm", text.split(), b'')
        instruction = self.parser._buildBinaryCode(text.split()[0], "STATE9", arglist, ins)
        immediate = 4
        expectedOutput = bytes((0b01000001,)) + bytes((0b00000000,)) + immediate.to_bytes(4, byteorder='big')
        self.assertEqual(instruction, expectedOutput)

        text = "JMP <E> label"
        arglist = text.split()[1:]
        ins = self.parser._findInstructionCode("InsFlagImm", text.split(), b'')
        instruction = self.parser._buildBinaryCode(text.split()[0], "STATE9", arglist, ins)
        immediate = 4
        self.assertEqual(instruction, bytes((0b01000001,)) + bytes((0b00000100,)) + b':label:')

    def test_buildBinaryCodeJMPR(self):
        """
        Tests the method:
        _buildBinaryCodeFromInstructionAndArguments(self, ins, state, arglist, instruction)
        for the JMPR instruction
        """

        text = "JMPR <> $B"
        arglist = text.split()[1:]
        ins = self.parser._findInstructionCode("InsFlagReg", text.split(), b'')
        instruction = self.parser._buildBinaryCode(text.split()[0], "STATE10", arglist, ins)
        self.assertEqual(instruction, bytes((0b01010000,)) + bytes((0b00000001,)))

        text = "JMPR <> #4"
        arglist = text.split()[1:]
        ins = self.parser._findInstructionCode("InsFlagImm", text.split(), b'')
        instruction = self.parser._buildBinaryCode(text.split()[0], "STATE9", arglist, ins)
        immediate = 4
        expectedOutput = bytes((0b01000000,)) + bytes((0b00000000,)) + immediate.to_bytes(4, byteorder='big')
        self.assertEqual(instruction, expectedOutput)

    def test_buildBinaryCodeMEMR(self):
        """
        Tests the method:
        _buildBinaryCodeFromInstructionAndArguments(self, ins, state, arglist, instruction)
        for the MEMR instruction
        """

        text = "MEMR [1] $B $C"
        arglist = text.split()[1:]
        ins = self.parser._findInstructionCode("InsWidthRegReg", text.split(), b'')
        instruction = self.parser._buildBinaryCode(text.split()[0], "STATE8", arglist, ins)
        self.assertEqual(instruction, bytes((0b00010000,)) + bytes((0b00010001,)) + bytes((0b00000010,)))

        text = "MEMR [1] #4 $B"
        arglist = text.split()[1:]
        ins = self.parser._findInstructionCode("InsWidthImmReg", text.split(), b'')
        instruction = self.parser._buildBinaryCode(text.split()[0], "STATE6", arglist, ins)
        immediate = 4
        expectedOutput = bytes((0b00000001,)) + bytes((0b00010001,)) + immediate.to_bytes(4, byteorder='big')
        self.assertEqual(instruction, expectedOutput)

    def test_buildBinaryCodeMEMW(self):
        """
        Tests the method:
        _buildBinaryCodeFromInstructionAndArguments(self, ins, state, arglist, instruction)
        for the MEMW instruction
        """

        text = "MEMW [1] $B $C"
        arglist = text.split()[1:]
        ins = self.parser._findInstructionCode("InsWidthRegReg", text.split(), b'')
        instruction = self.parser._buildBinaryCode(text.split()[0], "STATE8", arglist, ins)
        self.assertEqual(instruction, bytes((0b00010001,)) + bytes((0b00010001,)) + bytes((0b00000010,)))

        text = "MEMW [1] #4 $B"
        arglist = text.split()[1:]
        ins = self.parser._findInstructionCode("InsWidthImmReg", text.split(), b'')
        instruction = self.parser._buildBinaryCode(text.split()[0], "STATE6", arglist, ins)
        immediate = 4
        expectedOutput = bytes((0b00000000,)) + bytes((0b00010001,)) + immediate.to_bytes(4, byteorder='big')
        self.assertEqual(instruction, expectedOutput)

        text = "MEMW [1] $B #4"
        arglist = text.split()[1:]
        ins = self.parser._findInstructionCode("InsWidthRegImm", text.split(), b'')
        instruction = self.parser._buildBinaryCode(text.split()[0], "STATE7", arglist, ins)
        immediate = 4
        expectedOutput = bytes((0b00100000,)) + bytes((0b00010001,)) + immediate.to_bytes(4, byteorder='big')
        self.assertEqual(instruction, expectedOutput)

        text = "MEMW [1] #4 #6"
        arglist = text.split()[1:]
        ins = self.parser._findInstructionCode("InsWidthImmImm", text.split(), b'')
        instruction = self.parser._buildBinaryCode(text.split()[0], "STATE5", arglist, ins)
        immediate, immediate2 = 4, 6
        expectedOutput = bytes((0b00110000,)) + bytes((0b00000001,)) + immediate.to_bytes(4, byteorder='big') + \
                                                                       immediate2.to_bytes(4, byteorder='big')
        self.assertEqual(instruction, expectedOutput)

    def test_buildBinaryCodeMOV(self):
        """
        Tests the method:
        _buildBinaryCodeFromInstructionAndArguments(self, ins, state, arglist, instruction)
        for the MOV instruction
        """

        text = "MOV $B $C"
        arglist = text.split()[1:]
        ins = self.parser._findInstructionCode("InsRegReg", text.split(), b'')
        instruction = self.parser._buildBinaryCode(text.split()[0], "STATE2", arglist, ins)
        self.assertEqual(instruction, bytes((0b10011011,)) + bytes((0b00010010,)))

        text = "MOV #4 $B"
        arglist = text.split()[1:]
        ins = self.parser._findInstructionCode("InsImmReg", text.split(), b'')
        instruction = self.parser._buildBinaryCode(text.split()[0], "STATE4", arglist, ins)
        immediate = 4
        expectedOutput = bytes((0b01100000,)) + immediate.to_bytes(4, byteorder='big') + bytes((0b00000001,))
        self.assertEqual(instruction, expectedOutput)

        text = "MOV label $B"
        arglist = text.split()[1:]
        ins = self.parser._findInstructionCode("InsImmReg", text.split(), b'')
        instruction = self.parser._buildBinaryCode(text.split()[0], "STATE4", arglist, ins)
        self.assertEqual(instruction, bytes((0b01100000,)) + b':label:' + bytes((0b00000001,)))

    def test_buildBinaryCodeMUL(self):
        """
        Tests the method:
        _buildBinaryCodeFromInstructionAndArguments(self, ins, state, arglist, instruction)
        for the MUL instruction
        """

        text = "MUL $B $C"
        arglist = text.split()[1:]
        ins = self.parser._findInstructionCode("InsRegReg", text.split(), b'')
        instruction = self.parser._buildBinaryCode(text.split()[0], "STATE2", arglist, ins)
        self.assertEqual(instruction, bytes((0b10010100,)) + bytes((0b00010010,)))

    def test_buildBinaryCodeNOP(self):
        """
        Tests the method:
        _buildBinaryCodeFromInstructionAndArguments(self, ins, state, arglist, instruction)
        for the NOP instruction
        """

        text = "NOP"
        arglist = text.split()[1:]
        ins = self.parser._findInstructionCode("Ins", text.split(), b'')
        instruction = self.parser._buildBinaryCode(text.split()[0], "STATE0", arglist, ins)
        self.assertEqual(instruction, bytes((0b11111111,)))

    def test_buildBinaryCodeNOT(self):
        """
        Tests the method:
        _buildBinaryCodeFromInstructionAndArguments(self, ins, state, arglist, instruction)
        for the NOT instruction
        """

        text = "NOT $B"
        arglist = text.split()[1:]
        ins = self.parser._findInstructionCode("InsReg", text.split(), b'')
        instruction = self.parser._buildBinaryCode(text.split()[0], "STATE1", arglist, ins)
        self.assertEqual(instruction, bytes((0b01110000,)) + bytes((0b00000001,)))

    def test_buildBinaryCodeOR(self):
        """
        Tests the method:
         _buildBinaryCodeFromInstructionAndArguments(self, ins, state, arglist, instruction)
        for the OR instruction
        """

        text = "OR $B $C"
        arglist = text.split()[1:]
        ins = self.parser._findInstructionCode("InsRegReg", text.split(), b'')
        instruction = self.parser._buildBinaryCode(text.split()[0], "STATE2", arglist, ins)
        self.assertEqual(instruction, bytes((0b10011000,)) + bytes((0b00010010,)))

        text = "OR #4 $B"
        arglist = text.split()[1:]
        ins = self.parser._findInstructionCode("InsImmReg", text.split(), b'')
        instruction = self.parser._buildBinaryCode(text.split()[0], "STATE4", arglist, ins)
        immediate = 4
        expectedOutput = bytes((0b01100010,)) + immediate.to_bytes(4, byteorder='big') + bytes((0b00000001,))
        self.assertEqual(instruction, expectedOutput)

    def test_buildBinaryCodePOP(self):
        """
        Tests the method:
        _buildBinaryCodeFromInstructionAndArguments(self, ins, state, arglist, instruction)
        for the POP instruction
        """

        text = "POP $B"
        arglist = text.split()[1:]
        ins = self.parser._findInstructionCode("InsReg", text.split(), b'')
        instruction = self.parser._buildBinaryCode(text.split()[0], "STATE1", arglist, ins)
        self.assertEqual(instruction, bytes((0b01110100,)) + bytes((0b00000001,)))

    def test_buildBinaryCodePUSH(self):
        """
        Tests the method:
        _buildBinaryCodeFromInstructionAndArguments(self, ins, state, arglist, instruction)
        for the PUSH instruction
        """

        text = "PUSH $B"
        arglist = text.split()[1:]
        ins = self.parser._findInstructionCode("InsReg", text.split(), b'')
        instruction = self.parser._buildBinaryCode(text.split()[0], "STATE1", arglist, ins)
        self.assertEqual(instruction, bytes((0b01110011,)) + bytes((0b00000001,)))

        text = "PUSH #4"
        arglist = text.split()[1:]
        ins = self.parser._findInstructionCode("InsImm", text.split(), b'')
        instruction = self.parser._buildBinaryCode(text.split()[0], "STATE3", arglist, ins)
        immediate = 4
        expectedOutput = bytes((0b10000001,)) + immediate.to_bytes(4, byteorder='big')
        self.assertEqual(instruction, expectedOutput)

        text = "PUSH test"
        arglist = text.split()[1:]
        ins = self.parser._findInstructionCode("InsImm", text.split(), b'')
        instruction = self.parser._buildBinaryCode(text.split()[0], "STATE3", arglist, ins)
        self.assertEqual(instruction, bytes((0b10000001,)) + b':test:')

    def test_buildBinaryCodeRET(self):
        """
        Tests the method:
        _buildBinaryCodeFromInstructionAndArguments(self, ins, state, arglist, instruction)
        for the RET instruction
        """

        text = "RET"
        arglist = text.split()[1:]
        ins = self.parser._findInstructionCode("Ins", text.split(), b'')
        instruction = self.parser._buildBinaryCode(text.split()[0], "STATE0", arglist, ins)
        self.assertEqual(instruction, bytes((0b11110000,)))

    def test_buildBinaryCodeSFSTOR(self):
        """
        Tests the method:
        _buildBinaryCodeFromInstructionAndArguments(self, ins, state, arglist, instruction)
        for the SFSTOR instruction
        """

        text = "SFSTOR <E> $B"
        arglist = text.split()[1:]
        ins = self.parser._findInstructionCode("InsFlagReg", text.split(), b'')
        instruction = self.parser._buildBinaryCode(text.split()[0], "STATE10", arglist, ins)
        self.assertEqual(instruction, bytes((0b01010010,)) + bytes((0b01000001,)))

        text = "SFSTOR <LH> #4"
        arglist = text.split()[1:]
        ins = self.parser._findInstructionCode("InsFlagImm", text.split(), b'')
        instruction = self.parser._buildBinaryCode(text.split()[0], "STATE9", arglist, ins)
        immediate = 4
        expectedOutput = bytes((0b01000010,)) + bytes((0b00000011,)) + immediate.to_bytes(4, byteorder='big')
        self.assertEqual(instruction, expectedOutput)

    def test_buildBinaryCodeSIVR(self):
        """
        Tests the method:
        _buildBinaryCodeFromInstructionAndArguments(self, ins, state, arglist, instruction)
        for the SIVR instruction
        """

        text = "SIVR $B"
        arglist = text.split()[1:]
        ins = self.parser._findInstructionCode("InsReg", text.split(), b'')
        instruction = self.parser._buildBinaryCode(text.split()[0], "STATE1", arglist, ins)
        self.assertEqual(instruction, bytes((0b01110101,)) + bytes((0b00000001,)))

    def test_buildBinaryCodeSHL(self):
        """
        Tests the method:
        _buildBinaryCodeFromInstructionAndArguments(self, ins, state, arglist, instruction)
        for the SHL instruction
        """

        text = "SHL $B $C"
        arglist = text.split()[1:]
        ins = self.parser._findInstructionCode("InsRegReg", text.split(), b'')
        instruction = self.parser._buildBinaryCode(text.split()[0], "STATE2", arglist, ins)
        self.assertEqual(instruction, bytes((0b10010110,)) + bytes((0b00010010,)))

        text = "SHL #4 $B"
        arglist = text.split()[1:]
        ins = self.parser._findInstructionCode("InsImmReg", text.split(), b'')
        instruction = self.parser._buildBinaryCode(text.split()[0], "STATE4", arglist, ins)
        immediate = 4
        expectedOutput = bytes((0b01100101,)) + immediate.to_bytes(4, byteorder='big') + bytes((0b00000001,))
        self.assertEqual(instruction, expectedOutput)

    def test_buildBinaryCodeSHR(self):
        """
        Tests the method:
        _buildBinaryCodeFromInstructionAndArguments(self, ins, state, arglist, instruction)
        for the SHR instruction
        """

        text = "SHR $B $C"
        arglist = text.split()[1:]
        ins = self.parser._findInstructionCode("InsRegReg", text.split(), b'')
        instruction = self.parser._buildBinaryCode(text.split()[0], "STATE2", arglist, ins)
        self.assertEqual(instruction, bytes((0b10011001,)) + bytes((0b00010010,)))

        text = "SHR #4 $B"
        arglist = text.split()[1:]
        ins = self.parser._findInstructionCode("InsImmReg", text.split(), b'')
        instruction = self.parser._buildBinaryCode(text.split()[0], "STATE4", arglist, ins)
        immediate = 4
        expectedOutput = bytes((0b01100100,)) + immediate.to_bytes(4, byteorder='big') + bytes((0b00000001,))
        self.assertEqual(instruction, expectedOutput)

    def test_buildBinaryCodeSUB(self):
        """
        Tests the method:
        _buildBinaryCodeFromInstructionAndArguments(self, ins, state, arglist, instruction)
        For the SUB instruction
        """

        text = "SUB $B $C"
        arglist = text.split()[1:]
        ins = self.parser._findInstructionCode("InsRegReg", text.split(), b'')
        instruction = self.parser._buildBinaryCode(text.split()[0], "STATE2", arglist, ins)
        self.assertEqual(instruction, bytes((0b10010011,)) + bytes((0b00010010,)))

        text = "SUB #4 $B"
        arglist = text.split()[1:]
        ins = self.parser._findInstructionCode("InsImmReg", text.split(), b'')
        instruction = self.parser._buildBinaryCode(text.split()[0], "STATE4", arglist, ins)
        immediate = 4
        expectedOutput = bytes((0b01100111,)) + immediate.to_bytes(4, byteorder='big') + bytes((0b00000001,))
        self.assertEqual(instruction, expectedOutput)

    def test_buildBinaryCodeXOR(self):
        """
        Tests the method:
        _buildBinaryCodeFromInstructionAndArguments(self, ins, state, arglist, instruction)
        for the XOR instruction
        """

        text = "XOR $B $C"
        arglist = text.split()[1:]
        ins = self.parser._findInstructionCode("InsRegReg", text.split(), b'')
        instruction = self.parser._buildBinaryCode(text.split()[0], "STATE2", arglist, ins)
        expectedOutput = bytes((0b10010000,)) + bytes((0b00010010,))
        self.assertEqual(instruction, bytes((0b10010000,)) + bytes((0b00010010,)))

        text = "XOR #4 $B"
        arglist = text.split()[1:]
        ins = self.parser._findInstructionCode("InsImmReg", text.split(), b'')
        instruction = self.parser._buildBinaryCode(text.split()[0], "STATE4", arglist, ins)
        immediate = 4
        expectedOutput = bytes((0b01100011,)) + immediate.to_bytes(4, byteorder='big') + bytes((0b00000001,))
        self.assertEqual(instruction, expectedOutput)

    def test_buildBinaryCodeError(self):
        """
        Tests ValueErrors for the method:
        _buildBinaryCodeFromInstructionAndArguments(self, ins, state, arglist, instruction)
        """

        text = "XOR #4 $B"
        arglist = text.split()[1:]
        ins = self.parser._findInstructionCode("InsImmReg", text.split(), b'')

        try:
            self.parser._buildBinaryCode(text.split()[0], "STATE11", arglist, ins)
        except ValueError:
            pass
        else:
            raise AssertionError("ValueError was not raised")

    def test_translateTextFlagsToCodeFlags(self):
        """
        Test the method:
        translateTextFlagsToCodeFlags(self, textFlags):
        """
        self.assertEqual(0b000, self.parser.translateTextFlags(""))
        self.assertEqual(0b100, self.parser.translateTextFlags("Z"))  # Flag (Z)ero is set
        self.assertEqual(0b100, self.parser.translateTextFlags("E"))  # Flag (Z)ero is set
        self.assertEqual(0b010, self.parser.translateTextFlags("L"))  # Flag (L)ower is set
        self.assertEqual(0b110, self.parser.translateTextFlags("LE"))  # Flag (L)ower and Z(ero) are set
        self.assertEqual(0b110, self.parser.translateTextFlags("LZ"))  # Flag (L)ower and Z(ero) are set
        self.assertEqual(0b001, self.parser.translateTextFlags("H"))  # FLAG (H)igher is set
        self.assertEqual(0b101, self.parser.translateTextFlags("HE"))  # FLAG (H)igher and Z(ero) are set
        self.assertEqual(0b101, self.parser.translateTextFlags("HZ"))  # FLAG (H)igher and Z(ero) are set
        self.assertRaises(ValueError, self.parser.translateTextFlags, "F")  # Invalid flag

    def test_translateTextImmediateToImmediate(self):
        """
        Test the method:
        translateTextImmediateToImmediate(self, textImmediate: str=""):
        """
        self.assertEqual(0x0, self.parser.translateTextImmediate(textImmediate="0"))
        self.assertEqual(((0b1 ^ 0xFFFFFFFF) + 1), self.parser.translateTextImmediate(textImmediate="-1"))
        self.assertEqual(0b11, self.parser.translateTextImmediate(textImmediate="0b11"))
        self.assertEqual(0xFF, self.parser.translateTextImmediate(textImmediate="0xFF"))
        self.assertRaises(ValueError, self.parser.translateTextImmediate, "0xAAFFFFFFFF")

    def test_translateRegisterNameToRegisterCode(self):
        """
        Test the method:
        translateRegisterNameToRegisterCode(self, registerName: str=""):
        """
        self.assertEqual(0b00, self.parser.translateRegisterName(registerName="A"))
        self.assertEqual(0b01, self.parser.translateRegisterName(registerName="B"))
        self.assertEqual(0b10, self.parser.translateRegisterName(registerName="C"))
        self.assertEqual(0b11, self.parser.translateRegisterName(registerName="D"))
        self.assertEqual(0b100, self.parser.translateRegisterName(registerName="E"))
        self.assertEqual(0b101, self.parser.translateRegisterName(registerName="F"))
        self.assertEqual(0b110, self.parser.translateRegisterName(registerName="G"))
        self.assertEqual(0b111, self.parser.translateRegisterName(registerName="S"))
        self.assertEqual(0b1000, self.parser.translateRegisterName(registerName="A2"))
        self.assertEqual(0b1001, self.parser.translateRegisterName(registerName="B2"))
        self.assertEqual(0b1010, self.parser.translateRegisterName(registerName="C2"))
        self.assertEqual(0b1011, self.parser.translateRegisterName(registerName="D2"))
        self.assertEqual(0b1100, self.parser.translateRegisterName(registerName="E2"))
        self.assertEqual(0b1101, self.parser.translateRegisterName(registerName="F2"))
        self.assertEqual(0b1110, self.parser.translateRegisterName(registerName="G2"))
        self.assertEqual(0b1111, self.parser.translateRegisterName(registerName="S2"))
        self.assertRaises(ValueError, self.parser.translateRegisterName, "x")  # Invalid register





