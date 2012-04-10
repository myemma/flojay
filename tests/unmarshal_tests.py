import flojay
from unittest import TestCase
from nose.tools import eq_

class UnmarshalTests(TestCase):
    def test_unmarshal(self):
        gen = flojay.unmarshal(['a'])
        eq_(gen.next(), '[')
        eq_(gen.next(), '"a"')
        eq_(gen.next(), ']')

    def test_unmarshal_nested_array(self):
        gen = flojay.unmarshal(['a', ['b', 1.0, ['d']]])
        eq_(''.join(gen), '["a",["b",1.0,["d"]]]')
        eq_(''.join(flojay.unmarshal([])), '[]')

    def test_dict(self):
        eq_(''.join(flojay.unmarshal({})), '{}')
        gen = flojay.unmarshal({u'key': 3.14})
        eq_(''.join(gen), '{"key":3.14}')
        gen = flojay.unmarshal({'a': 1, 'b': 2})
        eq_(''.join(gen), '{"a":1,"b":2}')

    def test_true_false_null(self):
        eq_(''.join(flojay.unmarshal([True, False, None])), \
                '[true,false,null]')

    def test_longs(self):
        result = ''.join(flojay.unmarshal([100L]))
        eq_(result, '[100]')

    def test_unicode(self):
        result = ''.join(flojay.unmarshal([u'test']))
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

        eq_(''.join(flojay.unmarshal(empty())), '[]')
        eq_(''.join(flojay.unmarshal([generator(), 3])),
            '[[1,2,["a","b","c"]],3]')

    def test_custom_object_handlerer(self):
        import datetime

        def handle_custom_json(obj):
            if isinstance(obj, datetime.datetime):
                return (True, obj.strftime('@D:%Y-%m-%d'))
            else:
                return (False, None)

        eq_(''.join(flojay.unmarshal(
                    ['date', datetime.datetime(2012, 3, 17)],
                    type_handler=handle_custom_json)),
            '["date",@D:2012-03-17]')

    def test_string_escape(self):
        s = '"A Good Man Is Hard To Find" by Flannery O\'Connor'

        eq_(''.join(flojay.unmarshal([s])),
            '["\\"A Good Man Is Hard To Find\\" by Flannery O\'Connor"]')

        s = 'C:\DOS>'
        eq_(''.join(flojay.unmarshal([s])),
            '["C:\\\\DOS>"]')

        s = "I have eaten\nthe plums\nthat were in\n..."
        print s
        eq_(''.join(flojay.unmarshal([s])),
            '["I have eaten\\nthe plums\\nthat were in\\n..."]')

    def test_utf8(self):
        eq_(''.join(flojay.unmarshal(
                    ['Hern\xe1n'])),
            '["Hern\xe1n"]')
