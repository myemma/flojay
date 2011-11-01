import flojay
from flojay.exception import SyntaxError
from unittest import TestCase
from nose.tools import eq_, assert_raises


class ArrayTests(TestCase):
    def setUp(self):
        self.called_methods = []

    def __getattr__(self, attr):
        def _method(*args, **kwargs):
            self.called_methods.append(attr)
        return _method

    def test_array(self):
        p = flojay.Parser()
        p.parse('["a]",1,true]', self)

        eq_(self.called_methods,
            ["handle_array_begin",
             "handle_array_element_begin",
             "handle_string_begin",
             "handle_string_character",
             "handle_string_end",
             "handle_array_element_end",
             "handle_array_element_begin",
             "handle_number_begin",
             "handle_number_character",
             "handle_number_end",
             "handle_array_element_end",
             "handle_array_element_begin",
             "handle_atom_begin",
             "handle_atom_character",
             "handle_atom_end",
             "handle_array_element_end",
             "handle_array_end"])

    def test_nested_array(self):
        p = flojay.Parser()
        p.parse('[[1],2]', self)

        eq_(self.called_methods,
            ["handle_array_begin",
             "handle_array_element_begin",
             "handle_array_begin",
             "handle_array_element_begin",
             "handle_number_begin",
             "handle_number_character",
             "handle_number_end",
             "handle_array_element_end",
             "handle_array_end",
             "handle_array_element_end",
             "handle_array_element_begin",
             "handle_number_begin",
             "handle_number_character",
             "handle_number_end",
             "handle_array_element_end",
             "handle_array_end"])

    def test_empty(self):
        p = flojay.Parser()
        p.parse('[]', self)
        eq_(self.called_methods, ["handle_array_begin", "handle_array_end"])

    def test_one(self):
        p = flojay.Parser()
        p.parse('[1]', self)
        eq_(self.called_methods,
            ["handle_array_begin",
             "handle_array_element_begin",
             "handle_number_begin",
             "handle_number_character",
             "handle_number_end",
             "handle_array_element_end",
             "handle_array_end"])

    def test_two(self):
        p = flojay.Parser()
        p.parse('[1,2]', self)
        eq_(self.called_methods,
            ["handle_array_begin",
             "handle_array_element_begin",
             "handle_number_begin",
             "handle_number_character",
             "handle_number_end",
             "handle_array_element_end",
             "handle_array_element_begin",
             "handle_number_begin",
             "handle_number_character",
             "handle_number_end",
             "handle_array_element_end",
             "handle_array_end"])

    def test_syntax_errors(self):
        for s in ['[,null]', '[null,]', '[null,,null]', '[null}',
                  '[null null]']:
            def tst():
                p = flojay.Parser()
                print "Trying " + s
                p.parse(s, self)
            assert_raises(SyntaxError, tst)
