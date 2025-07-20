//========================================================================
// 32 bits x 256 words SRAM
//========================================================================

`ifndef SRAM_32x256_1rw
`define SRAM_32x256_1rw

`include "sram/SRAM_generic.v"

`ifndef SYNTHESIS

module SRAM_32x256_1rw
(
  input  logic        clk0,
  input  logic        web0,
  input  logic        csb0,
  input  logic [3:0]  wmask0,
  input  logic [7:0]  addr0,
  input  logic [31:0] din0,
  output logic [31:0] dout0
);

  sram_SRAM_generic
  #(
    .p_data_nbits  (32),
    .p_num_entries (256)
  )
  sram_generic
  (
    .clk0   (clk0),
    .web0   (web0),
    .csb0   (csb0),
    .wmask0 (wmask0),
    .addr0  (addr0),
    .din0   (din0),
    .dout0  (dout0)
  );

endmodule

`endif /* SYNTHESIS */

`endif /* SRAM_32x256_1rw */

