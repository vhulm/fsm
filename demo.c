#include <stdio.h>
#include "fsm.h"
#include "fsm_conf.h"

TYPE_STATE_MGR *AudSmHnd;

int main()
{
    AudSmHnd = XXX_StateMachineCreate();
    HandleEvent(AudSmHnd,EVENT_1);
	
	return 0;
}

