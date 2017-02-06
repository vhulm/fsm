此项目是FSM(Finite State Machine)的C语言实现，你可以按照下面步骤配置并使用它

0x00:
    编辑“fsm_conf.json”文件为你想要的样子。
0x01:
    执行“gcode.py”脚本,它会按照你在“fsm_conf.json”文件中的配置生成一个状态机实例和一个demo程序
    到一个app文件夹（文件夹以状态机名字命名）。
0x02:
    进入到app文件夹，简单编辑demo程序，对下面的C文件编译连接执行目标程序即可看到效果。
    

Quick Start (Unix 环境)

root:~# cd fsm/
root:~/fsm# ./gcode.py 
root:~/fsm# cd Aud/
root:~/fsm# vim demo.c
root:~/fsm/Aud# make 
root:~/fsm/Aud# ./demo 
