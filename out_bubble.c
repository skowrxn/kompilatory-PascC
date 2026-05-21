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
