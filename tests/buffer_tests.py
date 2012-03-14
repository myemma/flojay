import flojay
from unittest import TestCase
from nose.tools import eq_, assert_raises

class BufferTests(TestCase):
    def test_skip_whitespace(self):
        b = flojay.Buffer("s    abcd")
        b.take()
        b.skip_whitespace()
        eq_("a", b.peek())

    def test_take_until(self):
        b = flojay.Buffer("abcd")
        eq_("", b.take_until(set("a")))
        eq_("a", b.take_until(set("b")))
        eq_("bcd", b.take_until(set("z")))
