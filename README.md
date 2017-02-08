此项目是FSM(Finite State Machine)的C语言实现，你可以按照下面步骤配置并使用它

0x00:
    编辑“fsm_conf.json”文件为你想要的样子。(参照 “fsm_conf.json文件格式说明”)
0x01:
    执行“gcode.py”脚本,它会按照你在“fsm_conf.json”文件中的配置生成一个状态机实例和一个demo程序
    到一个app文件夹（文件夹以状态机名字命名）。
0x02:
    进入到app文件夹，简单编辑demo程序，填充*fsm_conf.c文件中Hook函数中的内容
    然后对下面的C文件编译链接执行目标程序即可看到效果。
    

Quick Start (Unix 环境)

root:~# cd fsm/
root:~/fsm# ./gcode.py 
root:~/fsm# cd Aud/
root:~/fsm# vim demo.c
root:~/fsm/Aud# make 
root:~/fsm/Aud# ./demo 


fsm_conf.json文件格式说明

{
  "name": "Aud",    //状态机名字，
  "init_state":"STA_2D",    //状态机初始进入的状态
  "states": [   //包含整个状态机中的所有状态
    {   //state格式
      "name": "子状态的名字",
      "parent": "该状态的父状态"
    },
    {   //demo
      "name": "STA_1A", 
      "parent": "root"
    },
    {
      "name": "STA_1B",
      "parent": "root"
    },
    {
      "name": "STA_1C",
      "parent": "root"
    },
    {
      "name": "STA_2A",
      "parent": "STA_1A"
    }
  ],
  "actuators": [    //所有状态包含的所有actuator
    {
      "actuator": ["隶属于哪个状态", "接收什么消息", "目标状态，如果不做状态的迁移目标状态写自己即可"]   //actuator格式     
    },
    {
      "actuator": ["STA_1A", "EVENT_1", "STA_1A"]   //demo
    },
    {
      "actuator": ["STA_1B", "EVENT_1", "STA_2D"]
    },
    {
      "actuator": ["STA_1C", "EVENT_1", "STA_2D"]
    },
    {
      "actuator": ["STA_2A", "EVENT_1", "STA_2D"]
    }
  ]
}
