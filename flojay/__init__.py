import string
import types
import functools

number_chars = set(string.digits)


class SyntaxError(Exception):
    pass


# true, false, and null
class AtomState(object):
    def __init__(self, atom):
        self.count = 0
        self.atom = atom

    def parse_buf(self, parser, buf, handler):
        atom = buf.take_n(len(self.atom) - self.count)

        if atom != self.atom[self.count:self.count + len(atom)]:
            raise SyntaxError
        handler.handle_atom_character(atom)
        self.count += len(atom)
        if self.count == len(self.atom):
            handler.handle_atom_end()
            parser.leave_state()

number_chars = set(string.digits)
terminal_characters = set(']},' + string.whitespace)


def parse_base_number_state(parser, buf, handler):
    num = buf.take_while(number_chars)
    if num == '':
        num = buf.peek()
        if num in terminal_characters:
            handler.handle_number_end()
            parser.leave_state()
        else:
            raise SyntaxError
    else:
        handler.handle_number_character(num)
        handler.handle_number_end()
        parser.leave_state()


def parse_number_sign_state(parser, buf, handler):
    buf.take()
    handler.handle_number_character('-')
    parser.switch_state(parse_number_state)


def parse_number_state(parser, buf, handler):
    num = buf.take_while(number_chars)
    if num == "":
        num = buf.peek()
        if num in terminal_characters:
            handler.handle_number_end()
            parser.leave_state()
        elif num == '.':
            buf.take()
            handler.handle_number_character(num)
            parser.switch_state(parse_base_number_state)
        elif num == 'e' or num == 'E':
            buf.take()
            handler.handle_number_character(num)
            parser.switch_state(parse_exp_sign_state)
        else:
            raise SyntaxError
    else:
        handler.handle_number_character(num)


def parse_exp_sign_state(parser, buf, handler):
    c = buf.peek()
    if c in '-+':
        buf.take()
        handler.handle_number_character(c)
    parser.switch_state(parse_base_number_state)


class UnicodeCodepointState(object):

    hexdigits = set(string.hexdigits)

    def __init__(self):
        self.buf = ""

    def parse_buf(self, parser, buf, handler):
        self.buf += buf.take_n(4 - len(self.buf))
        if len(self.buf) == 4:
            handler.handle_string_character(unichr(int(self.buf, 16)))
            parser.leave_state()


class InvalidEscapeCharacter(Exception):
    pass


escape_chars = {'t': "\t", 'n': "\n", 'b': "\b", 'f': "\f",
                'r': "\r", '/': '/', '"': '"', '\\': '\\'}


def parse_escape_chars_state(parser, buf, handler):
    c = buf.take()
    if c in escape_chars:
        escape_char = escape_chars[c]
        handler.handle_string_character(escape_char)
        parser.leave_state()
    elif c == 'u':
        parser.switch_state(UnicodeCodepointState().parse_buf)
    else:
        raise InvalidEscapeCharacter


string_terminals = set('"\\')


def parse_string_state(parser, buf, handler):
    c = buf.take_until(string_terminals)
    if c == "":
        c = buf.take()
        if c == '"':
            handler.handle_string_end()
            parser.leave_state()
        elif c == '\\':
            parser.enter_state(parse_escape_chars_state)
    else:
        handler.handle_string_character(c)


def parse_toplevel_state(parser, buf, handler):
    buf.skip_whitespace()
    if buf.pointer >= buf.buffer_length:
        return
    try:
        parser.state_transitions[buf.peek()](buf, handler)
    except KeyError:
        raise SyntaxError("Unexpected character '%s'" % buf.peek())


def parse_array_state(parser, buf, handler):
    buf.skip_whitespace()
    c = buf.peek()
    if c == ']':
        buf.take()
        handler.handle_array_end()
        parser.leave_state()
    elif c == ',':
        raise SyntaxError
    else:
        parser.enter_state(parse_array_delim_state)


def parse_array_delim_state(parser, buf, handler):
    c = buf.peek()
    if c == ',':
        raise SyntaxError
    handler.handle_array_element_begin()
    parser.switch_state(parse_array_element_state)
    parse_toplevel_state(parser, buf, handler)


def parse_array_element_state(parser, buf, handler):
    buf.skip_whitespace()
    c = buf.peek()
    if c == ']':
        handler.handle_array_element_end()
        parser.leave_state()
    elif c == ',':
        handler.handle_array_element_end()
        buf.take()
        parser.switch_state(parse_array_delim_state)
    else:
        raise SyntaxError

def parse_object_state(parser, buf, handler):
    buf.skip_whitespace()
    c = buf.peek()
    if c == '}':
        buf.take()
        parser.leave_state()
        handler.handle_object_end()
    else:
        parser.enter_state(parse_object_key_state)
        handler.handle_object_key_begin()

def parse_object_key_state(parser, buf, handler):
    buf.skip_whitespace()
    c = buf.take()
    if c != '"':
        raise SyntaxError
    parser.switch_state(parse_object_pair_delim_state)
    parser.enter_state(parse_string_state)
    handler.handle_string_begin()


def parse_object_pair_delim_state(parser, buf, handler):
    c = buf.take()
    if c != ':':
        raise SyntaxError
    handler.handle_object_key_end()
    parser.switch_state(parse_object_value_prelim_state)
    handler.handle_object_value_begin()


def parse_object_value_prelim_state(parser, buf, handler):
    if buf.peek() in ',}':
        raise SyntaxError
    parser.switch_state(parse_object_value_state)


def parse_object_value_state(parser, buf, handler):
    c = buf.peek()
    if c == '}':
        handler.handle_object_value_end()
        parser.leave_state()
    elif c == ',':
        buf.take()
        handler.handle_object_value_end()
        parser.switch_state(parse_object_key_state)
        handler.handle_object_key_begin()
    else:
        parse_toplevel_state(parser, buf, handler)


class Buffer(object):
    def __init__(self, string):
        self.pointer = 0
        self.buf = string
        self.buffer_length = len(self.buf)

    def peek(self):
        return self.buf[self.pointer]

    def take_while(self, whitelist):
        ptr = self.pointer
        buf = self.buf
        l = self.buffer_length
        while ptr < l and buf[ptr] in whitelist:
            ptr += 1
        return self.take_n(ptr - self.pointer)

    def take_until(self, terminals):
        ptr = self.pointer
        buf = self.buf
        l = self.buffer_length
        while ptr < l and buf[ptr] not in terminals:
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

    def __init__(self):
        self.states = [None] * 64
        self.state_pointer = 0
        self.enter_state(parse_toplevel_state)
        self.state_transitions = self._make_toplevel_state_transitions()

    def enter_array_state(self, handler):
        self.enter_state(parse_array_state)
        handler.handle_array_begin()

    def enter_object_state(self, handler):
        self.enter_state(parse_object_state)
        handler.handle_object_begin()

    def enter_string_state(self, handler):
        self.enter_state(parse_string_state)
        handler.handle_string_begin()

    def enter_atom_state(self, atom, handler):
        self.enter_state(AtomState(atom).parse_buf)
        handler.handle_atom_begin()

    def enter_number_state(self, handler):
        self.enter_state(parse_number_state)
        handler.handle_number_begin()

    def enter_number_sign_state(self, handler):
        self.enter_state(parse_number_sign_state)
        handler.handle_number_begin()

    def parse(self, json, handler):
        buf = Buffer(json)
        while(buf.pointer < buf.buffer_length):
            self.states[self.state_pointer - 1](self, buf, handler)

    def switch_state(self, state_func):
        self.states[self.state_pointer - 1] = state_func

    def enter_state(self, state_func):
        if len(self.states) <= self.state_pointer:
            self.states.append(state_func)
        else:
            self.states[self.state_pointer] = state_func
        self.state_pointer += 1

    def leave_state(self):
        self.state_pointer -= 1

    def _make_toplevel_state_transitions(self):

        def enter_str(buf, handler):
            buf.take()
            self.enter_string_state(handler)

        def enter_obj(buf, handler):
            buf.take()
            self.enter_object_state(handler)

        def enter_array(buf, handler):
            buf.take()
            self.enter_array_state(handler)

        states = {}
        states['"'] = enter_str
        for key in number_chars:
            states[key] = lambda buf, handler: self.enter_number_state(handler)
        states['-'] = lambda buf, handler: self.enter_number_sign_state(handler)
        states['t'] = lambda buf, handler: self.enter_atom_state('true', handler)
        states['f'] = lambda buf, handler: self.enter_atom_state('false', handler)
        states['n'] = lambda buf, handler: self.enter_atom_state('null', handler)
        states['{'] = enter_obj
        states['['] = enter_array
        return states


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
        self.current_thing = []

    def handle_string_character(self, c):
        self.current_thing.append(c)

    def handle_string_end(self):
        self.current_thing = "".join(self.current_thing)

    def handle_number_begin(self):
        self.current_thing = []

    def handle_number_character(self, c):
        self.current_thing.append(c)

    def handle_number_end(self):
        self.current_thing = float("".join(self.current_thing))

    def handle_atom_begin(self):
        self.current_thing = []

    def handle_atom_character(self, c):
        self.current_thing.append(c)

    def handle_atom_end(self):
        current_thing = "".join(self.current_thing)
        if current_thing == 'true':
            self.current_thing = True
        elif current_thing == 'false':
            self.current_thing = False
        elif current_thing == 'null':
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
    p = Parser()
    p.parse(json, handler)
    return handler.current_thing


def unmarshal(obj, type_handler=None):
    recurse = functools.partial(unmarshal, type_handler=type_handler)

    def unmarshal_gen(gen):
        yield '['
        try:
            g = gen.next()
            for elt in recurse(g):
                yield elt
            for g in gen:
                yield ','
                for elt in recurse(g):
                    yield elt
        except StopIteration:
            pass

        yield ']'

    def unmarshal_list(lst):
        yield '['
        if len(lst) > 0:
            for elt in recurse(lst[0]):
                yield elt
            for elt in lst[1:]:
                yield ','
                for elt2 in recurse(elt):
                    yield elt2
        yield ']'

    def unmarshal_dict(dict_):
        yield '{'
        keylist = dict_.keys()
        if len(keylist) > 0:
            for k in recurse(keylist[0]):
                yield k
            yield ':'
            for v in recurse(dict_[keylist[0]]):
                yield v
            for k in keylist[1:]:
                yield ','
                for k_elt in recurse(k):
                    yield k_elt
                yield ':'
                for v in recurse(dict_[k]):
                    yield v
        yield '}'

    def unmarshal_number(num):
        yield str(num)

    def unmarshal_string(str_):
        yield '"'
        yield str(str_)
        yield '"'

    if type_handler:
        match, str_ = type_handler(obj)
        if match:
            return str_
    if type(obj) is types.GeneratorType:
        return unmarshal_gen(obj)
    if isinstance(obj, [].__class__):
        return unmarshal_list(obj)
    elif isinstance(obj, {}.__class__):
        return unmarshal_dict(obj)
    elif isinstance(obj, ''.__class__) or \
            isinstance(obj, u''.__class__):
        return unmarshal_string(obj)
    elif obj is False:
        def _false():
            yield 'false'
        return _false()
    elif obj is True:
        def _true():
            yield 'true'
        return _true()
    elif obj is None:
        def _null():
            yield 'null'
        return _null()
    elif isinstance(obj, int) or \
            isinstance(obj, float) or \
            isinstance(obj, long):
        return unmarshal_number(obj)
    else:
        raise Exception("Unexpected object %s" % repr(obj))
