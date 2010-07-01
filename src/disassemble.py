import disassemblers.x64

def disassemble(buf, virt, sections, binary, arch='x64'):
    archs = {
        'x64': disassemblers.x64

    }
    return archs[arch].disassemble(buf, virt, sections, binary)
