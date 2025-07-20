#ifndef UBMARK_BLASTN_HELPER_H
#define UBMARK_BLASTN_HELPER_H
#include "ubmark-blastn.h"
#include "stdio.h"

int mod(int a, int b);
int match_list_length(MatchList* match_list);
int compress_block_from_int(const int* input, int count);
int* compress_int_array(const int* input, int length);
int convert_linkedlist_to_array(MatchList* match_list, int** query_pos, int** database_pos, int** extend_size, int** extend_score);
void convert_result_array(ExtendedList* result, int* query_start_t, int* base_start_t, int* len_t, int*score_t);
void convert_result_array_xcel(ExtendedList* result, int** query_start_t, int** base_start_t, int** len_t, int** score_t);
void free_match_list(MatchList* match_list);
void free_extended_list(ExtendedList* extended_list);
void free_hash_table(hash_table ht);
#endif/* UBMARK_BLASTN_HELPER_H */