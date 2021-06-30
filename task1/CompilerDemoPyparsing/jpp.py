import sys
from compiler_demo import program

if __name__ == "__main__":
    path = sys.argv[1]
    res = ""
    with open(path, "r") as inp:
        res += inp.readline()
        res += inp.readline()
        res += program.execute(inp.read())