"""Parser LALR(1) dla translatora PascC — ply.yacc."""

import ply.yacc as yacc
from lexer import tokens, build_lexer  # noqa: F401 — tokens wymagane przez PLY
from ast_nodes import (
    Program, Block, VarSection, VarDecl, ProcedureDecl, FunctionDecl,
    ParamGroup, CompoundStatement, Assignment, ProcedureCall,
    IfStatement, WhileStatement, ForStatement, RepeatStatement,
    WriteStatement, ReadStatement, WriteArg,
    BinOp, UnaryOp, IntConst, RealConst, CharConst, StringConst,
    BoolConst, VarRef, FunctionCallExpr,
)
from errors import ParseError

# ── Priorytety ────────────────────────────────────────────────────────────────
precedence = (
    ('nonassoc', 'IF_WITHOUT_ELSE'),
    ('nonassoc', 'ELSE'),
    ('left',     'OR'),
    ('left',     'AND'),
    ('right',    'NOT'),
    ('nonassoc', 'EQ', 'NEQ', 'LT', 'GT', 'LE', 'GE'),
    ('left',     'PLUS', 'MINUS'),
    ('left',     'STAR', 'SLASH', 'DIV', 'MOD'),
    ('right',    'UMINUS', 'UPLUS'),
)


def _line(p, n=1):
    return getattr(p.slice[n], 'lineno', 0)


# ── Program ───────────────────────────────────────────────────────────────────
def p_program(p):
    '''program : PROGRAM ID SEMICOLON block DOT'''
    p[0] = Program(name=p[2], block=p[4], line=_line(p))


def p_block(p):
    '''block : declarations compound_statement'''
    var_sec, sub_decls = p[1]
    p[0] = Block(var_section=var_sec, sub_decls=sub_decls,
                 compound=p[2], line=_line(p))


# ── Deklaracje ────────────────────────────────────────────────────────────────
def p_declarations_with_var(p):
    '''declarations : var_section sub_declarations'''
    p[0] = (p[1], p[2])


def p_declarations_no_var(p):
    '''declarations : sub_declarations'''
    p[0] = (None, p[1])


def p_sub_declarations_proc(p):
    '''sub_declarations : sub_declarations procedure_decl'''
    p[0] = p[1] + [p[2]]


def p_sub_declarations_func(p):
    '''sub_declarations : sub_declarations function_decl'''
    p[0] = p[1] + [p[2]]


def p_sub_declarations_empty(p):
    '''sub_declarations : empty'''
    p[0] = []


def p_var_section(p):
    '''var_section : VAR var_decl_list'''
    p[0] = VarSection(declarations=p[2], line=_line(p))


def p_var_decl_list_multi(p):
    '''var_decl_list : var_decl_list var_decl'''
    p[0] = p[1] + [p[2]]


def p_var_decl_list_single(p):
    '''var_decl_list : var_decl'''
    p[0] = [p[1]]


def p_var_decl(p):
    '''var_decl : id_list COLON type_spec SEMICOLON'''
    p[0] = VarDecl(names=p[1], type_name=p[3], line=_line(p))


def p_id_list_multi(p):
    '''id_list : id_list COMMA ID'''
    p[0] = p[1] + [p[3]]


def p_id_list_single(p):
    '''id_list : ID'''
    p[0] = [p[1]]


def p_type_spec(p):
    '''type_spec : TYPE_INTEGER
                 | TYPE_REAL
                 | TYPE_BOOLEAN
                 | TYPE_CHAR
                 | TYPE_STRING'''
    p[0] = p[1].lower()


# ── Procedury i funkcje ───────────────────────────────────────────────────────
def p_procedure_decl_no_params(p):
    '''procedure_decl : PROCEDURE ID SEMICOLON sub_block SEMICOLON'''
    p[0] = ProcedureDecl(name=p[2], params=[], sub_block=p[4], line=_line(p))


def p_procedure_decl_params(p):
    '''procedure_decl : PROCEDURE ID LPAREN param_list RPAREN SEMICOLON sub_block SEMICOLON'''
    p[0] = ProcedureDecl(name=p[2], params=p[4], sub_block=p[7], line=_line(p))


def p_function_decl_no_params(p):
    '''function_decl : FUNCTION ID COLON type_spec SEMICOLON sub_block SEMICOLON'''
    p[0] = FunctionDecl(name=p[2], params=[], return_type=p[4],
                        sub_block=p[6], line=_line(p))


def p_function_decl_params(p):
    '''function_decl : FUNCTION ID LPAREN param_list RPAREN COLON type_spec SEMICOLON sub_block SEMICOLON'''
    p[0] = FunctionDecl(name=p[2], params=p[4], return_type=p[7],
                        sub_block=p[9], line=_line(p))


def p_sub_block_with_var(p):
    '''sub_block : var_section compound_statement'''
    p[0] = Block(var_section=p[1], sub_decls=[], compound=p[2], line=_line(p))


def p_sub_block_no_var(p):
    '''sub_block : compound_statement'''
    p[0] = Block(var_section=None, sub_decls=[], compound=p[1], line=_line(p))


def p_param_list_multi(p):
    '''param_list : param_list SEMICOLON param_group'''
    p[0] = p[1] + [p[3]]


def p_param_list_single(p):
    '''param_list : param_group'''
    p[0] = [p[1]]


def p_param_group_val(p):
    '''param_group : id_list COLON type_spec'''
    p[0] = ParamGroup(names=p[1], type_name=p[3], by_ref=False, line=_line(p))


def p_param_group_ref(p):
    '''param_group : VAR id_list COLON type_spec'''
    p[0] = ParamGroup(names=p[2], type_name=p[4], by_ref=True, line=_line(p))


# ── Instrukcje złożone ────────────────────────────────────────────────────────
def p_compound_statement(p):
    '''compound_statement : BEGIN statement_list END'''
    p[0] = CompoundStatement(statements=p[2], line=_line(p))


def p_statement_list_multi(p):
    '''statement_list : statement_list SEMICOLON statement'''
    if p[3] is not None:
        p[0] = p[1] + [p[3]]
    else:
        p[0] = p[1]


def p_statement_list_single(p):
    '''statement_list : statement'''
    p[0] = [p[1]] if p[1] is not None else []


def p_statement(p):
    '''statement : assignment
                 | procedure_call
                 | compound_statement
                 | if_statement
                 | while_statement
                 | for_statement
                 | repeat_statement
                 | write_statement
                 | writeln_statement
                 | read_statement
                 | readln_statement
                 | empty'''
    p[0] = p[1]


def p_assignment(p):
    '''assignment : ID ASSIGN expression'''
    p[0] = Assignment(target=p[1], value=p[3], line=_line(p))


def p_procedure_call_args(p):
    '''procedure_call : ID LPAREN argument_list RPAREN'''
    p[0] = ProcedureCall(name=p[1], args=p[3], line=_line(p))


def p_procedure_call_no_args(p):
    '''procedure_call : ID LPAREN RPAREN'''
    p[0] = ProcedureCall(name=p[1], args=[], line=_line(p))


def p_procedure_call_bare(p):
    '''procedure_call : ID'''
    p[0] = ProcedureCall(name=p[1], args=[], line=_line(p))


# ── Instrukcje sterowania ─────────────────────────────────────────────────────
def p_if_then(p):
    '''if_statement : IF expression THEN statement %prec IF_WITHOUT_ELSE'''
    p[0] = IfStatement(condition=p[2], then_branch=p[4],
                       else_branch=None, line=_line(p))


def p_if_then_else(p):
    '''if_statement : IF expression THEN statement ELSE statement'''
    p[0] = IfStatement(condition=p[2], then_branch=p[4],
                       else_branch=p[6], line=_line(p))


def p_while(p):
    '''while_statement : WHILE expression DO statement'''
    p[0] = WhileStatement(condition=p[2], body=p[4], line=_line(p))


def p_for_to(p):
    '''for_statement : FOR ID ASSIGN expression TO expression DO statement'''
    p[0] = ForStatement(var=p[2], start=p[4], end=p[6],
                        direction='to', body=p[8], line=_line(p))


def p_for_downto(p):
    '''for_statement : FOR ID ASSIGN expression DOWNTO expression DO statement'''
    p[0] = ForStatement(var=p[2], start=p[4], end=p[6],
                        direction='downto', body=p[8], line=_line(p))


def p_repeat(p):
    '''repeat_statement : REPEAT statement_list UNTIL expression'''
    p[0] = RepeatStatement(body=p[2], condition=p[4], line=_line(p))


# ── I/O ───────────────────────────────────────────────────────────────────────
def p_write(p):
    '''write_statement : WRITE LPAREN write_arg_list RPAREN'''
    p[0] = WriteStatement(newline=False, args=p[3], line=_line(p))


def p_writeln_args(p):
    '''writeln_statement : WRITELN LPAREN write_arg_list RPAREN'''
    p[0] = WriteStatement(newline=True, args=p[3], line=_line(p))


def p_writeln_empty(p):
    '''writeln_statement : WRITELN LPAREN RPAREN'''
    p[0] = WriteStatement(newline=True, args=[], line=_line(p))


def p_write_arg_list_multi(p):
    '''write_arg_list : write_arg_list COMMA write_arg'''
    p[0] = p[1] + [p[3]]


def p_write_arg_list_single(p):
    '''write_arg_list : write_arg'''
    p[0] = [p[1]]


def p_write_arg_plain(p):
    '''write_arg : expression'''
    p[0] = WriteArg(expr=p[1], line=_line(p))


def p_write_arg_width(p):
    '''write_arg : expression COLON INTEGER_CONST'''
    p[0] = WriteArg(expr=p[1], width=p[3], line=_line(p))


def p_write_arg_width_dec(p):
    '''write_arg : expression COLON INTEGER_CONST COLON INTEGER_CONST'''
    p[0] = WriteArg(expr=p[1], width=p[3], decimals=p[5], line=_line(p))


def p_read(p):
    '''read_statement : READ LPAREN id_list RPAREN'''
    p[0] = ReadStatement(newline=False, vars=p[3], line=_line(p))


def p_readln_args(p):
    '''readln_statement : READLN LPAREN id_list RPAREN'''
    p[0] = ReadStatement(newline=True, vars=p[3], line=_line(p))


def p_readln_empty(p):
    '''readln_statement : READLN LPAREN RPAREN'''
    p[0] = ReadStatement(newline=True, vars=[], line=_line(p))


# ── Wyrażenia ─────────────────────────────────────────────────────────────────
def p_expression_binop(p):
    '''expression : expression PLUS expression
                  | expression MINUS expression
                  | expression STAR expression
                  | expression SLASH expression
                  | expression DIV expression
                  | expression MOD expression
                  | expression AND expression
                  | expression OR expression
                  | expression EQ expression
                  | expression NEQ expression
                  | expression LT expression
                  | expression GT expression
                  | expression LE expression
                  | expression GE expression'''
    p[0] = BinOp(left=p[1], op=p[2], right=p[3], line=_line(p))


def p_expression_uminus(p):
    '''expression : MINUS expression %prec UMINUS'''
    p[0] = UnaryOp(op='-', operand=p[2], line=_line(p))


def p_expression_uplus(p):
    '''expression : PLUS expression %prec UPLUS'''
    p[0] = p[2]


def p_expression_not(p):
    '''expression : NOT expression'''
    p[0] = UnaryOp(op='not', operand=p[2], line=_line(p))


def p_expression_group(p):
    '''expression : LPAREN expression RPAREN'''
    p[0] = p[2]


def p_expression_int(p):
    '''expression : INTEGER_CONST'''
    p[0] = IntConst(value=p[1], line=_line(p))


def p_expression_real(p):
    '''expression : REAL_CONST'''
    p[0] = RealConst(value=p[1], line=_line(p))


def p_expression_char(p):
    '''expression : CHAR_CONST'''
    p[0] = CharConst(value=p[1], line=_line(p))


def p_expression_string(p):
    '''expression : STRING_CONST'''
    p[0] = StringConst(value=p[1], line=_line(p))


def p_expression_true(p):
    '''expression : TRUE'''
    p[0] = BoolConst(value=True, line=_line(p))


def p_expression_false(p):
    '''expression : FALSE'''
    p[0] = BoolConst(value=False, line=_line(p))


def p_expression_funcall(p):
    '''expression : ID LPAREN argument_list RPAREN'''
    p[0] = FunctionCallExpr(name=p[1], args=p[3], line=_line(p))


def p_expression_funcall_empty(p):
    '''expression : ID LPAREN RPAREN'''
    p[0] = FunctionCallExpr(name=p[1], args=[], line=_line(p))


def p_expression_id(p):
    '''expression : ID'''
    p[0] = VarRef(name=p[1], line=_line(p))


def p_argument_list_multi(p):
    '''argument_list : argument_list COMMA expression'''
    p[0] = p[1] + [p[3]]


def p_argument_list_single(p):
    '''argument_list : expression'''
    p[0] = [p[1]]


def p_empty(p):
    '''empty :'''
    p[0] = None


def p_error(p):
    if p:
        raise ParseError(
            f"Nieoczekiwany token '{p.value}'", p.lineno)
    else:
        raise ParseError("Nieoczekiwany koniec pliku")


def build_parser(**kwargs):
    return yacc.yacc(**kwargs)


def parse(source: str, debug: bool = False):
    lexer = build_lexer()
    parser = build_parser(debug=False, write_tables=False, errorlog=yacc.NullLogger())
    return parser.parse(source, lexer=lexer, debug=debug)
