# PascC - Transpiler podzbioru języka Pascal do C

Bartłomiej Skowron (bskowron@student.agh.edu.pl)

---

## Opis projektu

**PascC** to transpiler (kompilator źródło-źródło) tłumaczący podzbiór języka **Pascal** na równoważny kod języka **C**. Program przetwarza pliki `.pas` i generuje czytelny, poprawny kod `.c` gotowy do kompilacji przez `gcc` lub `clang`.

---

## Cele programu

Transpilator obsługuje następujący podzbiór Pascala:

- **Program:** nagłówek `program`, sekcja `var`, ciało `begin...end.`
- **Typy danych:** `integer`, `real`, `boolean`, `char`, `string`
- **Zmienne:** deklaracje globalne i lokalne w procedurach/funkcjach
- **Wyrażenia:** arytmetyczne (`+`, `-`, `*`, `/`, `div`, `mod`), relacyjne (`=`, `<>`, `<`, `>`, `<=`, `>=`), logiczne (`and`, `or`, `not`)
- **Instrukcje:** przypisanie (`:=`), blok `begin...end`, pusta instrukcja
- **Instrukcje warunkowe:** `if...then`, `if...then...else`
- **Pętle:** `while...do`, `for...to...do`, `for...downto...do`, `repeat...until`
- **Procedury i funkcje:** deklaracja, parametry przez wartość i przez referencję (`var`), rekurencja
- **Wejście/Wyjście:** `writeln`, `write`, `readln`, `read`
- **Komentarze:** blokowe `{ }` oraz `(* *)`

---

## Rodzaj translatora

**Kompilator źródło-źródło (transpiler):**

```
Plik .pas  ->  [Lexer -> Parser -> Analiza semantyczna -> Generator kodu]  ->  Plik .c
```

Potok przetwarzania składa się z czterech faz:

1. **Skaner** - tokenizuje tekst wejściowy (ply.lex)
2. **Parser** - buduje drzewo AST (ply.yacc, LALR(1))
3. **Analiza semantyczna** - weryfikuje typy i zakres symboli
4. **Generator kodu** - emituje kod C (wzorzec Visitor)

---

## Język implementacji

**Python 3.11+** - czytelna składnia, bogaty ekosystem, dostępność dojrzałych generatorów parserów.

Jedyna zewnętrzna zależność:

```bash
pip install ply
```

### Uruchomienie

```bash
# Transpilacja
python main.py --input examples/factorial.pas --output factorial.c

# Kompilacja i uruchomienie
gcc factorial.c -o factorial && ./factorial

# Tryb debugowania (tokeny + AST)
python main.py --input examples/factorial.pas --debug
```

---

## Przykład działania — silnia rekurencyjna

**Plik wejściowy `examples/factorial.pas`:**

```pascal
program Factorial;

var
  n: integer;

function Fact(n: integer): integer;
begin
  if n <= 1 then
    Fact := 1
  else
    Fact := n * Fact(n - 1)
end;

begin
  readln(n);
  writeln(Fact(n));
end.
```

**Wygenerowany plik `factorial.c`:**

```c
#include <stdio.h>

int Fact(int n) {
    int _result_Fact = 0;
    if ((n <= 1)) {
        _result_Fact = 1;
    } else {
        _result_Fact = (n * Fact((n - 1)));
    }
    return _result_Fact;
}

int main(void) {
    int n;
    scanf("%d", &n);
    printf("%d\n", Fact(n));
    return 0;
}
```

---

## Sposób realizacji skanera i parsera

### Skaner (`lexer.py`) - `ply.lex`

Skaner oparty jest na module `ply.lex`, który buduje DFA (deterministyczny automat skończony) z wyrażeń regularnych. Każdy token jest definiowany przez funkcję lub zmienną z przedrostkiem `t_`. Słowa kluczowe są rozpoznawane case-insensitively - każdy identyfikator jest sprawdzany w słowniku `KEYWORDS` przed zwróceniem tokenu `ID`. Komentarze (`{ }` i `(* *)`) oraz białe znaki są pomijane. Numery linii są zliczane w regule `t_NEWLINE`.

### Parser (`parser.py`) - `ply.yacc` (LALR(1))

Parser zbudowany jest na module `ply.yacc` implementującym algorytm LALR(1). Gramatyka jest zapisana jako zbiór funkcji `p_*` z docstringami zawierającymi produkcje w notacji BNF. Każda funkcja buduje odpowiedni węzeł AST (dataclass z `ast_nodes.py`) i przypisuje go do `p[0]`. Niejednoznaczność `dangling else` jest rozwiązana przez sztuczny token priorytetowy `IF_WITHOUT_ELSE`. Priorytety operatorów są zdefiniowane w krotce `precedence` - od najniższego (`OR`) do najwyższego (`UMINUS`).

---

## Spis tokenów

### Słowa kluczowe (case-insensitive)

| Token          | Wzorzec     | Opis                                |
| -------------- | ----------- | ----------------------------------- |
| `PROGRAM`      | `program`   | Nagłówek programu                   |
| `VAR`          | `var`       | Sekcja deklaracji zmiennych         |
| `BEGIN`        | `begin`     | Otwarcie bloku instrukcji           |
| `END`          | `end`       | Zamknięcie bloku instrukcji         |
| `IF`           | `if`        | Instrukcja warunkowa                |
| `THEN`         | `then`      | Gałąź warunku                       |
| `ELSE`         | `else`      | Gałąź alternatywna                  |
| `WHILE`        | `while`     | Pętla z warunkiem wstępnym          |
| `DO`           | `do`        | Ciało pętli while/for               |
| `FOR`          | `for`       | Pętla iteracyjna                    |
| `TO`           | `to`        | Zakres w górę (pętla for)           |
| `DOWNTO`       | `downto`    | Zakres w dół (pętla for)            |
| `REPEAT`       | `repeat`    | Otwarcie pętli repeat               |
| `UNTIL`        | `until`     | Warunek zakończenia pętli repeat    |
| `PROCEDURE`    | `procedure` | Definicja procedury                 |
| `FUNCTION`     | `function`  | Definicja funkcji                   |
| `AND`          | `and`       | Koniunkcja logiczna                 |
| `OR`           | `or`        | Alternatywa logiczna                |
| `NOT`          | `not`       | Negacja logiczna                    |
| `DIV`          | `div`       | Dzielenie całkowite                 |
| `MOD`          | `mod`       | Reszta z dzielenia                  |
| `TRUE`         | `true`      | Literał logiczny prawda             |
| `FALSE`        | `false`     | Literał logiczny fałsz              |
| `TYPE_INTEGER` | `integer`   | Typ całkowitoliczbowy               |
| `TYPE_REAL`    | `real`      | Typ zmiennoprzecinkowy              |
| `TYPE_BOOLEAN` | `boolean`   | Typ logiczny                        |
| `TYPE_CHAR`    | `char`      | Typ znakowy                         |
| `TYPE_STRING`  | `string`    | Typ tekstowy                        |
| `WRITELN`      | `writeln`   | Wyjście z nową linią                |
| `WRITE`        | `write`     | Wyjście bez nowej linii             |
| `READLN`       | `readln`    | Wejście z przejściem do nowej linii |
| `READ`         | `read`      | Wejście                             |

### Identyfikatory i literały

| Token           | Wzorzec (regex)          | Opis                               | Przykład                 |
| --------------- | ------------------------ | ---------------------------------- | ------------------------ |
| `ID`            | `[a-zA-Z_][a-zA-Z0-9_]*` | Identyfikator                      | `x`, `counter`, `myProc` |
| `INTEGER_CONST` | `[0-9]+`                 | Literał całkowity                  | `42`, `0`, `1000`        |
| `REAL_CONST`    | `[0-9]+\.[0-9]+`         | Literał zmiennoprzecinkowy         | `3.14`, `0.5`            |
| `CHAR_CONST`    | `'[^']'`                 | Literał znakowy (dokładnie 1 znak) | `'a'`, `'Z'`             |
| `STRING_CONST`  | `'[^']*'`                | Literał tekstowy                   | `'hello'`, `'Pascal'`    |

> Zarówno znaki jak i napisy są ujmowane w apostrofy. Skaner rozróżnia je długością: jeden znak -> `CHAR_CONST`, wiele znaków -> `STRING_CONST`.

### Operatory i separatory

| Token       | Wzorzec | Opis                         |
| ----------- | ------- | ---------------------------- |
| `ASSIGN`    | `:=`    | Operator przypisania         |
| `COLON`     | `:`     | Separator (deklaracje typów) |
| `SEMICOLON` | `;`     | Separator instrukcji         |
| `COMMA`     | `,`     | Separator listy              |
| `DOT`       | `.`     | Koniec programu              |
| `DOTDOT`    | `..`    | Zakres (tablice)             |
| `LPAREN`    | `(`     | Nawias okrągły lewy          |
| `RPAREN`    | `)`     | Nawias okrągły prawy         |
| `PLUS`      | `+`     | Dodawanie                    |
| `MINUS`     | `-`     | Odejmowanie / minus unarny   |
| `STAR`      | `*`     | Mnożenie                     |
| `SLASH`     | `/`     | Dzielenie rzeczywiste        |
| `EQ`        | `=`     | Równość                      |
| `NEQ`       | `<>`    | Nierówność                   |
| `LT`        | `<`     | Mniejsze niż                 |
| `GT`        | `>`     | Większe niż                  |
| `LE`        | `<=`    | Mniejsze lub równe           |
| `GE`        | `>=`    | Większe lub równe            |

### Tokeny ignorowane

| Kategoria           | Wzorzec            | Opis                      |
| ------------------- | ------------------ | ------------------------- |
| Białe znaki         | `[ \t]+`           | Spacje i tabulatory       |
| Nowe linie          | `\n+`              | Zliczane dla numeru linii |
| Komentarz klamrowy  | `\{[^}]*\}`        | Komentarz `{ ... }`       |
| Komentarz nawiasowy | `\(\*[\s\S]*?\*\)` | Komentarz `(* ... *)`     |

---

## Gramatyka języka

Gramatyka zapisana w notacji EBNF. Parser używa notacji BNF (produkcje PLY/yacc).

```ebnf
(* ── Program ── *)
program         = "program" ID ";" block "." ;
block           = declarations compound_statement ;
declarations    = [ var_section ] { procedure_decl | function_decl } ;

(* ── Zmienne ── *)
var_section     = "var" var_decl { var_decl } ;
var_decl        = id_list ":" type_spec ";" ;
id_list         = ID { "," ID } ;
type_spec       = "integer" | "real" | "boolean" | "char" | "string" ;

(* ── Procedury i funkcje ── *)
procedure_decl  = "procedure" ID [ "(" param_list ")" ] ";" sub_block ";" ;
function_decl   = "function"  ID [ "(" param_list ")" ] ":" type_spec ";" sub_block ";" ;
sub_block       = [ var_section ] compound_statement ;
param_list      = param_group { ";" param_group } ;
param_group     = [ "var" ] id_list ":" type_spec ;

(* ── Instrukcje ── *)
compound_statement = "begin" statement_list "end" ;
statement_list  = statement { ";" statement } ;

statement       = assignment
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
                | (* pusta *) ;

assignment      = ID ":=" expression ;
procedure_call  = ID [ "(" argument_list ")" ] ;

if_statement    = "if" expression "then" statement [ "else" statement ] ;
while_statement = "while" expression "do" statement ;
for_statement   = "for" ID ":=" expression ( "to" | "downto" ) expression "do" statement ;
repeat_statement = "repeat" statement_list "until" expression ;

write_statement   = "write"   "(" write_arg_list ")" ;
writeln_statement = "writeln" "(" [ write_arg_list ] ")" ;
write_arg_list    = write_arg { "," write_arg } ;
write_arg         = expression [ ":" INTEGER_CONST [ ":" INTEGER_CONST ] ] ;

read_statement    = "read"   "(" id_list ")" ;
readln_statement  = "readln" "(" [ id_list ] ")" ;

(* ── Wyrażenia ── *)
expression      = simple_expression [ rel_op simple_expression ] ;
rel_op          = "=" | "<>" | "<" | ">" | "<=" | ">=" ;

simple_expression = term { add_op term } ;
add_op          = "+" | "-" | "or" ;

term            = factor { mul_op factor } ;
mul_op          = "*" | "/" | "div" | "mod" | "and" ;

factor          = INTEGER_CONST
                | REAL_CONST
                | CHAR_CONST
                | STRING_CONST
                | "true"  | "false"
                | ID
                | ID "(" argument_list ")"
                | "(" expression ")"
                | "not" factor
                | ( "+" | "-" ) factor ;

argument_list   = expression { "," expression } ;
```

### Priorytety operatorów (od najniższego do najwyższego)

| Priorytet     | Operator(y)                | Łączność     |
| ------------- | -------------------------- | ------------ |
| 1 (najniższy) | `if` bez `else`            | -            |
| 2             | `else`                     | -            |
| 3             | `or`                       | lewostronna  |
| 4             | `and`                      | lewostronna  |
| 5             | `not`                      | prawostronna |
| 6             | `=` `<>` `<` `>` `<=` `>=` | bezłączna    |
| 7             | `+` `-`                    | lewostronna  |
| 8             | `*` `/` `div` `mod`        | lewostronna  |
| 9 (najwyższy) | unarny `-` `+`             | prawostronna |
