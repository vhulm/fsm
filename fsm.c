#include <stdio.h>
#include "fsm.h"

static TYPE_ACTUATOR *SearchActuator(TYPE_STATE_MGR *this,TYPE_EVENT Event);
static TYPE_STATE *SearchTargetState(TYPE_STATE_MGR *this,TYPE_STATE *TargetState);
static void StateRoutePlay(TYPE_STATE_MGR *this);

static TYPE_STATE *SearchUP(TYPE_STATE_MGR *this,TYPE_STATE *TargetState);
static TYPE_STATE *SearchDown(TYPE_STATE_MGR *this,TYPE_STATE *TargetState);

static TYPE_STATE *SearchSiblingNodes(TYPE_STATE_MGR *this,TYPE_STATE *State,TYPE_STATE *TargetState);

static TYPE_STATE *RecursionSearch(TYPE_STATE_MGR *this,TYPE_STATE *State,TYPE_STATE *TargetState);

static void StateRouteRecord(TYPE_STATE_MGR *this,TYPE_STATE_OPT StateOpt,TYPE_STATE *State);

static FP_STATE_EX_FUNC StackPOP(TYPE_STACK *this);
static FP_STATE_EX_FUNC StackPUSH(TYPE_STACK *this,FP_STATE_EX_FUNC CallFunc);
static FP_STATE_EX_FUNC StackView(TYPE_STACK *this);

static void NULL_FUNC(void);

void HandleEvent(TYPE_STATE_MGR *this,TYPE_EVENT Event)
{
	TYPE_ACTUATOR *pActuator = NULL;
	TYPE_STATE *pTargetState = NULL;

	pActuator = SearchActuator(this,Event);
	if (pActuator != NULL)
	{
		pTargetState = SearchTargetState(this,pActuator->TargetState);
		if(pTargetState !=NULL)
		{
			StateRoutePlay(this);
			this->pCurState = pTargetState;
		}
	}
}

static TYPE_ACTUATOR *SearchActuator(TYPE_STATE_MGR *this,TYPE_EVENT Event)
{
	TYPE_STATE *pCurSerchState = this->pCurState;
	TYPE_ACTUATOR **pCurActuator = NULL;
	
	while(pCurSerchState != this->pRoot)
	{
		pCurActuator = pCurSerchState->pActuators;
		while(*pCurActuator != NULL)
		{
			if((*pCurActuator)->RecvEvent == Event)
			{
				((*pCurActuator)->CallFunc)();
				return *pCurActuator;
			}
			pCurActuator++;
		}
		pCurSerchState = pCurSerchState->pParent;
	}
	return NULL;
}

static TYPE_STATE *SearchTargetState(TYPE_STATE_MGR *this,TYPE_STATE *TargetState)
{
	if(SearchUP(this,TargetState) == TargetState)
	{
		return TargetState;
	}else
	{
		 return SearchDown(this,TargetState);
	}	
}

static void StateRoutePlay(TYPE_STATE_MGR *this)
{
	TYPE_STACK *pStack = this->pStack;
	FP_STATE_EX_FUNC CallFunc = NULL;
	T16U SP = 0;
	
	while((pStack->SP) != SP)
	{
		CallFunc = pStack->Stack[SP++];
		CallFunc();
	}
	pStack->SP = 0;
}

static TYPE_STATE *SearchUP(TYPE_STATE_MGR *this,TYPE_STATE *TargetState)
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

static TYPE_STATE *SearchDown(TYPE_STATE_MGR *this,TYPE_STATE *TargetState)
{
	TYPE_STATE **pCurSerchState = this->pRoot->pChilds;

	while(*pCurSerchState != NULL)
	{
		if(RecursionSearch(this,*pCurSerchState,TargetState) == TargetState)
		{
			return TargetState;
		}

		pCurSerchState++;
	}
	return NULL;
}

static TYPE_STATE *SearchSiblingNodes(TYPE_STATE_MGR *this,TYPE_STATE *State,TYPE_STATE *TargetState)
{
	TYPE_STATE **pState = State->pChilds;
	
	while (*pState != NULL)
	{
		if(*pState == TargetState)
		{
			StateRouteRecord(this,STATE_ENTRY,*pState);
			return *pState;
		}
		pState++;
	}
	return NULL;
}

static TYPE_STATE *RecursionSearch(TYPE_STATE_MGR *this,TYPE_STATE *State,TYPE_STATE *TargetState)
{
	TYPE_STATE **pChild = State->pChilds;
	
	StateRouteRecord(this,STATE_ENTRY,State);
	
	if(*(State->pChilds) == NULL)
	{
		StateRouteRecord(this,STATE_EXIT,State);
		return NULL;
	}
	
	if(SearchSiblingNodes(this,State,TargetState) == TargetState)
	{
		return TargetState;
	}else
	{
		while(*pChild != NULL)
		{
			if(RecursionSearch(this,*pChild,TargetState) == TargetState)
			{
				return TargetState;
			}

			pChild++;
		}
		StateRouteRecord(this,STATE_EXIT,State);
		return NULL;
	}
}

static void StateRouteRecord(TYPE_STATE_MGR *this,TYPE_STATE_OPT StateOpt,TYPE_STATE *State)
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

static FP_STATE_EX_FUNC StackPOP(TYPE_STACK *this)
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

static FP_STATE_EX_FUNC StackPUSH(TYPE_STACK *this,FP_STATE_EX_FUNC CallFunc)
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

static FP_STATE_EX_FUNC StackView(TYPE_STACK *this)
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

static void NULL_FUNC(void)
{
	
}

int printf_null(char *fmt, ...)
{	
	return 0;
}

T32S StackTest(void)
{
	TYPE_STACK Stack= {{0}, 0};
	T32U i=0;
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

