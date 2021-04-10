from abc import ABC, abstractmethod
from contextlib import suppress
from typing import Optional, Union, Tuple, Callable

from .semantic import TYPE_CONVERTIBILITY, BIN_OP_TYPE_COMPATIBILITY, BinOp, \
    TypeDesc, IdentDesc, ScopeType, IdentScope, SemanticException


class AstNode(ABC):
    """Базовый абстрактый класс узла AST-дерева
    """

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

    def semantic_error(self, message: str):
        raise SemanticException(message, self.row, self.col)

    def semantic_check(self, scope: IdentScope) -> None:
        pass

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


class ExprNode(AstNode, ABC):
    """Абстракный класс для выражений в AST-дереве
    """

    pass


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

    def semantic_check(self, scope: IdentScope) -> None:
        self.node_type = TypeDesc.STR
        # if isinstance(self.value, bool):
        #     self.node_type = TypeDesc.BOOL
        # # проверка должна быть позже bool, т.к. bool наследник от int
        # elif isinstance(self.value, int):
        #     self.node_type = TypeDesc.INT
        # elif isinstance(self.value, float):
        #     self.node_type = TypeDesc.FLOAT
        # elif isinstance(self.value, str):
        #     self.node_type = TypeDesc.STR
        # else:
        #     self.semantic_error('Неизвестный тип {} для {}'.format(type(self.value), self.value))

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

    @property
    def childs(self) -> Tuple[IdentNode, ...]:
        return (self.func, *self.params)

    def semantic_check(self, scope: IdentScope) -> None:
        func = scope.get_ident(self.func.name)
        if func is None:
            self.semantic_error('Функция {} не найдена'.format(self.func.name))
        if not func.type.func:
            self.semantic_error('Идентификатор {} не является функцией'.format(func.name))
        if len(func.type.params) != len(self.params):
            self.semantic_error('Кол-во аргументов {} не совпадает (ожидалось {}, передано {})'.format(
                func.name, len(func.type.params), len(self.params)
            ))
        params = []
        error = False
        decl_params_str = fact_params_str = ''
        for i in range(len(self.params)):
            param: ExprNode = self.params[i]
            param.semantic_check(scope)
            if (len(decl_params_str) > 0):
                decl_params_str += ', '
            decl_params_str += str(func.type.params[i])
            if (len(fact_params_str) > 0):
                fact_params_str += ', '
            fact_params_str += str(param.node_type)
            try:
                params.append(type_convert(param, func.type.params[i]))
            except:
                error = True
        if error:
            self.semantic_error('Фактические типы ({1}) аргументов функции {0} не совпадают с формальными ({2})\
                                    и не приводимы'.format(
                func.name, fact_params_str, decl_params_str
            ))
        else:
            self.params = tuple(params)
            self.func.node_type = func.type
            self.func.node_ident = func
            self.node_type = func.type.return_type