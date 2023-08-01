#include<stdio.h>
#include<sys/inotify.h>
#include<unistd.h>
#include<stdlib.h>
#include<signal.h>
#include<fcntl.h>
#include<string.h>

int main(int argc, char **argv){
    char *path_to_be_watched;
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
           if (event->mask & IN_CREATE) {
               printf("file: %s created\n", event->name);
           } else if (event->mask & IN_DELETE) {
               printf("file: %s deleted\n", event->name);
           } else if (event->mask & IN_MODIFY) {
               printf("file: %s modified\n", event->name);
           }
       } else {
           printf("no event!!!\n");
           break; /* something fishy */
       }
    }
  
}
