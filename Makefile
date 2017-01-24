a.out:demo.o fsm.o fsm_conf.o
	gcc demo.o fsm.o fsm_conf.o
demo.o:demo.c fsm.h fsm_conf.h
	gcc -c demo.c -o demo.o
fsm.o:fsm.c fsm.h fsm_conf.h
	gcc -c fsm.c -o fsm.o
fsm_conf.o:fsm_conf.c fsm_conf.h fsm.h
	gcc -c fsm_conf.c -o fsm_conf.o

clean:
	rm ./*.o
	rm ./a.out
