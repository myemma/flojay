import flojay
from flojay.exception import SyntaxError
from unittest import TestCase
from nose.tools import eq_, assert_raises


class AtomTests(TestCase):
    def setUp(self):
        self.buf = ""
        self.begin = 0
        self.end = 0

    def handle_atom_character(self, c):
        self.buf += c

    def handle_atom_begin(self):
        self.begin = 1

    def handle_atom_end(self):
        self.end = 1

    def test_flag(self):
        def tst():
            p = flojay.Parser(self)
            p.parse("truf")
        assert_raises(SyntaxError, tst)

    def test_false(self):
        p = flojay.Parser(self)
        p.parse("false")
        eq_(self.buf, "false")

    def test_true(self):
        p = flojay.Parser(self)
        p.parse("true")
        eq_(self.buf, "true")

    def test_null(self):
        p = flojay.Parser(self)
        p.parse("null")
        eq_(self.buf, "null")

    def test_partial(self):
        p = flojay.Parser(self)
        p.parse("nu")
        p.parse("ll")
        eq_(self.buf, "null")
