//========================================================================
// Unit tests for increment written in assembly
//========================================================================

#include "ece6745.h"
#include "asm-incr-asm.h"

//------------------------------------------------------------------------
// Test basic
//------------------------------------------------------------------------

void test_case_1_basic()
{
  ECE6745_CHECK( L"test_case_1_basic" );

  int array[] = { 1, 2, 3, 4 };
  int ref[]   = { 2, 3, 4, 5 };

  incr_asm( array, 4 );

  for ( int i = 0; i < 4; i++ )
    ECE6745_CHECK_INT_EQ( array[i], ref[i] );
}

//------------------------------------------------------------------------
// main
//------------------------------------------------------------------------

int main( int argc, char** argv )
{
  __n = ( argc == 1 ) ? 0 : ece6745_atoi( argv[1] );

  if ( (__n <= 0) || (__n == 1) ) test_case_1_basic();

  ece6745_wprintf( L"\n\n" );
  return ece6745_check_status;
}

