#include "file_io.h"
#include <stdio.h>

void csv_load(char *fname, Student **head){
    FILE *fp = fopen(fname, "r");
    if(fp == NULL){
        printf("Error: not exist file\n");
        return;
    }
    char student[64];
    int id, score; char name[32];

    fgets(student, sizeof(student),fp);

    while(fgets(student,sizeof(student),fp) != NULL){
        int n = sscanf(student,"%d %[^,],%d", &id, name, &score);
        if(n == 3){
            add(head, id, name, score);
        }else{
            printf("Error: invaild format\n");
        }
    }
    fclose(fp);
    
}
void csv_save(char *fname, Student *head){
    FILE *fp = fopen(fname, "w");
    if(fp == NULL){
        printf("Error: not exist file\n");
        return;
    }
    
}