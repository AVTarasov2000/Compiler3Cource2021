class Log:
    def __init__(self, name, call, row) -> None:
        self.name = name
        self.call = call
        self.row = row


class VarInitLog(Log):
    def __init__(self, type, name, call, row) -> None:
        super().__init__(name=name, row=row, call=call)
        self.type = type
        self.log_title = "var_init"


class FuncInitLog(Log):
    def __init__(self, type, name, call, row) -> None:
        super().__init__(name=name, row=row, call=call)
        self.type = type


class CollVarLog(Log):
    def __init__(self, name, call, row) -> None:
        super().__init__(name=name, row=row, call=call)


class AwaitCall(Log):
    def __init__(self, name, call, row) -> None:
        super().__init__(name=name, row=row, call=call)
