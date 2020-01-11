# Brookshear Machine Assembler

## Background

The Brookshear Machine Model is a model of a simple computer with several
GP-Registers and a small fixed-width instruction set. It is freqeuntly used by
CS courses around the globe to teach students the basics of Computer
Architecture. An example of this instruction set (which is not compatible with
the implementation in this Repo though) can be found
[here](https://brookshear.jfagerberg.me/#). A compatible Brookshear machine can
be found here: [Github IO](http://joeledstrom.github.io/brookshear-emu/)

## Introduction

An Assembler translates Assembly Code to raw bytes (*Machine Language*). My
Python implementation follows the following instruction set.

### Instruction Set

All values are handled in two's complement representation unless stated
differently.

| OpCode        | Operands           | Description  |
| ------------- |:-------------:| -----:|
| 1     | RXY | Load Byte from Addr. XY into Reg. R |
| 2     | RXY      |   Load value XY into Reg. R |
| 3 | RXY      |    Store content of Reg. R into Addr. XY |
| 4 | 0RS      |    Move content of Reg. R into Reg. S |
| 5 | RST      |    Add contents of Reg. S and Reg. T and store result in Reg. R |
| 6 | RST      |    Add contents of Reg. S and Reg. T and store result in Reg. R (values in IEEE 754 8-bit FP format)|
| 7 | RST     |    OR contents of Reg. S and Reg. T and store result in Reg. R |
| 8 | RST      |    AND contents of Reg. S and Reg. T and store result in Reg. R |
| 9 | RST      |    XOR contents of Reg. S and Reg. T and store result in Reg. R |
| 0xA | R0X      |    Rotate content of Reg. R to the right by X places |
| 0xB | RXY      |    JUMP to Addr. XY if content of Reg. R equals content of Reg. 0 |
| 0xC | 000     |    Halt program execution |

## Assembly Instructions

| OpCode        | Operands           | Assembler Notation  |
| ------------- |:-------------:| -----:|
| 1     | RXY | LOAD R, XY |
| 2     | RXY      |  LOADI R, XY |
| 3 | RXY      |    STORE XY, R |
| 4 | 0RS      |    MOVE S, R |
| 5 | RST      |    ADD R, S, T |
| 6 | RST      |    ADD-FLOAT R, S, T |
| 7 | RST     |    OR R, S ,T |
| 8 | RST      |    AND R, S, T |
| 9 | RST      |    XOR R, S, T |
| 0xA | R0X      |    ROTATE-RIGHT R, X |
| 0xB | RXY      |    JUMP XY, R |
| 0xC | 000     |    HALT |

## To-Do

Currently, the assembler doesn't support labels.
