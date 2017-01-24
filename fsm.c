#include <stdio.h>
#include "fsm.h"

void NULL_FUNC(void)
{
	
}

int printf_null(char *fmt, ...)
{	
	return 0;
}

FP_STATE_EX_FUNC StackPOP(TYPE_STACK *this)
{
	T16U SP = this->SP;
	
	if(SP == 0)
	{
		return &NULL_FUNC;
	}else
	{
		return this->Stack[--(this->SP)];
	}
}

FP_STATE_EX_FUNC StackPUSH(TYPE_STACK *this,FP_STATE_EX_FUNC CallFunc)
{
	T16U SP = this->SP;

	if(SP >= MAX_ROUTE_STACK_DEEP)
	{
		return &NULL_FUNC;
	}else
	{
		this->Stack[this->SP++] = CallFunc;
		return CallFunc;
	}
}

FP_STATE_EX_FUNC StackView(TYPE_STACK *this)
{
	T16U SP = this->SP;
	
	if(SP == 0)
	{
		return &NULL_FUNC;
	}else
	{
		return this->Stack[--SP];
	}
}

void StateRouteRecord(TYPE_STATE_MGR *this,TYPE_STATE_OPT StateOpt,TYPE_STATE *State)
{
	if(StackView(this->pStack) == &NULL_FUNC)
	{
		/*Stack empty*/
		/*nothing to do*/
	}

	if(StateOpt == STATE_ENTRY)
	{
		if(StackView(this->pStack) == (State->ExitFunc))
		{
			StackPOP(this->pStack);
		}else
		{
			StackPUSH(this->pStack,State->EntryFunc);
		}
	}else if(StateOpt == STATE_EXIT)
	{
		if(StackView(this->pStack) == (State->EntryFunc))
		{
			StackPOP(this->pStack);
		}else
		{
			StackPUSH(this->pStack,State->ExitFunc);
		}
	}else
	{
		pprintf("Arg \"StateOpt\" Error!\n");
	}
}

TYPE_STATE *SearchSiblingNodes(TYPE_STATE_MGR *this,TYPE_STATE *State,TYPE_STATE *TargetState)
{
	TYPE_STATE *pState = State->pChilds;
	while (pState != NULL)
	{
		if(pState == TargetState)
		{
			StateRouteRecord(this,STATE_ENTRY,pState);
			return pState;
		}
		pState++;
	}
	return NULL;
}

TYPE_STATE *StateSearchUP(TYPE_STATE_MGR *this,TYPE_STATE *TargetState)
{
	TYPE_STATE *pCurSerchState = this->pCurState;

	while(pCurSerchState != this->pRoot)
	{
		if(pCurSerchState != TargetState)
		{
			StateRouteRecord(this,STATE_EXIT,pCurSerchState);
			if(SearchSiblingNodes(this,pCurSerchState->pParent,TargetState) == TargetState)
			{
				return TargetState;
			}
		}else
		{
			return TargetState;
		}
		pCurSerchState = pCurSerchState->pParent;
	}	
	return NULL;
}

TYPE_STATE *StateSearchDown(TYPE_STATE_MGR *this,TYPE_STATE *TargetState)
{
	TYPE_STATE *pCurSerchState = this->pRoot->pChilds;

	while(pCurSerchState != NULL)
	{
		if(StateRecursionSearch(this,pCurSerchState,TargetState) == TargetState)
		{
			return TargetState;
		}

		pCurSerchState++;
	}
	return NULL;
	
}

TYPE_STATE *StateRecursionSearch(TYPE_STATE_MGR *this,TYPE_STATE *State,TYPE_STATE *TargetState)
{
	TYPE_STATE *pChild = State->pChilds;
	
	StateRouteRecord(this,STATE_ENTRY,State);
	
	if(State->pChilds == NULL)
	{
		StateRouteRecord(this,STATE_EXIT,State);
		return NULL;
	}
	
	if(SearchSiblingNodes(this,State,TargetState) == TargetState)
	{
		return TargetState;
	}else
	{
		while(pChild != NULL)
		{
			if(StateRecursionSearch(this,pChild,TargetState) == TargetState)
			{
				return TargetState;
			}

			pChild++;
		}
		StateRouteRecord(this,STATE_EXIT,State);
		return NULL;
	}
}

TYPE_STATE *StateSearchTargetState(TYPE_STATE_MGR *this,TYPE_STATE *TargetState)
{
	StateSearchUP(this,TargetState);
	StateSearchDown(this,TargetState);
	
	return NULL;
}

void HandleEvent(TYPE_STATE_MGR *this,TYPE_EVENT Event)
{
	
}

T32S StackTest(void)
{
	TYPE_STACK Stack= {0};
	T16U i=0;
	Stack.SP = 0;
	printf("NULL_FUNC:%p\n",NULL_FUNC);
	printf("**********************\n");
	printf("StackPOP :%p\n",StackPOP(&Stack));
	printf("**********************\n");
	printf("StackView:%p\n",StackView(&Stack));
	printf("**********************\n");
	printf("StackPOP:%p\n",StackPOP(&Stack));
	printf("**********************\n");
	printf("StackPUSH:%p\n",StackPUSH(&Stack,(FP_STATE_EX_FUNC)456));
	printf("**********************\n");
	for(i=0;i<MAX_ROUTE_STACK_DEEP+5;i++)
	{
		printf("StackPUSH:%p\n",StackPUSH(&Stack,(FP_STATE_EX_FUNC)i));
	}
	printf("**********************\n");
	printf("StackView:%p\n",StackView(&Stack));
	printf("**********************\n");
	printf("StackPOP:%p\n",StackPOP(&Stack));
	printf("**********************\n");
	for(i=0;i<MAX_ROUTE_STACK_DEEP+5;i++)
	{
		printf("StackPOP:%p\n",StackPOP(&Stack));
	}
	printf("**********************\n");
	printf("StackPOP:%p\n",StackPOP(&Stack));
	printf("**********************\n");

	printf("Test complete!!!\n");
	return 0;
}

