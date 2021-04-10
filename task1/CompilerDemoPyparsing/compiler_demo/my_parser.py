import inspect

import pyparsing as pp
from pyparsing import pyparsing_common as ppc

from .ast import *


# noinspection PyPep8Naming
def make_parser():
    LPAR, RPAR = pp.Literal('(').suppress(), pp.Literal(')').suppress()
    LBRACK, RBRACK = pp.Literal("[").suppress(), pp.Literal("]").suppress()
    LBRACE, RBRACE = pp.Literal("{").suppress(), pp.Literal("}").suppress()
    SEMI, COMMA = pp.Literal(';').suppress(), pp.Literal(',').suppress()
    ASSIGN = pp.Literal('=')

    ADD, SUB = pp.Literal('+'), pp.Literal('-')
    MUL, DIV, MOD = pp.Literal('*'), pp.Literal('/'), pp.Literal('%')
    AND = pp.Literal('&&')
    OR = pp.Literal('||')
    BIT_AND = pp.Literal('&')
    BIT_OR = pp.Literal('|')
    GE, LE, GT, LT = pp.Literal('>='), pp.Literal('<='), pp.Literal('>'), pp.Literal('<')
    NEQUALS, EQUALS = pp.Literal('!='), pp.Literal('==')

    PRIVATE = pp.Literal('private')
    PROTECTED = pp.Literal('protected')
    PUBLIC = pp.Literal('public')
    access_keys = PUBLIC | PROTECTED | PRIVATE

    # access = pp.Optional(PRIVATE | PROTECTED | PUBLIC)

    STATIC = pp.Literal('static')
    VOID = pp.Literal('void').suppress()

    CLASS = pp.Literal('class').suppress()

    ASYNC = pp.Literal('async')
    AWAIT = pp.Literal('await')

    IF = pp.Keyword('if')
    FOR = pp.Keyword('for')
    RETURN = pp.Keyword('return')
    keywords = IF | FOR | RETURN

    num = pp.Regex('[+-]?\\d+\\.?\\d*([eE][+-]?\\d+)?')
    str_ = pp.QuotedString('"', escChar='\\', unquoteResults=False, convertWhitespaceEscapes=False)
    literal = num | str_ | pp.Regex('true|false')

    ident = (~keywords + ppc.identifier.copy()).setName('ident')
    type_ = ident.copy().setName('type')
    access = ident.copy().setName('access')

    add = pp.Forward()
    expr = pp.Forward()
    stmt = pp.Forward()
    stmt_list = pp.Forward()
    class_init = pp.Forward()
    assign = pp.Forward()
    body = pp.Forward()

    call = ident + LPAR + pp.Optional(expr + pp.ZeroOrMore(COMMA + expr)) + RPAR

    assign = ident + ASSIGN.suppress() + expr
    var_inner = assign | ident
    vars_ = type_ + var_inner + pp.ZeroOrMore(COMMA + var_inner)

    simple_stmt = assign | call

    group = (
            literal |
            call |  # обязательно перед ident, т.к. приоритетный выбор (или использовать оператор ^ вместо | )
            ident |
            LPAR + expr + RPAR
    )

    mult = pp.Group(group + pp.ZeroOrMore((MUL | DIV | MOD) + group)).setName('bin_op')
    add << pp.Group(mult + pp.ZeroOrMore((ADD | SUB) + mult)).setName('bin_op')
    compare1 = pp.Group(add + pp.Optional((GE | LE | GT | LT) + add)).setName('bin_op')
    compare2 = pp.Group(compare1 + pp.Optional((EQUALS | NEQUALS) + compare1)).setName('bin_op')
    logical_and = pp.Group(compare2 + pp.ZeroOrMore(AND + compare2)).setName('bin_op')
    logical_or = pp.Group(logical_and + pp.ZeroOrMore(OR + logical_and)).setName('bin_op')
    expr << logical_or

    param = type_ + ident
    params = pp.Optional(param + pp.ZeroOrMore(COMMA + param))
    func = (ASYNC | pp.Group(pp.Empty())) + (access_keys | pp.Group(pp.Empty())) + (STATIC | pp.Group(pp.Empty())) + type_ + ident + LPAR + params + RPAR + body

    stmt << (
             class_init
             | func
             | vars_ + SEMI
             | body
    )
    stmt_list = pp.ZeroOrMore(stmt)

    body << LBRACE + stmt_list + RBRACE

    class_init << (access_keys | pp.Group(pp.Empty())) + CLASS + ident + body

    program = pp.ZeroOrMore(class_init)
    start = program


    def set_parse_action_magic(rule_name: str, parser_element: pp.ParserElement) -> None:
        if rule_name == rule_name.upper():
            return
        if getattr(parser_element, 'name', None) and parser_element.name.isidentifier():
            rule_name = parser_element.name
        if rule_name in ('bin_op',):
            def bin_op_parse_action(s, loc, tocs):
                node = tocs[0]
                if not isinstance(node, AstNode):
                    node = bin_op_parse_action(s, loc, node)
                for i in range(1, len(tocs) - 1, 2):
                    second_node = tocs[i + 1]
                    if not isinstance(second_node, AstNode):
                        second_node = bin_op_parse_action(s, loc, second_node)
                    node = BinOpNode(BinOp(tocs[i]), node, second_node, loc=loc)
                return node

            parser_element.setParseAction(bin_op_parse_action)
        else:
            cls = ''.join(x.capitalize() for x in rule_name.split('_')) + 'Node'
            with suppress(NameError):
                cls = eval(cls)
                if not inspect.isabstract(cls):
                    def parse_action(s, loc, tocs):
                        if cls is FuncNode:
                            return FuncNode(tocs[0], tocs[1], tocs[2],tocs[3], tocs[4], tocs[5:-1], tocs[-1], loc=loc)
                        else:
                            return cls(*tocs, loc=loc)

                    parser_element.setParseAction(parse_action)

    for var_name, value in locals().copy().items():
        if isinstance(value, pp.ParserElement):
            set_parse_action_magic(var_name, value)

    return start


parser = make_parser()


def parse(prog: str) -> StmtListNode:
    locs = []
    row, col = 0, 0
    for ch in prog:
        if ch == '\n':
            row += 1
            col = 0
        elif ch == '\r':
            pass
        else:
            col += 1
        locs.append((row, col))

    old_init_action = AstNode.init_action

    def init_action(node: AstNode) -> None:
        loc = getattr(node, 'loc', None)
        if isinstance(loc, int):
            node.row = locs[loc][0] + 1
            node.col = locs[loc][1] + 1

    AstNode.init_action = init_action
    try:
        prog: StmtListNode = parser.parseString(str(prog))[0]
        prog.program = True
        return prog
    finally:
        AstNode.init_action = old_init_action
