# ocd - ocd C decompiler

**ocd** is a C decompiler written in Python, currently supporting decompilation of Linux programs compiled for the x64 architecture.

The decompiler tries to infer the program structure, performing control and data flow analysis.

If you'd like to learn how it works, check out my article on [how decompilers work](https://lukezapart.com/how-decompilers-work). 

More in-depth documentation is available in the [doc/ocd.md file](doc/ocd.md).

## Quick start

Run `./ocd program` to decompile `program` (e.g. `./ocd /usr/bin/yes`). 

There are some test programs in the `tests/` directory. To check them out, do `cd tests; make`, then for example run `./ocd tests/test_ack`.

Run `./ocd --help` to get more options.

## Requirements

* Python 3
* objdump

## Notes

* ocd uses [Immunity libdisassembly v2.0](https://web.archive.org/web/20140209154423/http://www.immunitysec.com/resources-freesoftware.shtml)

## Example

<table><tr><td valign="top">

```c
int ack(int m, int n)
{
    if (m == 0) 
        return n + 1;
    else
    {
        if (n == 0) 
            return ack(m - 1, 1);
        else 
            return ack(m - 1, ack(m, n - 1));
    }
}
int main()
{
    return printf("%d\n", ack(3, 4));
}
```

</td><td>

```c
int ack()
{
    var_0 = temp_2;
    var_1 = temp_3;
    var_2 = var_0 - 0;
    if (var2)
    {
        var_2 = var_1 - 0;
        if (var2)
        {
            temp_4 = ack(temp_5 - 1, ack(var_0, temp_4 - 1));
        }
        else
        {
            temp_4 = ack(temp_4 - 1, 1);
        }
    }
    else
    {
        temp_4 = temp_4 + 1;
    }
    return temp_4;
}
int main()
{
    return unknown_function("%d\n", ack(3, 4));
}
```

</tr>
<tr><td align="center">Original code</td><td align="center">ocd output</td></tr>
</table>
