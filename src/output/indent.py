from copy import copy

class Indent():
    '''
    Auto-indentation.
    '''
    def __init__(self, level=0):
        '''
        Initialize indentation level.
        '''
        self.level = level

    def inc(self):
        '''
        Increment indentation level.
        '''
        new = copy(self)
        new.level += 1
        return new

    def out(self):
        '''
        Output indentation.
        '''
        return '\t'*self.level
