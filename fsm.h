#ifndef FSM_H
#define FSM_H

#include <stdio.h>

#define NO_ERROR 0
#define ERROR_1 -1

//#define DEBUG

#ifdef DEBUG
	#define pprintf printf
#else
	#define pprintf printf_null
#endif

int printf_null(char *fmt, ...);

typedef signed char 	T8S;
typedef unsigned char 	T8U;
typedef signed short 	T16S;
typedef unsigned short 	T16U;
typedef signed int 		T32S;
typedef unsigned int 	T32U;

typedef void (*FP_ACT_CALL_BACK_FUNC)(void);

typedef void (*FP_STATE_EX_FUNC)(void);

typedef enum
{
	STATE_ENTRY = 0,
	STATE_EXIT,
	TYPE_STATE_OPT_MAX,
}TYPE_STATE_OPT;

void NULL_FUNC(void);


typedef struct tSTATE TYPE_STATE;

typedef unsigned char TYPE_EVENT;

typedef struct tACTUATOR
{
	TYPE_EVENT RecvEvent;
	FP_ACT_CALL_BACK_FUNC CallFunc;
	TYPE_STATE *TargetState;
}TYPE_ACTUATOR;

struct tSTATE
{
	TYPE_STATE *pParent;
	FP_STATE_EX_FUNC EntryFunc;
	FP_STATE_EX_FUNC ExitFunc;
	TYPE_STATE *pChilds;
	TYPE_ACTUATOR *pActuators;
};

#define MAX_ROUTE_STACK_DEEP 300

typedef struct tSTACK
{
	FP_STATE_EX_FUNC Stack[MAX_ROUTE_STACK_DEEP];
	T16U SP;
}TYPE_STACK;

typedef struct tSTATE_MGR
{
	TYPE_STATE *pRoot;
	TYPE_STATE *pCurState;
	TYPE_STACK *pStack;
}TYPE_STATE_MGR;

FP_STATE_EX_FUNC StackPOP(TYPE_STACK *this);
FP_STATE_EX_FUNC StackPUSH(TYPE_STACK *this,FP_STATE_EX_FUNC CallFunc);
FP_STATE_EX_FUNC StackView(TYPE_STACK *this);

void StateRouteRecord(TYPE_STATE_MGR *this,TYPE_STATE_OPT StateOpt,TYPE_STATE *State);

TYPE_STATE *SearchSiblingNodes(TYPE_STATE_MGR *this,TYPE_STATE *State,TYPE_STATE *TargetState);
TYPE_STATE *StateSearchUP(TYPE_STATE_MGR *this,TYPE_STATE *TargetState);

TYPE_STATE *StateSearchDown(TYPE_STATE_MGR *this,TYPE_STATE *TargetState);
TYPE_STATE *StateRecursionSearch(TYPE_STATE_MGR *this,TYPE_STATE *State,TYPE_STATE *TargetState);

TYPE_STATE *StateSearchTargetState(TYPE_STATE_MGR *this,TYPE_STATE *TargetState);

void HandleEvent(TYPE_STATE_MGR *this,TYPE_EVENT Event);

T32S StackTest(void);

#endif

