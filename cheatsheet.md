# Ściągawka do projektu PascC — dla kogoś kto nigdy nie był na kompilatorach

---

## Co w ogóle robi ten projekt?

Wyobraź sobie tłumacza języków. Masz tekst po polsku, tłumaczysz go na angielski — słowo po słowie, zdanie po zdaniu, zachowując sens.

Ten projekt robi dokładnie to samo, tylko zamiast języków naturalnych są języki programowania:

> **Bierzemy kod napisany w Pascalu → i zamieniamy go na kod w C.**

Takie narzędzie nazywa się **transpilerem** (albo kompilatorem źródło-źródło).

Przykład. Masz taki kod w Pascalu:
```pascal
writeln('Witaj, swiecie!');
```

Program zamienia to automatycznie na C:
```c
printf("Witaj, swiecie!\n");
```

Efektem jest plik `.c`, który można normalnie skompilować przez `gcc` i uruchomić.

---

## Dlaczego akurat Pascal → C?

Pascal to stary język akademicki, prosty i czytelny. C to język niżej poziomu, bliższy sprzętowi. Tłumaczenie między nimi jest dobrym ćwiczeniem, bo:
- Pascal jest na tyle prosty, że nie ma setek wyjątków
- C jest wystarczająco podobny, żeby tłumaczenie było proste konceptualnie
- To klasyczne ćwiczenie na przedmiocie „Techniki Kompilacji"

---

## Jak działa od środka? — 4 etapy

Wyobraź sobie fabrykę z taśmą produkcyjną. Plik `.pas` wchodzi na początku, plik `.c` wychodzi na końcu. Po drodze są 4 stanowiska:

```
Plik .pas
    │
    ▼
┌──────────────┐
│  1. LEXER    │  → rozpoznaje słowa i znaki
└──────┬───────┘
       ▼
┌──────────────┐
│  2. PARSER   │  → sprawdza czy zdania mają sens gramatyczny
└──────┬───────┘
       ▼
┌──────────────┐
│  3. SEMANTIC │  → sprawdza czy kod ma logiczny sens
└──────┬───────┘
       ▼
┌──────────────┐
│  4. CODEGEN  │  → pisze gotowy kod C
└──────┬───────┘
       ▼
    Plik .c
```

### Etap 1 — Lexer (skaner) [`lexer.py`]

**Co robi:** Czyta plik znak po znaku i grupuje je w **tokeny** (żetony).

Token to najmniejsza sensowna jednostka języka — jak słowo w zdaniu.

Przykład: tekst `x := 42;` zostaje rozłożony na tokeny:
```
ID("x")   ASSIGN(":=")   INTEGER_CONST(42)   SEMICOLON(";")
```

To jak rozkładanie zdania na części mowy: rzeczownik, czasownik, przymiotnik...

Lexer rozumie:
- słowa kluczowe: `begin`, `end`, `if`, `while`, `for` itp.
- liczby: `42`, `3.14`
- napisy: `'hello'`
- operatory: `:=`, `+`, `<=`, `<>` itp.
- **ignoruje** komentarze i spacje

### Etap 2 — Parser [`parser.py`]

**Co robi:** Bierze strumień tokenów od lexera i sprawdza, czy mają **poprawną strukturę gramatyczną**. Jeśli tak — buduje drzewo AST.

AST (Abstract Syntax Tree) to drzewo, które reprezentuje strukturę programu. Zamiast tekstu mamy obiekty Pythona połączone w hierarchię.

Przykład — dla `if x > 0 then writeln(x)` drzewo wygląda tak:
```
IfStatement
├── condition: BinOp(VarRef("x"), ">", IntConst(0))
├── then_branch: WriteStatement(newline=True, args=[VarRef("x")])
└── else_branch: None
```

Parser używa **gramatyki** — zestawu reguł mówiących co jest poprawną składnią. Na przykład: `if_statement = "if" expression "then" statement`. Jeśli struktura tokenów nie pasuje do żadnej reguły — błąd składniowy.

### Etap 3 — Analiza semantyczna [`semantic.py`]

**Co robi:** Sprawdza czy kod ma **logiczny sens**, nawet jeśli jest gramatycznie poprawny.

Gramatycznie poprawne, ale semantycznie błędne przykłady:
- używasz zmiennej `x`, ale nigdy jej nie zadeklarowałeś
- próbujesz dodać liczbę całkowitą do wartości logicznej (`true + 5`)
- wywołujesz funkcję z 3 argumentami, ale ona przyjmuje 2

Analiza przechodzi przez całe drzewo AST i buduje **tablicę symboli** — słownik, który zapamiętuje wszystkie zmienne, funkcje, procedury i ich typy. Potem sprawdza każde użycie względem tej tablicy.

### Etap 4 — Generator kodu [`codegen.py`]

**Co robi:** Przechodzi przez drzewo AST i dla każdego węzła **wypisuje odpowiedni kod C**.

Używa wzorca **Visitor** — dla każdego rodzaju węzła jest osobna metoda `visit_NazwaWęzła`.

Przykłady tłumaczeń:
| Pascal | C |
|---|---|
| `x := 5` | `x = 5;` |
| `writeln(x)` | `printf("%d\n", x);` |
| `readln(n)` | `scanf("%d", &n);` |
| `a div b` | `a / b` (dzielenie całkowite) |
| `a = b` (porównanie) | `a == b` |
| `a <> b` | `a != b` |
| `and` | `&&` |
| `or` | `\|\|` |
| `not` | `!` |
| `integer` | `int` |
| `real` | `double` |
| `boolean` | `int` (0 lub 1) |

---

## Pliki w projekcie — co robi każdy

| Plik | Rola | Kiedy uruchamiany |
|---|---|---|
| `main.py` | Punkt wejścia, obsługuje argumenty CLI | zawsze jako pierwszy |
| `lexer.py` | Zamienia tekst na tokeny | etap 1 |
| `parser.py` | Buduje drzewo AST z tokenów | etap 2 |
| `ast_nodes.py` | Definicje klas węzłów drzewa | używany przez parser i codegen |
| `semantic.py` | Sprawdza poprawność semantyczną | etap 3 |
| `codegen.py` | Generuje kod C | etap 4 |
| `errors.py` | Klasy błędów (leksykalny, składniowy, semantyczny) | w razie błędu |
| `examples/*.pas` | Przykładowe programy Pascala do przetestowania | ręcznie |

---

## Kluczowe pojęcia — wyjaśnione prosto

### Token
Najmniejsza jednostka języka. Jak litera w Scrabble — sam w sobie ma typ i wartość. Np. token `INTEGER_CONST` o wartości `42`.

### Gramatyka
Zbiór reguł opisujący co jest poprawnym programem. Np. "instrukcja `if` musi mieć słowo `then` po warunku". Jeśli kod łamie regułę — parser zgłasza błąd.

### AST (Abstract Syntax Tree)
Drzewo obiektów w Pythonie reprezentujące strukturę programu. Zamiast operować na tekście, reszta programu operuje na tym drzewie — to wygodniejsze i bezpieczniejsze.

### Tablica symboli
Słownik przechowujący wszystkie znane nazwy (zmienne, funkcje, procedury) i ich typy. Analiza semantyczna używa jej do sprawdzania, czy używasz rzeczy, które istnieją.

### LALR(1)
Algorytm, którym działa parser (PLY/yacc). Skrót od "Look-Ahead Left-to-Right, Rightmost derivation, 1 token lookahead". W uproszczeniu: parser patrzy na jeden token do przodu i na podstawie tego decyduje co zrobić. Wystarczający dla większości popularnych języków programowania.

### Wzorzec Visitor
Sposób organizacji kodu generatora. Zamiast jednej wielkiej funkcji `if isinstance(node, X)...elif isinstance(node, Y)...`, mamy osobną metodę `visit_X`, `visit_Y` dla każdego typu węzła. Czytelniejsze i łatwiejsze w rozbudowie.

### Parametr `var` w Pascalu
W Pascalu możesz przekazać zmienną do procedury przez referencję — procedura dostaje dostęp do oryginału, nie kopii. W C odpowiada to wskaźnikom. Pascal: `procedure Swap(var a: integer)` → C: `void Swap(int* a)`. Przy wywołaniu Pascal: `Swap(x)` → C: `Swap(&x)`. Wewnątrz procedury Pascal: `a := 5` → C: `*a = 5`.

### Dangling else
Klasyczna niejednoznaczność gramatyczna. Dla `if A then if B then S1 else S2` — do którego `if` należy `else`? Standardowo do najbliższego. Rozwiązanie w PLY: sztuczny token priorytetowy `IF_WITHOUT_ELSE` z niższym priorytetem niż `ELSE`.

---

## Jak uruchomić

```bash
# Podstawowe użycie
py main.py --input examples/hello.pas --output hello.c

# Tryb debug — pokazuje tokeny i drzewo AST
py main.py --input examples/hello.pas --debug

# Skompiluj i uruchom wynik
gcc hello.c -o hello && hello.exe
```

---

## Możliwe pytania prowadzącego i odpowiedzi

**P: Co to jest transpiler i czym różni się od kompilatora?**

Kompilator tłumaczy kod źródłowy na kod maszynowy (zera i jedynki). Transpiler tłumaczy kod źródłowy na inny kod źródłowy — w naszym przypadku Pascal na C. Wynik transpilacji nadal trzeba skompilować kompilatorem C.

---

**P: Z czego składa się potok przetwarzania w tym projekcie?**

Z czterech etapów: lexer (tokenizacja), parser (budowa AST), analiza semantyczna (sprawdzanie typów i zakresów), generator kodu (emisja C). Każdy etap jest osobnym modułem.

---

**P: Co to jest token i podaj przykład?**

Token to atomowa jednostka języka — najmniejszy fragment, który ma znaczenie. Np. dla tekstu `x := 42` mamy trzy tokeny: `ID("x")`, `ASSIGN(":=")`, `INTEGER_CONST(42)`.

---

**P: Co to jest AST?**

Abstract Syntax Tree — drzewo obiektów reprezentujące strukturę programu. Zamiast tekstu, mamy hierarchię obiektów Pythona (dataclassy). Parser buduje to drzewo, analiza semantyczna je sprawdza, generator kodu przez nie chodzi.

---

**P: Jak działa tablica symboli?**

To stos słowników (jeden na każdy zakres leksykalny — globalny, lokalny funkcji itp.). Przechowuje nazwy i typy wszystkich zmiennych, funkcji i procedur. Przy każdym użyciu zmiennej sprawdzamy, czy jest w tablicy. Przy wywołaniu funkcji — czy liczba i typy argumentów się zgadzają.

---

**P: Jak obsługujesz parametry by-ref (var) z Pascala?**

W C nie ma referencji jak w C++, więc używamy wskaźników. Parametr `var a: integer` w Pascalu staje się `int* a` w C. Przy wywołaniu dodajemy `&` przed argumentem. Wewnątrz ciała procedury każde odwołanie do takiego parametru jest dereferencją: `(*a)`, a przypisanie: `*a = wartość`.

---

**P: Jak rozwiązałeś problem dangling else?**

Za pomocą sztucznego tokenu priorytetowego `IF_WITHOUT_ELSE` w PLY. Reguła `if...then` (bez else) ma niższy priorytet niż token `ELSE`, więc gdy parser widzi `else`, zawsze dołącza go do najbliższego `if`.

---

**P: Co robi PLY?**

PLY (Python Lex-Yacc) to biblioteka do budowy skanerów i parserów w Pythonie. `ply.lex` buduje DFA z wyrażeń regularnych do tokenizacji. `ply.yacc` buduje parser LALR(1) z reguł gramatycznych zapisanych jako funkcje Pythona z docstringami.

---

**P: Jak w Pascalu działa zwracanie wartości z funkcji?**

W Pascalu funkcja zwraca wartość przez przypisanie do własnej nazwy: `Fact := 1`. To nie jest standardowa zmienna — to specjalny mechanizm. W generowanym C tworzymy lokalną zmienną `_result_NazwaFunkcji`, przypisanie do nazwy funkcji zamieniane jest na przypisanie do tej zmiennej, a na końcu `return _result_NazwaFunkcji`.

---

**P: Jakie błędy wykrywa ten transpiler?**

Trzy rodzaje:
- **Leksykalne** — nieznany znak (np. `@`)
- **Składniowe** — naruszenie gramatyki (np. brak `then` po `if`)
- **Semantyczne** — niezadeklarowana zmienna, niezgodność typów, zła liczba argumentów

Każdy błąd zawiera numer linii i opis problemu.

---

## Mapa typów Pascal → C

| Pascal | C | Uwagi |
|---|---|---|
| `integer` | `int` | |
| `real` | `double` | nie `float`, bo Pascal real ma podwójną precyzję |
| `boolean` | `int` | 0 = false, 1 = true |
| `char` | `char` | |
| `string` | `char*` | wskaźnik na ciąg znaków |

## Mapa formatów printf/scanf

| Typ | Format |
|---|---|
| `integer` | `%d` |
| `real` | `%lf` |
| `char` | `%c` |
| `string` | `%s` |
