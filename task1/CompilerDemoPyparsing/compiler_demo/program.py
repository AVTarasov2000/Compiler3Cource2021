import os

from . import my_parser as parser
from .ast import FuncNode, IdentNode, AccessNode, AssignNode, VarsNode


def execute(prog: str) -> None:
    prog = parser.parse(prog)
    ast_tree = prog.tree
    satck = []
    satck.append(prog.childs[1])
    while len(satck) != 0:
        curr_element = satck.pop()
        coords = " [call: " + str(curr_element.col) + " row: " + str(curr_element.row) + "]"
        if (FuncNode.__name__ == curr_element.__class__.__name__):
            print("Function: " + curr_element.__class__.__name__ + " " + str(curr_element.type) + " " + str(curr_element.name) + coords)
        elif (IdentNode.__name__ == curr_element.__class__.__name__):
            print("Ident: " + curr_element.__class__.__name__ + " " + curr_element.__str__()  + coords)
        elif (AccessNode.__name__ == curr_element.__class__.__name__):
            print("Access: " + curr_element.__class__.__name__ + " " + str(curr_element.type)  + coords)
        elif (AssignNode.__name__ == curr_element.__class__.__name__):
            print("Assign: " + curr_element.__class__.__name__ + " var:" + str(curr_element.var) + " , val: " + str(curr_element.val) + coords)
        elif (VarsNode.__name__ == curr_element.__class__.__name__):
            print("VarsNode: " + curr_element.__class__.__name__ + " type:" + str(curr_element.type) + " , vars " + str(*(curr_element.vars)) + coords)
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
