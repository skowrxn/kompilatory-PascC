"""Analiza semantyczna — tablica symboli i sprawdzanie typów."""

from ast_nodes import (
    Program, Block, VarSection, VarDecl, ProcedureDecl, FunctionDecl,
    ParamGroup, CompoundStatement, Assignment, ProcedureCall,
    IfStatement, WhileStatement, ForStatement, RepeatStatement,
    WriteStatement, ReadStatement, WriteArg,
    BinOp, UnaryOp, IntConst, RealConst, CharConst, StringConst,
    BoolConst, VarRef, FunctionCallExpr,
    ArrayDecl, ArrayAccess, ArrayAssignment,
)
from errors import SemanticError

NUMERIC = {'integer', 'real'}
SCALAR  = {'integer', 'real', 'boolean', 'char', 'string'}


class SymbolTable:
    """Stos słowników reprezentujących zakresy leksykalne."""

    def __init__(self):
        self.scopes: list[dict] = [{}]

    def push_scope(self):
        self.scopes.append({})

    def pop_scope(self):
        self.scopes.pop()

    def declare(self, name: str, symbol: dict, line: int = 0):
        key = name.lower()
        if key in self.scopes[-1]:
            raise SemanticError(f"Redefinicja symbolu '{name}'", line)
        self.scopes[-1][key] = symbol

    def lookup(self, name: str, line: int = 0) -> dict:
        key = name.lower()
        for scope in reversed(self.scopes):
            if key in scope:
                return scope[key]
        raise SemanticError(f"Niezadeklarowany symbol '{name}'", line)

    def lookup_or_none(self, name: str):
        key = name.lower()
        for scope in reversed(self.scopes):
            if key in scope:
                return scope[key]
        return None


class SemanticAnalyzer:
    """Przechodzi AST i weryfikuje poprawność semantyczną programu."""

    def __init__(self):
        self.symbols = SymbolTable()
        self._current_func: str | None = None  # nazwa bieżącej funkcji (dla := return)

    # ── publiczne API ─────────────────────────────────────────────────────────
    def analyze(self, node):
        self.visit(node)

    # ── dispatcher ────────────────────────────────────────────────────────────
    def visit(self, node):
        if node is None:
            return None
        method = 'visit_' + type(node).__name__
        visitor = getattr(self, method, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        return None

    # ── węzły ─────────────────────────────────────────────────────────────────
    def visit_Program(self, node: Program):
        self.visit(node.block)

    def visit_Block(self, node: Block):
        if node.var_section:
            self.visit(node.var_section)
        for decl in node.sub_decls:
            self.visit(decl)
        self.visit(node.compound)

    def visit_VarSection(self, node: VarSection):
        for decl in node.declarations:
            self.visit(decl)

    def visit_VarDecl(self, node: VarDecl):
        for name in node.names:
            self.symbols.declare(name, {'kind': 'var', 'type': node.type_name}, node.line)

    def visit_ArrayDecl(self, node: ArrayDecl):
        for name in node.names:
            self.symbols.declare(name, {
                'kind': 'array',
                'elem_type': node.elem_type,
                'low': node.low,
                'high': node.high,
            }, node.line)

    def visit_ArrayAccess(self, node: ArrayAccess) -> str:
        sym = self.symbols.lookup(node.name, node.line)
        if sym['kind'] != 'array':
            raise SemanticError(f"'{node.name}' nie jest tablicą", node.line)
        self.visit(node.index)
        return sym['elem_type']

    def visit_ArrayAssignment(self, node: ArrayAssignment):
        sym = self.symbols.lookup(node.name, node.line)
        if sym['kind'] != 'array':
            raise SemanticError(f"'{node.name}' nie jest tablicą", node.line)
        self.visit(node.index)
        val_type = self.visit(node.value)
        self._check_assign_compat(sym['elem_type'], val_type, node.line)

    def visit_ProcedureDecl(self, node: ProcedureDecl):
        params_info = self._params_info(node.params)
        self.symbols.declare(node.name,
                             {'kind': 'proc', 'params': params_info}, node.line)
        self.symbols.push_scope()
        self._declare_params(node.params)
        self.visit(node.sub_block)
        self.symbols.pop_scope()

    def visit_FunctionDecl(self, node: FunctionDecl):
        params_info = self._params_info(node.params)
        self.symbols.declare(node.name,
                             {'kind': 'func', 'type': node.return_type,
                              'params': params_info}, node.line)
        self.symbols.push_scope()
        self._declare_params(node.params)
        # wynik funkcji pod specjalnym kluczem, nie pod nazwą funkcji
        self.symbols.declare('__retval__',
                             {'kind': 'retval', 'type': node.return_type}, node.line)
        prev = self._current_func
        self._current_func = node.name.lower()
        self.visit(node.sub_block)
        self._current_func = prev
        self.symbols.pop_scope()

    def visit_CompoundStatement(self, node: CompoundStatement):
        for stmt in node.statements:
            self.visit(stmt)

    def visit_Assignment(self, node: Assignment):
        # przypisanie do nazwy funkcji = return value
        if self._current_func and node.target.lower() == self._current_func:
            retval = self.symbols.lookup('__retval__', node.line)
            val_type = self.visit(node.value)
            self._check_assign_compat(retval['type'], val_type, node.line)
            return
        sym = self.symbols.lookup(node.target, node.line)
        val_type = self.visit(node.value)
        if sym['kind'] in ('var', 'retval'):
            self._check_assign_compat(sym['type'], val_type, node.line)

    def visit_ProcedureCall(self, node: ProcedureCall):
        sym = self.symbols.lookup_or_none(node.name)
        if sym is None:
            raise SemanticError(
                f"Niezadeklarowana procedura/funkcja '{node.name}'", node.line)
        if sym['kind'] not in ('proc', 'func'):
            raise SemanticError(
                f"'{node.name}' nie jest procedurą ani funkcją", node.line)
        self._check_args(node.name, sym.get('params', []), node.args, node.line)

    def visit_IfStatement(self, node: IfStatement):
        self.visit(node.condition)
        self.visit(node.then_branch)
        if node.else_branch:
            self.visit(node.else_branch)

    def visit_WhileStatement(self, node: WhileStatement):
        self.visit(node.condition)
        self.visit(node.body)

    def visit_ForStatement(self, node: ForStatement):
        sym = self.symbols.lookup(node.var, node.line)
        if sym['type'] != 'integer':
            raise SemanticError(
                f"Zmienna sterująca pętli for '{node.var}' musi być integer", node.line)
        self.visit(node.start)
        self.visit(node.end)
        self.visit(node.body)

    def visit_RepeatStatement(self, node: RepeatStatement):
        for stmt in node.body:
            self.visit(stmt)
        self.visit(node.condition)

    def visit_WriteStatement(self, node: WriteStatement):
        for arg in node.args:
            self.visit(arg.expr if isinstance(arg, WriteArg) else arg)

    def visit_ReadStatement(self, node: ReadStatement):
        for name in node.vars:
            self.symbols.lookup(name, node.line)

    # ── wyrażenia ─────────────────────────────────────────────────────────────
    def visit_BinOp(self, node: BinOp) -> str:
        lt = self.visit(node.left)
        rt = self.visit(node.right)
        op = node.op.lower()

        if op in ('+', '-', '*', '/'):
            if lt in NUMERIC and rt in NUMERIC:
                return 'real' if 'real' in (lt, rt) else 'integer'
            if op == '+' and lt == 'string' and rt == 'string':
                return 'string'
        if op in ('div', 'mod'):
            return 'integer'
        if op in ('and', 'or'):
            return 'boolean'
        if op in ('=', '<>', '<', '>', '<=', '>='):
            return 'boolean'
        return lt or 'integer'

    def visit_UnaryOp(self, node: UnaryOp) -> str:
        t = self.visit(node.operand)
        if node.op == 'not':
            return 'boolean'
        return t or 'integer'

    def visit_VarRef(self, node: VarRef) -> str:
        sym = self.symbols.lookup(node.name, node.line)
        return sym.get('type', 'integer')

    def visit_FunctionCallExpr(self, node: FunctionCallExpr) -> str:
        sym = self.symbols.lookup(node.name, node.line)
        if sym['kind'] != 'func':
            raise SemanticError(
                f"'{node.name}' nie jest funkcją", node.line)
        self._check_args(node.name, sym.get('params', []), node.args, node.line)
        return sym.get('type', 'integer')

    def visit_IntConst(self, node: IntConst) -> str:    return 'integer'
    def visit_RealConst(self, node: RealConst) -> str:  return 'real'
    def visit_CharConst(self, node: CharConst) -> str:  return 'char'
    def visit_StringConst(self, node: StringConst) -> str: return 'string'
    def visit_BoolConst(self, node: BoolConst) -> str:  return 'boolean'

    # ── pomocnicze ────────────────────────────────────────────────────────────
    def _params_info(self, params: list) -> list:
        result = []
        for pg in params:
            for name in pg.names:
                result.append({'name': name, 'type': pg.type_name, 'by_ref': pg.by_ref})
        return result

    def _declare_params(self, params: list):
        for pg in params:
            for name in pg.names:
                self.symbols.declare(name, {'kind': 'var', 'type': pg.type_name})

    def _check_args(self, fname: str, params: list, args: list, line: int):
        if len(params) != len(args):
            raise SemanticError(
                f"'{fname}': oczekiwano {len(params)} argumentów, "
                f"podano {len(args)}", line)

    def _check_assign_compat(self, expected: str, got: str | None, line: int):
        if got is None:
            return
        if expected == got:
            return
        if expected == 'real' and got == 'integer':
            return
        if expected == 'string' and got == 'char':
            return
        raise SemanticError(
            f"Niezgodność typów: oczekiwano '{expected}', otrzymano '{got}'", line)
