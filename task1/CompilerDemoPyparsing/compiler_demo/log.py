class Log:
    def __init__(self, name, call, row) -> None:
        self.name = name
        self.call = call
        self.row = row


class VarInitLog(Log):
    def __init__(self, type_, name, call, row) -> None:
        super().__init__(name=name, row=row, call=call)
        self.type = type_
        self.log_title = "var_init"


class FuncInitLog(Log):
    def __init__(self, type_, name, call, row) -> None:
        super().__init__(name=name, row=row, call=call)
        self.type = type_


class CollVarLog(Log):
    def __init__(self, name, call, row) -> None:
        super().__init__(name=name, row=row, call=call)


class AwaitCall(Log):
    def __init__(self, name, call, row) -> None:
        super().__init__(name=name, row=row, call=call)
