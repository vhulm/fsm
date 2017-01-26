#include <stdio.h>
#include "fsm.h"
#include "Audfsm_conf.h"

TYPE_STATE_MGR *AudSmHnd;

int main()
{
    AudSmHnd = Aud_StateMachineCreate();
    HandleEvent(AudSmHnd,EVENT_1);
	
	return 0;
}

