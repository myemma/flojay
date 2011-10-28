from flojay.state import ParserState
from flojay.string_state import StringState
from flojay.number import NumberState, NumberSignState
from flojay.atom import AtomState
from flojay.exception import SyntaxError
from flojay.state import ParserState
import string

class ToplevelState(ParserState):

    number_chars = set(string.digits)

    def parse_buf(self, parser, buf):
        buf.skip_whitespace()
        if not buf:
            return
        c = buf.peek()
        if c == '"':
            buf.take()
            parser.enter_string_state()
        elif c in self.number_chars:
            parser.enter_number_state()
        elif c == '-':
            parser.enter_number_sign_state()
        elif c == 't':
            parser.enter_atom_state('true')
        elif c == 'f':
            parser.enter_atom_state('false')
        elif c == 'n':
            parser.enter_atom_state('null')
        elif c == '[':
            buf.take()
            parser.enter_array_state()
        elif c == '{':
            buf.take()
            parser.enter_object_state()
        else:
            raise SyntaxError


class ArrayState(ParserState):

    """
    Okay so the thing is we chomp the whitespace 
    """

    def parse_buf(self, parser, buf):
        buf.skip_whitespace()
        c = buf.peek()
        if c == ']':
            buf.take()
            parser.leave_state()
            parser.invoke_handler_for_array_end()
        elif c == ',':
            raise SyntaxError
        else:
            parser.enter_state(ArrayDelimState)


class ArrayDelimState(ToplevelState):

    def parse_buf(self, parser, buf):
        c = buf.peek()
        if c == ',':
            raise SyntaxError
        parser.invoke_handler_for_array_element_begin()
        parser.switch_state(ArrayElementState)
        super(self.__class__, self).parse_buf(parser, buf)


class ArrayElementState(ParserState):

    def parse_buf(self, parser, buf):
        buf.skip_whitespace()
        c = buf.peek()
        if c == ']':
            parser.invoke_handler_for_array_element_end()
            parser.leave_state()
        elif c == ',':
            parser.invoke_handler_for_array_element_end()
            buf.take()
            parser.switch_state(ArrayDelimState)
        else:
            raise SyntaxError


class ObjectState(ParserState):

    def parse_buf(self, parser, buf):
        buf.skip_whitespace()
        c = buf.peek()
        if c == '}':
            buf.take()
            parser.leave_state()
            parser.invoke_handler_for_object_end()
        else:
            parser.enter_state(ObjectKeyState)
            parser.invoke_handler_for_object_key_begin()


class ObjectKeyState(ParserState):

    def parse_buf(self, parser, buf):
        buf.skip_whitespace()
        c = buf.take()
        if c == '"':
            parser.switch_state(ObjectPairDelimState)
            parser.enter_state(StringState)
            parser.invoke_handler_for_string_begin()
        else:
            raise SyntaxError


class ObjectPairDelimState(ParserState):

    def parse_buf(self, parser, buf):
        c = buf.take()
        if c != ':':
            raise SyntaxError
        parser.invoke_handler_for_object_key_end()
        parser.switch_state(ObjectValuePrelimState)
        parser.invoke_handler_for_object_value_begin()


class ObjectValuePrelimState(ParserState):
    def parse_buf(self, parser, buf):
        if buf.peek() in ',}':
            raise SyntaxError
        parser.switch_state(ObjectValueState)


class ObjectValueState(ToplevelState):
    def parse_buf(self, parser, buf):
        c = buf.peek()
        if c == '}':
            parser.invoke_handler_for_object_value_end()
            parser.leave_state()
        elif c == ',':
            buf.take()
            parser.invoke_handler_for_object_value_end()
            parser.switch_state(ObjectKeyState)
            parser.invoke_handler_for_object_key_begin()
        else:
            super(self.__class__, self).parse_buf(parser, buf)

class Buffer(object):
    def __init__(self, string):
        self.pointer = 0
        self.buf = string
    
    def __nonzero__(self):
        return True if self.pointer < len(self.buf) else False

    def peek(self):
        return self.buf[self.pointer]

    def take_while(self, whitelist):
        ptr = self.pointer
        buf = self.buf
        while ptr < len(buf) and buf[ptr] in whitelist:
            ptr += 1
        return self.take_n(ptr - self.pointer)

    def take_until(self, terminals):
        ptr = self.pointer
        buf = self.buf
        while ptr < len(buf) and buf[ptr] not in terminals:
            ptr += 1
        return self.take_n(ptr - self.pointer)

    def take_n(self, n):
        value = self.buf[self.pointer:self.pointer + n]
        self.pointer += n
        return value

    def take(self):
        value = self.buf[self.pointer]
        self.pointer += 1
        return value

    whitespace = set(string.whitespace)

    def skip_whitespace(self):
        self.take_while(self.whitespace)


class Parser(object):
    whitespace = set(string.whitespace)

    def __init__(self, event_handler):
        self.event_handler = event_handler
        self.states = []
        self.enter_state(ToplevelState)

    def enter_array_state(self):
        self.enter_state(ArrayState)
        self.invoke_handler_for_array_begin()

    def enter_object_state(self):
        self.enter_state(ObjectState)
        self.invoke_handler_for_object_begin()

    def enter_string_state(self):
        self.enter_state(StringState)
        self.invoke_handler_for_string_begin()

    def enter_atom_state(self, atom):
        self.enter_state(AtomState, atom)
        self.invoke_handler_for_atom_begin()

    def enter_number_state(self):
        self.enter_state(NumberState)
        self.invoke_handler_for_number_begin()

    def enter_number_sign_state(self):
        self.enter_state(NumberSignState)
        self.invoke_handler_for_number_begin()

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
        buf = Buffer(json)
        while(buf):
            self.states[-1].parse_buf(self, buf)

    def switch_state(self, state_class, *args):
        self.leave_state()
        self.enter_state(state_class, *args)

    def enter_state(self, state_class, *args):
        state = state_class(self, *args)
        self.states.append(state)

    def leave_state(self):
        state = self.states.pop()


class MarshallEventHandler(object):
    def __init__(self):
        self.container = None
        self.parents = []
        self.keys = []

    def handle_array_begin(self):
        self.parents.append(self.container)
        self.container = []

    def handle_array_end(self):
        self.current_thing = self.container
        self.container = self.parents.pop()

    def handle_array_element_begin(self):
        pass

    def handle_array_element_end(self):
        self.container.append(self.current_thing)

    def handle_string_begin(self):
        self.current_thing = ""

    def handle_string_character(self, c):
         self.current_thing += c

    def handle_string_end(self):
        pass

    def handle_number_begin(self):
        self.current_thing = ""

    def handle_number_character(self, c):
        self.current_thing += c

    def handle_number_end(self):
        self.current_thing = float(self.current_thing)

    def handle_atom_begin(self):
        self.current_thing = ""

    def handle_atom_character(self, c):
        self.current_thing += c

    def handle_atom_end(self):
        if self.current_thing == 'true':
            self.current_thing = True
        elif self.current_thing == 'false':
            self.current_thing = False
        elif self.current_thing == 'null':
            self.current_thing = None
        else:
            raise Exception("Invalid atom")

    def handle_object_begin(self):
        self.parents.append(self.container)
        self.container = {}

    def handle_object_key_begin(self):
        pass

    def handle_object_value_begin(self):
        pass

    def handle_object_key_end(self):
        self.keys.append(self.current_thing)

    def handle_object_value_end(self):
        self.container[self.keys.pop()] = self.current_thing

    def handle_object_end(self):
        self.current_thing = self.container
        self.container = self.parents.pop()


def marshal(json):
    handler = MarshallEventHandler()
    p = Parser(handler)
    p.parse(json)
    return handler.current_thing
