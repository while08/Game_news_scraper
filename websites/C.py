
class C:
    R = '\033[31m'
    Y = '\033[33m'
    G = '\033[32m'
    B = '\033[34m'
    END = '\033[0m'

    @classmethod
    def RED(cls, text: str):
        return (C.R + text + C.END)

    @classmethod
    def YELLOW(cls, text: str):
        return (C.Y + text + C.END)

    @classmethod
    def GREEN(cls, text: str):
        return (C.G + text + C.END)

    @classmethod
    def BLUE(cls, text: str):
        return (C.B + text + C.END)
