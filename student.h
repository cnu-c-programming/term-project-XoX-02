#ifndef STUDENT_H
#define STUDENT_H
typedef struct Student Student;

void add (int id, char *name, int score);
void delete(int id);
void find (int id);
void stats ();

#endif

