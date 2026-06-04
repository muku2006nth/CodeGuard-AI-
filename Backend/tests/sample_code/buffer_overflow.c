#include <stdio.h>
#include <string.h>

void copy_input(char *input) {
    char buffer[16];
    strcpy(buffer, input);
    printf("Copied: %s\n", buffer);
}

int main(int argc, char *argv[]) {
    if (argc > 1) {
        copy_input(argv[1]);
    }
    return 0;
}
