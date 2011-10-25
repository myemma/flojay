import flojay
from unittest import TestCase
from nose.tools import eq_


class MarshalTests(TestCase):

    def test_marshal_empty(self):
        eq_([], flojay.marshal("[]"))
        eq_({}, flojay.marshal("{}"))

    def test_marshal_arrays_and_stuff(self):
        eq_(['a', 1, True], flojay.marshal('["a", 1, true]'))
        eq_(['a', 1, ['b', 2]], flojay.marshal('["a", 1, ["b", 2]]'))

    def test_marshal_returns_a_string_if_there_is_no_toplevel_container(self):
        eq_('a', flojay.marshal('"a"'))
        eq_('1.5', flojay.marshal('1.5'))
        eq_('null', flojay.marshal("null"))

    def test_marshal_object(self):
        eq_({'foo': 1}, flojay.marshal('{"foo": 1}'))
        eq_({'foo': 1, 'bar': 2}, flojay.marshal('{"foo": 1, "bar": 2}'))
        eq_({'foo': ["a", 1]}, flojay.marshal('{"foo": ["a", 1]}'))
        eq_({'foo': ["a", {'bar': {'bazz': 'see it\'s a nested dictionary'}}]},
            flojay.marshal('{"foo": ["a", {"bar": {"bazz": "see it\'s a nested dictionary"}}]}'))

    def test_exp(self):
        eq_([1e+27], flojay.marshal('[1e27]'))

    def test_stress(self):
        eq_(
            {"pushed_at": 1316639683.0,
             "args": [1365900, 2320,
                      [{"fields": {"first_name": "First Name"}, "email": "Email"},
                       {"fields": {"first_name": "Q."}, "email": "qa_tester8@rocketmail.com"},
                       {"fields": {"first_name": "Q."}, "email": "qa_tester5@rocketmail.com"},
                       {"fields": {"first_name": "Q."}, "email": "qa_tester4@rocketmail.com"},
                       {"fields": {"first_name": "Q."}, "email": "qa_tester1@rocketmail.com"},
                       {"fields": {"first_name": "Q."}, "email": "qa_tester7@rocketmail.com"},
                       {"fields": {"first_name": "Q."}, "email": "qa_tester6@rocketmail.com"},
                       {"fields": {"first_name": "Q."}, "email": "qa_tester3@rocketmail.com"},
                       {"fields": {"first_name": "Q."}, "email": "qa_tester2@rocketmail.com"}],
                      False, 
                      ["42178"]],
             "target_spec": "audience.jobs:import_members",
             "kwargs": {}},
            flojay.marshal(
            """
            {"pushed_at": 1316639683.0,
             "args": [1365900, 2320,
                 [{"fields": {"first_name": "First Name"}, "email": "Email"},
                  {"fields": {"first_name": "Q."}, "email": "qa_tester8@rocketmail.com"},
                  {"fields": {"first_name": "Q."}, "email": "qa_tester5@rocketmail.com"},
                  {"fields": {"first_name": "Q."}, "email": "qa_tester4@rocketmail.com"},
                  {"fields": {"first_name": "Q."}, "email": "qa_tester1@rocketmail.com"},
                  {"fields": {"first_name": "Q."}, "email": "qa_tester7@rocketmail.com"},
                  {"fields": {"first_name": "Q."}, "email": "qa_tester6@rocketmail.com"},
                  {"fields": {"first_name": "Q."}, "email": "qa_tester3@rocketmail.com"},
                  {"fields": {"first_name": "Q."}, "email": "qa_tester2@rocketmail.com"}],
                 false, ["42178"]],
             "target_spec": "audience.jobs:import_members",
             "kwargs": {}}
            """))

