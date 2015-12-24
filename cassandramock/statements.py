# -*- coding: utf-8 -*-

class Statement(object):
    """The super class of all query statement
    """
    pass

class PreparedStatement(Statement):
    """for prepare method of session
    """
    
    def __init__(self, query):
        """The query is just of interpolation
        """
        self.statement = query
        self.py_format = query.replace('?', "{}")
        print "in ps", self.py_format
    def bind(self, vals_tuple):
        tup = []
        for term in vals_tuple:
            if type(term) == str:
                tup.append("'{}'".format(term))
            else:
                tup.append(term)
        return self.py_format.format(*tup)
