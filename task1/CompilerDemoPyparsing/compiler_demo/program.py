import os

from . import my_parser as parser
from .ast import FuncNode, IdentNode, AccessNode, AssignNode, VarsNode, CallNode, CallerNode, FuncStmtListNode
from .log import FuncInitLog, VarInitLog, CollVarLog, AwaitCall


def get_log_map(prog):
    result_list = []
    satck = []
    satck.append(prog.childs[1])
    while len(satck) != 0:
        curr_element = satck.pop()
        # if FuncNode.__name__ == curr_element.__class__.__name__:
        #     result_list.append(
        #         FuncInitLog(str(curr_element.type), curr_element.name.name, curr_element.col, curr_element.row))
        # elif CallNode.__name__ == curr_element.__class__.__name__:
        #     for x in curr_element.childs[1].childs:
        #         result_list.append(
        #             CollVarLog(x.childs[1].name, x.childs[1].col, x.childs[1].row))
        # elif CallerNode.__name__ == curr_element.__class__.__name__:
        #     if curr_element.childs[1].__class__.__name__ == IdentNode.__name__:
        #         result_list.append(
        #             CollVarLog(curr_element.childs[1].name, curr_element.childs[1].col,
        #                        curr_element.childs[1].row))
        #     elif curr_element.childs[1].__class__.__name__ == CallNode.__name__:
        #         result_list.append(
        #             AwaitCall(curr_element.childs[1].childs[0].name, curr_element.childs[1].childs[0].col,
        #                       curr_element.childs[1].childs[0].row))
        # elif VarsNode.__name__ == curr_element.__class__.__name__:
        #     if curr_element.vars[0].__class__.__name__ == IdentNode.__name__:
        #         for x in curr_element.vars:
        #             result_list.append(VarInitLog(str(curr_element.type), x.name, x.col, x.row))
        #     elif curr_element.vars[0].__class__.__name__ == AssignNode.__name__:
        #         result_list.append(VarInitLog(str(curr_element.type), curr_element.vars[0].var.name, curr_element.col,
        #                                       curr_element.row))

        # coords = " [call: " + str(curr_element.col) + " row: " + str(curr_element.row) + "]"
        # if FuncNode.__name__ == curr_element.__class__.__name__:
        #     print("Function: " + curr_element.__class__.__name__ + " " + str(curr_element.type) + " " + str(
        #         curr_element.name) + coords)
        #     params = [(x.type.name, x.childs[0].name)for x in curr_element.params]
        #     result_list.append(FuncInitLog(curr_element.access, curr_element.async_, curr_element.type.name,
        #                                    curr_element.name, curr_element.col, curr_element.row, params))
        # elif CallNode.__name__ == curr_element.__class__.__name__:
        #     print(
        #         "Call: " + curr_element.__class__.__name__ + " params: " + str(
        #             [x.childs[1].name for x in curr_element.childs[1].childs]) + coords)
        #     for x in curr_element.childs[1].childs:
        #         result_list.append(
        #             CollVarLog(x.childs[1].name, x.childs[1].col, x.childs[1].row))
        # elif FuncStmtListNode.__name__ == curr_element.__class__.__name__:
        #     print("")
        # elif CallerNode.__name__ == curr_element.__class__.__name__:
        #     if curr_element.childs[1].__class__.__name__ == IdentNode.__name__:
        #         print("Caller: " + curr_element.__class__.__name__ + " params: " + " " + str(
        #             curr_element.childs[1].name) + coords)
        #         result_list.append(
        #             CollVarLog(curr_element.childs[1].name, curr_element.childs[1].col,
        #                       curr_element.childs[1].row))
        #     elif curr_element.childs[1].__class__.__name__ == CallNode.__name__:
        #         print("Caller: " + curr_element.__class__.__name__ + " params: " + str(curr_element.call) + " " +
        #               curr_element.childs[1].childs[0].name + coords)
        #         result_list.append(AwaitCall(curr_element.childs[1].childs[0].name, curr_element.childs[1].childs[0].col, curr_element.childs[1].childs[0].row))
        # elif VarsNode.__name__ == curr_element.__class__.__name__:
        #     if curr_element.vars[0].__class__.__name__ == IdentNode.__name__:
        #         for x in curr_element.vars:
        #             print("VarsNode: " + curr_element.__class__.__name__ + " type:" + str(
        #                 curr_element.type) + " , var_name: " + x.name + " [" + str(x.col) + ":" + str(x.row) + "]")
        #             result_list.append(VarInitLog(str(curr_element.type), x.name, x.col, x.row))
        #     elif curr_element.vars[0].__class__.__name__ == AssignNode.__name__:
        #         print("VarsNode: " + curr_element.__class__.__name__ + " type:" + str(
        #             curr_element.type) + " , var_name: " + str(curr_element.vars[0].var.name) + coords)
        #         result_list.append(VarInitLog(str(curr_element.type), curr_element.vars[0].var.name, curr_element.col,
        #                          curr_element.row))
        #
        curr_element_childs = curr_element.childs
        if curr_element_childs is not None and len(curr_element_childs) != 0:
            satck.extend(curr_element.childs)
    return result_list

def to_jpp_code(prog)-> str:
    return prog.body.to_jpp_code()


def execute(prog: str) -> None:
    prog = parser.parse(prog)
    ast_tree = prog.tree
    replacemant_list = get_log_map(prog)

    print('ast:')
    print(*ast_tree, sep=os.linesep)
    print()
    print('semantic_check:')
    print(*[x.to_async_string() + "\n" for x in replacemant_list if x.__class__.__name__ == FuncInitLog.__name__])
    print(prog.to_jpp_code())

    # try:
    #     scope = semantic.prepare_global_scope()
    #     prog.semantic_check(scope)
    #     print(*prog.tree, sep=os.linesep)
    # except semantic.SemanticException as e:
    #     print('Ошибка: {}'.format(e.message))
    #     return
    # print()
