import flojay
from flojay.exception import SyntaxError
from unittest import TestCase
from nose.tools import eq_, assert_raises


class ObjectTest(TestCase):
    def setUp(self):
        self.called_methods = []

    def __getattr__(self, attr):
        def _method(*args, **kwargs):
            self.called_methods.append(attr)
        return _method

    def test_empty(self):
        p = flojay.Parser()
        p.parse('{}', self)
        eq_(self.called_methods, ["handle_object_begin", "handle_object_end"])

    def test_pair(self):
        p = flojay.Parser()
        p.parse('{"a"', self)
        p.parse(': 1}', self)
        eq_(self.called_methods,
            ["handle_object_begin",
             "handle_object_key_begin",
             "handle_string_begin",
             "handle_string_character",
             "handle_string_end",
             "handle_object_key_end",
             "handle_object_value_begin",
             "handle_number_begin",
             "handle_number_character",
             "handle_number_end",
             "handle_object_value_end",
             "handle_object_end"])

    def test_two(self):
        p = flojay.Parser()
        p.parse('{"a": 1,"b": 2}', self)
        eq_(self.called_methods,
            ["handle_object_begin",
             "handle_object_key_begin",
             "handle_string_begin",
             "handle_string_character",
             "handle_string_end",
             "handle_object_key_end",
             "handle_object_value_begin",
             "handle_number_begin",
             "handle_number_character",
             "handle_number_end",
             "handle_object_value_end",
             "handle_object_key_begin",
             "handle_string_begin",
             "handle_string_character",
             "handle_string_end",
             "handle_object_key_end",
             "handle_object_value_begin",
             "handle_number_begin",
             "handle_number_character",
             "handle_number_end",
             "handle_object_value_end",
             "handle_object_end"])

    def test_syntax_errors(self):
        for s in ['{a:1}', '{"a":}', '{"a" 1}', '{"a": 1,}', '{"a": 1, 2}', '{"a": 1 "b": 2}']:
            def tst():
                p = flojay.Parser()
                p.parse(s, self)
            assert_raises(SyntaxError, tst)
