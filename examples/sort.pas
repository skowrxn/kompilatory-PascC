program BubbleSort;

var
  i, j, tmp: integer;

procedure Swap(var a: integer; var b: integer);
var
  t: integer;
begin
  t := a;
  a := b;
  b := t;
end;

begin
  i := 1;
  j := 2;
  tmp := 3;
  if i > j then
    Swap(i, j);
  writeln(i);
  writeln(j);
end.
