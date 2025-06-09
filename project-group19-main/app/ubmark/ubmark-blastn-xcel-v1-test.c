#ifndef UBMARK_BLASTN_XCEL_V1_TEST_H
#define UBMARK_BLASTN_XCEL_V1_TEST_H

#include "ubmark-blastn-xcel-v1.h"
#include "ece6745.h"
#include "ubmark-blastn.h"
#include "ubmark-blastn-helper.h"
int ht_pos[HASH_LEN] = {0}; // 0 means not assigned, 1 means assigned

//------------------------------------------------------------------------
// Test positive inputs
//------------------------------------------------------------------------
void test_case_basic()
{
  // 0 1 2 3, 
  int q_seq[] = { A, C, G, T, C, G, A, T, A, C, G, T, A, C, G, T, T, G, A};
  int db_seq[] = { A, C, G, T, C, G, A, T, A, C, G, T, A, C, G, T, T, G, A };

  int q_seq_rev[] = { A, C, G, T, C, G, A, T, A, C, G, T, A, C, G, T, T, G, A };
  int db_seq_rev[] = { A, C, G, T, C, G, A, T, A, C, G, T, A, C, G, T, T, G, A };

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

  ExtendedList* result_extend = generate_extended_list(result, db_seq, q_seq, database_size, query_size);
  
  convert_result_array_xcel(result_extend, &query_start_t, &database_start_t, &len_t, &score_t);

  int max_score_base = 0, max_score_alt = 0;
  int max_size_base = 0, max_size_alt = 0;
  int max_start_base = 0, max_start_alt = 0;
  free_match_list(result);
  free_extended_list(result_extend);
  for(int i = 0; i < length; ++i) {
    if (max_score_base < score_t[i]) {
      max_score_base = score_t[i];
      max_size_base = len_t[i];
      max_start_base = query_start_t[i];
    }
  }

  extend_xcel_v1(query_start_tt, database_start_tt, len_t, score_t, length, db_seq_rev, q_seq_rev);
  for(int i = 0; i < length; ++i) {
    if (max_score_alt < score_t[i]) {
      max_score_alt = score_t[i];
      max_size_alt = len_t[i];
      max_start_alt = query_start_tt[i];
    }
  }
  ece6745_wprintf(L"score, size, start, base:%d %d %d, alt:%d %d %d\n"
                  , max_score_base, max_size_base, max_start_base, 
                    max_score_alt, max_size_alt, max_start_alt);
  ECE6745_CHECK( L"test_case_basic" );
  ECE6745_CHECK_INT_EQ(max_score_base, max_score_alt);
  ECE6745_CHECK_INT_EQ(max_size_base, max_size_alt);
  ECE6745_CHECK_INT_EQ(max_start_base, max_start_alt);
  ece6745_wprintf(L"\n");

}

void test_case_basic0()
{
  // 0 1 2 3, 
  int q_seq[] = { T, C, G, C, C, G, A, C, T, C, G, T, A, C, G, T, T, G, A};
  int db_seq[] = { G, A, G, T, C, G, A, T, A, C, G, T, A, C, G, T, T, G, A };

  int q_seq_rev[] = { T, C, G, C, C, G, A, C, T, C, G, T, A, C, G, T, T, G, A};
  int db_seq_rev[] = { G, A, G, T, C, G, A, T, A, C, G, T, A, C, G, T, T, G, A };


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
  int *score_tt = (int*)ece6745_malloc(length * (int)sizeof(int));
  int *len_tt = (int*)ece6745_malloc(length * (int)sizeof(int));

  for (int i = 0; i < length; ++i) {
    query_start_tt[i] = query_start_t[i];
    database_start_tt[i] = database_start_t[i];
    score_tt[i] = score_t[i];
    len_tt[i] = len_t[i];
    
  }

  ExtendedList* result_extend = generate_extended_list(result, db_seq, q_seq, database_size, query_size);
  
  convert_result_array_xcel(result_extend, &query_start_t, &database_start_t, &len_t, &score_t);

  int max_score_base = 0, max_score_alt = 0;
  int max_size_base = 0, max_size_alt = 0;
  int max_start_base = 0, max_start_alt = 0;
  free_match_list(result);
  free_extended_list(result_extend);
  for(int i = 0; i < length; ++i) {
    if (max_score_base < score_t[i]) {
      max_score_base = score_t[i];
      max_size_base = len_t[i];
      max_start_base = query_start_t[i];
    }
  }

  extend_xcel_v1(query_start_tt, database_start_tt, len_tt, score_tt, length, db_seq_rev, q_seq_rev);
  for(int i = 0; i < length; ++i) {
    if (max_score_alt < score_tt[i]) {
      max_score_alt = score_tt[i];
      max_size_alt = len_tt[i];
      max_start_alt = query_start_tt[i];
    }
  }
  ece6745_wprintf(L"score, size, start, base:%d %d %d, alt:%d %d %d\n"
                  , max_score_base, max_size_base, max_start_base, 
                    max_score_alt, max_size_alt, max_start_alt);

  ECE6745_CHECK( L"test_case_basic0" );
  ECE6745_CHECK_INT_EQ(max_score_base, max_score_alt);
  ECE6745_CHECK_INT_EQ(max_size_base, max_size_alt);
  ECE6745_CHECK_INT_EQ(max_start_base, max_start_alt);
  ece6745_wprintf(L"\n");
}

void test_case_basic1()
{
  // 0 1 2 3, 
  int q_seq[] = { A, A, G, T, C, T, G, G, C, A, C, T, T, A, G, G, C, G, T };
  int db_seq[] = { T, C, G, C, C, G, A, C, T, C, G, T, A, C, G, T, T, G, A };

  int q_seq_rev[] = { A, A, G, T, C, T, G, G, C, A, C, T, T, A, G, G, C, G, T };
  int db_seq_rev[] ={ T, C, G, C, C, G, A, C, T, C, G, T, A, C, G, T, T, G, A };

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

  ExtendedList* result_extend = generate_extended_list(result, db_seq, q_seq, database_size, query_size);
  
  convert_result_array_xcel(result_extend, &query_start_t, &database_start_t, &len_t, &score_t);

  int max_score_base = 0, max_score_alt = 0;
  int max_size_base = 0, max_size_alt = 0;
  int max_start_base = 0, max_start_alt = 0;
  free_match_list(result);
  free_extended_list(result_extend);
  for(int i = 0; i < length; ++i) {
    if (max_score_base < score_t[i]) {
      max_score_base = score_t[i];
      max_size_base = len_t[i];
      max_start_base = query_start_t[i];
    }
  }
  extend_xcel_v1(query_start_tt, database_start_tt, len_t, score_t, length, db_seq_rev, q_seq_rev);
  for(int i = 0; i < length; ++i) {
    if (max_score_alt < score_t[i]) {
      max_score_alt = score_t[i];
      max_size_alt = len_t[i];
      max_start_alt = query_start_tt[i];
    }
  }
  ece6745_wprintf(L"score, size, start, base:%d %d %d, alt:%d %d %d\n"
                  , max_score_base, max_size_base, max_start_base, 
                    max_score_alt, max_size_alt, max_start_alt);
  ECE6745_CHECK( L"test_case_basic1" );
  ECE6745_CHECK_INT_EQ(max_score_base, max_score_alt);
  ECE6745_CHECK_INT_EQ(max_size_base, max_size_alt);
  ECE6745_CHECK_INT_EQ(max_start_base, max_start_alt);
  ece6745_wprintf(L"\n");
}


void test_case_all_same()
{  // 0 1 2 3, 
  int q_seq[] = { A, A, A, A, A, A, A, A, A, A, A, A, A, A, G, G, C, G, T };
  int db_seq[] =  { A, A, A, A, A, A, A, A, A, A, A, A, A, A, G, G, C, G, T };

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

  int *query_start_tt = (int*)ece6745_malloc(length * (int)sizeof(int));
  int *database_start_tt = (int*)ece6745_malloc(length * (int)sizeof(int));
  for (int i = 0; i < length; ++i) {
    query_start_tt[i] = query_start_t[i];
    database_start_tt[i] = database_start_t[i];
  }

  ExtendedList* result_extend = generate_extended_list(result, db_seq, q_seq, database_size, query_size);
  
  convert_result_array_xcel(result_extend, &query_start_t, &database_start_t, &len_t, &score_t);

  int max_score_base = 0, max_score_alt = 0;
  int max_size_base = 0, max_size_alt = 0;
  int max_start_base = 0, max_start_alt = 0;
  free_match_list(result);
  free_extended_list(result_extend);
  for(int i = 0; i < length; ++i) {
    if (max_score_base < score_t[i]) {
      max_score_base = score_t[i];
      max_size_base = len_t[i];
      max_start_base = query_start_t[i];
    }
  }

  extend_xcel_v1(query_start_tt, database_start_tt, len_t, score_t, length, db_seq_rev, q_seq_rev);
  for(int i = 0; i < length; ++i) {
    if (max_score_alt < score_t[i]) {
      max_score_alt = score_t[i];
      max_size_alt = len_t[i];
      max_start_alt = query_start_tt[i];
    }
  }
  ece6745_wprintf(L"score, size, start, base:%d %d %d, alt:%d %d %d\n"
                  , max_score_base, max_size_base, max_start_base, 
                    max_score_alt, max_size_alt, max_start_alt);
  ECE6745_CHECK( L"test_case_all_same" );
  ECE6745_CHECK_INT_EQ(max_score_base, max_score_alt);
  ECE6745_CHECK_INT_EQ(max_size_base, max_size_alt);
  ECE6745_CHECK_INT_EQ(max_start_base, max_start_alt);
  ece6745_wprintf(L"\n");
}


int main( int argc, char** argv ) {
    __n = ( argc == 1 ) ? 0 : ece6745_atoi( argv[1] );
    if ( (__n <= 0) || (__n == 1) ) test_case_basic();
    if ( (__n <= 1) || (__n == 2) ) test_case_basic0();
    if ( (__n <= 2) || (__n == 3) ) test_case_basic1();
    if ( (__n <= 3) || (__n == 4) ) test_case_all_same();
    ece6745_wprintf(L"\n");
}

#endif /* UBMARK_BLASTN_XCEL_V1_TEST_H */