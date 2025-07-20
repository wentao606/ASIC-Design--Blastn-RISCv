#include "ubmark-blastn.dat"
#include "ubmark-blastn.h"
#include "ubmark-blastn-eval.h"
#include "ubmark-blastn-helper.h"
#include "stddef.h"
#include"ece6745.h"

int ht_pos[HASH_LEN] = {0}; // 0 means not assigned, 1 means assigned
void test_case_all_same()
{
  // ECE6745_CHECK( L"test_case_compress" );
  // 0 1 2 3, 
  int q_seq[] = { A, A, A, A, A, A, A, A, A, A, A, A, A, A, G, G, C, G, T };
  int db_seq[] =  { A, A, A, A, A, A, A, A, A, A, A, A, A, A, G, G, C, G, T };
  
  int database_size = 19;
  int query_size = 19;
  hash_table ht;
  // run base test
  // init hash table and generate linked list extend result
  init_hash_table(ht, database_size);
  make_hash_table(db_seq, ht_pos, ht, database_size);
  MatchList* result = generate_match_list(q_seq, ht, ht_pos, query_size);

  int *query_start_t = NULL;
  int *database_start_t = NULL;
  int *len_t = NULL;
  int *score_t = NULL;
  int length = convert_linkedlist_to_array(result, &query_start_t, 
    &database_start_t, &len_t, &score_t);

  int *query_start_tt = (int*)ece6745_malloc(length * (int)sizeof(int));
  int *database_start_tt = (int*)ece6745_malloc(length * (int)sizeof(int));
  for (int i = 0; i < length; ++i) {
    query_start_tt[i] = query_start_t[i];
    database_start_tt[i] = database_start_t[i];
  }
  // ece6745_stats_on();
  ExtendedList* result_extend = generate_extended_list(result, db_seq, q_seq, database_size, query_size);
  // ece6745_stats_off();
  convert_result_array_xcel(result_extend, &query_start_t, &database_start_t, &len_t, &score_t);
}

int main() {
    test_case_all_same();
}
