waitfortempfile.o: waitfortempfile.c
	cc -c waitfortempfile.c
inserttemp.o: inserttemp.c
	cc -c inserttemp.c
insertgas.o: insertgas.c
	cc -c insertgas.c
waitfordatafile: waitfortempfile.o insertgas.o inserttemp.o
	cc -o waitforgasfile waitfortempfile.o insertgas.o inserttemp.o -lpq
