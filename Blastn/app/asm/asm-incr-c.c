//========================================================================
// asm-incr-c
//========================================================================
// Example C application that increments elements in an array using C.

#include "asm-incr-c.h"

__attribute__ ((noinline))
void incr_c( int* array, int size )
{
  for ( int i = 0; i < size; i++ )
    array[i] += 1;
}

