import flojay
from flojay.exception import SyntaxError
from unittest import TestCase
from nose.tools import eq_, assert_raises


class NumberTests(TestCase):
    def setUp(self):
        self.buf = ""
        self.begin = 0
        self.end = 0

    def handle_number_character(self, c):
        self.buf += c

    def handle_number_begin(self):
        self.begin += 1

    def handle_number_end(self):
        self.end += 1

    def test_number(self):
        p = flojay.Parser(self)
        p.parse("123")
        eq_(self.buf, "123")

    def test_negative(self):
        p = flojay.Parser(self)
        p.parse("-123")
        eq_(self.buf, "-123")

    def test_decimal(self):
        p = flojay.Parser(self)
        p.parse("123.1")
        eq_(self.buf, "123.1")

    def test_exp(self):
        for e in ['1e27', '1E27', '1E-27', '1e+27']:
            p = flojay.Parser(self)
            p.parse(e)
            eq_(self.buf, e)
            self.buf = ""

    def test_bad_decimals(self):
        def tst1():
            p = flojay.Parser(self)
            p.parse("123.1.2")

        def tst2():
            p = flojay.Parser(self)
            p.parse(".123")

        assert_raises(SyntaxError, tst1)
        assert_raises(SyntaxError, tst2)

    def test_bad_negatives(self):
        def tst():
            p = flojay.Parser(self)
            p.parse("-1-1")

        assert_raises(SyntaxError, tst)

    def test_bad_exp(self):
        def tst():
            p = flojay.Parser(self)
            p.parse("1e27E-3")

        assert_raises(SyntaxError, tst)
