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
