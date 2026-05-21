"""Generator kodu C — wzorzec Visitor po węzłach AST."""

from ast_nodes import (
    Program, Block, VarSection, VarDecl, ProcedureDecl, FunctionDecl,
    ParamGroup, CompoundStatement, Assignment, ProcedureCall,
    IfStatement, WhileStatement, ForStatement, RepeatStatement,
    WriteStatement, ReadStatement, WriteArg,
    BinOp, UnaryOp, IntConst, RealConst, CharConst, StringConst,
    BoolConst, VarRef, FunctionCallExpr,
    ArrayDecl, ArrayAccess, ArrayAssignment,
)

TYPE_MAP = {
    'integer': 'int',
    'real':    'double',
    'boolean': 'int',
    'char':    'char',
    'string':  'char*',
}

FMT_MAP = {
    'integer': '%d',
    'real':    '%lf',
    'char':    '%c',
    'string':  '%s',
    'boolean': '%d',
}

OP_MAP = {
    '=':   '==',
    '<>':  '!=',
    'div': '/',
    'mod': '%',
    'and': '&&',
    'or':  '||',
}


class CodeGenerator:
    """Emituje kod C odwiedzając drzewo AST."""

    def __init__(self):
        self._indent = 0
        self._lines: list[str] = []
        self._needs_stdio = False
        self._needs_string = False
        # stos zakresów: każdy zakres to dict name->type
        self._scope_stack: list[dict] = [{}]
        # stos zbiorów nazw parametrów by-ref (są wskaźnikami w C)
        self._byref_stack: list[set] = [set()]
        # stos metadanych tablic: name -> {low, elem_type}
        self._array_meta_stack: list[dict] = [{}]
        # rejestr sygnatur: name -> [{name, by_ref, type}]
        self._func_registry: dict[str, list] = {}
        self._func_return_type: str | None = None
        self._func_name: str | None = None

    # ── publiczne API ─────────────────────────────────────────────────────────
    def generate(self, node) -> str:
        self.visit(node)
        headers = ['#include <stdio.h>']
        if self._needs_string:
            headers.append('#include <string.h>')
        return '\n'.join(headers) + '\n\n' + '\n'.join(self._lines)

    # ── dispatcher ────────────────────────────────────────────────────────────
    def visit(self, node):
        if node is None:
            return ''
        method = 'visit_' + type(node).__name__
        return getattr(self, method, self.generic_visit)(node)

    def generic_visit(self, node):
        return ''

    # ── pomocnicze ────────────────────────────────────────────────────────────
    def _emit(self, line: str = ''):
        self._lines.append('    ' * self._indent + line)

    def _push_scope(self):
        self._scope_stack.append({})
        self._byref_stack.append(set())
        self._array_meta_stack.append({})

    def _pop_scope(self):
        self._scope_stack.pop()
        self._byref_stack.pop()
        self._array_meta_stack.pop()

    def _set_array_meta(self, name: str, low: int, elem_type: str):
        self._array_meta_stack[-1][name.lower()] = {'low': low, 'elem_type': elem_type}

    def _get_array_meta(self, name: str) -> dict | None:
        for scope in reversed(self._array_meta_stack):
            if name.lower() in scope:
                return scope[name.lower()]
        return None

    def _set_type(self, name: str, typ: str):
        self._scope_stack[-1][name.lower()] = typ

    def _get_type(self, name: str) -> str:
        for scope in reversed(self._scope_stack):
            if name.lower() in scope:
                return scope[name.lower()]
        return 'integer'

    def _mark_byref(self, name: str):
        self._byref_stack[-1].add(name.lower())

    def _is_byref(self, name: str) -> bool:
        for s in reversed(self._byref_stack):
            if name.lower() in s:
                return True
        return False

    def _c_type(self, pascal_type: str) -> str:
        return TYPE_MAP.get(pascal_type, 'int')

    def _fmt(self, pascal_type: str) -> str:
        return FMT_MAP.get(pascal_type, '%d')

    def _op(self, op: str) -> str:
        return OP_MAP.get(op.lower(), op)

    # ── rejestracja sygnatur przed wizytą ciała ───────────────────────────────
    def _register_decls(self, sub_decls):
        for decl in sub_decls:
            if isinstance(decl, (ProcedureDecl, FunctionDecl)):
                params = []
                for pg in decl.params:
                    for name in pg.names:
                        params.append({'name': name.lower(),
                                       'type': pg.type_name,
                                       'by_ref': pg.by_ref})
                self._func_registry[decl.name.lower()] = params
                if isinstance(decl, FunctionDecl):
                    self._set_type(decl.name, decl.return_type)

    # ── węzły programu ────────────────────────────────────────────────────────
    def visit_Program(self, node: Program):
        self._needs_stdio = True
        self._collect_var_types(node.block.var_section)
        self._register_decls(node.block.sub_decls)
        for decl in node.block.sub_decls:
            self.visit(decl)
        self._emit('int main(void) {')
        self._indent += 1
        self._emit_var_section(node.block.var_section)
        self.visit(node.block.compound)
        self._emit('return 0;')
        self._indent -= 1
        self._emit('}')

    def _collect_var_types(self, var_section):
        if not var_section:
            return
        for decl in var_section.declarations:
            if isinstance(decl, ArrayDecl):
                for name in decl.names:
                    self._set_type(name, decl.elem_type)
                    self._set_array_meta(name, decl.low, decl.elem_type)
            else:
                for name in decl.names:
                    self._set_type(name, decl.type_name)

    def _emit_var_section(self, var_section):
        if not var_section:
            return
        for decl in var_section.declarations:
            if isinstance(decl, ArrayDecl):
                c_type = self._c_type(decl.elem_type)
                size = decl.high - decl.low + 1
                for name in decl.names:
                    self._set_type(name, decl.elem_type)
                    self._set_array_meta(name, decl.low, decl.elem_type)
                    self._emit(f'{c_type} {name}[{size}];')
            else:
                for name in decl.names:
                    self._set_type(name, decl.type_name)
                c_type = self._c_type(decl.type_name)
                names_str = ', '.join(decl.names)
                self._emit(f'{c_type} {names_str};')

    def visit_ProcedureDecl(self, node: ProcedureDecl):
        params_str = self._params_c(node.params)
        self._emit(f'void {node.name}({params_str}) {{')
        self._indent += 1
        self._push_scope()
        self._register_params(node.params)
        self._collect_var_types(node.sub_block.var_section)
        self._emit_var_section(node.sub_block.var_section)
        self.visit(node.sub_block.compound)
        self._pop_scope()
        self._indent -= 1
        self._emit('}')
        self._emit()

    def visit_FunctionDecl(self, node: FunctionDecl):
        ret_c = self._c_type(node.return_type)
        params_str = self._params_c(node.params)
        self._emit(f'{ret_c} {node.name}({params_str}) {{')
        self._indent += 1
        self._push_scope()
        self._register_params(node.params)
        self._set_type(node.name, node.return_type)
        self._emit(f'{ret_c} _result_{node.name} = 0;')
        prev_func = self._func_name
        prev_ret  = self._func_return_type
        self._func_name = node.name.lower()
        self._func_return_type = node.return_type
        self._collect_var_types(node.sub_block.var_section)
        self._emit_var_section(node.sub_block.var_section)
        self.visit(node.sub_block.compound)
        self._emit(f'return _result_{node.name};')
        self._func_name = prev_func
        self._func_return_type = prev_ret
        self._pop_scope()
        self._indent -= 1
        self._emit('}')
        self._emit()

    def _params_c(self, params: list) -> str:
        parts = []
        for pg in params:
            c_type = self._c_type(pg.type_name)
            ptr = '*' if pg.by_ref else ''
            for name in pg.names:
                parts.append(f'{c_type}{ptr} {name}')
        return ', '.join(parts)

    def _register_params(self, params: list):
        for pg in params:
            for name in pg.names:
                self._set_type(name, pg.type_name)
                if pg.by_ref:
                    self._mark_byref(name)

    # ── instrukcje ────────────────────────────────────────────────────────────
    def visit_CompoundStatement(self, node: CompoundStatement):
        for stmt in node.statements:
            self.visit(stmt)

    def visit_Assignment(self, node: Assignment):
        val = self.visit(node.value)
        if self._func_name and node.target.lower() == self._func_name:
            self._emit(f'_result_{node.target} = {val};')
        elif self._is_byref(node.target):
            self._emit(f'*{node.target} = {val};')
        else:
            self._emit(f'{node.target} = {val};')

    def visit_ArrayAssignment(self, node: ArrayAssignment):
        meta = self._get_array_meta(node.name)
        index = self.visit(node.index)
        value = self.visit(node.value)
        low = meta['low'] if meta else 0
        if low != 0:
            self._emit(f'{node.name}[({index}) - {low}] = {value};')
        else:
            self._emit(f'{node.name}[{index}] = {value};')

    def visit_ProcedureCall(self, node: ProcedureCall):
        args_str = self._build_call_args(node.name, node.args)
        self._emit(f'{node.name}({args_str});')

    def _build_call_args(self, fname: str, args: list) -> str:
        params = self._func_registry.get(fname.lower(), [])
        parts = []
        for i, arg in enumerate(args):
            by_ref = params[i]['by_ref'] if i < len(params) else False
            expr_str = self.visit(arg)
            if by_ref and isinstance(arg, VarRef):
                parts.append(f'&{arg.name}')
            else:
                parts.append(expr_str)
        return ', '.join(parts)

    def visit_IfStatement(self, node: IfStatement):
        cond = self.visit(node.condition)
        self._emit(f'if ({cond}) {{')
        self._indent += 1
        self.visit(node.then_branch)
        self._indent -= 1
        if node.else_branch:
            self._emit('} else {')
            self._indent += 1
            self.visit(node.else_branch)
            self._indent -= 1
        self._emit('}')

    def visit_WhileStatement(self, node: WhileStatement):
        cond = self.visit(node.condition)
        self._emit(f'while ({cond}) {{')
        self._indent += 1
        self.visit(node.body)
        self._indent -= 1
        self._emit('}')

    def visit_ForStatement(self, node: ForStatement):
        var   = node.var
        start = self.visit(node.start)
        end   = self.visit(node.end)
        if node.direction == 'to':
            cond = f'{var} <= {end}'
            step = f'{var}++'
        else:
            cond = f'{var} >= {end}'
            step = f'{var}--'
        self._emit(f'for ({var} = {start}; {cond}; {step}) {{')
        self._indent += 1
        self.visit(node.body)
        self._indent -= 1
        self._emit('}')

    def visit_RepeatStatement(self, node: RepeatStatement):
        self._emit('do {')
        self._indent += 1
        for stmt in node.body:
            self.visit(stmt)
        self._indent -= 1
        cond = self.visit(node.condition)
        self._emit(f'}} while (!({cond}));')

    # ── I/O ───────────────────────────────────────────────────────────────────
    def visit_WriteStatement(self, node: WriteStatement):
        if not node.args:
            if node.newline:
                self._emit('printf("\\n");')
            return

        fmt_parts = []
        val_parts = []
        for arg in node.args:
            expr_node = arg.expr if isinstance(arg, WriteArg) else arg
            width     = arg.width if isinstance(arg, WriteArg) else None
            decimals  = arg.decimals if isinstance(arg, WriteArg) else None
            expr_str  = self.visit(expr_node)
            typ       = self._infer_type(expr_node)

            if typ == 'string':
                self._needs_string = True

            if isinstance(expr_node, StringConst):
                fmt_parts.append(self._escape_string(expr_node.value))
            elif isinstance(expr_node, CharConst):
                fmt_parts.append(self._escape_string(expr_node.value))
            else:
                spec = self._build_fmt_spec(typ, width, decimals)
                fmt_parts.append(spec)
                val_parts.append(expr_str)

        nl = '\\n' if node.newline else ''
        fmt_str = ''.join(fmt_parts) + nl
        if val_parts:
            self._emit(f'printf("{fmt_str}", {", ".join(val_parts)});')
        else:
            self._emit(f'printf("{fmt_str}");')

    def _build_fmt_spec(self, typ: str, width, decimals) -> str:
        base = self._fmt(typ).lstrip('%')
        if width is not None and decimals is not None:
            return f'%{width}.{decimals}{base}'
        if width is not None:
            return f'%{width}{base}'
        return f'%{base}'

    def _escape_string(self, s: str) -> str:
        return s.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n')

    def visit_ReadStatement(self, node: ReadStatement):
        for var in node.vars:
            typ = self._get_type(var)
            fmt = self._fmt(typ)
            self._emit(f'scanf("{fmt}", &{var});')

    # ── wyrażenia ─────────────────────────────────────────────────────────────
    def visit_BinOp(self, node: BinOp) -> str:
        left  = self.visit(node.left)
        right = self.visit(node.right)
        op    = self._op(node.op)
        return f'({left} {op} {right})'

    def visit_UnaryOp(self, node: UnaryOp) -> str:
        operand = self.visit(node.operand)
        if node.op == 'not':
            return f'!({operand})'
        return f'{node.op}({operand})'

    def visit_IntConst(self, node: IntConst) -> str:
        return str(node.value)

    def visit_RealConst(self, node: RealConst) -> str:
        s = repr(node.value)
        return s if '.' in s else s + '.0'

    def visit_CharConst(self, node: CharConst) -> str:
        c = node.value.replace("'", "\\'")
        return f"'{c}'"

    def visit_StringConst(self, node: StringConst) -> str:
        return f'"{self._escape_string(node.value)}"'

    def visit_BoolConst(self, node: BoolConst) -> str:
        return '1' if node.value else '0'

    def visit_ArrayAccess(self, node: ArrayAccess) -> str:
        meta = self._get_array_meta(node.name)
        index = self.visit(node.index)
        low = meta['low'] if meta else 0
        if low != 0:
            return f'{node.name}[({index}) - {low}]'
        return f'{node.name}[{index}]'

    def visit_VarRef(self, node: VarRef) -> str:
        if self._func_name and node.name.lower() == self._func_name:
            return f'_result_{node.name}'
        if self._is_byref(node.name):
            return f'(*{node.name})'
        return node.name

    def visit_FunctionCallExpr(self, node: FunctionCallExpr) -> str:
        args_str = self._build_call_args(node.name, node.args)
        return f'{node.name}({args_str})'

    # ── inferencja typów ─────────────────────────────────────────────────────
    def _infer_type(self, node) -> str:
        if isinstance(node, IntConst):    return 'integer'
        if isinstance(node, RealConst):   return 'real'
        if isinstance(node, CharConst):   return 'char'
        if isinstance(node, StringConst): return 'string'
        if isinstance(node, BoolConst):   return 'boolean'
        if isinstance(node, VarRef):      return self._get_type(node.name)
        if isinstance(node, ArrayAccess):
            meta = self._get_array_meta(node.name)
            return meta['elem_type'] if meta else 'integer'
        if isinstance(node, FunctionCallExpr):
            return self._get_type(node.name)
        if isinstance(node, BinOp):
            lt = self._infer_type(node.left)
            rt = self._infer_type(node.right)
            op = node.op.lower()
            if op in ('=', '<>', '<', '>', '<=', '>=', 'and', 'or'):
                return 'boolean'
            if lt == 'real' or rt == 'real':
                return 'real'
            return 'integer'
        if isinstance(node, UnaryOp):
            return 'boolean' if node.op == 'not' else self._infer_type(node.operand)
        return 'integer'
