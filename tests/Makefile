CC	= gcc
CFLAGS	= -std=c99 -Wall -W -O0 -m64

SOURCES := $(wildcard *.c)
BINARIES := $(patsubst %.c, %, $(SOURCES))

all: $(BINARIES)	

clean:
	rm $(BINARIES)
