#include "ubmark-blastn-helper.h"
#include "ece6745.h"

int mod(int a, int b) {
    while (a >= b) {
        a -= b;
    }
    return a;
}

int match_list_length(MatchList* match_list) {
    int length = 0;
    while (match_list != NULL) {
      length++;
      match_list = match_list->next;
    }
    return length;
  }
  
  int compress_block_from_int(const int* input, int count) {
    int result = 0;
    for (int i = 0; i < count; i++) {
      result |= (input[i] & 0x3) << (2 * (count - 1 - i));
    }
    return result;
  }
  
  int* compress_int_array(const int* input, int length) {
    int block_size = 16;
    int compress_length = (length + block_size - 1) / block_size;
    int* compressed = (int*)ece6745_malloc(compress_length * (int)sizeof(int));
  
    for (int i = 0; i < compress_length; i++) {
      int count = (i == compress_length - 1) ? (length - i * block_size) : block_size;
      compressed[i] = compress_block_from_int(input + i * block_size, count);
    }
    return compressed;
  }
  
  // return length
  int convert_linkedlist_to_array(MatchList* match_list, int** query_pos, 
    int** database_pos, int** extend_size, int** extend_score) {
    int length = match_list_length(match_list);
    *extend_size = (int*)ece6745_malloc(length * (int)sizeof(int));
    *query_pos = (int*)ece6745_malloc(length * (int)sizeof(int));
    *database_pos = (int*)ece6745_malloc(length * (int)sizeof(int));
    *extend_score = (int*)ece6745_malloc(length * (int)sizeof(int));
    // convert the linked list to array
    for (int i = 0; i < length; i++)
    {
      (*extend_size)[i] = 0;
      (*query_pos)[i] = 0;
      (*database_pos)[i] = 0;
      (*extend_score)[i] = 0;
    }
    int n = 0;
    for (MatchList* current = match_list; current != NULL; current = current->next) {
      (*query_pos)[n] = current->pos_query;;
      (*database_pos)[n] = current->pos[0];
      (*extend_size)[n] = KMER;
      (*extend_score)[n] = KMER + 20;
      // ece6745_wprintf(L"query_pos: %d, database_pos: %d\n", 
      //   (*query_pos)[n],  (*database_pos)[n]);
      n++;
    }
    return length;
  }


void convert_result_array(ExtendedList* result, int* query_start_t, 
                          int* base_start_t, int* len_t, int*score_t) {
  int n = 0;
  while (result != NULL) {
    query_start_t[n] = result->start_query;
    base_start_t[n] = result->start_data;
    len_t[n] = result->end_query - result->start_query + 1;
    score_t[n] = result->alignment_score;
    result = result->next;
    n++;
  }
}

void convert_result_array_xcel(ExtendedList* result, int** query_start_t, 
                          int** base_start_t, int** len_t, int* *score_t) {
  int n = 0;
  while (result != NULL) {
    (*query_start_t)[n] = result->start_query;
    (*base_start_t)[n] = result->start_data;
    (*len_t)[n] = result->end_query - result->start_query + 1;
    (*score_t)[n] = result->alignment_score;
    result = result->next;
    n++;
  }
}

void free_match_list(MatchList* match_list) {
  while (match_list != NULL) {
    MatchList* temp = match_list;
    match_list = match_list->next;
    ece6745_free(temp);
  }
}
void free_extended_list(ExtendedList* extended_list) {
  while (extended_list != NULL) {
    ExtendedList* temp = extended_list;
    extended_list = extended_list->next;
    ece6745_free(temp);
  }
}
void free_hash_table(hash_table ht) {
  for (int i = 0; i < HASH_LEN; ++i) {
    Node* current = ht[i];
    while (current != NULL) {
      Node* temp = current;
      current = current->next;
      ece6745_free(temp);
    }
  }
}