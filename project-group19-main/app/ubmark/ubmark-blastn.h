#ifndef UBMARK_BLASTN_H
#define UBMARK_BLASTN_H

#define A 0
#define C 1
#define G 2
#define T 3

#define KMER 3

#define QUERY_LEN 7
#define DATABASE_SIZE 11
#define THRESHOLD 20
#define POSSIZE 10


#define HASH_LEN 13

// size of node is 416 bytes
typedef struct node {
	int value[KMER+1]; // value[4] = '\0'
	int pos[10];
	struct node* next;
} Node;

typedef struct match_list {
	int value[KMER+1];
	int pos[10]; // position at database
	int pos_query; // position at query
	struct match_list * next;
}MatchList;

typedef struct extended_list {
	int start_data;
	int end_data;
	int start_query;
	int end_query;
	int alignment_score;
	struct extended_list * next;
}ExtendedList;

typedef Node* hash_table[HASH_LEN];

// function declarations
void init_hash_table(hash_table ht, int database_size);
int cal_hash_key(int * seq);
void make_hash_table(int* database, int* ht_pos, hash_table ht, int database_size);
MatchList* generate_match_list(int* query, hash_table ht, int* ht_pos, int query_size);
ExtendedList* generate_extended_list(MatchList* match_list, int* database, int* query_seq, int database_size, int query_size);

#endif /* UBMARK_BLASTN_H */