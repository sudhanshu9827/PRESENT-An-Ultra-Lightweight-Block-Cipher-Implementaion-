TARGET = simpleserial-present

PLATFORM ?= CW308_STM32F3

CRYPTO_TARGET = NONE

FIRMWAREPATH = ..

SRC += present.c
SRC += simpleserial-present.c

VPATH += .

EXTRAINCDIRS += .

SS_VER = SS_VER_1_1

CDEFS += -DSS_VER=$(SS_VER)

include $(FIRMWAREPATH)/Makefile.inc
