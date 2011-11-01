# true, false and null

from flojay.state import ParserState
from flojay.exception import SyntaxError


class AtomState(ParserState):
    def setUp(self, atom):
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
