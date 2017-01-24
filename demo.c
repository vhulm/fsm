#include <stdio.h>
#include "fsm.h"
#include "fsm_conf.h"

TYPE_STATE_MGR *AudStateHnd;

int main()
{
#ifdef DEBUG
	StackTest();
#endif
    AudStateHnd = XXX_StateMachineCreate();
    HandleEvent(AudStateHnd,EVENT_1);
	printf("Hello World!\n");
	return 0;
}

