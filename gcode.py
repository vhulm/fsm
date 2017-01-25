#!/usr/bin/env python3
# -*-coding:utf-8-*-
import os
import json

CONF_FILE = "./fsm_conf.json"

OBJ_FILE_DIR = "./"
CONF_HEADER_FILE = "fsm_conf.h"
CONF_SOURCE_FILE = "fsm_conf.c"

STRUCT_END = "NULL};" + str(os.linesep)
NEW_LINE = str(os.linesep)


def print_iterable(items):
    for item in items:
        print(item)


class ConfParser(object):
    def __init__(self, filename):
        self.filename = filename
        with open(filename, "r") as f:
            self.conf = json.load(f)

        self.actuators = self.conf.get("actuators", [])
        self.states = self.conf.get("states", [])

    @staticmethod
    def _get_states_func_declare(state):
        return "static void {entryfunc}(void);{new_line}static void {exitfunc}(void);{new_line}{new_line}".format(
            new_line=NEW_LINE,
            **state)

    @staticmethod
    def _get_states_func_define(state):
        return "static void {entryfunc}(void){new_line}{{{new_line}\tprintf(\"{entryfunc}\\n\");{new_line}}}{new_line}{new_line}static void {exitfunc}(void){new_line}{{{new_line}\tprintf(\"{exitfunc}\\n\");{new_line}}}{new_line}{new_line}".format(
            new_line=NEW_LINE,
            **state)

    @staticmethod
    def _get_actuators_func_declare(actuator):
        return "static void {}(void);{new_line}".format(actuator["actuator"][3], new_line=NEW_LINE)

    @staticmethod
    def _get_actuators_func_define(actuator):
        return "static void {0[3]}(void){new_line}{{{new_line}\tprintf(\"{0[3]}\\n\");{new_line}}}{new_line}{new_line}".format(
            actuator["actuator"],
            new_line=NEW_LINE)

    def _update_states(self):
        self.states.insert(0, dict(name="root", parent="root"))  # Insert the "root" node to the head
        temp_dict = {}
        for state in self.states:
            state["entryfunc"] = state["name"] + "_EntryFunc"
            state["exitfunc"] = state["name"] + "_ExitFunc"
            state["childs"] = []
            state["actuators"] = []
            temp_dict[state["name"]] = state

        for state in self.states:
            temp_dict[state["parent"]]["childs"].append(state["name"])

        temp_dict["root"]["childs"].remove("root")

        self.states_index = temp_dict
        self.states_list = list(self.states_index.keys())

    def _update_actuators(self):
        for actuator in self.actuators:
            act = actuator["actuator"]
            name = act[0] + "_" + act[1] + "Actor"
            action = act[0] + "_" + act[1] + "Action"
            act.insert(0, name)
            act.insert(3, action)
            self._from_actuators_update_states(act)

    def _from_actuators_update_states(self, act):
        self.states_index[act[1]]["actuators"].append(act[0])

    def resolve(self):
        self._update_states()
        # print_iterable(self.states)
        self._update_actuators()
        print_iterable(self.actuators)
        print_iterable(self.states)
        print_iterable(self.states_index.items())

    def _write_header_file(self):
        f = open(CONF_HEADER_FILE, "w")
        f.write("""#ifndef FSM_CONF_H
#define FSM_CONF_H

#include "fsm.h"

typedef enum
{
    EVENT_1 = 0,
    EVENT_2,
    EVENT_3,
    EVENT_4,
    EVENT_5,
    XXX_EVENT_MAX,
}XXX_EVENT;
""")
        f.write("{new_line}TYPE_STATE_MGR *XXX_StateMachineCreate(void);{new_line}{new_line}".format(new_line=NEW_LINE))

        f.write("""#endif

""")
        f.close()

    def _format_actuator(self, actuator):
        act = actuator["actuator"]
        return "TYPE_ACTUATOR {0[0]} = {{{0[2]}, {0[3]}, (TYPE_STATE *){1}U}};{new_line}".format(
            act, self.states_list.index(act[4]), new_line=NEW_LINE)

    def _write_actuators(self, fd):
        for actuator in self.actuators:
            fd.write(self._format_actuator(actuator))

        fd.write("{new_line}TYPE_ACTUATOR *AllActors[] = {{ \\{new_line}".format(new_line=NEW_LINE))
        for actuator in self.actuators:
            fd.write("&{},  \\{new_line}".format(actuator["actuator"][0], new_line=NEW_LINE))

        fd.write(STRUCT_END)
        fd.write(NEW_LINE)

    def _writes_state_child(self, fd, state):
        fd.write("TYPE_STATE *{name}_State_Childs[] = {{".format(**state))
        for child in state["childs"]:
            fd.write("(TYPE_STATE *){}U, ".format(self.states_list.index(child)))
        fd.write(STRUCT_END)

    def _writes_state_actuator(self, fd, state):
        fd.write("TYPE_ACTUATOR *{name}_State_Actuators[] = {{".format(**state))
        for actuator in state["actuators"]:
            fd.write("&{}, ".format(actuator))
        fd.write(STRUCT_END)

    def _writes_states(self, fd):
        for state in self.states:
            self._writes_state_child(fd, state)
            self._writes_state_actuator(fd, state)
            fd.write(
                "TYPE_STATE {0}_State = {{ \\{new_line}(TYPE_STATE *){1}U, \\{new_line}{0}_EntryFunc, \\{new_line}{0}_ExitFunc, \\{new_line}(TYPE_STATE **){0}_State_Childs, \\{new_line}(TYPE_ACTUATOR **){0}_State_Actuators, \\{new_line}}};{new_line}{new_line}".format(
                    state["name"], self.states_list.index(state["parent"]), new_line=NEW_LINE))

        fd.write("TYPE_STATE *AllStates[] = {")
        for state in self.states_list:
            fd.write("&{}_State, ".format(state))
        fd.write(STRUCT_END)
        fd.write(NEW_LINE)

    def _write_data_const_func(self, fd):
        fd.write("""TYPE_STACK Stack = {{0}, 0};

TYPE_STATE_MGR StateMgr = {&root_State,&STA_2D_State,&Stack};

TYPE_STATE_MGR *XXX_StateMachineCreate(void)
{
    TYPE_ACTUATOR **pAllActors = (TYPE_ACTUATOR **)AllActors;
    TYPE_STATE **pAllStates = (TYPE_STATE **)AllStates;
    TYPE_STATE **pChilds = NULL;
    T32U TargetStateID = 0;

    while(*pAllActors != NULL)
    {
        TargetStateID = (T32U)((*pAllActors)->TargetState);
        ((*pAllActors)->TargetState) = AllStates[TargetStateID];
        pAllActors++;
    }

    while(*pAllStates != NULL)
    {
        TargetStateID = (T32U)((*pAllStates)->pParent);
        (*pAllStates)->pParent = AllStates[TargetStateID];
        pChilds = (*pAllStates)->pChilds;
        while(*pChilds != NULL)
        {
            TargetStateID = (T32U)(*pChilds);
            (*pChilds) = AllStates[TargetStateID];
            pChilds++;
        }
        pAllStates++;
    }

    return &StateMgr;
}
""")

    def _write_func_declare(self, fd):
        for state in self.states:
            fd.write(ConfParser._get_states_func_declare(state))

        for actuator in self.actuators:
            fd.write(ConfParser._get_actuators_func_declare(actuator))

        fd.write(NEW_LINE)

    def _write_source_file(self):
        f = open(CONF_SOURCE_FILE, "w")
        f.write(r'''#include <stdio.h>
#include "fsm_conf.h"

''')
        self._write_func_declare(f)
        self._write_actuators(f)
        self._writes_states(f)
        self._write_data_const_func(f)
        for state in self.states:
            f.write(ConfParser._get_states_func_define(state))

        for actuator in self.actuators:
            f.write(ConfParser._get_actuators_func_define(actuator))
        f.close()

    def write_to_file(self):
        self._write_header_file()
        self._write_source_file()


def main():
    parser = ConfParser(CONF_FILE)
    parser.resolve()
    parser.write_to_file()


if __name__ == "__main__":
    main()
