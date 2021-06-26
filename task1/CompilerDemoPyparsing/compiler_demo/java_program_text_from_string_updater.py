from task1.CompilerDemoPyparsing.compiler_demo.vission_parser import Vision
from task1.CompilerDemoPyparsing.compiler_demo.log import Log


def parseAsyncAwaitJavaCode(program: str, logs: list, triggers: list, vision: Vision):
    for i in logs:
        vision.addLog(i)
    for i in triggers:
        vision.listToChange(i)
    rows = program.split("\n")

    pass
