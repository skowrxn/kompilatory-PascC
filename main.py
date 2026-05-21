"""PascC — Transpiler Pascal → C. Punkt wejścia CLI."""

import argparse
import sys
import os

from parser import parse
from semantic import SemanticAnalyzer
from codegen import CodeGenerator
from errors import LexError, ParseError, SemanticError


def _status(label: str, ok: bool = True):
    tag = 'OK' if ok else 'BŁĄD'
    print(f'[INFO] {label:<20} {tag}')


def main():
    ap = argparse.ArgumentParser(description='PascC — Transpiler Pascal → C')
    ap.add_argument('--input',  required=True,  help='Plik wejściowy .pas')
    ap.add_argument('--output', default='out.c', help='Plik wyjściowy .c')
    ap.add_argument('--debug',  action='store_true', help='Wypisz tokeny i AST')
    args = ap.parse_args()

    # ── czytanie źródła ───────────────────────────────────────────────────────
    try:
        with open(args.input, encoding='utf-8') as f:
            source = f.read()
    except FileNotFoundError:
        print(f'[BŁĄD] Nie znaleziono pliku: {args.input}', file=sys.stderr)
        sys.exit(1)

    # ── tokenizacja i parsowanie ──────────────────────────────────────────────
    try:
        if args.debug:
            from lexer import build_lexer
            lex = build_lexer()
            lex.input(source)
            print('=== TOKENY ===')
            for tok in lex:
                print(tok)
            print()

        ast = parse(source)
        _status('Skanowanie...')
        _status('Parsowanie...')
    except (LexError, ParseError) as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)

    if args.debug:
        import pprint
        print('=== AST ===')
        pprint.pprint(ast)
        print()

    # ── analiza semantyczna ───────────────────────────────────────────────────
    try:
        analyzer = SemanticAnalyzer()
        analyzer.analyze(ast)
        _status('Analiza sem...')
    except SemanticError as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)

    # ── generacja kodu ────────────────────────────────────────────────────────
    gen = CodeGenerator()
    c_code = gen.generate(ast)
    _status('Generacja kodu...')

    with open(args.output, 'w', encoding='utf-8') as f:
        f.write(c_code)
        f.write('\n')

    print(f'[OK] Wygenerowano: {args.output}')


if __name__ == '__main__':
    main()
