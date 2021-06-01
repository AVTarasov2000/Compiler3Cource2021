class Log:
    def __init__(self, name, call, row) -> None:
        self.name = name
        self.call = call
        self.row = row


class VarInitLog(Log):
    def __init__(self, type, name, call, row) -> None:
        super().__init__(name=name, row=row, call=call)
        self.type = type

class FuncInitLog(Log):
    def __init__(self, access, async_, type, name, call, row, params) -> None:
        super().__init__(name=name, row=row, call=call)
        self.type = type
        self.access = access
        self.async_ = async_
        self.params = params

    def to_string(self):
        params = ', '.join(f"{i.type} {i.name}" for i in self.params)
        return f"{self.access} {self.async_} {self.type} {self.name} ({params})"

    def to_async_string(self):
        params = ', '.join(f"Promise<{i[0]}> {i[1]}" for i in self.params)
        return f"{self.access} Promise<{self.type}> {self.name} ({params})"


class CollVarLog(Log):
    def __init__(self, name, call, row) -> None:
        super().__init__(name=name, row=row, call=call)


class AwaitCall(Log):
    def __init__(self, name, call, row) -> None:
        super().__init__(name=name, row=row, call=call)
