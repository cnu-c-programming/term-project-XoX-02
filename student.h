#ifndef STUDENT_H
#define STUDENT_H
typedef struct Student{
    int id;
    char name[32];
    int score;
    struct Student* next;
} Student;

void add (Student** head, int id, char *name, int score);
void update(Student** head, int id, int score);
void delete(Student** head, int id);
Student* find (Student* head, int id);
void stats (Student* head);
void list(Student* head);
void free_all(Student** head);

#endif

