"""Skaner (lexer) dla translatora PascC — ply.lex."""

import ply.lex as lex
from errors import LexError

# ── Słowa kluczowe (case-insensitive) ────────────────────────────────────────
KEYWORDS = {
    'program':   'PROGRAM',
    'var':       'VAR',
    'begin':     'BEGIN',
    'end':       'END',
    'if':        'IF',
    'then':      'THEN',
    'else':      'ELSE',
    'while':     'WHILE',
    'do':        'DO',
    'for':       'FOR',
    'to':        'TO',
    'downto':    'DOWNTO',
    'repeat':    'REPEAT',
    'until':     'UNTIL',
    'procedure': 'PROCEDURE',
    'function':  'FUNCTION',
    'and':       'AND',
    'or':        'OR',
    'not':       'NOT',
    'div':       'DIV',
    'mod':       'MOD',
    'true':      'TRUE',
    'false':     'FALSE',
    'integer':   'TYPE_INTEGER',
    'real':      'TYPE_REAL',
    'boolean':   'TYPE_BOOLEAN',
    'char':      'TYPE_CHAR',
    'string':    'TYPE_STRING',
    'writeln':   'WRITELN',
    'write':     'WRITE',
    'readln':    'READLN',
    'read':      'READ',
}

tokens = list(set(KEYWORDS.values())) + [
    'ID',
    'INTEGER_CONST',
    'REAL_CONST',
    'CHAR_CONST',
    'STRING_CONST',
    'ASSIGN',
    'COLON',
    'SEMICOLON',
    'COMMA',
    'DOT',
    'DOTDOT',
    'LPAREN',
    'RPAREN',
    'PLUS',
    'MINUS',
    'STAR',
    'SLASH',
    'EQ',
    'NEQ',
    'LT',
    'GT',
    'LE',
    'GE',
]

# ── Operatory i separatory ────────────────────────────────────────────────────
t_ASSIGN    = r':='
t_COLON     = r':'
t_SEMICOLON = r';'
t_COMMA     = r','
t_DOTDOT    = r'\.\.'
t_DOT       = r'\.'
t_LPAREN    = r'\('
t_RPAREN    = r'\)'
t_PLUS      = r'\+'
t_MINUS     = r'-'
t_STAR      = r'\*'
t_SLASH     = r'/'
t_EQ        = r'='
t_NEQ       = r'<>'
t_LE        = r'<='
t_GE        = r'>='
t_LT        = r'<'
t_GT        = r'>'


def t_REAL_CONST(t):
    r'[0-9]+\.[0-9]+'
    t.value = float(t.value)
    return t


def t_INTEGER_CONST(t):
    r'[0-9]+'
    t.value = int(t.value)
    return t


def t_STRING_CONST(t):
    r"'[^']*'"
    raw = t.value[1:-1]
    if len(raw) == 1:
        t.type = 'CHAR_CONST'
        t.value = raw
    else:
        t.value = raw
    return t


def t_ID(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    t.type = KEYWORDS.get(t.value.lower(), 'ID')
    return t


# ── Komentarze i białe znaki ──────────────────────────────────────────────────
def t_COMMENT_BRACE(t):
    r'\{[^}]*\}'
    t.lexer.lineno += t.value.count('\n')


def t_COMMENT_PAREN(t):
    r'\(\*[\s\S]*?\*\)'
    t.lexer.lineno += t.value.count('\n')


def t_NEWLINE(t):
    r'\n+'
    t.lexer.lineno += len(t.value)


t_ignore = ' \t'


def t_error(t):
    raise LexError(f"Nieznany znak '{t.value[0]}'", t.lexer.lineno)


def build_lexer(**kwargs):
    return lex.lex(**kwargs)
