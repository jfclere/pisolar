#include <stdio.h>
#include <sys/inotify.h>
#include <unistd.h>
#include <stdlib.h>
#include <signal.h>
#include <fcntl.h>
#include <string.h>
#include <time.h>

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
   if (!fptr)
       return 1;
   size_t size = 100;
   char *input = malloc(100);
   int ret = 0;
   while (fgets(input, size, fptr)>0) {
       if (strstr(input, "no2")) {
           info->no2 = readval(input);
           ret++;
       } else if (strstr(input, "alcohol")) {
           info->alcohol = readval(input);
           ret++;
       } else if (strstr(input, "voc")) {
           info->voc = readval(input);
           ret++;
       } if (strstr(input, "co")) {
           info->co = readval(input);
           ret++;
       }
   }
   fclose(fptr);
   free(input);
   if (ret == 4)
       return 0;
   return 1;
}

int main(int argc, char **argv){
    if (argc != 3) {
        printf("Need directory name and table name\n");
        exit(1);
    }
    char *path_to_be_watched = argv[1];
    char *table = argv[2];

    int fd = inotify_init();
/*
    if (fcntl(fd, F_SETFL, O_NONBLOCK) < 0) {
        printf("fcntl failed: Could not watch : %s\n",path_to_be_watched);
        exit(1);
    }
 */
    int wd = inotify_add_watch(fd,path_to_be_watched, IN_ALL_EVENTS);
    if (wd==-1){
        printf("inotify_add_watch failed: Could not watch : %s\n",path_to_be_watched);
        exit(1);
    }
    int size = strlen(path_to_be_watched) + 1 + sizeof(sizeof (struct inotify_event));
    size = 1024 * 2;
    char *buffer = malloc(size);
    while(1) {
       int ret = read(fd,buffer,size);
       if (ret < 0) {
           printf("read failed\n");
           break; /* something wrong */
       }
       int offset = 0;
       while (ret>0) {
           struct inotify_event *event = (struct inotify_event *) &buffer[offset];
           if (debug)
               printf("file: event length %d read: %d\n", event->len+sizeof(struct inotify_event), ret);
           if (event->len) {
               if (event->mask & IN_CREATE) {
                   if (debug)
                       printf("file: %s created\n", event->name);
               } else if (event->mask & IN_DELETE) {
                   if (debug)
                       printf("file: %s deleted\n", event->name);
               } else if (event->mask & IN_MODIFY || event->mask & IN_MOVE) {
                   if (debug)
                       printf("file: %s modified or moved\n", event->name);
                   if (!strcmp(event->name, "temp.txt")) {
                       /* The has changed let's tell the world */
                       struct info info;
                       char fullname[100];
                       strcpy(fullname, path_to_be_watched);
                       strcat(fullname, "/temp.txt");
                       int err = readtempfile(fullname, &info);
                       if (!err) {
                           time_t t = time(NULL);
                           if (debug)
                               printf("%d %f %f %f\n", t, info.temp, info.pres, info.humi);
                           inserttemp(table, t, info.temp, info.pres, info.humi);
                       }
                   }
                   if (!strcmp(event->name, "gas.txt")) {
                       /* The has changed let's tell the world */
                       struct gasinfo info;
                       char fullname[100];
                       strcpy(fullname, path_to_be_watched);
                       strcat(fullname, "/gas.txt");
                       int err = readgasfile(fullname, &info);
                       if (!err) {
                           time_t t = time(NULL);
                           if (debug)
                               printf("%d %f %f %f\n", t, info.no2, info.alcohol, info.voc, info.co);
                           insertgas(table, t, info.no2, info.alcohol, info.voc, info.co);
                       }
                   }
               } else {
                   if (debug)
                       printf("file: event %d on %s\n", event->mask, event->name);
               }
           } else {
               if (debug)
                   printf("event %d len zero!!!\n", event->mask);
           }
           /* there might be several events in the buffer */
           offset = offset + event->len+sizeof(struct inotify_event);
           ret = ret - (event->len+sizeof(struct inotify_event));
           if (debug)
               printf("file: event offset %d remaining %d\n", offset , ret);
        }
    }
  
}
