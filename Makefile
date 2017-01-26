demo: demo.o fsm.o Audfsm_conf.o
	gcc -o $@ $^

demo.o: demo.c
	gcc -o $@ -c $<

fsm.o: fsm.c
	gcc -o $@ -c $<

Audfsm_conf.o: Audfsm_conf.c
	gcc -o $@ -c $<

clean:
	rm *.o
	rm demo
