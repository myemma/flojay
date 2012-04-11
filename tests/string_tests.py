import flojay
from unittest import TestCase
from nose.tools import eq_, assert_raises
from StringIO import StringIO



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

    def test_some_other_thing(self):
        p = flojay.Parser()
        h = flojay.MarshallEventHandler()
        x = StringIO('[{"fields": {"first_name": "Robert", "last_name": "Church"}, "email": "rchurch@myemma.com"}, {"fields": {"first_name": "Hern\xc3n", "last_name": "Ciudad"}, "email": "hciudad@myemma.com"}]')

        while 1:
            buf = x.read(1)
            if not buf:
                break
            p.parse(buf, h)
        a = h.current_thing
        eq_(a,
            [dict(email=u'rchurch@myemma.com',
                  fields=dict(last_name='Church',
                              first_name='Robert')),
             dict(email=u'hciudad@myemma.com',
                  fields=dict(last_name='Ciudad',
                              first_name='Hern\xc3n'))])
        