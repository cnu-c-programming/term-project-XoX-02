#include "command.h"
#include "file_io.h"
#include "student.h"

char *p_fname;

ShellResult handle_save(char* args, Student** head){
    int student_count = csv_save(p_fname,*head);
    if(student_count == -1){
        return SHELL_ERR_FILE_OPEN;
    }else{
        printf("Saved %d students to %s.\n", student_count, p_fname);
        return SHELL_OK;
    }
}
ShellResult handle_reload(char* args, Student** head){
    free_all(head);
    *head = NULL;
    int student_count = csv_load(p_fname,head);
    if(student_count == -1){
        return SHELL_ERR_FILE_OPEN;
    }else{
        printf("Reloaded %d students from %s.\n", student_count, p_fname);
        return SHELL_OK;
    }
}
ShellResult handle_add(char* args, Student** head);
ShellResult handle_delete(char* args, Student** head);
ShellResult handle_update(char* args, Student** head);
ShellResult handle_find(char* args, Student** head);
ShellResult handle_list(char* args, Student** head);
ShellResult handle_stats(char* args, Student** head);
ShellResult handle_help(char* args, Student** head);
ShellResult handle_clear(char* args, Student** head);
ShellResult handle_exit(char* args, Student** head);