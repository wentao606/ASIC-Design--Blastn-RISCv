//========================================================================
// FPAdd2stage
//========================================================================

`ifndef FPU_FPADD_2STAGE_V
`define FPU_FPADD_2STAGE_V

/* verilator lint_off LATCH */
`include "dw/DW_fp_addsub.v"
`include "dw/DW_fp_add.v"
/* verilator lint_on LATCH */

module tut13_dw_FPAdd2stage
(
  input  logic        clk,
  input  logic        reset,

  input  logic        in_val,
  input  logic [31:0] in0,
  input  logic [31:0] in1,

  output logic        out_val,
  output logic [31:0] out
);

  // pipeline registers

  logic        val_X0;
  logic [31:0] in0_X0;
  logic [31:0] in1_X0;

  always_ff @(posedge clk) begin
    if ( reset )
      val_X0 <= 1'b0;
    else
      val_X0 <= in_val;

    in0_X0 <= in0;
    in1_X0 <= in1;
  end

  // floating-point adder

  logic [7:0]  status_X0;
  logic [31:0] out_X0;

  DW_fp_add
  #(
    .sig_width       (23),
    .exp_width       (8),
    .ieee_compliance (1)
  )
  fp_add
  (
    .a      (in0_X0),
    .b      (in1_X0),
    .rnd    (3'b000),
    .z      (out_X0),
    .status (status_X0)
  );

  // retiming registers

  logic        val_X1;
  logic [31:0] out_X1;

  always_ff @(posedge clk) begin
    if ( reset )
      val_X1 <= 1'b0;
    else
      val_X1 <= val_X0;

    out_X1 <= out_X0;
  end

  // output logic

  assign out_val = val_X1;
  assign out = out_X1 & {32{val_X1}};

endmodule

`endif /* FPU_FPADD_2STAGE_V */

