def xor(num1, num2):
    num1, num2 = set_zeros(num1, num2)
    res = ""
    for i in range(len(num1)):
        if num1[i]!=num2[i]:
            res+="1"
        else:
            res+='0'
    return res


def andd(num1, num2):
    num1, num2 = set_zeros(num1, num2)
    res = ""
    for i in range(len(num1)):
        if num1[i] == num2[i]=="1":
            res += "1"
        else:
            res += '0'
    return res


def orr(num1, num2):
    num1, num2 = set_zeros(num1, num2)
    res = ""
    for i in range(len(num1)):
        if num1[i] == num2[i] == "0":
            res += "0"
        else:
            res += '1'
    return res


def set_zeros(num1, num2):
    if len(num1)<len(num2):
        while len(num1)!=len(num2):
            num1="0"+num1
    elif len(num2)<len(num1):
        while len(num2)!=len(num1):
            num2="0"+num2
    return num1, num2

def plus(num1, num2):
    res = str(bin(int(num1, base=2) + int(num2, base=2)))
    return res[2:]


def minus(num1, num2):
    res = str(bin(int(num1, base=2) - int(num2, base=2)))
    if res[0] == "-":
        return "-"+res[3:]
    return res[2:]


class Parser:

    def __init__(self, text: str):
        self.text = text.strip().split(" ")
        self.text.append("$")
        self.pos = 0

    @property
    def curr(self) -> str:
        return self.text[self.pos]

    def num(self):
        tmp = ''
        tmp += self.curr
        self.pos += 1
        return tmp

    def mult(self):
        res = self.num()
        while True:
            if self.curr == "xor":
                self.pos += 1
                res = xor(res, self.num())
            elif self.curr == "and":
                self.pos += 1
                res = andd(res, self.num())
            elif self.curr == "or":
                self.pos += 1
                res = orr(res, self.num())
            else:
                break
        return res

    def add(self) -> float:
        res = self.mult()
        while True:
            if self.curr == "plus":
                self.pos += 1
                arg2 = self.mult()
                res = plus(res, arg2)
            elif self.curr == "minus":
                self.pos += 1
                arg2 = self.mult()
                res = minus(res, arg2)
            else:
                break
        return res

    def start(self):
        return self.add()


def main(text):
    parser = Parser(text)
    print(parser.start())


def read_file():
    with open('input.txt') as f:
        length = int(f.readline())
        for i in range(length):
            main(f.readline())


if __name__ == '__main__':
    read_file()






