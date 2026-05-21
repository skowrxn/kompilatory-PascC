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
