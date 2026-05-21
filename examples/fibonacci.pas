program Fibonacci;

var
  i, n, a, b, tmp: integer;

begin
  readln(n);
  a := 0;
  b := 1;
  for i := 1 to n do
  begin
    writeln(a);
    tmp := a + b;
    a := b;
    b := tmp;
  end;
end.
