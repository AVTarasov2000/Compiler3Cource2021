import os

from . import my_parser as parser
from .ast import FuncNode, IdentNode, AccessNode, AssignNode, VarsNode, CallNode, CallerNode
from .log import FuncInitLog, VarInitLog, CollVarLog


def execute(prog: str) -> None:
    prog = parser.parse(prog)
    ast_tree = prog.tree
    satck = []
    satck.append(prog.childs[1])
    while len(satck) != 0:
        curr_element = satck.pop()
        coords = " [call: " + str(curr_element.col) + " row: " + str(curr_element.row) + "]"
        if FuncNode.__name__ == curr_element.__class__.__name__:
            print("Function: " + curr_element.__class__.__name__ + " " + str(curr_element.type) + " " + str(
                curr_element.name) + coords)
            log = FuncInitLog(str(curr_element.type), curr_element.name, curr_element.col, curr_element.row)
        elif IdentNode.__name__ == curr_element.__class__.__name__:
            print("Ident: " + curr_element.__class__.__name__ + " " + curr_element.__str__() + coords)
        elif AccessNode.__name__ == curr_element.__class__.__name__:
            print("Access: " + curr_element.__class__.__name__ + " " + str(curr_element.type) + coords)
        elif AssignNode.__name__ == curr_element.__class__.__name__:
            print("Assign: " + curr_element.__class__.__name__ + " var:" + str(curr_element.var) + " , val: " + str(
                curr_element.val) + coords)
        elif CallNode.__name__ == curr_element.__class__.__name__:
            print(
                "Call: " + curr_element.__class__.__name__ + " params: " + str([x.childs[1].name for x in curr_element.childs[1].childs]) + coords)

            # log = CollVarLog(curr_element.vars, curr_element.col, curr_element.row)
            # print("Call: " + curr_element.__class__.__name__ + " params: " + str(*curr_element.childs[1].childs) + coords)
        elif CallerNode.__name__ == curr_element.__class__.__name__:
            if curr_element.childs[1].__class__.__name__ == IdentNode.__name__:
                print("Caller: " + curr_element.__class__.__name__ + " params: " + " " + str(
                    curr_element.childs[1].name) + coords)
            elif curr_element.childs[1].__class__.__name__ == CallNode.__name__:
                print("Caller: " + curr_element.__class__.__name__ + " params: " + str(curr_element.call) + " " + curr_element.childs[1].childs[0].name + coords)
        elif VarsNode.__name__ == curr_element.__class__.__name__:
            if curr_element.vars[0].__class__.__name__ == IdentNode.__name__:
                print("VarsNode: " + curr_element.__class__.__name__ + " type:" + str(
                    curr_element.type) + " , var_name: " + str(*(curr_element.vars)) + coords)
                log = VarInitLog(str(curr_element.type), curr_element.vars, curr_element.col, curr_element.row)
            elif curr_element.vars[0].__class__.__name__ == AssignNode.__name__:
                print("VarsNode: " + curr_element.__class__.__name__ + " type:" + str(
                    curr_element.type) + " , var_name: " + str(curr_element.vars[0].var.name) + coords)
                log = VarInitLog(str(curr_element.type), curr_element.vars[0].var.name, curr_element.col, curr_element.row)

        else:
            print(curr_element.__class__.__name__)

        curr_element_childs = curr_element.childs
        if not curr_element_childs is None and len(curr_element_childs) != 0:
            satck.extend(curr_element.childs)
    # replacement_list

    print('ast:')
    print(*ast_tree, sep=os.linesep)
    print()
    print('semantic_check:')

    # try:
    #     scope = semantic.prepare_global_scope()
    #     prog.semantic_check(scope)
    #     print(*prog.tree, sep=os.linesep)
    # except semantic.SemanticException as e:
    #     print('Ошибка: {}'.format(e.message))
    #     return
    # print()
