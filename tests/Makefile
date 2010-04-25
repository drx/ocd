CC	= gcc
CFLAGS	= -std=c99 -Wall -W -O0

SOURCES := $(wildcard *.c)
BINARIES := $(patsubst %.c, %, $(SOURCES))

all: $(BINARIES)

clean:
	rm $(BINARIES)
