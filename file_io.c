#include <stdio.h>
#include "file_io.h"

int csv_load(char *fname, Student **head){
    FILE *fp = fopen(fname, "r");
    if(fp == NULL){
        printf("Error: not exist file\n");
        return -1;
    }
    char student[64];
    int id, score; char name[32];
    int count = 0;
    fgets(student, sizeof(student),fp);

    while(fgets(student,sizeof(student),fp) != NULL){
        int n = sscanf(student,"%d, %[^,],%d", &id, name, &score);
        if(n == 3){
            count++;
            add(head, id, name, score);
        }else{
            printf("Error: invaild format\n");
        }
    }
    fclose(fp);
    return count;
}

int csv_save(char *fname, Student *head){
    FILE *fp = fopen(fname, "w");
    if(fp == NULL){
        printf("Error: not exist file\n");
        return -1;
    }
    int count = 0;
    fprintf(fp,"id,name,score\n");
    while(head != NULL){
        count ++;
        fprintf(fp,"%d,%s,%d\n", head->id, head->name, head->score);
        head = head->next;
    }
    fclose(fp);
    return count;
    
}