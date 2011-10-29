# true, false and null

from flojay.state import ParserState
from flojay.exception import SyntaxError


class AtomState(ParserState):
    def setUp(self, atom):
        # This is the only one that has any state :(
        self.count = 0
        self.atom = atom

    def parse_buf(self, parser, buf):
        atom = buf.take_n(len(self.atom) - self.count)

        if atom != self.atom[self.count:self.count + len(atom)]:
            raise SyntaxError
        parser.invoke_handler_for_atom_character(atom)
        self.count += len(atom)
        if self.count == len(self.atom):
            parser.invoke_handler_for_atom_end()
            parser.leave_state()
