#ifndef COMMAND_H
#define COMMAND_H

extern char *p_fname;

typedef enum {
    SHELL_OK = 0,
    SHELL_EXIT,
    SHELL_ERR_UNKNOWN_COMMAND,
    SHELL_ERR_INVALID_ARGUMENT,
    SHELL_ERR_MISSING_ARGUMENT,
    SHELL_ERR_FILE_OPEN,
    SHELL_ERR_FILE_WRITE,
    SHELL_ERR_STUDENT_NOT_FOUND,
    SHELL_ERR_DUPLICATE_STUDENT,
    SHELL_ERR_INVALID_SCORE
} ShellResult;

typedef ShellResult (*CommandHandler)(char* args, Student **head);

typedef struct{
    const char* name;
    CommandHandler handler;
    const char* usage;
    const char* description;
}Command;

ShellResult handle_save(char* args, Student** head);
ShellResult handle_reload(char* args, Student** head);
ShellResult handle_add(char* args, Student** head);
ShellResult handle_delete(char* args, Student** head);
ShellResult handle_update(char* args, Student** head);
ShellResult handle_find(char* args, Student** head);
ShellResult handle_list(char* args, Student** head);
ShellResult handle_stats(char* args, Student** head);
ShellResult handle_help(char* args, Student** head);
ShellResult handle_clear(char* args, Student** head);
ShellResult handle_exit(char* args, Student** head);

#endif