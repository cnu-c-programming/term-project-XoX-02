#include "student.h"
#ifndef FILE_IO_H
#define FILE_IO_H
int csv_load(char *fname, Student **head);
int csv_save(char *fname, Student *head);


#endif