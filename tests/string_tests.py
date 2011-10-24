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
        p = flojay.Parser(self)
        p.parse('"test "')
        eq_(self.buf, "test ")

    def test_escaped_string(self):
        p = flojay.Parser(self)
        p.parse('"\\\"test\\\"\\\\"')
        eq_(self.buf, '"test"\\')
        eq_(self.begin, 1)
        eq_(self.end, 1)

    def test_partial(self):
        p = flojay.Parser(self)
        p.parse('"test')
        eq_(self.buf, "test")
        eq_(self.begin, 1)
        eq_(self.end, 0)

    def test_unicode(self):
        p = flojay.Parser(self)
        s = '"' + "".join(('\u%04x' % (ord(c)) for c in ('abcde'))) + '"'
        print s
        p.parse(s)
        eq_(self.buf, "abcde")
