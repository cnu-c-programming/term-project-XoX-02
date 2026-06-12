#include "student.h"
#include <string.h>

void add (Student** head, int id, char *name, int score){
    /*특히 중복된 ID가 입력된 경우 
    "duplicate" 또는 "Duplicate"가 포함된 에러 메시지를 출력, 
    점수 범위를 초과하는 등 잘못된 입력이 들어오면 
    "Error"를 포함한 메시지를 출력해야 합니다.*/
    Student *s = malloc(sizeof(Stduent));
    if (s == NULL) {
        printf("Error: Fail malloc\n");
        return;
    }
    s->id = id; strncpy(s->name,name,sizeof(s->name)); s->score = score; s->next = NULL;
    
    if(*head == NULL){
        *head = s;
        return;
    }else{
        Student *p = *head;
        while(p->next != NULL) { p = p -> next;}
        p->next = s;
    }
};
void update(Student** head, int id, int score){
    Student *p = *head;

    while(p != NULL && p->id != id) { p = p->next;}

    if(p == NULL){
        printf("Error: student not found.\n");
    }else{
        p->score = score;
    }
    
};
void delete(Student** head, int id){
    if (*head == NULL) {
        printf("Error: student not found.\n"); // 
        return;
    }
    Student *p = *head;

    if(p->id == id){
        *head = p->next;
        free(p);
        return;
    }

    while(p->next != NULL && p->next->id != id){
         p = p->next;
    }
   
    if(p->next == NULL){
        printf("Error: student not found.\n");
    }else{
        Student *t = p->next->next;
        free(p->next);
        p->next = t;
    }
};
void find (Student** head, int id);
void stats (Student** head);
void list(Student** head);
void free_all(Student** head);