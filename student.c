#include <string.h>
#include "student.h"

void add (Student** head, int id, char *name, int score){
    Student *s = malloc(sizeof(Student));
    if (s == NULL) {
        printf("Error: Fail malloc\n");
        return ;
    }
    s->id = id; strncpy(s->name,name,sizeof(s->name)); s->score = score; s->next = NULL;
    
    if(*head == NULL){
        *head = s;
        return ;
    }else{
        Student *p = *head;
        while(p->next != NULL) { p = p -> next;}
        p->next = s;
    }
}
void update(Student** head, int id, int score){
    Student *p = *head;

    while(p != NULL && p->id != id) { p = p->next;}

    if(p == NULL){
        printf("Error: student not found.\n");
    }else{
        p->score = score;
    }
    
}
void delete(Student** head, int id){
    if (*head == NULL) return;
    Student *p = *head;

    if(p->id == id){
        *head = p->next;
        free(p);
        return;
    }

    while(p->next != NULL && p->next->id != id){
         p = p->next;
    }
    
    if(p->nest != NULL){
        Student *t = p->next->next;
        free(p->next);
        p->next = t;
    }
}
Student* find (Student* head, int id){
    Student *p = head;
    while(p != NULL && p->id != id) { p = p->next;}
    return p;
}
void stats (Student* head){
    if(head == NULL){ 
        printf("No student data available\n");
        return;
    }
    int count = 0;
    int Sum = 0;
    int Max = 0;
    int Min = 100;
    while(head != NULL){
        count ++;
        Sum += head->score;
        if(head->score > Max){ Max = head->score;}
        if(head->score < Min){ Min = head->score;}
        head = head->next;
    }
    printf("Count: %d\n",count);
    printf("Average: %f\n", (float)Sum/count);
    printf("Max: %d\n",Max);
    printf("Min: %d\n",Min);
}
void list(Student* head){
    if(head == NULL){
        printf("No students found.\n");
        return;
    }

    printf("%-5s %-10s %-5s\n","ID","Name","Score");
    while(head != NULL){
        printf("%-5d %-10s %-5d\n",head->id,head->name,head->score);
        head = head->next;
    }
}
void free_all(Student** head){
    Student *p = *head;
    while(p != NULL){
        Student *t = p;
        p = p->next;
        free(t);
    }
    *head = NULL;
}