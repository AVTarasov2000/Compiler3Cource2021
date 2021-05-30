class Vision:
    def __init__(self, start: int):
        self.start = start
        self.visions = list()


    def configure(self, program):
        self.visions = list()
        i = self.start + 1
        while i < len(program):
            if program[i] == "{":
                v = Vision(i)
                i = v.configure(program)
                self.visions.append(v)
            elif program[i] == "}":
                self.end = i
                return i + 1
            i += 1


        # for i, char in enumerate(program):
        #     if char == "{":
        #         self.visions.append(Vision(program[i+1:len(program)], i))
        #     elif char == "}":
        #         self.end = i
        #         break

strt = " {gdfzjfhb{zdjfjv} " \
       "{bs d c}, hfhh " \
       "{shdbcjv" \
       "{ sjhbc}" \
       "jkrbf}" \
       "m sdh}"
v = Vision(0)
v.configure(strt)

print(v)
