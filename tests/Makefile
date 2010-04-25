ZAD	= test1
CC	= gcc
CFLAGS	=-std=c99 -Wall -W -O0 -static -lm

all:	$(ZAD)

$(ZAD):	$(ZAD).c
	$(CC) -o $@ $< $(CFLAGS)

clean:
	rm $(ZAD)
