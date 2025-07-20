#ifndef UBMARK_BLASTN_XCEL_V1_TEST_H
#define UBMARK_BLASTN_XCEL_V1_TEST_H

#include "ubmark-blastn-xcel-v1.h"
#include "ece6745.h"
#include "ubmark-blastn.h"

int ht_pos[HASH_LEN] = {0}; // 0 means not assigned, 1 means assigned


void test_case_all_same()
{
  // ECE6745_CHECK( L"test_case_compress" );
  // 0 1 2 3, 
  int q_seq_rev[] =  { A, A, A, A, A, A, A, A, A, A, A, A, A, A, G, G, C, G, T };
  int db_seq_rev[] = { A, A, A, A, A, A, A, A, A, A, A, A, A, A, G, G, C, G, T };

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


  extend_xcel_v1(query_start_t, database_start_t, len_t, score_t, length, db_seq_rev, q_seq_rev);
  ece6745_stats_off();
  for(int i = 0; i < length; ++i) {
    if (max_score_alt < score_t[i]) {
      max_score_alt = score_t[i];
      max_size_alt = len_t[i];
      max_start_alt = query_start_tt[i];
    }
  }
  // ece6745_wprintf(L"score, size, start, base:%d %d %d, alt:%d %d %d\n"
  //                 , max_score_base, max_size_base, max_start_base, 
  //                   max_score_alt, max_size_alt, max_start_alt);
  if (max_score_base == max_score_alt && max_size_base == max_size_alt && max_start_base == max_start_alt)
  {
    ece6745_wprintf(L"**Passed**\n");
  }
}


int main( int argc, char** argv ) {
    __n = ( argc == 1 ) ? 0 : ece6745_atoi( argv[1] );
    if ( (__n <= 0) || (__n == 1) ) test_case_all_same();
    ece6745_wprintf(L"\n");
}

#endif /* UBMARK_BLASTN_XCEL_V1_TEST_H */