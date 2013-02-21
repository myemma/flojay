import flojay
from unittest import TestCase
from nose.tools import eq_, raises


class EventBasedParserTests(TestCase):

    def test_number_callback(self):
        callbacks = UnaryCallbacks()
        p = flojay.JSONEventParser(callbacks)
        long_int = 1 + (2 ** 32)
        p.parse("[")
        p.parse("123,")
        p.parse("1.91")
        p.parse("," + str(long_int))
        p.parse(",-1, 1e27]")
        eq_(callbacks.buf, [123, 1.91, long_int, -1, 1e+27])

    def test_null_callback(self):
        callbacks = UnaryCallbacks()
        p = flojay.JSONEventParser(callbacks)
        p.parse("[null]")
        eq_(callbacks.buf, [None])

    def test_partial_nulls(self):
        callbacks = UnaryCallbacks()
        p = flojay.JSONEventParser(callbacks)
        p.parse("[nu")
        p.parse("ll]")
        eq_(callbacks.buf, [None])

    def test_boolean_callback(self):
        callbacks = UnaryCallbacks()
        p = flojay.JSONEventParser(callbacks)
        p.parse("[true, false, true]")
        eq_(callbacks.buf, [True, False, True])

    def test_string_callback(self):
        callbacks = UnaryCallbacks()
        p = flojay.JSONEventParser(callbacks)
        p.parse(u'["String", "Ren\xc3e"]')
        eq_(callbacks.buf, [u"String", u"Ren\xc3e"])

    def test_start_end_map(self):
        callbacks = MapCallbacks()
        p = flojay.JSONEventParser(callbacks)
        p.parse(u'{}')
        eq_(callbacks.buf, ['{', '}'])

    def test_map_key(self):
        callbacks = MapCallbacks()
        p = flojay.JSONEventParser(callbacks)
        p.parse(u'{"Ren\xc3e": 119}')
        eq_(callbacks.buf, ['{', u"Ren\xc3e", 119, '}'])

    def test_array_start_end(self):
        callbacks = ArrayCallbacks()
        p = flojay.JSONEventParser(callbacks)
        p.parse(u'[[], []]')
        eq_(callbacks.buf, ['[', '[', ']', '[', ']', ']'])

    @raises(AttributeError)
    def test_raises_exception_on_undefined_handlers(self):
        p = flojay.JSONEventParser(self)
        p.parse('[]')

    @raises(ZeroDivisionError)
    def test_exceptions_from_callbacks_are_propogated(self):
        flojay.JSONEventParser(CallbacksRaiseAnException()).\
            parse('[]')

    @raises(ValueError)
    def test_syntax_error_bad_map(self):
        flojay.JSONEventParser(NullCallbacks()).\
            parse('{[]: "a"}')

    @raises(ValueError)
    def test_syntax_error_missing_delimiter(self):
        flojay.JSONEventParser(NullCallbacks()).\
            parse('["1" "2" "3"]')

    @raises(ValueError)
    def test_syntax_error_mismatches(self):
        flojay.JSONEventParser(NullCallbacks()).\
            parse('[[}]')


class UnaryCallbacks(object):
    def __init__(self):
        self.buf = []

    def handle_start_array(self):
        pass

    def handle_end_array(self):
        pass

    def handle_number(self, number):
        self.buf.append(number)

    def handle_null(self):
        self.buf.append(None)

    def handle_boolean(self, value):
        self.buf.append(value)

    def handle_string(self, string):
        self.buf.append(string)


class MapCallbacks(object):
    def __init__(self):
        self.buf = []

    def handle_number(self, number):
        self.buf.append(number)

    def handle_map_key(self, key):
        self.buf.append(key)

    def handle_start_map(self):
        self.buf.append('{')

    def handle_end_map(self):
        self.buf.append('}')


class ArrayCallbacks(object):
    def __init__(self):
        self.buf = []

    def handle_start_array(self):
        self.buf.append('[')

    def handle_end_array(self):
        self.buf.append(']')


class CallbacksRaiseAnException(object):
    def handle_end_array(self):
        return 1 / 0

    def handle_start_array(self):
        return 1 / 0


class NullCallbacks(object):
    def handle_start_map(self):
        pass

    def handle_end_map(self):
        pass

    def handle_map_key(self, key):
        pass

    def handle_string(self, blah):
        pass

    def handle_end_array(self):
        pass

    def handle_start_array(self):
        pass
