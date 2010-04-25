T0	= test_return_0
T1	= test_add
T2	= test_add_var
CC	= gcc
CFLAGS	= -std=c99 -Wall -W -O0

all:	$(T0) $(T1) $(T2)

$(T0):	$(T0).c
	$(CC) -o $@ $< $(CFLAGS)

$(T1):	$(T1).c
	$(CC) -o $@ $< $(CFLAGS)

$(T2):	$(T2).c
	$(CC) -o $@ $< $(CFLAGS)

clean:
	rm $(T0) $(T1) $(T2)
