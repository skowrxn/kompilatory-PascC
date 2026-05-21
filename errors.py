"""Klasy wyjątków dla poszczególnych faz translatora PascC."""


class LexError(Exception):
    def __init__(self, msg, line=0):
        super().__init__(f"[BŁĄD LEKSYKALNY] linia {line}: {msg}")
        self.line = line


class ParseError(Exception):
    def __init__(self, msg, line=0):
        super().__init__(f"[BŁĄD SKŁADNIOWY] linia {line}: {msg}")
        self.line = line


class SemanticError(Exception):
    def __init__(self, msg, line=0):
        super().__init__(f"[BŁĄD SEMANTYCZNY] linia {line}: {msg}")
        self.line = line
