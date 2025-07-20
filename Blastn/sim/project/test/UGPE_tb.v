`timescale 1ns / 1ps
`include "/home/xk52/ece6745/project-group19/sim/project/UGPE.v"

module Project_UGPE_tb;

  localparam QUERY_LEN    = 16;
  localparam DATABASE_LEN = 16;

  logic clk;
  logic reset;

  logic               istream_val;
  logic               ostream_rdy;
  logic [223:0]       istream_msg;

  logic               ostream_val;
  logic               istream_rdy;
  logic [255:0]       ostream_msg;

  project_UGPE #( .query_len(QUERY_LEN), .database_len(DATABASE_LEN) ) dut (
    .clk(clk),
    .reset(reset),
    .istream_val(istream_val),
    .ostream_rdy(ostream_rdy),
    .istream_msg(istream_msg),
    .ostream_val(ostream_val),
    .istream_rdy(istream_rdy),
    .ostream_msg(ostream_msg)
  );

  // Clock generation
  always #5 clk = ~clk;

  // Task to send a single input message
  task send_input(
    input [31:0] query,
    input [31:0] database,
    input [31:0] hit_pos,
    input [31:0] addr_q_start,
    input [31:0] addr_d_start,
    input [31:0] addr_len,
    input [31:0] addr_score
  );
  begin
    wait (istream_rdy == 1);
    @(posedge clk);
    istream_val  = 1;
    istream_msg  = {
      addr_score,
      addr_len,
      addr_d_start,
      addr_q_start,
      hit_pos,
      database,
      query
    };
    @(posedge clk);
    istream_val = 0;
  end
  endtask

  // Dump for VCD
  initial begin
    $dumpfile("/home/xk52/ece6745/project-group19/sim/build/ugpe.vcd");
    $dumpvars(0, Project_UGPE_tb);
  end

  // Test sequence
  initial begin
    clk = 0;
    reset = 1;
    istream_val = 0;
    ostream_rdy = 0;
    istream_msg = 0;

    repeat (3) @(posedge clk);
    reset = 0;

    // Test 1: Identical input
    send_input(32'h01234567, 32'h01234567, 5, 32'h11111111, 32'h22222222, 32'h33333333, 32'h44444444);
    $display("[INFO] Test 1 sent");
    ostream_rdy = 1;
    wait (ostream_val == 1);
    print_output(1);
    @(posedge clk);

    // // Test 2: Random mismatched input
    // send_input(32'hAAAAFFFF, 32'h12345678, 7, 32'hA1, 32'hB2, 32'hC3, 32'hD4);
    // $display("[INFO] Test 2 sent");
    // ostream_rdy = 1;
    // wait (ostream_val == 1);
    // print_output(2);
    // @(posedge clk);

    // // Test 3: Edge case near end
    // send_input(32'hFFFFFFFF, 32'hFFFFFFFF, 15, 32'hABCDEF01, 32'h12345678, 32'h00000010, 32'h00000020);
    // $display("[INFO] Test 3 sent");
    // ostream_rdy = 1;
    // wait (ostream_val == 1);
    // print_output(3);
    // @(posedge clk);

    $finish;
  end

  // Print helper
  task print_output(input int test_id);
  begin
    $display("[RESULT %0d]", test_id);
    $display("  score         = %0d",      ostream_msg[ 31:  0]);
    $display("  len           = %0d",      ostream_msg[ 63: 32]);
    $display("  q_start       = %0d",      ostream_msg[ 95: 64]);
    $display("  d_start       = %0d",      ostream_msg[127: 96]);
    $display("  addr_q_start  = 0x%08x",   ostream_msg[159:128]);
    $display("  addr_d_start  = 0x%08x",   ostream_msg[191:160]);
    $display("  addr_len      = 0x%08x",   ostream_msg[223:192]);
    $display("  addr_score    = 0x%08x",   ostream_msg[255:224]);
  end
  endtask

  // Timeout watchdog
  initial begin
    #100000;
    $display("[ERROR] Timeout!");
    $finish;
  end

endmodule
