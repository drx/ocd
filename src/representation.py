import output.c

def output_functions(functions, lang='C'):
    '''
    Output all functions in a selected language.
    '''
    langs = {
        'C': output.c
    }
    return langs[lang].output(functions)
