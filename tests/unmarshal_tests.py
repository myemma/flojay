import flojay
from unittest import TestCase
from nose.tools import eq_

class UnmarshalTests(TestCase):
    def test_unmarshal(self):
        gen = flojay.unmarshal(['a'])
        eq_(gen.next(), '[')
        eq_(gen.next(), '"')
        eq_(gen.next(), 'a')
        eq_(gen.next(), '"')
        eq_(gen.next(), ']')

    def test_unmarshal_nested_array(self):
        gen = flojay.unmarshal(['a', ['b', 1.0, ['d']]])
        eq_(''.join(gen), '["a",["b",1.0,["d"]]]')
        eq_(''.join(flojay.unmarshal([])), '[]')

    def test_dict(self):
        eq_(''.join(flojay.unmarshal({})), '{}')
        gen = flojay.unmarshal({'key': 3.14})
        eq_(''.join(gen), '{"key":3.14}')
        gen = flojay.unmarshal({'a': 1, 'b': 2})
        eq_(''.join(gen), '{"a":1,"b":2}')

    def test_true_false_null(self):
        eq_(''.join(flojay.unmarshal([True, False, None])), \
                '[true,false,null]')
