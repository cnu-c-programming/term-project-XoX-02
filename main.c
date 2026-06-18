/*
 * main.c  –  Mini Student Shell
 *
 * TODO: Implement admin_shell and client_shell.
 *
 * Build:
 *   make admin   →  admin_shell  (compiled with -DADMIN_MODE)
 *   make client  →  client_shell (compiled with -DCLIENT_MODE)
 *
 * Usage:
 *   ./admin_shell [students.csv]
 *   ./admin_shell -f commands.txt [students.csv]
 *   ./client_shell [students.csv]
 *   ./client_shell -f commands.txt [students.csv]
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "student.h"
#include "command.h"
#include "file_io.h"

char *p_fname = NULL;

/* TODO: Add your own header includes here */
/* #include "student.h"  */
/* #include "file_io.h"  */
/* #include "command.h"  */

/* ---------------------------------------------------------------
 * TODO: Implement the interactive shell loop.
 *   - Print a prompt and read a line from stdin.
 *   - Parse the line into a command and arguments.
 *   - Dispatch to the appropriate handler function.
 *   - Loop until the user types "exit" or EOF.
 * --------------------------------------------------------------- */
void run_shell(const char *csv_path) {
    #ifdef ADMIN_MODE
        printf("[Admin Program]\n");
    #elif defined CLIENT_MODE
        printf("[Client Program]\n");
    #endif
    Student *head = NULL;
    char input[64];
    char cmd[32];
    p_fname = (char*)csv_path;
    for(int i = 0; commands[i].name != NULL; i++){
            if(strcmp("reload",commands[i].name) == 0){
                commands[i].handler(" ",&head);
                break;
            }
        }
    while(1){
        #ifdef ADMIN_MODE
        printf("Admin > ");
        #elif defined CLIENT_MODE
        printf("Client > ");
        #endif
        ShellResult result = SHELL_ERR_UNKNOWN_COMMAND;
        char *p = fgets(input, sizeof(input), stdin);
        if(p == NULL){
            printf("\n");
            break;
        }
        input[strcspn(input,"\n")] = '\0';
        if(strlen(input) == 0) continue;

        int cmd_num = sscanf(input, "%s", cmd);
        if(cmd_num != 1) continue;

        char *args = input + strlen(cmd);
        while(*args == ' ' || *args == '\t'){
            args++;
        }
        
        for(int i = 0; commands[i].name != NULL; i++){
            if(strcmp(cmd,commands[i].name) == 0){
                result = commands[i].handler(args,&head);
                break;
            }
        }
        
        switch (result)
        {
        case SHELL_ERR_UNKNOWN_COMMAND:
            printf("Error: Unknown command.\n");
            break;
        case SHELL_ERR_INVALID_ARGUMENT:
            printf("Error: Invaild argument.\n");
            break;
        case SHELL_ERR_MISSING_ARGUMENT:
            printf("Error: Format incorrect.\n");
            break;
        case SHELL_ERR_FILE_OPEN:
            printf("Error: File not exist.\n");
            break;
        case SHELL_ERR_FILE_WRITE:
            printf("Error: File write error.\n");
            break;
        case SHELL_ERR_STUDENT_NOT_FOUND:
            printf("Error: student not found.\n"); 
            break;
        case SHELL_ERR_DUPLICATE_STUDENT:
            printf("Error: Duplicate id\n");
            break;
        case SHELL_ERR_INVALID_SCORE:
            printf("Error: Invalid score.\n");
            break;
        default:
            break;
        }

        if(result == SHELL_EXIT){
            break;
        }

    }
    free_all(&head);
}

/* ---------------------------------------------------------------
 * TODO: Implement batch mode – read commands from a file.
 *   - Open cmd_file for reading.
 *   - Execute each line as a command (same logic as run_shell).
 *   - Close the file when done.
 * --------------------------------------------------------------- */
void run_command_file(const char *cmd_file, const char *csv_path) {
    #ifdef ADMIN_MODE
        printf("[Admin Program]\n");
    #elif defined CLIENT_MODE
        printf("[Client Program]\n");
    #endif
    int line_num = 0;
    Student *head = NULL;
    char input[64];
    char cmd[32];
    p_fname = (char*)csv_path;
    FILE *fp = fopen(cmd_file, "r");
    if(fp == NULL){
        printf("Error: not exist file\n");
        return;
    }
    for(int i = 0; commands[i].name != NULL; i++){
            if(strcmp("reload",commands[i].name) == 0){
                commands[i].handler(" ",&head);
                break;
            }
    }
    while(fgets(input,sizeof(input),fp)){
        ShellResult result = SHELL_ERR_UNKNOWN_COMMAND;
        line_num ++;
        printf("[command file:%d] %s",line_num, input);
        
        input[strcspn(input,"\n")] = '\0';
        if(strlen(input) == 0) continue;

        int cmd_num = sscanf(input, "%s", cmd);
        if(cmd_num != 1) continue;

        char *args = input + strlen(cmd);
        while(*args == ' ' || *args == '\t'){
            args++;
        }
        
        for(int i = 0; commands[i].name != NULL; i++){
            if(strcmp(cmd,commands[i].name) == 0){
                result = commands[i].handler(args,&head);
                break;
            }
        }
        
        switch (result)
        {
        case SHELL_ERR_UNKNOWN_COMMAND:
            printf("Error: Unknown command. Skipped line %d\n", line_num);
            break;
        case SHELL_ERR_INVALID_ARGUMENT:
            printf("Error: Invaild argument. Skipped line %d\n", line_num);
            break;
        case SHELL_ERR_MISSING_ARGUMENT:
            printf("Error: Format incorrect. Skipped line %d\n", line_num);
            break;
        case SHELL_ERR_FILE_OPEN:
            printf("Error: File not exist. Skipped line %d\n", line_num);
            break;
        case SHELL_ERR_FILE_WRITE:
            printf("Error: File write error. Skipped line %d\n", line_num);
            break;
        case SHELL_ERR_STUDENT_NOT_FOUND:
            printf("Error: student not found. Skipped line %d\n", line_num); 
            break;
        case SHELL_ERR_DUPLICATE_STUDENT:
            printf("Error: Duplicate id. Skipped line %d\n", line_num);
            break;
        case SHELL_ERR_INVALID_SCORE:
            printf("Error: Invalid score. Skipped line %d\n", line_num);
            break;
        default:
            break;
        }

        if(result == SHELL_EXIT){
            break;
        }
    }
    free_all(&head);
    fclose(fp);
}

/* TODO: Parse command-line arguments.
     *   Supported flags:
     *     -f <file>   run commands from <file> instead of stdin
     *   Remaining positional argument (if any): path to students CSV.
     *
     *   Example parsing skeleton:
     *
     *   for (int i = 1; i < argc; i++) {
     *       if (strcmp(argv[i], "-f") == 0 && i + 1 < argc) {
     *           cmd_file = argv[++i];
     *       } else {
     *           csv_path = argv[i];
     *       }
     *   }
     */
int main(int argc, char *argv[]) {
    const char *csv_path  = NULL; /* default CSV file */
    const char *cmd_file  = NULL;           /* -f <file> argument */

    for (int i = 1; i < argc; i++) {        
        if (strcmp(argv[i], "-f") == 0 && i + 1 < argc) {
            cmd_file = argv[++i];
        } else {
            csv_path = argv[i];
            }
        }
    if(csv_path == NULL){
        #ifdef ADMIN_MODE
        printf("Usage: ./admin_shell <csv_file> [-f command_file]\n");
        #elif defined(CLIENT_MODE)
        printf("Usage: ./client_shell <csv_file> [-f command_file]\n");
        #endif
        return 0;
    }

#ifdef ADMIN_MODE
    /* Admin shell: supports add, delete, update, save, load, sort, list, find, help, exit */
    if (cmd_file) {
        run_command_file(cmd_file, csv_path);
    } else {
        run_shell(csv_path);
    }

#elif defined(CLIENT_MODE)
    /* Client shell: supports find, list, help, exit  (read-only) */
    if (cmd_file) {
        run_command_file(cmd_file, csv_path);
    } else {
        run_shell(csv_path);
    }

#else
#error "Define either -DADMIN_MODE or -DCLIENT_MODE when compiling."
#endif

    return 0;
}
