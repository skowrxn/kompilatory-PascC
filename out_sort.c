#include <stdio.h>

void Swap(int* a, int* b) {
    int t;
    t = a;
    a = b;
    b = t;
}

int main(void) {
    int i, j, tmp;
    i = 1;
    j = 2;
    tmp = 3;
    if ((i > j)) {
        Swap(i, j);
    }
    printf("%d\n", i);
    printf("%d\n", j);
    return 0;
}
