# PascC — Transpiler podzbioru języka Pascal do C

Repozytorium: <https://github.com/skowrxn/kompilatory-PascC>

---

## 1. Dane studenta

**Bartłomiej Skowron**

## 2. Dane kontaktowe

E-mail: <bskowron@student.agh.edu.pl>

---

## 3. Założenia programu

### 3.1. Ogólne cele programu

**PascC** to transpiler tłumaczący podzbiór języka **Pascal** na równoważny kod
języka **C**. Program przetwarza pliki `.pas` i generuje czytelny, poprawny kod
`.c`, gotowy do kompilacji przez `gcc` lub `clang`.

Obsługiwany podzbiór języka Pascal:

- **Program:** nagłówek `program`, sekcja `var`, ciało `begin...end.`
- **Typy danych:** `integer`, `real`, `boolean`, `char`, `string`
- **Tablice:** `array [low..high] of type` — jednoindeksowe, dostęp i zapis przez `arr[i]`
- **Zmienne:** deklaracje globalne i lokalne w procedurach/funkcjach
- **Wyrażenia:** arytmetyczne (`+`, `-`, `*`, `/`, `div`, `mod`), relacyjne (`=`, `<>`, `<`, `>`, `<=`, `>=`), logiczne (`and`, `or`, `not`)
- **Instrukcje:** przypisanie (`:=`), przypisanie do elementu tablicy `arr[i] := expr`, blok `begin...end`, pusta instrukcja
- **Instrukcje warunkowe:** `if...then`, `if...then...else`
- **Pętle:** `while...do`, `for...to...do`, `for...downto...do`, `repeat...until`
- **Procedury i funkcje:** deklaracja, parametry przez wartość i przez referencję (`var`), rekurencja
- **Wejście/Wyjście:** `writeln`, `write`, `readln`, `read` (z obsługą formatowania `expr:width:decimals`)
- **Komentarze:** blokowe `{ }` oraz `(* *)`

### 3.2. Rodzaj translatora

**Kompilator źródło-źródło (transpiler).** Program nie wykonuje kodu wejściowego,
lecz tłumaczy go na inny język wysokiego poziomu (C).

### 3.3. Planowany wynik działania programu

Konwerter (kompilator) Pascala do C. Potok przetwarzania składa się z czterech faz:

```
Plik .pas  ->  [ Lexer -> Parser -> Analiza semantyczna -> Generator kodu ]  ->  Plik .c
```

1. **Skaner** — tokenizuje tekst wejściowy (`ply.lex`)
2. **Parser** — buduje drzewo AST (`ply.yacc`, LALR(1))
3. **Analiza semantyczna** — weryfikuje typy i zakres symboli
4. **Generator kodu** — emituje kod C (wzorzec Visitor)

Wynikowy plik `.c` jest gotowy do skompilowania standardowym kompilatorem C.

### 3.4. Planowany język implementacji

**Python 3.11+** — czytelna składnia, bogaty ekosystem, łatwość operowania na
strukturach dziedziczonych (`dataclasses` do AST) oraz dostępność dojrzałych
generatorów skanerów i parserów.

### 3.5. Sposób realizacji skanera/parsera

Wykorzystano generator skanerów i parserów odpowiedni dla języka implementacji —
bibliotekę zewnętrzną **PLY (Python Lex-Yacc)**, będącą portem narzędzi Lex i Yacc.
Skaner buduje ciąg tokenów za pomocą wyrażeń regularnych, a parser przetwarza
tokeny algorytmem **LALR(1)**, budując Drzewo Składni Abstrakcyjnej (AST).
Szczegóły zastosowanych pakietów opisano w sekcji 6.

---

## 4. Opis tokenów

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
| `ARRAY`        | `array`     | Typ tablicowy                       |
| `OF`           | `of`        | Element typu tablicowego            |

### Identyfikatory i literały

| Token           | Wzorzec (regex)          | Opis                               | Przykład                 |
| --------------- | ------------------------ | ---------------------------------- | ------------------------ |
| `ID`            | `[a-zA-Z_][a-zA-Z0-9_]*` | Identyfikator                      | `x`, `counter`, `myProc` |
| `INTEGER_CONST` | `[0-9]+`                 | Literał całkowity                  | `42`, `0`, `1000`        |
| `REAL_CONST`    | `[0-9]+\.[0-9]+`         | Literał zmiennoprzecinkowy         | `3.14`, `0.5`            |
| `CHAR_CONST`    | `'[^']'`                 | Literał znakowy (dokładnie 1 znak) | `'a'`, `'Z'`             |
| `STRING_CONST`  | `'[^']*'`                | Literał tekstowy                   | `'hello'`, `'Pascal'`    |

> Zarówno znaki, jak i napisy są ujmowane w apostrofy. Skaner rozróżnia je
> długością: jeden znak → `CHAR_CONST`, wiele znaków → `STRING_CONST`.

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
| `LBRACKET`  | `[`     | Nawias kwadratowy lewy       |
| `RBRACKET`  | `]`     | Nawias kwadratowy prawy      |
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

## 5. Gramatyka formatu

### 5.1. Notacja standardowa (EBNF)

Gramatyka w notacji EBNF (warstwowa, jednoznaczna; priorytety operatorów wynikają
ze struktury produkcji `expression` → `simple_expression` → `term` → `factor`):

```ebnf
(* ── Program ── *)
program         = "program" ID ";" block "." ;
block           = declarations compound_statement ;
declarations    = [ var_section ] { procedure_decl | function_decl } ;

(* ── Zmienne ── *)
var_section     = "var" var_decl { var_decl } ;
var_decl        = id_list ":" type_spec ";"
                | id_list ":" "array" "[" INTEGER_CONST ".." INTEGER_CONST "]" "of" type_spec ";" ;
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
                | array_assignment
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

assignment       = ID ":=" expression ;
array_assignment = ID "[" expression "]" ":=" expression ;
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
                | ID "[" expression "]"
                | ID "(" argument_list ")"
                | "(" expression ")"
                | "not" factor
                | ( "+" | "-" ) factor ;

argument_list   = expression { "," expression } ;
```

### 5.2. Notacja zastosowanego generatora parserów (PLY / yacc, BNF — bez akcji)

Poniżej rzeczywista gramatyka przekazywana do `ply.yacc` (produkcje z docstringów
funkcji `p_*` w pliku `parser.py`, bez kodu akcji). W odróżnieniu od EBNF reguła
`expression` jest płaska i niejednoznaczna — jednoznaczność zapewnia tablica
priorytetów `precedence`, a problem _dangling-else_ rozwiązuje sztuczny token
priorytetowy `IF_WITHOUT_ELSE`.

```yacc
/* ── Tablica priorytetów (od najniższego do najwyższego) ── */
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

/* ── Program ── */
program  : PROGRAM ID SEMICOLON block DOT

block    : declarations compound_statement

/* ── Deklaracje ── */
declarations     : var_section sub_declarations
                 | sub_declarations

sub_declarations : sub_declarations procedure_decl
                 | sub_declarations function_decl
                 | empty

var_section   : VAR var_decl_list

var_decl_list : var_decl_list var_decl
              | var_decl

var_decl : id_list COLON type_spec SEMICOLON
         | id_list COLON ARRAY LBRACKET INTEGER_CONST DOTDOT INTEGER_CONST RBRACKET OF type_spec SEMICOLON

id_list  : id_list COMMA ID
         | ID

type_spec : TYPE_INTEGER
          | TYPE_REAL
          | TYPE_BOOLEAN
          | TYPE_CHAR
          | TYPE_STRING

/* ── Procedury i funkcje ── */
procedure_decl : PROCEDURE ID SEMICOLON sub_block SEMICOLON
               | PROCEDURE ID LPAREN param_list RPAREN SEMICOLON sub_block SEMICOLON

function_decl  : FUNCTION ID COLON type_spec SEMICOLON sub_block SEMICOLON
               | FUNCTION ID LPAREN param_list RPAREN COLON type_spec SEMICOLON sub_block SEMICOLON

sub_block : var_section compound_statement
          | compound_statement

param_list  : param_list SEMICOLON param_group
            | param_group

param_group : id_list COLON type_spec
            | VAR id_list COLON type_spec

/* ── Instrukcje ── */
compound_statement : BEGIN statement_list END

statement_list : statement_list SEMICOLON statement
               | statement

statement : assignment
          | array_assignment
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
          | empty

assignment       : ID ASSIGN expression

array_assignment : ID LBRACKET expression RBRACKET ASSIGN expression

procedure_call   : ID LPAREN argument_list RPAREN
                 | ID LPAREN RPAREN
                 | ID

if_statement : IF expression THEN statement %prec IF_WITHOUT_ELSE
             | IF expression THEN statement ELSE statement

while_statement : WHILE expression DO statement

for_statement : FOR ID ASSIGN expression TO expression DO statement
              | FOR ID ASSIGN expression DOWNTO expression DO statement

repeat_statement : REPEAT statement_list UNTIL expression

/* ── Wejście / Wyjście ── */
write_statement   : WRITE LPAREN write_arg_list RPAREN

writeln_statement : WRITELN LPAREN write_arg_list RPAREN
                  | WRITELN LPAREN RPAREN

write_arg_list : write_arg_list COMMA write_arg
               | write_arg

write_arg : expression
          | expression COLON INTEGER_CONST
          | expression COLON INTEGER_CONST COLON INTEGER_CONST

read_statement   : READ LPAREN id_list RPAREN

readln_statement : READLN LPAREN id_list RPAREN
                 | READLN LPAREN RPAREN

/* ── Wyrażenia (płaskie, rozstrzygane przez precedence) ── */
expression : expression PLUS expression
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
           | expression GE expression
           | MINUS expression %prec UMINUS
           | PLUS expression %prec UPLUS
           | NOT expression
           | LPAREN expression RPAREN
           | INTEGER_CONST
           | REAL_CONST
           | CHAR_CONST
           | STRING_CONST
           | TRUE
           | FALSE
           | ID LPAREN argument_list RPAREN
           | ID LPAREN RPAREN
           | ID LBRACKET expression RBRACKET
           | ID

argument_list : argument_list COMMA expression
              | expression

empty :
```

### Priorytety operatorów (od najniższego do najwyższego)

| Priorytet     | Operator(y)                | Łączność     |
| ------------- | -------------------------- | ------------ |
| 1 (najniższy) | `if` bez `else`            | bezłączna    |
| 2             | `else`                     | bezłączna    |
| 3             | `or`                       | lewostronna  |
| 4             | `and`                      | lewostronna  |
| 5             | `not`                      | prawostronna |
| 6             | `=` `<>` `<` `>` `<=` `>=` | bezłączna    |
| 7             | `+` `-`                    | lewostronna  |
| 8             | `*` `/` `div` `mod`        | lewostronna  |
| 9 (najwyższy) | unarny `-` `+`             | prawostronna |

---

## 6. Informacje o stosowanych generatorach i pakietach zewnętrznych

Do budowy analizatorów wykorzystano standardowy w ekosystemie Pythona
odpowiednik pary Lex-Yacc — pakiet zewnętrzny **PLY (Python Lex-Yacc)**, który
w pełni obsługuje analizę leksykalną i składniową.

Instalacja jedynej zewnętrznej zależności:

```bash
pip install ply
```

- **Skaner (`lexer.py`, `ply.lex`).** Buduje w locie tabele **DFA**
  (deterministycznego automatu skończonego) z wyrażeń regularnych. Każdy token
  definiowany jest funkcją lub zmienną z przedrostkiem `t_`. Słowa kluczowe są
  rozpoznawane _case-insensitive_ — każdy identyfikator sprawdzany jest w
  słowniku `KEYWORDS` przed zwróceniem tokenu `ID`. Komentarze (`{ }` oraz
  `(* *)`) i białe znaki są pomijane, a numery linii zliczane w regule
  `t_NEWLINE` (dla precyzyjnej lokalizacji błędów).
- **Parser (`parser.py`, `ply.yacc`).** Implementuje mechanizm _shift-reduce_
  klasy **LALR(1)** i buduje własne Drzewo Składni Abstrakcyjnej (AST). Gramatyka
  zapisana jest w notacji **BNF** w docstringach funkcji `p_*`; każda funkcja
  tworzy odpowiedni węzeł AST (`dataclass` z `ast_nodes.py`) i przypisuje go do
  `p[0]`. Niejednoznaczność _dangling-else_ obsłużono sztucznym tokenem
  priorytetowym `IF_WITHOUT_ELSE`, a priorytety operatorów zdefiniowano w krotce
  `precedence`.

Pozostałe moduły standardowej biblioteki Pythona użyte w projekcie:
`argparse` (obsługa CLI), `dataclasses` (węzły AST), `pprint` (podgląd AST w
trybie `--debug`).

---

## 7. Krótka instrukcja obsługi

1. Zainstaluj wymaganą bibliotekę:

    ```bash
    pip install ply
    ```

2. Uruchom transpilację kodu z `.pas` (Pascal) do `.c` (C):

    ```bash
    python main.py --input examples/bubble_sort.pas --output out_bubble.c
    ```

3. Zbuduj finalny program kompilatorem C (np. `gcc`) i uruchom go:

    ```bash
    gcc out_bubble.c -o bubble && ./bubble
    ```

4. Opcjonalnie — tryb podglądu procesu. Aby obejrzeć strukturę wykrytych tokenów
   z lexera oraz zbudowane drzewo AST, przekaż flagę `--debug`:

    ```bash
    python main.py --input examples/bubble_sort.pas --debug
    ```

### Argumenty wiersza poleceń

| Argument   | Wymagany | Wartość domyślna | Opis                                   |
| ---------- | -------- | ---------------- | -------------------------------------- |
| `--input`  | tak      | —                | Ścieżka do pliku wejściowego `.pas`    |
| `--output` | nie      | `out.c`          | Ścieżka do pliku wyjściowego `.c`      |
| `--debug`  | nie      | wyłączony        | Wypisuje listę tokenów oraz drzewo AST |

W razie błędu (leksykalnego, składniowego lub semantycznego) program wypisuje
komunikat z numerem linii na standardowe wyjście błędów i kończy działanie kodem
wyjścia `1`.

---

## 8. Przykład użycia — sortowanie bąbelkowe

**Plik wejściowy `examples/bubble_sort.pas`:**

```pascal
program BubbleSort;

var
  arr: array [1..5] of integer;
  i, j, tmp, n: integer;

begin
  n := 5;
  arr[1] := 5;
  arr[2] := 3;
  arr[3] := 1;
  arr[4] := 4;
  arr[5] := 2;

  for i := 1 to n - 1 do
    for j := 1 to n - i do
      if arr[j] > arr[j + 1] then
      begin
        tmp := arr[j];
        arr[j] := arr[j + 1];
        arr[j + 1] := tmp;
      end;

  for i := 1 to n do
    writeln(arr[i]);
end.
```

**Wygenerowany plik `out_bubble.c`:**

```c
#include <stdio.h>

int main(void) {
    int arr[5];
    int i, j, tmp, n;
    n = 5;
    arr[(1) - 1] = 5;
    arr[(2) - 1] = 3;
    arr[(3) - 1] = 1;
    arr[(4) - 1] = 4;
    arr[(5) - 1] = 2;
    for (i = 1; i <= (n - 1); i++) {
        for (j = 1; j <= (n - i); j++) {
            if ((arr[(j) - 1] > arr[((j + 1)) - 1])) {
                tmp = arr[(j) - 1];
                arr[(j) - 1] = arr[((j + 1)) - 1];
                arr[((j + 1)) - 1] = tmp;
            }
        }
    }
    for (i = 1; i <= n; i++) {
        printf("%d\n", arr[(i) - 1]);
    }
    return 0;
}
```

**Wynik działania** (każda liczba w nowej linii):

```
1
2
3
4
5
```

> Indeksy tablic w Pascalu zaczynają się od `low` (tu: 1), dlatego generator
> przelicza je na indeksację od zera w C, emitując wyrażenie postaci
> `arr[(index) - 1]`.

Katalog `examples/` zawiera dodatkowe przykładowe programy źródłowe; w
repozytorium znajdują się też gotowe wyniki transpilacji (`out_bubble.c`,
`out_hello.c`, `out_sort.c`).

---

## 9. Inne informacje

### 9.1. Struktura projektu

| Plik / katalog | Rola                                                               |
| -------------- | ------------------------------------------------------------------ |
| `main.py`      | Punkt wejścia CLI; spina cały potok i obsługuje argumenty/błędy    |
| `lexer.py`     | Skaner (`ply.lex`) — definicje tokenów, słowa kluczowe, komentarze |
| `parser.py`    | Parser LALR(1) (`ply.yacc`) — gramatyka i budowa AST               |
| `ast_nodes.py` | Definicje węzłów AST (`dataclasses`)                               |
| `semantic.py`  | Analiza semantyczna — tablica symboli i sprawdzanie typów          |
| `codegen.py`   | Generator kodu C (wzorzec Visitor)                                 |
| `errors.py`    | Typy wyjątków: `LexError`, `ParseError`, `SemanticError`           |
| `examples/`    | Przykładowe programy wejściowe `.pas`                              |
| `out_*.c`      | Przykładowe pliki wynikowe (kod C)                                 |

### 9.2. Analiza semantyczna (`semantic.py`)

Faza analizy semantycznej przechodzi drzewo AST wzorcem Visitor i weryfikuje
poprawność programu w oparciu o **tablicę symboli** (`SymbolTable`) zbudowaną jako
stos słowników reprezentujących zakresy leksykalne (`push_scope` / `pop_scope`).
Sprawdzane są m.in.:

- **redefinicja symbolu** w tym samym zakresie oraz **użycie niezadeklarowanego symbolu**,
- **zgodność typów** przy przypisaniach, z dozwolonymi konwersjami niejawnymi
  `integer → real` oraz `char → string`,
- **typ zmiennej sterującej** pętli `for` (musi być `integer`),
- **liczba argumentów** w wywołaniach procedur i funkcji,
- poprawność użycia tablic (dostęp/zapis dozwolony tylko dla symboli typu tablicowego),
- obsługa **wartości zwracanej funkcji** poprzez przypisanie do jej nazwy
  (wewnętrznie pod kluczem `__retval__`).

### 9.3. Obsługa błędów (`errors.py`)

Każda faza zgłasza dedykowany wyjątek niosący komunikat oraz numer linii:
`LexError` (skaner), `ParseError` (parser, m.in. „Nieoczekiwany token” oraz
„Nieoczekiwany koniec pliku”) i `SemanticError` (analiza semantyczna). `main.py`
przechwytuje je, wypisuje komunikat na `stderr` i kończy działanie kodem `1`.

### 9.4. Reprezentacja pośrednia (AST)

Węzły AST zdefiniowano jako `dataclasses` w `ast_nodes.py` (m.in. `Program`,
`Block`, `VarDecl`, `ArrayDecl`, `ProcedureDecl`, `FunctionDecl`, `IfStatement`,
`ForStatement`, `WhileStatement`, `RepeatStatement`, `BinOp`, `UnaryOp`,
`ArrayAccess`, `ArrayAssignment`, literały). Każdy węzeł przechowuje numer linii,
co umożliwia raportowanie błędów na etapie analizy semantycznej.
