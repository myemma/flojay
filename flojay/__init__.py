from flojay.state import ParserState, ValueState
from flojay.string_state import StringState
from flojay.number import NumberState
from flojay.atom import AtomState
from flojay.exception import SyntaxError
import string


class ToplevelState(ParserState):
    def enter_array_state(self):
        self.enter_state(ArrayState)
        self.parser.invoke_handler_for_array_begin()
        self.parser.invoke_handler_for_array_element_begin()

    def enter_string_state(self):
        self.enter_state(StringState)
        self.parser.invoke_handler_for_string_begin()

    def enter_atom_state(self, atom):
        self.enter_state(AtomState, atom)
        self.parser.invoke_handler_for_atom_begin()    

    def enter_number_state(self):
        self.enter_state(NumberState)
        self.parser.invoke_handler_for_number_begin()

    def parse_teriminal_char(self, c):
        raise SyntaxError

    def parse_char(self, c):
        if c == '"':
            self.enter_string_state()
        elif c in string.digits + '-':
            self.enter_number_state()
            self.parser.parse_char(c)
        elif c == 't':
            self.enter_atom_state('true')
            self.parser.parse_char(c)
        elif c == 'f':
            self.enter_atom_state('false')
            self.parser.parse_char(c)
        elif c == 'n':
            self.enter_atom_state('null')
            self.parser.parse_char(c)
        elif c == '[':
            self.enter_array_state()
        else:
            raise SyntaxError


class ArrayState(ToplevelState):
    def parse_terminal_character(self, c):
        if c == ',':
            self.parser.invoke_handler_for_array_element_end()
            self.parser.invoke_handler_for_array_element_begin()
        elif c == ']':
            self.leave_state()
            self.parser.invoke_handler_for_array_element_end()
            self.parser.invoke_handler_for_array_end()
        else:
            raise SyntaxError


class PairKeyState(ParserState):
    def parse_terminal_character(self, c):
        if c != '}':
            raise SyntaxError

    def parse_char(self, c):
        if c != '"':
            raise SyntaxError
        self.enter_string_state()

    def handle_end(self):
        self.enter_state(PairDelimState)


class PairDelimState(ParserState):
    def parse_teriminal_character(self, c):
        self.parse_char(c)

    def parse_char(self, c):
        if c != ':':
            raise SyntaxError
        self.enter_value_state()


class PairValueState(ParserState):
    def handle_begin(self):
        pass

class PairState(ParserState):
    def handle_begin(self):
        self.enter_state(PairKeyState)

class ObjectState(ParserState):
    def handle_begin(self):
        self.enter_state(PairState)



class Parser(object):
    terminal_characters = ']},'

    def __init__(self, event_handler):
        self.event_handler = event_handler
        self.states = []
        self.enter_state(ToplevelState(self))

    def invoke_handler_for_string_character(self, c):
        self.event_handler.handle_string_character(c)

    def invoke_handler_for_string_begin(self):
        self.event_handler.handle_string_begin()

    def invoke_handler_for_string_end(self):
        self.event_handler.handle_string_end()

    def invoke_handler_for_atom_character(self, c):
        self.event_handler.handle_atom_character(c)

    def invoke_handler_for_atom_begin(self):
        self.event_handler.handle_atom_begin()

    def invoke_handler_for_atom_end(self):
        self.event_handler.handle_atom_end()

    def invoke_handler_for_number_begin(self):
        self.event_handler.handle_number_begin()

    def invoke_handler_for_number_end(self):
        self.event_handler.handle_number_end()

    def invoke_handler_for_number_character(self, c):
        self.event_handler.handle_number_character(c)

    def invoke_handler_for_whitespace_character(self, c):
        self.event_handler.handle_whitespace_character(c)

    def invoke_handler_for_array_begin(self):
        self.event_handler.handle_array_begin()

    def invoke_handler_for_array_end(self):
        self.event_handler.handle_array_end()

    def invoke_handler_for_array_element_begin(self):
        self.event_handler.handle_array_element_begin()

    def invoke_handler_for_array_element_end(self):
        self.event_handler.handle_array_element_end()

    def parse(self, json):
        print "Parsing %s" % (json,)
        for c in json:
            self.parse_char(c)

    def parse_char(self, c):
        print "Parsing: '%s' with state %s" % (c, self.states[-1])
        state = self.states[-1]
        if c in string.whitespace:
            state.parse_whitespace(c)
        elif c in self.terminal_characters:
            state.parse_terminal_character(c)
        else:
            self.states[-1].parse_char(c)

    def enter_state(self, state):
        self.states.append(state)
        state.handle_begin()

    def leave_state(self):
        state = self.states.pop()
        state.handle_end()
