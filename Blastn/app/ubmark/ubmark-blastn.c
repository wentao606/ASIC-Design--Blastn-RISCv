//========================================================================
// ubmark-blastn
//========================================================================

#include "ubmark-blastn.h"
#include "stddef.h"
#include "ece6745.h"
#include "ubmark-blastn-helper.h"

// initialize the hash table
void init_hash_table(hash_table ht, int database_size) {
  for (int i = 0; i < HASH_LEN; ++i) {  
    ht[i] = (Node*)ece6745_malloc((int)(sizeof(Node)));
    if (ht[i] != NULL) {
      for (int j = 0; j < KMER; ++j) {
        ht[i]->value[j] = 5; // 5 means not assigned
      }
      ht[i]->next = NULL;
      ht[i]->pos[0] = database_size+1;
    }
  }
}

// calculate the key
int cal_hash_key(int * seq) {
  int res = 0;
  int n = 0;
  for (int i = KMER - 1; i >= 0; --i) {
      res += seq[i] << (2 * n);
      n++;
  }
  return res;
}

// make the hash table for database
void make_hash_table(int* database, int* ht_pos, hash_table ht, int database_size) {
  for (int i = 0; i < database_size - KMER + 1; ++i) {
      int key = cal_hash_key(database + i);
      int key_mod = mod(key, HASH_LEN);
      if (ht_pos[key_mod] == 0) {
          ht_pos[key_mod] = 1;
          for (int j = 0; j < KMER; ++j) {
            ht[key_mod]->value[j] = database[i + j];
          }
          for (int j = 0; j < POSSIZE; j++) {
            if (ht[key_mod]->pos[j] == database_size + 1) {
              ht[key_mod]->pos[j] = i;
              for (int s = j + 1; s < POSSIZE; s++) {
                ht[key_mod]->pos[s] = database_size + 1;
              }
              break;
            }
          }
      } else {
          Node* new_node = (Node*)ece6745_malloc(sizeof(Node));
          if (new_node != NULL) {
            new_node->pos[0] = i;
            for (int k = 0; k < KMER; ++k) {
              new_node->value[k] = database[i + k];
            }

            for (int j = 1; j < POSSIZE; j++) {
              new_node->pos[j] = database_size + 1;
            }
            new_node->next = ht[key_mod];
            ht[key_mod] = new_node;
          }
      }
  }
}

// match the seeds on the table
MatchList* generate_match_list(int* query, hash_table ht, int* ht_pos, int query_size) {
  MatchList* head = NULL;
  MatchList* tail = NULL;

  int k = query_size > KMER ? KMER : query_size;

  for (int i = 0; i < query_size - (k - 1); i++) {
      int key = 0;
      int n = 0;
      for (int j = k - 1; j >= 0; --j) {
          key += query[i + j] << (2 * n);
          n++;
      }

      int key_mod = mod(key, HASH_LEN);

      if (ht_pos[key_mod] == 1) {
          Node* current = ht[key_mod];
          while (current != NULL) {
              int match = 1;
              for (int k = 0; k < KMER; k++) {
                  if (query[i + k] != current->value[k]) {
                      match = 0;
                      break;
                  }
              }

              if (match) {
                  MatchList* new_node = (MatchList*)ece6745_malloc(sizeof(MatchList));

                  for (int j = 0; j < KMER; j++) {
                      new_node->value[j] = current->value[j];
                  }

                  for (int j = 0; j < POSSIZE; j++) {
                      new_node->pos[j] = current->pos[j];
                  }

                  new_node->pos_query = i;

                  new_node->next = NULL;

                  if (head == NULL) {
                      head = tail = new_node;
                  } else {
                      tail->next = new_node;
                      tail = new_node;
                  }
              }

              current = current->next;
          }
      }
  }

  return head;
}

// extend the seeds
ExtendedList* generate_extended_list(MatchList* match_list, int* database, int* query_seq, int database_size, int query_size) {
  ExtendedList* head = NULL;
  ExtendedList* tail = NULL;

  for (MatchList* current = match_list; current != NULL; current = current->next) {
      int q_start = current->pos_query;
      int q_end = q_start + KMER - 1;

      for (int i = 0; current->pos[i] != database_size+1 && i < POSSIZE; i++) {
          int d_start = current->pos[i];
          int d_end = d_start + KMER - 1;

          int score = KMER;
          int max_score = KMER;
          int max_q_left = q_start;
          int max_d_left = d_start;
          int max_len = KMER;

          int left_q = q_start - 1;
          int left_d = d_start - 1;
          int right_q = q_end + 1;
          int right_d = d_end + 1;

          int final_left_q = q_start;
          int final_left_d = d_start;
          int final_right_q = q_end;

          while (1) {
              int new_score = 0;
              int can_extend = 0;

              if (left_q >= 0 && left_d >= 0) {
                  new_score += (query_seq[left_q] == database[left_d]) ? 1 : -3;
                  can_extend = 1;
              } else {
                  new_score += 0;
              }

              if (right_q < query_size && right_d < database_size) {
                  new_score += (query_seq[right_q] == database[right_d]) ? 1 : -3;
                  can_extend = 1;
              } else {
                  new_score += 0;
              }

              if (!can_extend || (max_score - (score + new_score)) > THRESHOLD) {
                  break;
              }

              score += new_score;

              if (left_q >= 0 && left_d >= 0) {
                  final_left_q = left_q;
                  final_left_d = left_d;
                  left_q--;
                  left_d--;
              }

              if (right_q < query_size && right_d < database_size) {
                  final_right_q = right_q;
                  right_q++;
                  right_d++;
              }
              if (score >= max_score) {
                max_score = score;
                max_q_left = final_left_q;
                max_d_left = final_left_d;
                max_len = final_right_q - final_left_q + 1;
            }
          }

          ExtendedList* new_node = (ExtendedList*)ece6745_malloc(sizeof(ExtendedList));
          new_node->start_query = max_q_left;
          new_node->end_query = max_q_left + max_len - 1;
          new_node->start_data = max_d_left;
          new_node->end_data = max_d_left + max_len - 1;
          new_node->alignment_score = max_score;
          new_node->next = NULL;

          if (head == NULL) {
              head = tail = new_node;
          } else {
              tail->next = new_node;
              tail = new_node;
          }
      }
  }

  return head;
}

