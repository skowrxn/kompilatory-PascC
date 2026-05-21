#include <stdio.h>

int main(void) {
    int i, n, a, b, tmp;
    scanf("%d", &n);
    a = 0;
    b = 1;
    for (i = 1; i <= n; i++) {
        printf("%d\n", a);
        tmp = (a + b);
        a = b;
        b = tmp;
    }
    return 0;
}
