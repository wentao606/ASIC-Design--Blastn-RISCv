//========================================================================
// Unit tests for ubmark blastn
//========================================================================

#include "ece6745.h"
#include "ubmark-blastn.h"
#include "ubmark-blastn-helper.h"

int query_seq[] = {A, G, C, T, G, A, C};
int database[] = {G, A, C, T, G, A, C, A, T, A, C};
int ht_pos[HASH_LEN] = {0}; // 0 means not assigned, 1 means assigned

//------------------------------------------------------------------------
// Test positive inputs
//------------------------------------------------------------------------
void test_case_cal_key()
{
  ECE6745_CHECK( L"test_case_cal_key" );

  int seq[] = { 2, 1, 0 };

  int result = cal_hash_key( seq );
  int true_res = 36;

  ECE6745_CHECK_INT_EQ( result, true_res );
}

//------------------------------------------------------------------------
// Test positive inputs
//------------------------------------------------------------------------
void test_case_0()
{
  hash_table ht;
  // ece6745_stats_on();
  init_hash_table(ht, DATABASE_SIZE);
  make_hash_table(database, ht_pos, ht, DATABASE_SIZE);
  MatchList* result = generate_match_list(query_seq, ht, ht_pos, QUERY_LEN);
  ExtendedList* result_extend = generate_extended_list(result, database, query_seq, DATABASE_SIZE, QUERY_LEN);
  int res = 1;
  int query_start[] = {2, 2, 2, 4};
  int base_start[] = {2, 2, 2, 0};
  int len[] ={3, 5, 5, 3};
  int score[] = {3, 5, 5, 3};
  int query_start_t[100];
  int base_start_t[100];
  int len_t[100];
  int score_t[100];
  convert_result_array(result_extend, query_start_t, base_start_t, len_t, score_t);
  ECE6745_CHECK( L"test_case_query" );
  for (int i = 0; i < 4; i++) {
    if (query_start[i] != query_start_t[i]) {
      res = 0;
      break;
    }
  }
  ECE6745_CHECK_INT_EQ( res, 1 );

  ECE6745_CHECK( L"test_case_data" );
  for (int i = 0; i < 4; i++) {
    if (base_start[i] != base_start_t[i]) {
      res = 0;
      break;
    }
  }
  ECE6745_CHECK_INT_EQ( res, 1 );

  ECE6745_CHECK( L"test_case_len" );
  for (int i = 0; i < 4; i++) {
    if (len[i] != len_t[i]) {
      ece6745_wprintf(L"len[%d]: %d, len_t[%d]: %d\n", i, len[i], i, len_t[i]);
      res = 0;
      break;
    }
  }
  ECE6745_CHECK_INT_EQ( res, 1 );

  ECE6745_CHECK( L"test_case_query" );
  for (int i = 0; i < 4; i++) {
    if (score[i] != score_t[i]) {
      res = 0;
      break;
    }
  }
  ECE6745_CHECK_INT_EQ( res, 1 );
  free_match_list(result);
  free_extended_list(result_extend);
  free_hash_table(ht);
}
//------------------------------------------------------------------------
// main
//------------------------------------------------------------------------

int main( int argc, char** argv )
{
  __n = ( argc == 1 ) ? 0 : ece6745_atoi( argv[1] );
  if ( (__n <= 0) || (__n == 1) ) test_case_cal_key();
  if ( (__n <= 0) || (__n == 2) ) test_case_0();
  ece6745_wprintf( L"\n\n" );
  // hash_table ht;
  // init_hash_table(ht);
  // make_hash_table(database, ht_pos, ht);
  // MatchList* result = generate_match_list(query_seq, ht, ht_pos);
  // for (MatchList* p = result; p != NULL; p = p->next) {
  //   ece6745_wprintf(L"Match value: ");
  //   for (int i = 0; i < KMER; i++) ece6745_wprintf(L"%d ", p->value[i]);
  //   ece6745_wprintf(L"\nPositions: ");
  //   for (int i = 0; i < POSSIZE && p->pos[i] != DATABASE_SIZE+1; i++) {
  //     ece6745_wprintf(L"%d ", p->pos[i]);
  //   }
  //   ece6745_wprintf(L"\nQuery position: %d\n", p->pos_query);
  //   ece6745_wprintf(L"\n\n");
  // }
  // ExtendedList* result_extend = generate_extended_list(result, database, query_seq);
  // while (result_extend != NULL) {
  //   ece6745_wprintf(L"  Query  : [%d, %d]\n", result_extend->start_query, result_extend->end_query);
  //   ece6745_wprintf(L"  Data   : [%d, %d]\n", result_extend->start_data, result_extend->end_data);
  //   ece6745_wprintf(L"  Score  : %d\n", result_extend->alignment_score);
  //   result_extend = result_extend->next;
  // }
  return ece6745_check_status;
}

