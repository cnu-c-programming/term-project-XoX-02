#ifndef FILE_IO_H
#define FILE_IO_H

#include "student.h"

void csv_load(char *fname, Student **head);
void csv_save(char *fname, Student *head);


#endif