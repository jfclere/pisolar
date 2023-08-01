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

int main(int argc, char **argv){
    char *path_to_be_watched;

    if (argc != 2) {
        printf("Need directory name\n");
        exit(1);
    }
    path_to_be_watched = argv[1];

    int fd = inotify_init();
/*
    if (fcntl(fd, F_SETFL, O_NONBLOCK) < 0) {
        printf("fcntl failed: Could not watch : %s\n",path_to_be_watched);
        exit(1);
    }
 */
    int wd = inotify_add_watch(fd,path_to_be_watched,IN_MODIFY | IN_CREATE | IN_DELETE);
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
       struct inotify_event *event = (struct inotify_event *) buffer;
       if (event->len) {
           /*
           if (event->mask & IN_CREATE) {
               printf("file: %s created\n", event->name);
           } else if (event->mask & IN_DELETE) {
               printf("file: %s deleted\n", event->name);
           } else if (event->mask & IN_MODIFY) {
           */
           if (event->mask & IN_MODIFY) {
               if (!strcmp(event->name, "temp.txt")) {
                   /* The has changed let's tell the world */
                   struct info info;
                   char fullname[100];
                   strcpy(fullname, path_to_be_watched);
                   strcat(fullname, "/temp.txt");
                   int err = readtempfile(fullname, &info);
                   if (!err) {
                       time_t t = time(NULL);
                       printf("%d %f %f %f\n", t, info.temp, info.pres, info.humi);
                   }
               }
           }
       } else {
           printf("no event!!!\n");
           break; /* something fishy */
       }
    }
  
}
