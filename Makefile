waitfortempfile.o: waitfortempfile.c
	cc -c waitfortempfile.c
inserttemp.o: inserttemp.c
	cc -c inserttemp.c
waitfortempfile: waitfortempfile.o inserttemp.o
	cc -o waitfortempfile waitfortempfile.o inserttemp.o -lpq
