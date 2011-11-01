import flojay
from unittest import TestCase
from nose.tools import eq_, assert_raises


class StringTests(TestCase):
    def setUp(self):
        self.buf = ""
        self.begin = 0
        self.end = 0

    def handle_string_begin(self):
        self.begin = 1

    def handle_string_character(self, c):
        self.buf += c

    def handle_string_end(self):
        self.end = 1

    def test_string(self):
        p = flojay.Parser()
        p.parse('"test "', self)
        eq_(self.buf, "test ")

    def test_escaped_string(self):
        p = flojay.Parser()
        p.parse('"\\\"test\\\"\\\\"', self)
        eq_(self.buf, '"test"\\')
        eq_(self.begin, 1)
        eq_(self.end, 1)
        self.buf = ''
        p.parse('"\\', self)
        p.parse('"', self)
        eq_(self.buf, '"')

    def test_partial(self):
        p = flojay.Parser()
        p.parse('"test', self)
        eq_(self.buf, "test")
        eq_(self.begin, 1)
        eq_(self.end, 0)

    def test_string_segments(self):
        p = flojay.Parser()
        p.parse('"test ', self)
        p.parse('parsing of ', self)
        p.parse('a string that is all busted out into chunks."', self)
        eq_(self.buf, "test parsing of a string that is all busted out into chunks.")

    def test_unicode(self):
        p = flojay.Parser()
        s = '"' + "".join(('\u%04x' % (ord(c)) for c in ('abcde'))) + '"'
        p.parse(s, self)
        eq_(self.buf, "abcde")
        self.buf = ''
        p.parse(s[0:2], self)
        p.parse(s[2:-1], self)
        eq_(self.buf, "abcde")
