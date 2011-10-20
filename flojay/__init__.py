from flojay.state import ParserState
from flojay.string_state import StringState
from flojay.number import NumberState
from flojay.atom import AtomState
from flojay.exception import SyntaxError
import string


class ArrayState(ParserState):

    def parse_terminal_character(self, c):
        self.parse_char(c)

    def parse_whitespace(self, c):
        pass

    def parse_char(self, c):
        if c == ']':
            self.leave_state()
            self.parser.invoke_handler_for_array_end()
        elif c == ',':
            raise SyntaxError
        else:
            self.enter_state(ArrayElementState)
            self.parser.invoke_handler_for_array_element_begin()
            self.reparse_char(c)


class ToplevelState(ParserState):
    def enter_array_state(self):
        self.enter_state(ArrayState)
        self.parser.invoke_handler_for_array_begin()

    def enter_object_state(self):
        self.enter_state(ObjectState)
        self.parser.invoke_handler_for_object_begin()

    def enter_string_state(self):
        self.enter_state(StringState)
        self.parser.invoke_handler_for_string_begin()

    def enter_atom_state(self, atom):
        self.enter_state(AtomState, atom)
        self.parser.invoke_handler_for_atom_begin()

    def enter_number_state(self):
        self.enter_state(NumberState)
        self.parser.invoke_handler_for_number_begin()

    def parse_terminal_character(self, c):
        raise SyntaxError

    def parse_char(self, c):
        if c == '"':
            self.enter_string_state()
        elif c in string.digits + '-':
            self.enter_number_state()
            self.reparse_char(c)
        elif c == 't':
            self.enter_atom_state('true')
            self.reparse_char(c)
        elif c == 'f':
            self.enter_atom_state('false')
            self.reparse_char(c)
        elif c == 'n':
            self.enter_atom_state('null')
            self.reparse_char(c)
        elif c == '[':
            self.enter_array_state()
        elif c == '{':
            self.enter_object_state()
        else:
            raise SyntaxError


class ArrayDelimState(ParserState):

    def parse_terminal_character(self, c):
        self.parse_char(c)

    def parse_whitespace(self, c):
        pass

    def parse_char(self, c):
        if c in ',]':
            raise SyntaxError
        self.switch_state(ArrayElementState)
        self.parser.invoke_handler_for_array_element_begin()
        self.reparse_char(c)


class ArrayElementState(ToplevelState):

    def parse_whitespace(self, c):
        self.parse_terminal_character(c)

    def parse_terminal_character(self, c):
        if c == ']':
            self.parser.invoke_handler_for_array_element_end()
            self.leave_state()
            self.reparse_char(c)
        elif c == ',':
            self.parser.invoke_handler_for_array_element_end()
            self.switch_state(ArrayDelimState)
        else:
            super(self.__class__, self).parse_terminal_character(c)


class ObjectState(ParserState):
    def parse_whitespace(self, c):
        pass

    def parse_terminal_character(self, c):
        self.parse_char(c)

    def parse_char(self, c):
        if c == '}':
            self.leave_state()
            self.parser.invoke_handler_for_object_end()
        else:
            self.enter_state(ObjectKeyState)
            self.parser.invoke_handler_for_object_key_begin()
            self.reparse_char(c)


class ObjectKeyState(ParserState):
    def parse_whitespace(self, c):
        pass

    def parse_terminal_character(self, c):
        self.parse_char(c)

    def parse_char(self, c):
        if c == '"':
            self.switch_state(ObjectPairDelimState)
            self.enter_state(StringState)
            self.parser.invoke_handler_for_string_begin()
        else:
            raise SyntaxError


class ObjectPairDelimState(ParserState):
    def parse_whitespace(self, c):
        pass

    def parse_terminal_character(self, c):
        self.parse_char(c)

    def parse_char(self, c):
        if c != ':':
            raise SyntaxError
        self.parser.invoke_handler_for_object_key_end()
        self.switch_state(ObjectValuePrelimState)
        self.parser.invoke_handler_for_object_value_begin()


class ObjectValuePrelimState(ParserState):
    def parse_whitespace(self, c):
        pass

    def parse_char(self, c):
        if c in ',}':
            raise SyntaxError
        self.switch_state(ObjectValueState)
        self.reparse_char(c)

    def parse_terminal_character(self, c):
        self.parse_char(c)


class ObjectValueState(ToplevelState):
    def parse_terminal_character(self, c):
        if c == '}':
            self.parser.invoke_handler_for_object_value_end()
            self.leave_state()
            self.reparse_char(c)
        elif c == ',':
            self.parser.invoke_handler_for_object_value_end()
            self.switch_state(ObjectKeyState)
            self.parser.invoke_handler_for_object_key_begin()
        else:
            super(self.__class__, self).parse_terminal_character(c)


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

    def invoke_handler_for_object_begin(self):
        self.event_handler.handle_object_begin()

    def invoke_handler_for_object_end(self):
        self.event_handler.handle_object_end()

    def invoke_handler_for_object_key_begin(self):
        self.event_handler.handle_object_key_begin()

    def invoke_handler_for_object_key_end(self):
        self.event_handler.handle_object_key_end()

    def invoke_handler_for_object_value_begin(self):
        self.event_handler.handle_object_value_begin()

    def invoke_handler_for_object_value_end(self):
        self.event_handler.handle_object_value_end()

    def parse(self, json):
        for c in json:
            self.parse_char(c)

    def parse_char(self, c):
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


class MarshallEventHandler(object):
    def __init__(self):
        self.parent = None
        self.root = None
        self.current = self.parent

    def handle_array_begin(self):
        self.parent = self.current
        self.current = []
        if not self.root:
            self.root = self.current

    def handle_array_end(self):
        print "Array end. Adding %s to %s" % (self.current, self.parent)
        # if self.parent:
        #     self.parent.append(self.current)
        self.current_thing = self.current
        self.current = self.parent

    def handle_array_element_begin(self):
        pass

    def handle_array_element_end(self):
        self.current.append(self.current_thing)

    def handle_string_begin(self):
        self.char_buffer = ""

    def handle_string_character(self, c):
        self.char_buffer += c

    def handle_string_end(self):
        self.current_thing = self.char_buffer

    def handle_number_begin(self):
        self.char_buffer = ""

    def handle_number_character(self, c):
        self.char_buffer += c

    def handle_number_end(self):
        self.current_thing = float(self.char_buffer)

    def handle_atom_begin(self):
        self.char_buffer = ""

    def handle_atom_character(self, c):
        self.char_buffer += c

    def handle_atom_end(self):
        if self.char_buffer == 'true':
            self.current_thing = True
        elif self.char_buffer == 'false':
            self.current_thing = False
        elif self.char_buffer == 'null':
            self.current_thing = None
        else:
            raise Exception("Invalid atom")


def marshal(json):
    handler = MarshallEventHandler()
    p = Parser(handler)
    p.parse(json)
    return handler.root
