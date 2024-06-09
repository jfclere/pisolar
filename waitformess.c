#include <stdio.h>
#include <sys/inotify.h>
#include <unistd.h>
#include <stdlib.h>
#include <signal.h>
#include <fcntl.h>
#include <string.h>
#include <time.h>
#include <zlib.h>
#include "MQTTAsync.h"

#if defined(_WRS_KERNEL)
#include <OsWrapper.h>
#endif

#define ADDRESS     "tcp://localhost:1883"
#define CLIENTID    "ExampleClientSub"
#define TOPIC       "topic/test"
#define PAYLOAD     "Hello World!"
#define QOS         1
#define TIMEOUT     10000L
#define USERNAME    "admin"
#define PASSWORD    "admin"

int disc_finished = 0;
int subscribed = 0;
int finished = 0;

static float readval(char *input) {
   char s[100], u[10];
   float v;
   sscanf(input, "%s : %f%s", s, &v, u);
   return v;
}
struct info {
   float temp;
   float pres;
   float humi;
};
struct gasinfo {
   float no2;
   float alcohol;
   float voc;
   float co;
};

int debug = 0;

void inserttemp(char *table, time_t t, float temp, float pres, float humi);
void insertgas(char *table, time_t t, float no2, float alcohol, float voc, float co);

static int getsumfile(char *filename) {
   FILE *fptr = fopen(filename, "r");
   if (!fptr)
       return 0;
   size_t size = 100;
   char *input = malloc(100);
   int sum = 0;
   while (fgets(input, size, fptr)>0) {
       sum  = sum + crc32(0x80000000, input, strlen(input));
   }
   fclose(fptr); 
   free(input);
   return sum;
}

/* read the Temperature, Pressure and Humidity from the temp.txt file */
static int readtempfile(char *filename, struct info *info) {
   FILE *fptr = fopen(filename, "r");
   if (!fptr)
       return 1;
   size_t size = 100;
   char *input = malloc(100);
   int ret = 0;
   while (fgets(input, size, fptr)>0) {
       if (strstr(input, "Temperature")) {
           info->temp = readval(input);
           ret++;
       } else if (strstr(input, "Pressure")) {
           info->pres = readval(input);
           ret++;
       } if (strstr(input, "Humidity")) {
           info->humi = readval(input);
           ret++;
       }
   }
   fclose(fptr); 
   free(input);
   if (ret == 3)
       return 0;
   return 1;
}
static int readgasfile(char *filename, struct gasinfo *info) {
   FILE *fptr = fopen(filename, "r");
   if (!fptr) {
       if (debug)
           printf("readgasfile: open %s failed\n", filename);
       return 1;
   }
   size_t size = 100;
   char *input = malloc(100);
   int ret = 0;
   while (fgets(input, size, fptr)>0) {
       if (strstr(input, "No2")) {
           info->no2 = readval(input);
           ret++;
           if (debug)
               printf("readgasfile: got No2\n");
       } else if (strstr(input, "Alcohol")) {
           info->alcohol = readval(input);
           ret++;
           if (debug)
               printf("readgasfile: got Alcohol\n");
       } else if (strstr(input, "Voc")) {
           info->voc = readval(input);
           ret++;
           if (debug)
               printf("readgasfile: got Voc\n");
       } if (strstr(input, "Co")) {
           info->co = readval(input);
           ret++;
           printf("readgasfile: got Co\n");
       }
   }
   fclose(fptr);
   free(input);
   if (ret == 4)
       return 0;
   return 1;
}

void onConnect(void* context, MQTTAsync_successData* response);
void onConnectFailure(void* context, MQTTAsync_failureData* response);

void connlost(void *context, char *cause)
{
	MQTTAsync client = (MQTTAsync)context;
	MQTTAsync_connectOptions conn_opts = MQTTAsync_connectOptions_initializer;
	int rc;

	printf("\nConnection lost\n");
	if (cause)
		printf("     cause: %s\n", cause);

	printf("Reconnecting\n");
	conn_opts.keepAliveInterval = 20;
	conn_opts.cleansession = 1;
	conn_opts.onSuccess = onConnect;
	conn_opts.onFailure = onConnectFailure;
        conn_opts.username = USERNAME;
        conn_opts.password = PASSWORD;
	if ((rc = MQTTAsync_connect(client, &conn_opts)) != MQTTASYNC_SUCCESS)
	{
		printf("Failed to start connect, return code %d\n", rc);
		finished = 1;
	}
}


int msgarrvd(void *context, char *topicName, int topicLen, MQTTAsync_message *message)
{
    printf("Message arrived\n");
    printf("     topic: %s\n", topicName);
    printf("   message: %.*s\n", message->payloadlen, (char*)message->payload);
    MQTTAsync_freeMessage(&message);
    MQTTAsync_free(topicName);
    return 1;
}

void onDisconnectFailure(void* context, MQTTAsync_failureData* response)
{
	printf("Disconnect failed, rc %d\n", response->code);
	disc_finished = 1;
}

void onDisconnect(void* context, MQTTAsync_successData* response)
{
	printf("Successful disconnection\n");
	disc_finished = 1;
}

void onSubscribe(void* context, MQTTAsync_successData* response)
{
	printf("Subscribe succeeded\n");
	subscribed = 1;
}

void onSubscribeFailure(void* context, MQTTAsync_failureData* response)
{
	printf("Subscribe failed, rc %d\n", response->code);
	finished = 1;
}


void onConnectFailure(void* context, MQTTAsync_failureData* response)
{
	printf("Connect failed, rc %d\n", response->code);
	finished = 1;
}


void onConnect(void* context, MQTTAsync_successData* response)
{
	MQTTAsync client = (MQTTAsync)context;
	MQTTAsync_responseOptions opts = MQTTAsync_responseOptions_initializer;
	int rc;

	printf("Successful connection\n");

	printf("Subscribing to topic %s\nfor client %s using QoS%d\n\n"
           "Press Q<Enter> to quit\n\n", TOPIC, CLIENTID, QOS);
	opts.onSuccess = onSubscribe;
	opts.onFailure = onSubscribeFailure;
	opts.context = client;
	if ((rc = MQTTAsync_subscribe(client, TOPIC, QOS, &opts)) != MQTTASYNC_SUCCESS)
	{
		printf("Failed to start subscribe, return code %d\n", rc);
		finished = 1;
	}
}

int main(int argc, char* argv[])
{
	MQTTAsync client;
	MQTTAsync_connectOptions conn_opts = MQTTAsync_connectOptions_initializer;
	MQTTAsync_disconnectOptions disc_opts = MQTTAsync_disconnectOptions_initializer;
	int rc;
	int ch;

	if ((rc = MQTTAsync_create(&client, ADDRESS, CLIENTID, MQTTCLIENT_PERSISTENCE_NONE, NULL))
			!= MQTTASYNC_SUCCESS)
	{
		printf("Failed to create client, return code %d\n", rc);
		rc = EXIT_FAILURE;
		goto exit;
	}

	if ((rc = MQTTAsync_setCallbacks(client, client, connlost, msgarrvd, NULL)) != MQTTASYNC_SUCCESS)
	{
		printf("Failed to set callbacks, return code %d\n", rc);
		rc = EXIT_FAILURE;
		goto destroy_exit;
	}

	conn_opts.keepAliveInterval = 20;
	conn_opts.cleansession = 1;
	conn_opts.onSuccess = onConnect;
	conn_opts.onFailure = onConnectFailure;
	conn_opts.context = client;
        conn_opts.username = USERNAME;
        conn_opts.password = PASSWORD;
	if ((rc = MQTTAsync_connect(client, &conn_opts)) != MQTTASYNC_SUCCESS)
	{
		printf("Failed to start connect, return code %d\n", rc);
		rc = EXIT_FAILURE;
		goto destroy_exit;
	}

	while (!subscribed && !finished)
		#if defined(_WIN32)
			Sleep(100);
		#else
			usleep(10000L);
		#endif

	if (finished)
		goto exit;

	do 
	{
		ch = getchar();
	} while (ch!='Q' && ch != 'q');

	disc_opts.onSuccess = onDisconnect;
	disc_opts.onFailure = onDisconnectFailure;
	if ((rc = MQTTAsync_disconnect(client, &disc_opts)) != MQTTASYNC_SUCCESS)
	{
		printf("Failed to start disconnect, return code %d\n", rc);
		rc = EXIT_FAILURE;
		goto destroy_exit;
	}
 	while (!disc_finished)
 	{
		#if defined(_WIN32)
			Sleep(100);
		#else
			usleep(10000L);
		#endif
 	}

destroy_exit:
	MQTTAsync_destroy(&client);
exit:
 	return rc;
}
