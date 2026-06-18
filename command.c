#include "command.h"
#include "file_io.h"
#include "student.h"
#include <stdio.h>

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
ShellResult handle_add(char* args, Student** head){
    int id;
    char name[32];
    int score;
    int arg_num = sscanf(args,"%d %s %d", &id, name, &score);

    if(arg_num < 3){
        printf("Error: Format incorect\n");
        return SHELL_ERR_MISSING_ARGUMENT;
    }
    if(id <= 0 || (score < 0 || score > 100)){
        return SHELL_ERR_INVALID_ARGUMENT;
    }
    Student *s = find(*head,id);
    if(s != NULL){
        printf("Error: Duplicate id\n");
        return SHELL_ERR_DUPLICATE_STUDENT;
    }
    add(head,id,name,score);
    return SHELL_OK;

}
ShellResult handle_delete(char* args, Student** head){
    int id;
    int arg_num = sscanf(args,"%d",&id);
    if(arg_num < 1){
        return SHELL_ERR_MISSING_ARGUMENT;
    }
    Student *s = find(*head, id);
    if(s == NULL){
        printf("Error: student not found.\n"); 
        return SHELL_ERR_STUDENT_NOT_FOUND;
    }
    delete(head,id);
    return SHELL_OK;
}
ShellResult handle_update(char* args, Student** head){
    int id;
    int score;
    int arg_num = sscanf(args,"%d %d", &id, &score);
    if(arg_num < 2){
        return SHELL_ERR_MISSING_ARGUMENT;
    }
    if(score < 0 || score > 100){
        return SHELL_ERR_INVALID_ARGUMENT;
    }
    Student *s = find(*head,id);
    if(s == NULL){
        return SHELL_ERR_STUDENT_NOT_FOUND;
    }else {
        s -> score = score;
        return SHELL_OK;
    }
}
ShellResult handle_find(char* args, Student** head){
    int id;
    int arg_num = sscanf(args,"%d", &id);
    if(arg_num < 1){
        return SHELL_ERR_MISSING_ARGUMENT;
    }
    Student *s = find(*head,id);
    if(s == NULL){
        return SHELL_ERR_STUDENT_NOT_FOUND;
    }else{
        printf("ID: %d\nName: %s\nScore: %d\n",s->id,s->name,s->score);
        return SHELL_OK;
    }
}
ShellResult handle_list(char* args, Student** head){
    list(*head);
    return SHELL_OK;
}
ShellResult handle_stats(char* args, Student** head){
    stats(*head);
    return SHELL_OK;
}
ShellResult handle_help(char* args, Student** head);
ShellResult handle_clear(char* args, Student** head);
ShellResult handle_exit(char* args, Student** head);