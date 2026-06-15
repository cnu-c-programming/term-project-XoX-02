CC     = gcc
CFLAGS = -Wall -Wextra -std=c11

# TODO: Add all your .c source files here (e.g., student.c file_io.c command.c)
SRCS   = main.c student.c file_io.c command.c

.PHONY: all admin client clean

all: admin client

admin:
	$(CC) $(CFLAGS) -DADMIN_MODE $(SRCS) -o admin_shell

client:
	$(CC) $(CFLAGS) -DCLIENT_MODE $(SRCS) -o client_shell

clean:
	rm -f admin_shell client_shell *.o
