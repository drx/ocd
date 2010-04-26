CC	= gcc
CFLAGS	= -std=c99 -Wall -W -O

SOURCES := $(wildcard *.c)
BINARIES := $(patsubst %.c, %, $(SOURCES))

all: $(BINARIES)

clean:
	rm $(BINARIES)
