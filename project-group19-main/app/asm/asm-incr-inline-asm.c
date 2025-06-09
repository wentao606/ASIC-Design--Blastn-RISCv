//========================================================================
// asm-incr-asm
//========================================================================
// Example C application that increments elements in an array using
// inline assembly.

#include "asm-incr-inline-asm.h"

//------------------------------------------------------------------------
// add
//------------------------------------------------------------------------
// We usually encapsulate inline assembly in a small inline function.
// Since the _RISCV preprocessor macro is only defined when
// cross-compiling, we can use this macro to provide two different
// implementations of the function: one version for when we are compiling
// natively and a different version (using inline assembly) when we are
// cross-compiling.

#ifdef _RISCV

inline
int add( int a, int b )
{
  int result;
  __asm__ ( "nop; nop; add %0, %1, %2; nop; nop" :
            "=r"(result) : "r"(a), "r"(b) );
  return result;
}

#else

inline
int add( int a, int b )
{
  return a + b;
}

#endif

//------------------------------------------------------------------------
// incr_asm
//------------------------------------------------------------------------

__attribute__ ((noinline))
void incr_inline_asm( int* array, int size )
{
  for ( int i = 0; i < size; i++ )
    array[i] = add( array[i], 1 );
}

