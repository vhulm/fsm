#include <stdio.h>
#include "fsm.h"

int main()
{
#ifdef DEBUG
	StackTest();
#endif

	printf("Hello World!\n");
	return 0;
}

