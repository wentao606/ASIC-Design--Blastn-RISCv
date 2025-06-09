#ifndef UBMARK_BLASTN_XCEL_V1_H
#define UBMARK_BLASTN_XCEL_V1_H

#include "ubmark-blastn.h"
#include "ubmark-blastn-xcel-v1.h"
#include "ubmark-blastn-helper.h"

void extend_xcel_v1(int* query_pos, int* database_pos, int* extend_size,
    int* extend_score, int length, int *compressed_db, int *compressed_query);

#endif /* UBMARK_BLASTN_XCEL_V1_H */