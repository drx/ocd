# Introduction

ocd is a C decompiler written in Python, currently supporting decompilation of programs compiled for the x64 architecture. The internal data structures used for instructions are quite universal, so it should be trivial to add additional architectures as they are needed, as well as new output languages. The decompiler performs some inferences as to the program structure (such as control and data flow analysis).

# Using ocd

ocd reads a specified object file, performs decompilation on it and prints the results on standard output. It can also output a set of control flow graphs in dot format. 

The usage of the program is as follows:

    Usage: ocd [options] file

    Options:
      -h, --help            show this help message and exit
      -d OPTION, --debug=OPTION
                            turn debug option on
      -g FILE, --graph=FILE
                            output a control flow graph

An example control flow graph is shown below:

![A cfg example](images/cfg_example.png?raw=true)

# Operation

## Overview

The decompilation occurs in stages. The program is built to be modular and each stage is separate.

![Stages of decompilation](images/graph_stages.png?raw=true)

## Object dump

Currently, ocd executes the GNU utility objdump and retrieves the list of object exports from it.

## Disassembly

ocd supports decompilation of x86-64 and uses a slightly modified library called libdisassemble to disassemble code.

## Control flow analysis

### Control flow graph generation

A block of code is a list of instructions.

**B<sub>1</sub>** is a subblock of **B<sub>2</sub>** if **B<sub>1</sub>** is a sublist of **B<sub>2</sub>**.

A block of code **B** is uninterruptible if both of these conditions hold:

* no instruction jumps to an instruction within **B** other than the first (i.e. the only allowed entry point in **B** is its head)
* no instruction in **B**, other than the last, jumps (i.e. the only exit point in **B** is its last instruction)

A block of code **B** is maximally uninterruptible if it is interruptible and has both an entry point and an exit point.

A control flow graph **cfg<sub>B</sub>** of a code block **B** is a digraph **<V,E>**. The set of nodes **V** is the set of all maximally uninterruptible subblocks of **B**. An edge **<B_1, B_2> ∈ E** if and only if there is an instruction in **B<sub>1</sub>** that jumps to **B<sub>2</sub>**.

Generating the cfg of a block of code consists of finding all jumps in the block and then chopping the block into maximally interruptible blocks based on the list of jumps. 

### Control flow graph reduction

A cfg of a block of code gives insight into how control flows through the block of code and ideally gives insight into what the program structure was originally. 


<table>
  <tr>
    <th colspan="2">CFG patterns</th>
  </tr>
  <tr>
    <td>![if](images/cfg_if.png?raw=true)</td>
    <td>![if/else](images/cfg_ifelse.png?raw=true)</td>
  </tr>
  <tr>
    <td>if</td>
    <td>if/else</td>
  <tr>
    <td>![while](images/cfg_while.png?raw=true)</td>
    <td>![cons](images/cfg_cons.png?raw=true)</td>
  </tr>
  <tr>
    <td>while</td>
    <td>cons</td>
  <tr>
</table>

Logical structures can be recognized by finding patterns in the cfg. The patterns are listed above. The patterns are used to define a decreasing graph rewriting system (not unlike a context-sensitive grammar) in which a single step finds a pattern and contracts it to a single node containing information about the pattern's respective logical structure. Ideally, the fixed point of such a transformation will result in a single node containing the abstract syntax tree of the original program.

## Data flow analysis

### Variable inference

In this phase, instruction operands are substituted with newly assigned names.

## Computation collapse

In this phase, the program's computation is analyzed. Dead instructions are removed and others are folded into more coherent expressions. For example,

    a = a + 1
    b = a * 2
    n = 2
    n = b - a

might be converted into:

    n = (a+1)*2-a+1

## Program output

The program is output recursively on the cfgs of its symbols.
