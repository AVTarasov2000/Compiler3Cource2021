from abc import ABC, abstractmethod
from contextlib import suppress
from typing import Optional, Union, Tuple, Callable

from .semantic import TYPE_CONVERTIBILITY, BIN_OP_TYPE_COMPATIBILITY, BinOp, \
    TypeDesc, IdentDesc, ScopeType, IdentScope, SemanticException, AccessType

TYPES = {"int": "Integer", "float": "Float", "double": "Double", "boolean": "Boolean", "short": "Short", "char": "Char",
         "long": "Long", "byte": "Byte"}


class AstNode(ABC):
    """Базовый абстрактый класс узла AST-дерева"""

    init_action: Callable[['AstNode'], None] = None

    def __init__(self, row: Optional[int] = None, col: Optional[int] = None, **props) -> None:
        super().__init__()
        self.row = row
        self.col = col
        for k, v in props.items():
            setattr(self, k, v)
        if AstNode.init_action is not None:
            AstNode.init_action(self)
        self.node_type: Optional[TypeDesc] = None
        self.node_ident: Optional[IdentDesc] = None
        self.await_names = []
        self.type_changing = []
        self.is_async = False
        self.external_await_names = []
        self.external_type_changing = []

    @abstractmethod
    def __str__(self) -> str:
        pass

    @property
    def childs(self) -> Tuple['AstNode', ...]:
        return ()

    def to_str(self):
        return str(self)

    def to_str_full(self):
        r = ''
        if self.node_ident:
            r = str(self.node_ident)
        elif self.node_type:
            r = str(self.node_type)
        return self.to_str() + (' : ' + r if r else '')

    @property
    def tree(self) -> [str, ...]:
        r = [self.to_str_full()]
        childs = self.childs
        for i, child in enumerate(childs):
            ch0, ch = '├', '│'
            if i == len(childs) - 1:
                ch0, ch = '└', ' '
            r.extend(((ch0 if j == 0 else ch) + ' ' + s for j, s in enumerate(child.tree)))
        return tuple(r)

    def __getitem__(self, index):
        return self.childs[index] if index < len(self.childs) else None


class _GroupNode(AstNode):
    """Класс для группировки других узлов (вспомогательный, в синтаксисе нет соотвествия)
    """

    def __init__(self, name: str, *childs: AstNode,
                 row: Optional[int] = None, col: Optional[int] = None, **props) -> None:
        super().__init__(row=row, col=col, **props)
        self.name = name
        self._childs = childs

    def __str__(self) -> str:
        return self.name

    @property
    def childs(self) -> Tuple['AstNode', ...]:
        return self._childs

    def to_jpp_code(self, await_names, type_changing, is_async, external_await_names, external_type_changing):
        return ""


class ExprNode(AstNode, ABC):
    """Абстракный класс для выражений в AST-дереве
    """

    def to_jpp_code(self, await_names, type_changing, is_async, external_await_names, external_type_changing):
        return ""


class LiteralNode(ExprNode):
    """Класс для представления в AST-дереве литералов (числа, строки, логическое значение)
    """

    def __init__(self, literal: str,
                 row: Optional[int] = None, col: Optional[int] = None, **props) -> None:
        super().__init__(row=row, col=col, **props)
        self.literal = literal
        if literal in ('true', 'false'):
            self.value = bool(literal)
        else:
            self.value = eval(literal)

    def __str__(self) -> str:
        return self.literal

    def to_jpp_code(self, await_names, type_changing, is_async, external_await_names, external_type_changing):
        return self.literal


class IdentNode(ExprNode):
    """Класс для представления в AST-дереве идентификаторов
    """

    def __init__(self, name: str,
                 row: Optional[int] = None, col: Optional[int] = None, **props) -> None:
        super().__init__(row=row, col=col, **props)
        self.name = str(name)

    def __str__(self) -> str:
        return str(self.name)

    def to_jpp_code(self, await_names, type_changing, is_async, external_await_names, external_type_changing) -> str:
        if self.name in await_names or self.name in type_changing:
            return f"{self.name}.value()"
        return f"{self.name}"


class TypeNode(IdentNode):
    """Класс для представления в AST-дереве типов данный
       (при появлении составных типов данных должен быть расширен)
    """

    def __init__(self, name: str,
                 row: Optional[int] = None, col: Optional[int] = None, **props) -> None:
        super().__init__(name, row=row, col=col, **props)
        self.type = None
        with suppress(SemanticException):
            self.type = TypeDesc.from_str(name)

    def to_str_full(self):
        return self.to_str()

    def to_jpp_code(self, await_names, type_changing, is_async, external_await_names, external_type_changing) -> str:
        return f"{self.name}"

    def await_names_check(self):
        return [], []


class AccessNode(IdentNode):

    def __init__(self, name: str,
                 row: Optional[int] = None, col: Optional[int] = None, **props) -> None:
        super().__init__(name, row=row, col=col, **props)
        self.type = None
        with suppress(SemanticException):
            self.type = AccessType.from_str(name)

    def to_str_full(self):
        return self.to_str()

    def to_jpp_code(self, await_names, type_changing, is_async, external_await_names, external_type_changing) -> str:
        return f"{self.name}"

    def await_names_check(self):
        return [], []


class BinOpNode(ExprNode):
    """Класс для представления в AST-дереве бинарных операций
    """

    def __init__(self, op: BinOp, arg1: ExprNode, arg2: ExprNode,
                 row: Optional[int] = None, col: Optional[int] = None, **props) -> None:
        super().__init__(row=row, col=col, **props)
        self.op = op
        self.arg1 = arg1
        self.arg2 = arg2

    def __str__(self) -> str:
        return str(self.op.value)

    def to_jpp_code(self, await_names, type_changing, is_async, external_await_names, external_type_changing) -> str:
        self.await_names.extend(await_names)
        self.type_changing.extend(type_changing)
        self.is_async = is_async
        self.external_await_names.extend(external_await_names)
        self.external_type_changing.extend(external_type_changing)
        if self.op.value == '.':
            return f"{self.arg1.to_jpp_code(self.await_names, self.type_changing, self.is_async, self.external_await_names, self.external_type_changing)}{self.op.value}{self.arg2.to_jpp_code(self.await_names, self.type_changing, self.is_async, self.external_await_names, self.external_type_changing)}"
        else:
            return f"{self.arg1.to_jpp_code(self.await_names, self.type_changing, self.is_async, self.external_await_names, self.external_type_changing)} {self.op.value} {self.arg2.to_jpp_code(self.await_names, self.type_changing, self.is_async, self.external_await_names, self.external_type_changing)}"

    def await_names_check(self):
        return [], []

    @property
    def childs(self) -> Tuple[ExprNode, ExprNode]:
        return self.arg1, self.arg2


class CallNode(ExprNode):
    """Класс для представления в AST-дереве вызова функций
       (в языке программирования может быть как expression, так и statement)
    """

    def __init__(self, func: IdentNode, *params: ExprNode,
                 row: Optional[int] = None, col: Optional[int] = None, **props) -> None:
        super().__init__(row=row, col=col, **props)
        self.func = func
        self.params = params

    def __str__(self) -> str:
        return 'call'

    def to_jpp_code(self, await_names, type_changing, is_async, external_await_names, external_type_changing) -> str:
        self.await_names.extend(await_names)
        self.type_changing.extend(type_changing)
        self.is_async = is_async
        self.external_await_names.extend(external_await_names)
        self.external_type_changing.extend(external_type_changing)

        params = ", ".join(x.to_jpp_code(self.await_names, self.type_changing, self.is_async, self.external_await_names,
                                         self.external_type_changing) for x in self.childs[1].childs)
        return f"{self.childs[0].to_jpp_code(self.await_names, self.type_changing, self.is_async, self.external_await_names, self.external_type_changing)}({params})"

    def await_names_check(self):
        return [], []

    @property
    def childs(self) -> Tuple[AstNode, ...]:
        return self.func, _GroupNode('params', *self.params)


class CallerNode(ExprNode):
    """Класс для представления в AST-дереве вызова функций
       (в языке программирования может быть как expression, так и statement)
    """

    def __init__(self, call: CallNode, expr: ExprNode,
                 row: Optional[int] = None, col: Optional[int] = None, **props) -> None:
        super().__init__(row=row, col=col, **props)
        self.call = call
        self.expr = expr

    def __str__(self) -> str:
        return 'caller'

    def to_jpp_code(self, await_names, type_changing, is_async, external_await_names, external_type_changing) -> str:
        self.await_names.extend(await_names)
        self.type_changing.extend(type_changing)
        self.is_async = is_async
        self.external_await_names.extend(external_await_names)
        self.external_type_changing.extend(external_type_changing)
        if isinstance(self.expr, CallNode) and self.call == 'await':
            line = [x.to_jpp_code(self.await_names, self.type_changing, self.is_async, self.external_await_names, self.external_type_changing) for x in self.expr.params]
            params = ", ".join(f"new Promise({x}.value)" if x in await_names else f"new Promise({x})" for x in line)
            return f"AsyncLib.async(()->{self.expr.func.to_jpp_code(self.await_names, self.type_changing, self.is_async, self.external_await_names, self.external_type_changing)}({params}))"
        else:
            return f"{self.expr.to_jpp_code(self.await_names, self.type_changing, self.is_async, self.external_await_names, self.external_type_changing)}"

    def is_await(self):
        if isinstance(self.childs[1], CallNode) and self.childs[1].col == "await":
            return True
        else:
            return False

    @property
    def childs(self) -> Tuple[AstNode, ...]:
        return _GroupNode(str(self.call)), self.expr

    def await_names_check(self):
        return [], []


class TypeConvertNode(ExprNode):
    """Класс для представления в AST-дереве операций конвертации типов данных
       (в языке программирования может быть как expression, так и statement)
    """

    def __init__(self, expr: ExprNode, type_: TypeDesc,
                 row: Optional[int] = None, col: Optional[int] = None, **props) -> None:
        super().__init__(row=row, col=col, **props)
        self.expr = expr
        self.type = type_
        self.node_type = type_

    def __str__(self) -> str:
        return 'convert'

    @property
    def childs(self) -> Tuple[AstNode, ...]:
        return (_GroupNode(str(self.type), self.expr),)


class StmtNode(ExprNode, ABC):
    """Абстракный класс для деклараций или инструкций в AST-дереве
    """

    def to_str_full(self):
        return self.to_str()

    def to_jpp_code(self, await_names, type_changing, is_async, external_await_names, external_type_changing):
        return ""

    def await_names_check(self):
        return [], []


class FuncStmtNode(ExprNode, ABC):
    """Абстракный класс для деклараций или инструкций в AST-дереве
    """

    def to_str_full(self):
        return self.to_str()


class AssignNode(ExprNode):
    """Класс для представления в AST-дереве оператора присваивания
    """

    def __init__(self, var: IdentNode, val: ExprNode,
                 row: Optional[int] = None, col: Optional[int] = None, **props) -> None:
        super().__init__(row=row, col=col, **props)
        self.var = var
        self.val = val

    def __str__(self) -> str:
        return '='

    def to_jpp_code(self, await_names, type_changing, is_async, external_await_names, external_type_changing) -> str:
        self.await_names.extend(await_names)
        self.type_changing.extend(type_changing)
        self.is_async = is_async
        self.external_await_names.extend(external_await_names)
        self.external_type_changing.extend(external_type_changing)

        return f"{self.childs[0].name} = {self.childs[1].to_jpp_code(self.await_names, self.type_changing, self.is_async, self.external_await_names, self.external_type_changing)}"

    def await_names_check(self):
        if self.childs[1].is_await():
            return [self.childs[0].name], [self.childs[0].name]
        else:
            return [], []

    @property
    def childs(self) -> Tuple[IdentNode, ExprNode]:
        return self.var, self.val


class VarsNode(StmtNode):
    """Класс для представления в AST-дереве объявления переменнных
    """

    def __init__(self, type_: TypeNode, *vars_: Union[IdentNode, 'AssignNode'],
                 row: Optional[int] = None, col: Optional[int] = None, **props) -> None:
        super().__init__(row=row, col=col, **props)
        self.type = type_
        self.vars = vars_

    def __str__(self) -> str:
        return str(self.type)

    def to_jpp_code(self, await_names, type_changing, is_async, external_await_names, external_type_changing) -> str:
        self.await_names.extend(await_names)
        self.type_changing.extend(type_changing)
        self.is_async = is_async
        self.external_await_names.extend(external_await_names)
        self.external_type_changing.extend(external_type_changing)

        is_valuable = False
        for x in self.childs:
            if isinstance(x, AssignNode):
                is_valuable = True if x.var.name in self.type_changing else False
            else:
                is_valuable = True if x.name in self.type_changing else False

        body = ", ".join(
            x.to_jpp_code(self.await_names, self.type_changing, self.is_async,
                          self.external_await_names, self.external_type_changing) if isinstance(x,
                                                                                                AssignNode) else x.name
            for x in
            self.childs)

        type_name = TYPES.get(self.type.name) if self.type.name in TYPES else self.type.name
        type_ = f"Valuable<{type_name}>" if is_valuable else f"{self.type.name}"
        return f"{type_} {body}"

    def await_names_check(self):
        result, type_change = [], []
        for i in self.childs:
            if isinstance(i, AssignNode):
                if i.childs[1].call == 'await':
                    self.is_async = True
                    type_change.append(i.childs[0].name)
                    result.append(i.childs[0].name)
                tmp_result, tmp_type_change = i.await_names_check()
                result.extend(tmp_result)
                type_change.extend(tmp_type_change)

        return result, type_change

    @property
    def childs(self) -> Tuple[AstNode, ...]:
        return self.vars


class NewNode(StmtNode):
    """Класс для представления в AST-дереве оператора return
    """

    def __init__(self, val: CallNode,
                 row: Optional[int] = None, col: Optional[int] = None, **props) -> None:
        super().__init__(row=row, col=col, **props)
        self.val = val

    def __str__(self) -> str:
        return 'new '

    def to_jpp_code(self, await_names, type_changing, is_async, external_await_names, external_type_changing) -> str:
        self.await_names.extend(await_names)
        self.type_changing.extend(type_changing)
        self.is_async = is_async
        self.external_await_names.extend(external_await_names)
        self.external_type_changing.extend(external_type_changing)
        return f" new {self.val.to_jpp_code(self.await_names, self.type_changing, self.is_async, self.external_await_names, self.external_type_changing)}"

    def await_names_check(self):
        return [], []

    @property
    def childs(self) -> Tuple[ExprNode]:
        return (self.val,)


class ReturnNode(StmtNode):
    """Класс для представления в AST-дереве оператора return
    """

    def __init__(self, val: ExprNode,
                 row: Optional[int] = None, col: Optional[int] = None, **props) -> None:
        super().__init__(row=row, col=col, **props)
        self.val = val

    def __str__(self) -> str:
        return 'return'

    def to_jpp_code(self, await_names, type_changing, is_async, external_await_names, external_type_changing):
        self.await_names.extend(await_names)
        self.type_changing.extend(type_changing)
        self.is_async = is_async
        self.external_await_names.extend(external_await_names)
        self.external_type_changing.extend(external_type_changing)
        return f"return {self.val.to_jpp_code(self.await_names, self.type_changing, self.is_async, self.external_await_names, self.external_type_changing)}"

    @property
    def childs(self) -> Tuple[ExprNode]:
        return (self.val,)

    def await_names_check(self, is_await):
        return [], []


class IfNode(StmtNode):
    """Класс для представления в AST-дереве условного оператора
    """

    def __init__(self, cond: ExprNode, then_stmt: StmtNode, else_stmt: Optional[StmtNode] = None,
                 row: Optional[int] = None, col: Optional[int] = None, **props) -> None:
        super().__init__(row=row, col=col, **props)
        self.cond = cond
        self.then_stmt = then_stmt
        self.else_stmt = else_stmt

        self.await_names = []
        self.type_changing = []
        self.is_async = []
        self.external_await_names = []
        self.await_names = []

    def __str__(self) -> str:
        return 'if'

    def to_jpp_code(self, await_names, type_changing, is_async, external_await_names, external_type_changing):
        self.await_names.extend(await_names)
        self.type_changing.extend(type_changing)
        self.is_async = is_async
        self.external_await_names.extend(external_await_names)
        self.external_type_changing.extend(external_type_changing)
        then = '   ' + '\n   '.join(
            self.then_stmt.to_jpp_code(self.await_names, self.type_changing, self.is_async,
                                       self.external_await_names, self.external_type_changing).split('\n'))
        cond = self.cond.to_jpp_code(self.await_names, self.type_changing, self.is_async,
                                     self.external_await_names, self.external_type_changing)
        if self.else_stmt is not None:
            else_ = '   ' + '\n   '.join(
                self.else_stmt.to_jpp_code(self.await_names, self.type_changing, self.is_async,
                                           self.external_await_names, self.external_type_changing).split('\n'))
            return f"if ({cond}){{\n{then}\n}}\nelse{{\n{else_}\n}}"
        return f"if ({cond}){{\n{then}\n}}"

    def await_names_check(self):
        result, type_change = [], []
        for x in self.childs:
            tmp_result, tmp_type_change = x.await_names_check()
            result.extend(tmp_result)
            type_change.extend(tmp_type_change)
        return result, type_change

    @property
    def childs(self) -> Tuple[ExprNode, StmtNode, Optional[StmtNode]]:
        return (self.cond, self.then_stmt, *((self.else_stmt,) if self.else_stmt else tuple()))


class ForNode(StmtNode):
    """Класс для представления в AST-дереве цикла for
    """

    def __init__(self, init: Optional[StmtNode], cond: Optional[ExprNode],
                 step: Optional[StmtNode], body: Optional[StmtNode],
                 row: Optional[int] = None, col: Optional[int] = None, **props) -> None:
        super().__init__(row=row, col=col, **props)
        self.init = init if init else EMPTY_STMT
        self.cond = cond if cond else EMPTY_STMT
        self.step = step if step else EMPTY_STMT
        self.body = body if body else EMPTY_STMT

    def __str__(self) -> str:
        return 'for'

    @property
    def childs(self) -> Tuple[AstNode, ...]:
        return self.init, self.cond, self.step, self.body

    def to_jpp_code(self, await_names, type_changing, is_async, external_await_names, external_type_changing):
        self.await_names.extend(await_names)
        self.type_changing.extend(type_changing)
        self.is_async = is_async
        self.external_await_names.extend(external_await_names)
        self.external_type_changing.extend(external_type_changing)

        body = '   ' + '\n   '.join(
            self.body.to_jpp_code(self.await_names, self.type_changing, self.is_async, self.external_await_names,
                                  self.external_type_changing).split('\n'))
        return f"for ({self.init.to_jpp_code(self.await_names, self.type_changing, self.is_async, self.external_await_names, self.external_type_changing)} ; " \
               f"{self.cond.to_jpp_code(self.await_names, self.type_changing, self.is_async, self.external_await_names, self.external_type_changing)} ; " \
               f"{self.step.to_jpp_code(self.await_names, self.type_changing, self.is_async, self.external_await_names, self.external_type_changing)[:-1]}){{\n{body}\n}}"

    def await_names_check(self):
        result, type_change = [], []
        for x in self.childs:
            tmp_result, tmp_type_change = x.await_names_check()
            result.extend(tmp_result)
            type_change.extend(tmp_type_change)
        return result, type_change


class TryNode(StmtNode):
    """Класс для представления в AST-дереве цикла for
    """

    def __init__(self, body: Optional[StmtNode],
                 row: Optional[int] = None, col: Optional[int] = None, **props) -> None:
        super().__init__(row=row, col=col, **props)
        self.body = body if body else EMPTY_STMT

    def __str__(self) -> str:
        return 'try'

    @property
    def childs(self) -> Tuple[AstNode, ...]:
        return [self.body]

    def to_jpp_code(self, await_names, type_changing, is_async, external_await_names, external_type_changing):
        self.await_names.extend(await_names)
        self.type_changing.extend(type_changing)
        self.is_async = is_async
        self.external_await_names.extend(external_await_names)
        self.external_type_changing.extend(external_type_changing)

        body = '   ' + '\n   '.join(
            self.body.to_jpp_code(self.await_names, self.type_changing, self.is_async, self.external_await_names,
                                  self.external_type_changing).split('\n'))
        return f"try{{\n{body}\n}}"

    def await_names_check(self):
        result, type_change = [], []
        for x in self.childs:
            tmp_result, tmp_type_change = x.await_names_check()
            result.extend(tmp_result)
            type_change.extend(tmp_type_change)
        return result, type_change


class CatchNode(StmtNode):
    """Класс для представления в AST-дереве цикла for
    """

    def __init__(self, var: VarsNode, body: Optional[StmtNode],
                 row: Optional[int] = None, col: Optional[int] = None, **props) -> None:
        super().__init__(row=row, col=col, **props)
        self.var = var
        self.body = body if body else EMPTY_STMT

    def __str__(self) -> str:
        return 'catch'

    @property
    def childs(self) -> Tuple[AstNode, ...]:
        return self.var, self.body

    def to_jpp_code(self, await_names, type_changing, is_async, external_await_names, external_type_changing):
        self.await_names.extend(await_names)
        self.type_changing.extend(type_changing)
        self.is_async = is_async
        self.external_await_names.extend(external_await_names)
        self.external_type_changing.extend(external_type_changing)
        body = '   ' + '\n   '.join(
            self.body.to_jpp_code(self.await_names, self.type_changing, self.is_async, self.external_await_names,
                                  self.external_type_changing).split('\n'))
        return f"catch ({self.var.to_jpp_code(self.await_names, self.type_changing, self.is_async, self.external_await_names, self.external_type_changing)}){{\n{body}\n}}"

    def await_names_check(self):
        result, type_change = [], []
        for x in self.childs:
            tmp_result, tmp_type_change = x.await_names_check()
            result.extend(tmp_result)
            type_change.extend(tmp_type_change)
        return result, type_change


class ParamNode(StmtNode):
    """Класс для представления в AST-дереве объявления параметра функции
    """

    def __init__(self, type_: TypeNode, name: IdentNode,
                 row: Optional[int] = None, col: Optional[int] = None, **props) -> None:
        super().__init__(row=row, col=col, **props)
        self.type = type_
        self.name = name

    def __str__(self) -> str:
        return str(self.type)

    @property
    def childs(self) -> Tuple[IdentNode]:
        return self.name,


class FuncNode(StmtNode):
    """Класс для представления в AST-дереве объявления функции
    """

    def __init__(self, async_: AccessNode, access: AccessNode, static: AccessNode, type_: TypeNode, name: IdentNode,
                 params: Tuple[ParamNode], body: Optional[StmtNode] = None,
                 row: Optional[int] = None, col: Optional[int] = None, **props) -> None:
        super().__init__(row=row, col=col, **props)
        self.async_ = async_
        self.access = access if access else empty_access
        self.static = static
        self.type = type_
        self.name = name
        self.params = params
        self.body = body

    def __str__(self) -> str:
        return 'function'

    def to_jpp_code(self, await_names, type_changing, is_async, external_await_names, external_type_changing) -> str:
        self.await_names.extend(await_names)
        self.type_changing.extend(type_changing)
        self.is_async = is_async
        self.external_await_names.extend(external_await_names)
        self.external_type_changing.extend(external_type_changing)

        if self.async_ == "async":
            self.is_async = True
            params = ', '.join(f"Valuable<{i.type.name}> {i.name.name}" for i in self.params)

            self.external_await_names = await_names
            self.external_type_changing = type_changing
        else:
            # type_ = f"Valuable<{self.type.name}>" if self.type.name is not 'void' else f"{self.type.name}"
            # return f"{self.access} {self.static} " + type_ + f" {self.name} ({params}) {{\n{self.body.to_jpp_code(self.await_names, self.type_changing, True, self.external_await_names, self.external_type_changing)} \n}}\n "
            params = ', '.join(f"{i.type.name} {i.name.name}" for i in self.params)
        return f"{self.access} {self.static} {self.type} {self.name} ({params}) {{\n{self.body.to_jpp_code(self.await_names, self.type_changing,  self.is_async, self.external_await_names, self.external_type_changing)}\n}}\n"

    def await_names_check(self):
        if self.async_ == "async":
            self.await_names.extend([x.name.name for x in self.params])
            tmp_result, temp_type_change = self.body.await_names_check(True)
        else:
            tmp_result, temp_type_change = self.body.await_names_check(False)
        self.await_names.extend(tmp_result)
        self.type_changing.extend(temp_type_change)

    @property
    def childs(self) -> Tuple[AstNode, ...]:
        return _GroupNode(str(self.async_),
                          _GroupNode(str(self.access),
                                     _GroupNode(str(self.static),
                                                _GroupNode(str(self.type),
                                                           self.name),
                                                ))), _GroupNode('params', *self.params), self.body


class StmtListNode(StmtNode):
    """Класс для представления в AST-дереве последовательности инструкций
    """

    def __init__(self, *exprs: StmtNode,
                 row: Optional[int] = None, col: Optional[int] = None, **props) -> None:
        super().__init__(row=row, col=col, **props)
        self.exprs = exprs
        self.program = False

    def __str__(self) -> str:
        return '...'

    @property
    def childs(self) -> Tuple[StmtNode, ...]:
        return self.exprs

    def await_names_check(self):
        result = []
        type_change = []
        for x in self.childs:
            if isinstance(x, FuncNode):
                x.await_names_check()
            else:
                tmp_result, tmp_type_change = x.await_names_check()
                result.extend(tmp_result)
                type_change.extend(tmp_type_change)
        return result, type_change

    def to_jpp_code(self, await_names, type_changing, is_async, external_await_names, external_type_changing):
        self.await_names.extend(await_names)
        self.type_changing.extend(type_changing)
        self.is_async = is_async
        self.external_await_names.extend(external_await_names)
        self.external_type_changing.extend(external_type_changing)
        result = "\n".join(x.to_jpp_code(self.await_names, self.type_changing, self.is_async, self.external_await_names,
                                         self.external_type_changing)
                           if isinstance(x, FuncNode)
                           else (
                x.to_jpp_code(self.await_names, self.type_changing, self.is_async, self.external_await_names,
                              self.external_type_changing) + ";")
                           for x in self.childs)
        return result


class FuncStmtListNode(StmtNode):
    """Класс для представления в AST-дереве последовательности инструкций
    """

    def __init__(self, *exprs: StmtNode,
                 row: Optional[int] = None, col: Optional[int] = None, **props) -> None:
        super().__init__(row=row, col=col, **props)
        self.exprs = exprs
        self.program = False

    def __str__(self) -> str:
        return '...'

    def to_jpp_code(self, await_names, type_changing, is_async, external_await_names, external_type_changing) -> str:
        self.await_names.extend(await_names)
        self.type_changing.extend(type_changing)
        self.is_async = is_async
        self.external_await_names.extend(external_await_names)
        self.external_type_changing.extend(external_type_changing)


        body = '\n   '.join(
            f"{x.to_jpp_code(self.await_names, self.type_changing, self.is_async, self.external_await_names, self.external_type_changing)}" if isinstance(
                x, IfNode) or isinstance(x,
                                         ForNode) or isinstance(x,
                                         TryNode) or isinstance(x,
                                         CatchNode) else f"{x.to_jpp_code(self.await_names, self.type_changing, self.is_async, self.external_await_names, self.external_type_changing)};"
            for x in self.exprs)
        return body

    def await_names_check(self, *args):
        result, type_change = [], []
        for x in self.exprs:
            if isinstance(x, ReturnNode):
                tmp_result, tmp_type_change = x.await_names_check(args[0])
            else :
                tmp_result, tmp_type_change = x.await_names_check()
            result.extend(tmp_result)
            type_change.extend(tmp_type_change)
        return result, type_change

    @property
    def childs(self) -> Tuple[StmtNode, ...]:
        return self.exprs


EMPTY_STMT = StmtListNode()
EMPTY_IDENT = IdentDesc('', TypeDesc.VOID)


class ClassInitNode(StmtNode):
    """Класс для представления в AST-дереве объявления функции
    """

    def __init__(self, access: AccessNode, name: IdentNode, body: Optional[StmtListNode] = None,
                 row: Optional[int] = None, col: Optional[int] = None, **props) -> None:
        super().__init__(row=row, col=col, **props)
        self.access = access if access else empty_access
        self.name = name
        self.body = body if body else empty_statement_list

    def __str__(self) -> str:
        return 'class'

    def to_jpp_code(self, *args):
        if args:
            self.await_names = args[0]
            self.type_changing = args[1]
            self.is_async = args[2]
            self.external_await_names = args[3]
            self.external_type_changing = args[4]


        tmp_await_names, tmp_type_changing = self.body.await_names_check()
        self.await_names.extend(tmp_await_names)
        self.type_changing.extend(tmp_type_changing)
        lines = self.body.to_jpp_code(self.await_names, self.type_changing, self.is_async,
                                      self.external_await_names,
                                      self.external_type_changing).split('\n')
        body = '   ' + '\n   '.join(line for line in lines)
        return f"{self.access} class {self.name} {{\n{body}}}"

    @property
    def childs(self) -> Tuple[AstNode, ...]:
        return _GroupNode(str(self.access), self.name), self.body


empty_statement_list = StmtListNode()
empty_access = AccessNode("")
