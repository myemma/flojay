import flojay
from unittest import TestCase
from nose.tools import eq_, raises


class DecoderCallbackTests(TestCase):
    def loads(self, json_string):
        callbacks = flojay.PythonDecoderCallbacks()
        p = flojay.JSONEventParser(callbacks)
        p.parse(json_string)
        root = callbacks.root
        print "root is ", root
        return root
        
    def test_array_of_numbers(self):
        eq_(self.loads("[1, 2, 3]"),
            [1, 2, 3])

    def test_nested_array_of_numbers(self):
        root = self.loads("[1, [2, [4, 5], 6]]")
        eq_(root, 
            [1, [2, [4, 5], 6]])

    def test_strings_booleans_and_none(self):
        eq_(self.loads(u'["Ren\xc3e", false, true, null, null]'),
            [u"Ren\xc3e", False, True, None, None])

    def test_simple_map(self):
        eq_(self.loads('{"a": 1, "b": 2, "c": 3}'),
            {"a": 1, "b": 2, "c": 3})

    def test_nested_map(self):
        eq_(self.loads('{"a": {"a": 1}, "b": {"bb": {"c": {"cc": 3}}, "d": 4}}'),
            {"a": {"a": 1}, "b": {"bb": {"c": {"cc": 3}}, "d": 4}})

    def test_arrays_and_maps_together(self):
        eq_(self.loads('[{"a": [1, 2, {"b": 3}]}, "c", [{"d": 4}, "e", [{}], []]]'),
            [{"a": [1, 2, {"b": 3}]}, "c", [{"d": 4}, "e", [{}], []]])

    def test_root_with_partial_results(self):
        callbacks = flojay.PythonDecoderCallbacks()
        p = flojay.JSONEventParser(callbacks)
        p.parse('["a","b')
        eq_(callbacks.root, ["a"])
        p.parse('", {"c":')
        eq_(callbacks.root, ["a", "b"])
        p.parse('1, "d": 2,')
        eq_(callbacks.root, ["a", "b"])
        p.parse('"e": 3}, "f"]')
        eq_(callbacks.root, ["a", "b", {"c": 1, "d": 2, "e": 3}, "f"])

    def test_root_can_be_empited_out_now_and_again_with_no_apparent_ill_effects(self):
        callbacks = flojay.PythonDecoderCallbacks()
        p = flojay.JSONEventParser(callbacks)
        p.parse('["a", "b"')
        eq_(callbacks.root, ["a", "b"])
        del callbacks.root[0:1]
        eq_(callbacks.root, [])
        p.parse(', "c", "d"')
        eq_(callbacks.root, ["c", "d"])
        p.parse("]")
        eq_(callbacks.root, ["c", "d"])
