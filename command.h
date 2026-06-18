#ifndef COMMAND_H
#define COMMAND_H

extern char *p_fname;
extern Command commands[];

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


#endif