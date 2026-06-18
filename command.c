#include "command.h"
#include "file_io.h"
#include "student.h"
#include <stdio.h>
#include <string.h>
#ifdef ADMIN_MODE
Command commands[] = {
 {"save", handle_save, "save", "Save students to CSV"},
 {"reload", handle_reload, "reload", "Reload students from CSV"},
 {"add", handle_add, "add <id> <name> <score>", "Add a student"},
 {"delete", handle_delete, "delete <id>", "Delete a student"},
 {"update", handle_update, "update <id> <score>", "Update student score"},
 {"find", handle_find, "find <id>", "Find student"},
 {"list", handle_list, "list", "List students"},
 {"stats", handle_stats, "stats", "Show statistics"},
 {"help", handle_help, "help", "Show help"},
 {"clear", handle_clear, "clear", "Clear screen"},
 {"exit", handle_exit, "exit", "Exit shell"},
 {NULL,NULL,NULL,NULL}
};
#endif
#ifdef CLIENT_MODE
Command commands[] = {
 {"reload", handle_reload, "reload", "Reload students from CSV"},
 {"find", handle_find, "find <id>", "Find student"},
 {"list", handle_list, "list", "List students"},
 {"stats", handle_stats, "stats", "Show statistics"},
 {"help", handle_help, "help", "Show help"},
 {"clear", handle_clear, "clear", "Clear screen"},
 {"exit", handle_exit, "exit", "Exit shell"},
 {NULL,NULL,NULL,NULL}
};
#endif

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
        return SHELL_ERR_MISSING_ARGUMENT;
    }
    if(id <= 0 || (score < 0 || score > 100)){
        return SHELL_ERR_INVALID_ARGUMENT;
    }
    Student *s = find(*head,id);
    if(s != NULL){
        return SHELL_ERR_DUPLICATE_STUDENT;
    }
    add(head,id,name,score);
    printf("Student added.\n");
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
        return SHELL_ERR_INVALID_SCORE;
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
ShellResult handle_help(char* args, Student** head){
    printf("Commands:\n");
    for(int i = 0; i < sizeof(commands)/sizeof(Command); i++){
         printf("%-20s%-20s\n",commands[i].usage,commands[i].description);
    }
    return SHELL_OK;
}
ShellResult handle_clear(char* args, Student** head){
    printf("\033[2J\033[H");
    return SHELL_OK;
}
ShellResult handle_exit(char* args, Student** head){
    free_all(head);
    printf("Goodbye.");
    return SHELL_EXIT;
}