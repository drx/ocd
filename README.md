# ocd - ocd C decompiler

## Quick introduction

**ocd** is a C decompiler written in Python, currently supporting decompilation of programs compiled for the x64 architecture.

The decompiler tries to infer the program structure, performing control and data flow analysis.

More in-depth documentation is available in the `doc/` directory.

## Quick start

Run `./ocd $program` (e.g. `./ocd /usr/bin/yes`) to decompile `$program`. 

There are some tests in the `tests/` directory. To check them out, do `cd tests; make`, then for example run `./ocd tests/test_ack`.

Run `./ocd --help` to get more options.

## Requirements

* Python 3
* objdump

## Notes

ocd uses [Immunity libdisassembly v2.0](http://www.immunitysec.com/resources-freesoftware.shtml).

