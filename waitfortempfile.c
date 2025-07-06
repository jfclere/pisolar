#include <stdio.h>
#include <sys/inotify.h>
#include <unistd.h>
#include <stdlib.h>
#include <signal.h>
#include <fcntl.h>
#include <string.h>
#include <time.h>
#include <zlib.h>

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
   float batt;
};
struct gasinfo {
   float no2;
   float alcohol;
   float voc;
   float co;
};
struct watinfo {
   float bat;
   float hyd;
   float sol;
   float wat;
};
struct powinfo {
   float f1;
   float f2;
   float f3;
};

int debug = 0;

void inserttemp(char *table, time_t t, float temp, float pres, float humi, float batt);
void insertgas(char *table, time_t t, float no2, float alcohol, float voc, float co);
void insertwat(char *table, time_t t, float bat, float hyd, float sol, float wat);
void insertpow(char *table, time_t t, float f1, float f2, float f3);

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
/* read the Temperature, Pressure and Humidity from the dongle*.txt files */
/* format is something like: "0 25.75 963.04 55.37 36.00" */
static int readtempdongle(char *filename, struct info *info) {
   FILE *fptr = fopen(filename, "r");
   if (!fptr)
       return 1;
   int time = 0;
   if (fscanf(fptr, "%d %f %f %f %f\n", &time, &info->temp, &info->pres, &info->humi, &info->batt) != 5) {
     fclose(fptr);
     return 1;
   }
   fclose(fptr);
   return 0;
}
/* read gaz values from the multi channel gaz sensor */
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
static int readwatfile(char *filename, struct watinfo *info) {
   FILE *fptr = fopen(filename, "r");
   if (!fptr) {
       if (debug)
           printf("readwatfile: open %s failed\n", filename);
       return 1;
   }
   size_t size = 100;
   char *input = malloc(100);
   int ret = 0;
   info->wat = 0.00;
   while (fgets(input, size, fptr)>0) {
       if (strstr(input, "Bat")) {
           info->bat = readval(input);
           ret++;
           if (debug)
               printf("readwatfile: got Bat\n");
       } else if (strstr(input, "Hyd")) {
           info->hyd = readval(input);
           ret++;
           if (debug)
               printf("readwatfile: got Hyd\n");
       } else if (strstr(input, "Sol")) {
           info->sol = readval(input);
           ret++;
           if (debug)
               printf("readwatfile: got Sol\n");
       } if (strstr(input, "Wat")) {
           info->wat = readval(input);
           ret++;
           printf("readwatfile: got Wat\n");
       }
   }
   fclose(fptr);
   free(input);
   if (ret == 3)
       if (info->wat == 0.00)
           ret++;
   if (ret == 4)
       return 0;
   return 1;
}
static int readpowfile(char *filename, struct powinfo *info) {
   FILE *fptr = fopen(filename, "r");
   if (!fptr) {
       if (debug)
           printf("readwatfile: open %s failed\n", filename);
       return 1;
   }
   size_t size = 100;
   char *input = malloc(100);
   int ret = 0;
   while (fgets(input, size, fptr)>0) {
       if (strstr(input, "Current")) {
           info->f1 = readval(input);
           ret++;
           if (debug)
               printf("readwatfile: got Current\n");
       } else if (strstr(input, "Voltage")) {
           info->f2 = readval(input);
           ret++;
           if (debug)
               printf("readwatfile: got Voltage\n");
       } else if (strstr(input, "Power")) {
           info->f3 = readval(input);
           ret++;
           if (debug)
               printf("readwatfile: got Power\n");
       }
   }
   fclose(fptr);
   free(input);
   if (ret == 3)
       return 0;
   return 1;
}

int main(int argc, char **argv){
    if (argc != 3) {
        printf("Need directory name and table name\n");
        exit(1);
    }
    if (getenv("DEBUG")) {
        debug = 1;
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
    int checksum = 0;
    while(1) {
       int ret = read(fd,buffer,size);
       if (ret < 0) {
           printf("read failed\n");
           break; /* something wrong */
       }
       if (debug)
           printf("read: %d with events\n", ret);
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
                       /* If the fle has changed let's tell the world */
                       struct info info;
                       char fullname[100];
                       strcpy(fullname, path_to_be_watched);
                       strcat(fullname, "/temp.txt");
                       int err = readtempfile(fullname, &info);
                       if (!err) {
                           time_t t = time(NULL);
                           if (debug)
                               printf("%d %f %f %f\n", t, info.temp, info.pres, info.humi);
                           int sum = getsumfile(fullname);
                           if (sum != checksum) {
                               inserttemp(table, t, info.temp, info.pres, info.humi, 0.0);
                               checksum = sum;
                           }
                       } else {
                           if (debug)
                               printf("file: %s ERROR reading %d\n", event->name, err);
                       }
                   }
                   if (!strncmp(event->name, "dongle", 6)) {
                       /* If the dongle*.txt file has changed let's tell the world */ 
                       struct info info;
                       char fullname[100];
                       strcpy(fullname, path_to_be_watched);
                       strcat(fullname, event->name);
                       int err = readtempdongle(fullname, &info);
                       if (!err) {
                           time_t t = time(NULL);
                           if (debug)
                               printf("%d %f %f %f %f\n", t, info.temp, info.pres, info.humi, info.batt);
                           int sum = getsumfile(fullname);
                           if (sum != checksum) {
                               inserttemp(table, t, info.temp, info.pres, info.humi, info.batt);
                               checksum = sum;
                           }
                       } else {
                           if (debug)
                               printf("file: %s ERROR reading %d\n", event->name, err);
                       }
                   }
                   if (!strcmp(event->name, "gas.txt")) {
                       /* If the fle has changed let's tell the world */
                       struct gasinfo info;
                       char fullname[100];
                       strcpy(fullname, path_to_be_watched);
                       strcat(fullname, "/gas.txt");
                       int err = readgasfile(fullname, &info);
                       if (!err) {
                           time_t t = time(NULL);
                           if (debug)
                               printf("%d %f %f %f %f\n", t, info.no2, info.alcohol, info.voc, info.co);
                           int sum = getsumfile(fullname);
                           if (sum != checksum) {
                               insertgas(table, t, info.no2, info.alcohol, info.voc, info.co);
                               checksum = sum;
                           }
                       } else {
                           if (debug)
                               printf("file: %s ERROR reading %d\n", event->name, err);
                       }
                   }
                   if (!strcmp(event->name, "value.txt")) {
                       /* If the fle has changed let's tell the world */
                       struct watinfo info;
                       char fullname[100];
                       strcpy(fullname, path_to_be_watched);
                       strcat(fullname, "/value.txt");
                       int err = readwatfile(fullname, &info);
                       if (!err) {
                           time_t t = time(NULL);
                           if (debug)
                               printf("%d %f %f %f %f\n", t, info.bat, info.hyd, info.sol, info.wat);
                           int sum = getsumfile(fullname);
                           if (sum != checksum) {
                               insertwat(table, t, info.bat, info.hyd, info.sol, info.wat);
                               checksum = sum;
                           }
                       } else {
                           if (debug)
                               printf("file: %s ERROR reading %d\n", event->name, err);
                       }
                   }
                   if (!strcmp(event->name, "current.txt")) {
                       /* If the fle has changed let's tell the world */
                       struct powinfo info;
                       char fullname[100];
                       strcpy(fullname, path_to_be_watched);
                       strcat(fullname, "/current.txt");
                       int err = readpowfile(fullname, &info);
                       if (!err) {
                           time_t t = time(NULL);
                           if (debug)
                               printf("%d %f %f %f %f\n", t, info.f1, info.f2, info.f3);
                           int sum = getsumfile(fullname);
                           if (sum != checksum) {
                               insertpow(table, t, info.f1, info.f2, info.f3);
                               checksum = sum;
                           }
                       } else {
                           if (debug)
                               printf("file: %s ERROR reading %d\n", event->name, err);
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
