import flojay
from unittest import TestCase
from nose.tools import eq_, raises


class UnmarshalTests(TestCase):
    def encode(self, it):
        return flojay.JSONEncoder().iterencode(it)

    def test_unmarshal(self):
        encoder = flojay.JSONEncoder(buffer_size=1)
        gen = encoder.iterencode(["a"])
        eq_(gen.next(), '["a"')
        eq_(gen.next(), ']')

    def test_unary(self):
        eq_(''.join(self.encode('this is just a flat  string')),
                    '"this is just a flat  string"')

        eq_(''.join(self.encode(1)), "1")

    def test_unmarshal_nested_array(self):
        gen = self.encode(['a', ['b', 1.0, ['d']]])
        eq_(''.join(gen), '["a",["b",1.0,["d"]]]')
        eq_(''.join(self.encode([])), '[]')

    def test_dict(self):
        eq_(''.join(self.encode({})), '{}')
        gen = self.encode({u'key': 3.14})
        eq_(''.join(gen), '{"key":3.14}')
        gen = self.encode({'a': 1, 'b': 2})
        eq_(''.join(gen), '{"a":1,"b":2}')

    def test_true_false_null(self):
        eq_(''.join(self.encode([True, False, None])), \
                '[true,false,null]')

    def test_longs(self):
        result = ''.join(self.encode([100L]))
        eq_(result, '[100]')

    def test_unicode(self):
        result = ''.join(self.encode([u'test']))
        eq_(result, '["test"]')
        eq_(result, str(result))

    def test_generator(self):
        def empty():
            if False is True:
                yield "Impossible!"

        def generator():
            yield 1
            yield 2
            yield ['a', 'b', 'c']

        def generator_with_dict():
            yield {'a': 1, 'b': 2}

        eq_(''.join(self.encode([generator(), 3])),
            '[[1,2,["a","b","c"]],3]')
        eq_(''.join(self.encode(empty())), '[]')
        eq_(''.join(self.encode(generator_with_dict())), '[{"a":1,"b":2}]')

    def test_custom_object_handlerer(self):
        import datetime

        def handle_custom_json(obj):
            if isinstance(obj, datetime.datetime):
                return obj.strftime('@D:%Y-%m-%d')
            else:
                raise TypeError("Can't encode this " + repr(obj))

        encoder = flojay.JSONEncoder(default=handle_custom_json)

        eq_(''.join(encoder.iterencode(
                    ['date', datetime.datetime(2012, 3, 17)])),
            '["date","@D:2012-03-17"]')

    @raises(TypeError)
    def test_unknown_object_type(self):
        ''.join(self.encode({'self': self}))

    def test_string_escape(self):
        s = '"A Good Man Is Hard To Find" by Flannery O\'Connor'

        eq_(''.join(self.encode([s])),
            '["\\"A Good Man Is Hard To Find\\" by Flannery O\'Connor"]')

        s = 'C:\DOS>'
        eq_(''.join(self.encode([s])),
            '["C:\\\\DOS>"]')

        s = "I have eaten\nthe plums\nthat were in\n..."
        eq_(''.join(self.encode([s])),
            '["I have eaten\\nthe plums\\nthat were in\\n..."]')

    # I want to implement this sometime, but it's not really
    # necessary.
    # def test_ascii(self):
    #     eq_(
    #         ''.join(flojay.JSONEncoder(ensure_ascii=True).\
    #         iterencode([u'Hern\xc3n'])),
    #         '["Hern\u00c3n"]'
    #     )

    def test_utf8(self):
        eq_(
            ''.join(flojay.JSONEncoder().\
            iterencode([u'Hern\xc3n'])),
            '["' + u'Hern\xc3n'.encode('utf8') + '"]'
        )

    def test_beautify(self):
        beauty = ''.join(flojay.JSONEncoder(beautify=True, indent_string=' ').\
                iterencode(['a', {'b':2, 'c':3}]))
        eq_(
            beauty,
            '[\n "a",\n {\n  "c": 3,\n  "b": 2\n }\n]\n')
