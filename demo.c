#include <stdio.h>
#include "fsm.h"
#include "fsm_conf.h"

TYPE_STATE_MGR *AudState;

int main()
{
#ifdef DEBUG
	StackTest();
#endif
    AudState = XXX_StateMachineCreate();
    HandleEvent(AudState,EVENT_1);
	printf("Hello World!\n");
	return 0;
}

