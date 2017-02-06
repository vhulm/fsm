#!/usr/bin/env python3
# -*-coding:utf-8-*-
import os
import shutil
import json
from jinja2 import Template

CONF_FILE = "./fsm_conf.json"

CORE_FILE_PATH = "src"

OBJ_FILE_NAME_TEMP = "{}fsm_conf.{}"
DEMO_FILE_NAME = "demo"
MAKEFILE_FILE_NAME = "Makefile"

HEADER_FILE_TEMP = '''#ifndef {{ name.upper() }}_FSM_CONF_H
#define {{ name.upper() }}_FSM_CONF_H

#include "fsm.h"

typedef enum
{
    {% for event in events -%}
    {{ event }}
    {%- if loop.first %}=0{% endif -%}
    ,
    {% endfor %}{{ name.upper() }}_EVENT_MAX,
}{{ name.upper() }}_EVENT;

TYPE_STATE_MGR *{{ name }}_StateMachineCreate(void);

#endif
'''

SOURCE_FILE_TEMP = '''#include <stdio.h>
#include "{{ name }}fsm_conf.h"

{% for state in states %}
static void {{ state["name"] }}_EntryFunc(void);
static void {{ state["name"] }}_ExitFunc(void);
{% endfor %}

{% for actor in actuators -%}
static void {{ actor[1] }}_{{ actor[2] }}Action(void);
{% endfor %}

{% for actor in actuators -%}
TYPE_ACTUATOR {{ actor[0] }} = {{ '{' }}{{ actor[2] }}, {{ actor[1] }}_{{ actor[2] }}Action, (TYPE_STATE *){{ states_index[actor[3]] }}U{{ '}' }};
{% endfor %}

TYPE_ACTUATOR *{{ name }}AllActors[] = { \\
{% for actor in actuators -%}
&{{ actor[0] }}, \\
{% endfor %}NULL{{ '}' }};

{% for state in states %}
TYPE_STATE *{{ state["name"] }}_State_Childs[] = {{ '{' }}
{%- for child in state["childs"] -%}
(TYPE_STATE *){{ states_index[child] }}U,
{%- endfor %} NULL{{ '}' }};
TYPE_ACTUATOR *{{ state["name"] }}_State_Actuators[] = {
{%- for actor in state["actuators"] -%}
&{{ actor }},
{%- endfor -%}
NULL{{ '}' }};
TYPE_STATE {{ state["name"] }}_State = {{ '{' }} \\
(TYPE_STATE *){{ states_index[state["parent"]] }}U, \\
{{ state["name"] }}_EntryFunc, \\
{{ state["name"] }}_ExitFunc, \\
(TYPE_STATE **){{ state["name"] }}_State_Childs, \\
(TYPE_ACTUATOR **){{ state["name"] }}_State_Actuators, \\
{{ '}' }};
{% endfor %}

TYPE_STATE *{{ name }}AllStates[] = {
{%- for state in states -%}
&{{ state["name"] }}_State,
{%- endfor %}NULL{{ '}' }};

TYPE_STACK {{ name }}Stack = {{ '{{0}, 0};' }}

TYPE_STATE_MGR {{ name }}StateMgr = {{ '{' }}&root_State,&STA_2D_State,&{{ name }}Stack{{ '}' }};

TYPE_STATE_MGR *{{ name }}_StateMachineCreate(void)
{{ '{' }}
    TYPE_ACTUATOR **pAllActors = (TYPE_ACTUATOR **){{ name }}AllActors;
    TYPE_STATE **pAllStates = (TYPE_STATE **){{ name }}AllStates;
    TYPE_STATE **pChilds = NULL;
    T32U TargetStateID = 0;
    static T8U {{ name }}_SMActive = 0;

    if({{ name }}_SMActive == 1)
    {{ '{' }}
        return &{{ name }}StateMgr;
    {{ '}' }}
    while(*pAllActors != NULL)
    {{ '{' }}
        TargetStateID = (T32U)((*pAllActors)->TargetState)-1U;
        ((*pAllActors)->TargetState) = {{ name }}AllStates[TargetStateID];
        pAllActors++;
    {{ '}' }}

    while(*pAllStates != NULL)
    {{ '{' }}
        TargetStateID = (T32U)((*pAllStates)->pParent)-1U;
        (*pAllStates)->pParent = {{ name }}AllStates[TargetStateID];
        pChilds = (*pAllStates)->pChilds;
        while(*pChilds != NULL)
        {{ '{' }}
            TargetStateID = (T32U)(*pChilds)-1U;
            (*pChilds) = {{ name }}AllStates[TargetStateID];
            pChilds++;
        {{ '}' }}
        pAllStates++;
    {{ '}' }}

    {{ name }}_SMActive = 1;
    return &{{ name }}StateMgr;
{{ '}' }}

{% for state in states%}
static void {{ state["name"] }}_EntryFunc(void)
{
	pprintf("{{ state["name"] }}_EntryFunc\\n");
}

static void {{ state["name"] }}_ExitFunc(void)
{
    pprintf("{{ state["name"] }}_ExitFunc\\n");
}
{% endfor %}

{% for actor in actuators%}
static void {{ actor[1] }}_{{ actor[2] }}Action(void)
{
    pprintf("{{ actor[1] }}_{{ actor[2] }}Action\\n");
}
{% endfor %}

'''
DEMO_FILE_TEMP = '''#include <stdio.h>
#include "fsm.h"
#include "{{ name }}fsm_conf.h"

TYPE_STATE_MGR *{{ name }}SmHnd;

int main()
{
    {{ name }}SmHnd = {{ name }}_StateMachineCreate();
    /*
	HandleEvent({{ name }}SmHnd,USER_EVENT);
	HandleEvent({{ name }}SmHnd,USER_EVENT);
	*/

	return 0;
}

'''
MAKEFILE_FILE_TEMP = '''{{ demo }}: {{ demo }}.o fsm.o {{ name }}fsm_conf.o
	gcc -o $@ $^

{{ demo }}.o: {{ demo }}.c
	gcc -o $@ -c $<

fsm.o: fsm.c
	gcc -o $@ -c $<

{{ name }}fsm_conf.o: {{ name }}fsm_conf.c
	gcc -o $@ -c $<

clean:
	rm *.o
	rm {{ demo }}

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
        self.states_index = dict()

        self.app_path = self.name
        app_path = self.app_path

        if not os.path.exists(app_path):
            os.mkdir(app_path)
            print("Create < {} > succeed!!!".format(app_path))
        else:
            print("Directory < {} > Exists!!!".format(app_path))

        self.header_file_path = os.path.join(app_path, OBJ_FILE_NAME_TEMP.format(self.name, "h"))
        self.source_file_path = os.path.join(app_path, OBJ_FILE_NAME_TEMP.format(self.name, "c"))
        self.demo_file_path = os.path.join(app_path, DEMO_FILE_NAME + ".c")
        self.makefile_file_path = os.path.join(app_path, MAKEFILE_FILE_NAME)

        del app_path

        self.header_file_temp = Template(HEADER_FILE_TEMP)
        self.source_file_temp = Template(SOURCE_FILE_TEMP)
        self.demo_file_temp = Template(DEMO_FILE_TEMP)
        self.makefile_file_temp = Template(MAKEFILE_FILE_TEMP)

    def _update_states(self):
        self.states.insert(0, dict(name="root", parent="root"))  # Insert the "root" node to the head
        self.states_hash = {}
        for state in self.states:
            state["childs"] = []
            state["actuators"] = []
            self.states_hash[state["name"]] = state

        for state in self.states:
            self.states_hash[state["parent"]]["childs"].append(state["name"])

        self.states_hash["root"]["childs"].remove("root")

        for index, state in enumerate(self.states, 1):
            self.states_index[state["name"]] = index

    def _update_actuators(self):
        actuators = []
        for actuator in self.actuators:
            actor = actuator["actuator"]
            name = actor[0] + "_" + actor[1] + "Actor"
            self.events.add(actor[1])
            actor.insert(0, name)
            self.states_hash[actor[1]]["actuators"].append(actor[0])
            actuators.append(actor)

        self.actuators = actuators

        self.events = list(self.events)
        self.events.sort()

    def resolve(self):
        self._update_states()
        self._update_actuators()
        print_iterable(self.actuators)
        print_iterable(self.states)
        print_iterable(self.states_hash.items())
        print_iterable(self.events)
        print_iterable(self.states_index.items())

    def _write_header_file(self):
        with open(self.header_file_path, "w") as f:
            f.write(self.header_file_temp.render(name=self.name, events=self.events))

    def _write_source_file(self):
        with open(self.source_file_path, "w") as f:
            f.write(self.source_file_temp.render(name=self.name, states=self.states, actuators=self.actuators,
                                                 states_index=self.states_index))

    def _write_demo_file(self):
        with open(self.demo_file_path, "w") as f:
            f.write(self.demo_file_temp.render(name=self.name))

    def _write_makefile_file(self):
        with open(self.makefile_file_path, "w") as f:
            f.write(self.makefile_file_temp.render(name=self.name, demo=DEMO_FILE_NAME))

    def _copy_core_file(self):
        shutil.copy(os.path.join(CORE_FILE_PATH, "fsm.c"), self.app_path)
        shutil.copy(os.path.join(CORE_FILE_PATH, "fsm.h"), self.app_path)

    def write_to_file(self):
        self._write_header_file()
        self._write_source_file()
        self._write_demo_file()
        self._write_makefile_file()
        self._copy_core_file()


def main():
    parser = ConfParser(CONF_FILE)
    parser.resolve()
    parser.write_to_file()


if __name__ == "__main__":
    main()
