import sys
from compiler_demo import program

if __name__ == "__main__":
    path = sys.argv[1]
    print(path)
    with open(path, "r") as inp:
        # print(inp.read())
        program.execute(inp.read())