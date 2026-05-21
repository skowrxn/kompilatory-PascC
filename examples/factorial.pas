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
