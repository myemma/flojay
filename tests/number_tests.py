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
        p = flojay.Parser()
        p.parse("123", self)
        eq_(self.buf, "123")
        self.buf = ''
        p.parse("1", self)
        p.parse("23", self)
        eq_(self.buf, "123")

    def test_negative(self):
        p = flojay.Parser()
        p.parse("-123", self)
        eq_(self.buf, "-123")
        self.buf = ''
        p = flojay.Parser()
        p.parse('-', self)
        p.parse('123', self)
        eq_(self.buf, '-123')

    def test_negative_only_allowed_at_the_beginning(self):
        def syntax_error():
            p = flojay.Parser()
            p.parse("-", self)
            p.parse("-123", self)

        assert_raises(SyntaxError, syntax_error)

        def tst():
            p = flojay.Parser()
            p.parse("-1-1", self)

        assert_raises(SyntaxError, tst)

    def test_decimal(self):
        p = flojay.Parser()
        p.parse("123.1", self)
        eq_(self.buf, "123.1")

    def test_exp(self):
        for e in ['1e27', '1E27', '1E-27', '1e+27']:
            p = flojay.Parser()
            p.parse(e, self)
            eq_(self.buf, e)
            self.buf = ""

    def test_bad_decimals(self):
        def tst1():
            p = flojay.Parser()
            p.parse("123.1.2", self)

        def tst2():
            p = flojay.Parser()
            p.parse(".123", self)

        assert_raises(SyntaxError, tst1)
        assert_raises(SyntaxError, tst2)

    def test_bad_exp(self):
        def tst():
            p = flojay.Parser()
            p.parse("1e27E-3", self)

        assert_raises(SyntaxError, tst)
