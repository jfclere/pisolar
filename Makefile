waitfortempfile.o: waitfortempfile.c
	cc -c waitfortempfile.c
waitfortmess.o: waitfortmess.c
	cc -c waitformess.c
inserttemp.o: inserttemp.c
	cc -c inserttemp.c
insertgas.o: insertgas.c
	cc -c insertgas.c
insertwat.o: insertwat.c
	cc -c insertwat.c
waitfordatafile: waitfortempfile.o insertgas.o inserttemp.o insertwat.o
	cc -o waitfordatafile waitfortempfile.o insertgas.o inserttemp.o insertwat.o -lpq -lz
waitfordatamess: waitformess.o insertgas.o inserttemp.o
	cc -o waitfordatamess waitformess.o insertgas.o inserttemp.o -lpq -lz -lpaho-mqtt3as
