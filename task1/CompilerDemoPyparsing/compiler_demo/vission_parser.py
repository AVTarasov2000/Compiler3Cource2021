from task1.CompilerDemoPyparsing.compiler_demo.log import Log, VarInitLog


class Vision:
    def __init__(self, row: int, col: int, parent):
        self.parent = parent
        self.row_start = row
        self.col_start = col
        self.visions = list()
        self.logs = list()

    def configure(self, program):
        self.visions = list()
        row = self.row_start
        col = self.col_start
        while row < len(program):
            while col < len(program[row]):
                if program[row][col] == "{":
                    v = Vision(row, col+1, self)
                    row, col = v.configure(program)
                    self.visions.append(v)
                elif program[row][col] == "}":
                    self.col_end = col
                    self.row_end = row
                    return row, col
                col += 1
            row += 1
            col = 0

    def isIn(self, log: Log):
        return max((self.row_start, self.col_start), (log.row, log.call), key=lambda s:(s[0], s[1])) == (log.row, log.call) and\
               min((self.row_end, self.col_end), (log.row, log.call), key=lambda s:(s[0], s[1])) == (log.row, log.call)


    def addLog(self, log: Log):
        for vis in self.visions:
            if vis.isIn(log):
                vis.addLog(log)
                return
        self.logs.append(log)

    def hasInit(self, log: Log):
        for lg in self.logs:
            if log.name == lg.name:
                if lg.__class__.__name__ == VarInitLog.__name__:
                    return True

    def listToChange(self, log: Log):
        result = list()
        check = True
        for vis in self.visions:
            if vis.isIn(log):
                checkTmp, res = vis.listToChange(log)
                for i in res:
                    result.append(i)
                if checkTmp:
                    check = False
        if check:
            for i in self.logs:
                if i.name == log.name:
                    result.append(i)
        if self.hasInit(log):
            return True, result
        else:
            return not check, result




strt = " {gdfzjfhb{zdjfjv} \n" \
       "{bs d c}, hfhh \n" \
       "{shdbcjv \n" \
       "{ sjhbc} \n" \
       "jkrbf} \n" \
       "m sdh} \n"
v = Vision(0, 0, None)

v.configure(strt.split("\n"))
log = Log("a", 3, 0)
log1 = Log("a", 7, 0)
log2 = VarInitLog("int", "a", 13, 0)
log3 = Log("a", 14, 0)
v.addLog(log)
v.addLog(log1)
v.addLog(log2)
v.addLog(log3)

triger = Log("a", 15, 0)
res = v.listToChange(triger)
for i in res[1]:
    print(f"{i.name}, {i.row}, {i.call}")

print(v)
