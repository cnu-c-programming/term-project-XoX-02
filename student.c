struct Student
{
    int id;
    char name[32];
    int score;
    struct Student* next;
};

void add (int id, char *name, int score);
void delete(int id);
void find (int id);
void stats ();