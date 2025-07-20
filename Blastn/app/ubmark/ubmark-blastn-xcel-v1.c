//========================================================================
// ubmark-blastn
//========================================================================

#include "stddef.h"
#include "ece6745.h"
#include "ubmark-blastn-helper.h"
#include "ubmark-blastn.h"
#ifdef _RISCV

void reverse_array(int* arr, int length) {
  for (int i = 0; i < length / 2; ++i) {
    int temp = arr[i];
    arr[i] = arr[length - 1 - i];
    arr[length - 1 - i] = temp;
  }
  return;
}

void remove_three_elements(int* src, int n, int* dst) {
  int i, j = 0;
  for (i = 0; i < 19; ++i) {
      if (i < n || i >= n + 3) {
          dst[j++] = src[i];
      }
  }
}

void extend_xcel_v1(int* query_pos, int* database_pos, int* extend_size,
                      int* extend_score, int length, int *compressed_db, int *compressed_query) 
{
  int new_query_pos = 0;
  int new_database_pos = 0;
  ece6745_wprintf(L"extend_xcel_v1: %d\n", length);
  int rev_db[16];
  int rev_q[16];
  // traverse all seeds
  for (int i = 0; i < length; i++) {
    query_pos[i] = query_pos[i] == 0?1:query_pos[i];
    query_pos[i] = query_pos[i] == 16?15:query_pos[i];
    database_pos[i] = database_pos[i] == 0?1:database_pos[i];
    database_pos[i] = database_pos[i] == 16?15:database_pos[i];
    remove_three_elements(compressed_db, database_pos[i], rev_db);
    remove_three_elements(compressed_query, query_pos[i], rev_q);
    reverse_array(rev_db, 16);
    reverse_array(rev_q, 16);
    int * rev_db_cp = compress_int_array(rev_db, 16);
    int * rev_q_cp = compress_int_array(rev_q, 16);
    ece6745_stats_on();
    __asm__ (
      "csrw 0x7e1, %[q_seq];\n"
      "csrw 0x7e2, %[db_seq];\n"
      "csrw 0x7e3, %[q_start];\n"
      "csrw 0x7e4, %[db_start];\n"
      "csrw 0x7e0, x0;\n"
      "csrr %[score], 0x7e1;\n"
      "csrr %[size],  0x7e2;\n"
      "csrr %[new_query_pos],0x7e3;\n"
      "csrr %[new_database_pos], 0x7e4;\n"
      "csrr x0, 0x7e0;\n"
  
      // Outputs from the inline assembly block
      : [score]    "=r"((extend_score[i])),
        [size]     "=r"((extend_size[i])),
        [new_query_pos]  "=r"((new_query_pos)),
        [new_database_pos] "=r"((new_database_pos))
  
      // Inputs to the inline assembly block
  
      : [q_seq]    "r"((rev_q_cp[0])),
        [db_seq]    "r"((rev_db_cp[0])),
        [q_start]    "r"((query_pos[i])),
        [db_start]    "r"((database_pos[i]))
        
      // Tell the compiler this accelerator read/writes memory
  
      : "memory"
    );
    ece6745_stats_off();
    query_pos[i] = new_query_pos;
    database_pos[i] = new_database_pos;
    extend_score[i] = extend_score[i] + 3;
    extend_size[i] = extend_size[i] + 3;
  }
  // ece6745_wprintf(L"finished\n");
  return;
}

#else
void extend_xcel_v1(int* query_pos, int* database_pos, int* extend_size,
  int* extend_score, int length, int *compressed_db, int *compressed_query) 
{
  int database_size = 19;
  int query_size = 19;
  hash_table ht;
  int ht_pos[HASH_LEN] = {0};
  int *query_start_t = NULL;
  int *database_start_t = NULL;
  int *len_t = NULL;
  int *score_t = NULL;
  // run base test
  // init hash table and generate linked list extend result
  init_hash_table(ht, database_size);
  make_hash_table(compressed_db, ht_pos, ht, database_size);
  MatchList* result = generate_match_list(compressed_query, ht, ht_pos, query_size);
  convert_linkedlist_to_array(result, &query_start_t, 
    &database_start_t, &len_t, &score_t);
  ExtendedList* result_extend =
   generate_extended_list(result, compressed_db, 
    compressed_query, database_size, query_size);
  convert_result_array_xcel(result_extend, &query_start_t, &database_start_t, &len_t, &score_t);
  for (int i = 0; i < length; ++i) {
    query_pos[i] = query_start_t[i];
    database_pos[i] = database_start_t[i];
    extend_size[i] = len_t[i];
    extend_score[i] = score_t[i];
  }
  return;
}
#endif