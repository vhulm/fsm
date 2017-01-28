#!/usr/bin/env python3
# -*-coding:utf-8-*-
import json
from jinja2 import Template

CONF_FILE = "./fsm_conf.json"

OBJ_FILE_DIR = "./"
OBJ_FILE_NAME_TEMP = "{}fsm_conf.{}"

HEADER_FILE_TEMP = '''#ifndef {{name.upper()}}_FSM_CONF_H
#define {{name.upper()}}_FSM_CONF_H

#include "fsm.h"

typedef enum
{
    {% for event in events -%}
    {{event}}
    {%- if loop.first %}=0{% endif -%}
    ,
    {% endfor %}{{name.upper()}}_EVENT_MAX,
}{{name.upper()}}_EVENT;

TYPE_STATE_MGR *{{name.upper()}}_StateMachineCreate(void);

#endif
'''

SOURCE_FILE_TEMP = '''#include <stdio.h>
#include "{{name}}fsm_conf.h"

{% for state in states %}
static void {{state["name"]}}_EntryFunc(void);
static void {{state["name"]}}_ExitFunc(void);
{% endfor %}

{% for actuator in actuators -%}
static void {{actuator["actuator"][1]}}_{{actuator["actuator"][2]}}Action(void);
{% endfor %}

{% for actuator in actuators -%}
TYPE_ACTUATOR {{actuator["actuator"][0]}} = {{'{'}}{{actuator["actuator"][2]}}, {{actuator["actuator"][1]}}_{{actuator["actuator"][2]}}Action, (TYPE_STATE *){{states_hash[actuator["actuator"][3]]}}U{{'}'}};
{% endfor %}

TYPE_ACTUATOR *{{name}}AllActors[] = { \\
{% for actuator in actuators -%}
&{{actuator["actuator"][0]}}, \\
{% endfor %}NULL{{'}'}};

{% for state in states %}
TYPE_STATE *{{state["name"]}}_State_Childs[] = {{'{'}}
{%- for child in state["childs"] -%}
(TYPE_STATE *){{states_hash[child]}}U,
{%- endfor %} NULL{{'}'}};
TYPE_ACTUATOR *{{state["name"]}}_State_Actuators[] = {
{%- for actuator in state["actuators"] -%}
&{{ actuator }},
{%- endfor -%}
NULL{{'}'}};
TYPE_STATE {{state["name"]}}_State = {{'{'}} \\
(TYPE_STATE *){{states_hash[state["parent"]]}}U, \\
{{state["name"]}}_EntryFunc, \\
{{state["name"]}}_ExitFunc, \\
(TYPE_STATE **){{state["name"]}}_State_Childs, \\
(TYPE_ACTUATOR **){{state["name"]}}_State_Actuators, \\
{{'}'}};
{% endfor %}

TYPE_STATE *{{ name }}AllStates[] = {
{%- for state in states -%}
&{{state["name"]}}_State,
{%- endfor %}NULL{{'}'}};

TYPE_STACK {{name}}Stack = {{'{{0}, 0};'}}

TYPE_STATE_MGR {{name}}StateMgr = {{'{'}}&root_State,&STA_2D_State,&{{name}}Stack{{'}'}};

TYPE_STATE_MGR *{{name}}_StateMachineCreate(void)
{{'{'}}
    TYPE_ACTUATOR **pAllActors = (TYPE_ACTUATOR **){{name}}AllActors;
    TYPE_STATE **pAllStates = (TYPE_STATE **){{name}}AllStates;
    TYPE_STATE **pChilds = NULL;
    T32U TargetStateID = 0;

    while(*pAllActors != NULL)
    {{'{'}}
        TargetStateID = (T32U)((*pAllActors)->TargetState)-1U;
        ((*pAllActors)->TargetState) = {{name}}AllStates[TargetStateID];
        pAllActors++;
    {{'}'}}

    while(*pAllStates != NULL)
    {{'{'}}
        TargetStateID = (T32U)((*pAllStates)->pParent)-1U;
        (*pAllStates)->pParent = {{name}}AllStates[TargetStateID];
        pChilds = (*pAllStates)->pChilds;
        while(*pChilds != NULL)
        {{'{'}}
            TargetStateID = (T32U)(*pChilds)-1U;
            (*pChilds) = {{name}}AllStates[TargetStateID];
            pChilds++;
        {{'}'}}
        pAllStates++;
    {{'}'}}

    return &{{name}}StateMgr;
{{'}'}}

{% for state in states%}
static void {{state["name"]}}_EntryFunc(void)
{
	pprintf("{{state["name"]}}_EntryFunc\\n");
}

static void {{state["name"]}}_ExitFunc(void)
{
    pprintf("{{state["name"]}}_ExitFunc\\n");
}
{% endfor %}

{% for actuator in actuators%}
static void {{actuator["actuator"][1]}}_{{actuator["actuator"][2]}}Action(void)
{
    pprintf("{{actuator["actuator"][1]}}_{{actuator["actuator"][2]}}Action\\n");
}
{% endfor %}

'''


def print_iterable(items):
    for item in items:
        print(item)


class ConfParser(object):
    def __init__(self, filename):
        self.filename = filename
        with open(filename, "r") as f:
            self.conf = json.load(f)

        self.name = self.conf.get("name", "")
        self.states = self.conf.get("states", [])
        self.actuators = self.conf.get("actuators", [])
        self.events = set()
        self.states_hash = dict()

        self.header_file_temp = Template(HEADER_FILE_TEMP)
        self.source_file_temp = Template(SOURCE_FILE_TEMP)

    def _update_states(self):
        self.states.insert(0, dict(name="root", parent="root"))  # Insert the "root" node to the head
        temp_dict = {}
        for state in self.states:
            state["childs"] = []
            state["actuators"] = []
            temp_dict[state["name"]] = state

        for state in self.states:
            temp_dict[state["parent"]]["childs"].append(state["name"])

        temp_dict["root"]["childs"].remove("root")
        self.states_index = temp_dict

        for index, state in enumerate(self.states, 1):
            self.states_hash[state["name"]] = index

    def _update_actuators(self):
        for actuator in self.actuators:
            act = actuator["actuator"]
            name = act[0] + "_" + act[1] + "Actor"
            self.events.add(act[1])
            act.insert(0, name)
            self._from_actuators_update_states(act)

        self.events = list(self.events)
        self.events.sort()

    def _from_actuators_update_states(self, act):
        self.states_index[act[1]]["actuators"].append(act[0])

    def resolve(self):
        self._update_states()
        self._update_actuators()
        print_iterable(self.actuators)
        print_iterable(self.states)
        print_iterable(self.states_index.items())
        print_iterable(self.events)
        print_iterable(self.states_hash.items())

    def _write_header_file(self):
        with open(OBJ_FILE_NAME_TEMP.format(self.name, "h"), "w") as f:
            f.write(self.header_file_temp.render(name=self.name, events=self.events))

    def _write_source_file(self):
        with open(OBJ_FILE_NAME_TEMP.format(self.name, "c"), "w") as f:
            f.write(self.source_file_temp.render(name=self.name, states=self.states, actuators=self.actuators,
                                                 states_hash=self.states_hash))

    def write_to_file(self):
        self._write_header_file()
        self._write_source_file()


def main():
    parser = ConfParser(CONF_FILE)
    parser.resolve()
    parser.write_to_file()


if __name__ == "__main__":
    main()
