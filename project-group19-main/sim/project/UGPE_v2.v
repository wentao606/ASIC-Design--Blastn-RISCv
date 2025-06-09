//=========================================================================
// Ungapped extension processing engine
//=========================================================================
// Extend array is packed in 2 bit wide and stored in a 32bit INT

`ifndef PROJECT_BLASTN_UGPE_V2_V
`define PROJECT_BLASTN_UGPE_V2_V

`include "vc/regs.v"
`include "vc/muxes.v"
`include "vc/arithmetic.v"
`include "vc/trace.v"

module project_UGPE_v2
(
  input logic clk,
  input logic reset,
  input logic istream_val,
  input logic ostream_rdy,
  input logic [255:0] istream_msg,

  output logic ostream_val,
  output logic istream_rdy,
  output logic [159:0] ostream_msg

);

  logic [31 : 0] query;
  logic [31 : 0] database;
  logic [31:0] hit_pos;
  logic [31:0] seq_len;
  logic [31:0] d_start;
  logic [31:0] q_start;
  logic [127:0] addr;

  logic [31:0] hit_pos_reg;
  logic [31:0] seq_len_reg;
  logic [31:0] d_start_reg;
  logic [31:0] q_start_reg;
  logic [127:0] addr_reg;
  logic [127:0] addr_reg_out;

  assign query = istream_msg[31:0];
  assign database = istream_msg[63:32];
  assign q_start = {16'd0, istream_msg[79:64] };
  assign d_start = {16'd0,istream_msg[95:80] };
  assign hit_pos = {16'd0,istream_msg[111:96] };
  assign seq_len = {16'd0,istream_msg[127:112] };
  assign addr = istream_msg[255:128];

  localparam thre = 20;
  localparam kmer = 32'd0;

  //initial value
  logic [31:0] idx_q_left;
  logic [31:0] idx_q_right;
  logic [31:0] idx_d_left;
  logic [31:0] idx_d_right;

  logic [31:0] idx_q_left_reg;
  logic [31:0] idx_q_right_reg;
  logic [31:0] idx_d_left_reg;
  logic [31:0] idx_d_right_reg;

  assign idx_q_left = hit_pos;
  assign idx_q_right = hit_pos - 1 ;
  assign idx_d_left = hit_pos ;
  assign idx_d_right = hit_pos - 1;

    // split the qeury and database
    logic [31 : 0] query_left;
    logic [31 : 0] query_right;
    logic [31 : 0] database_left;  
    logic [31 : 0] database_right;

    logic [31:0] query_left_reg;
    logic [31:0] query_right_reg;
    logic [31:0] database_left_reg;
    logic [31:0] database_right_reg;


    //left part move to LSB
    assign query_left = (query >> idx_q_left * 2) & 32'hFFFFFFFF;
    // right paer shift to MSB
    assign query_right = (query << (32 - (idx_q_right + 1) * 2)) & 32'hFFFFFFFF;
    assign database_left = (database >> idx_d_left * 2) & 32'hFFFFFFFF;
    assign database_right = (database << (32 - (idx_d_right + 1) * 2)) & 32'hFFFFFFFF;
  
    //===================== dpath ========================
    // left extension
    // q mux
    logic [31:0] q_left_mux_out;
    logic [31:0] q_left_rshifter_out;
    logic        q_left_mux_sel;
    vc_Mux2#(32) q_left_mux
    (
    .sel (q_left_mux_sel), //ctrl signal
    .in0 (q_left_rshifter_out),
    .in1 (query_left),
    .out (q_left_mux_out)
    );

    // d mux
    logic [31:0] d_left_mux_out;
    logic [31:0] d_left_rshifter_out;
    logic        d_left_mux_sel;

    vc_Mux2#(32) d_left_mux
    (
    .sel (d_left_mux_sel), //ctrl signal
    .in0 (d_left_rshifter_out),
    .in1 (database_left),
    .out (d_left_mux_out)
    );

    // q register
    logic [31:0] q_left_reg_out;
    vc_Reg#(32) q_left_reg
    (
    .clk (clk),
    .d   (q_left_mux_out),
    .q   (q_left_reg_out)
    );

    // d register
    logic [31:0] d_left_reg_out;
    vc_Reg#(32) d_left_reg
    (
    .clk (clk),
    .d   (d_left_mux_out),
    .q   (d_left_reg_out)
    );

    // cmp_left
    logic eq_out_left;
    logic [1:0] q_left_cmp;
    logic [1:0] d_left_cmp;
    //q_left_reg_out[idx_q_left*2 + 1 : idx_q_left*2]
    // d_left_reg_out[idx_d_left*2 + 1 : idx_d_left*2]
    assign q_left_cmp =( q_left_reg_out ) & 32'b11; //q_left_reg_out[idx_q_left*2 + 1 : idx_q_left*2]
    assign d_left_cmp =( d_left_reg_out  ) & 32'b11; // d_left_reg_out[idx_d_left*2 + 1 : idx_d_left*2]
    vc_EqComparator #(2) left_comp
    (
        .in0 (q_left_cmp),
        .in1 (d_left_cmp),
        .out (eq_out_left)
    );

    // left_zero_mux
    logic [31:0] left_zero_mux_out;
    logic        left_zero_mux_sel;
    vc_Mux2#(32) left_zero_mux
    (
    .sel (left_zero_mux_sel), //ctrl signal
    .in0 ((eq_out_left)? 1 : -3),
    .in1 (32'd0),
    .out (left_zero_mux_out)
    );

    // rshift_q
    vc_RightLogicalShifter#(32,2) q_rshifter
    (
    .in    (q_left_reg_out),
    .shamt (2'd2),
    .out   (q_left_rshifter_out)
    );
    // rshift_d
    vc_RightLogicalShifter#(32,2) d_rshifter
    (
    .in    (d_left_reg_out),
    .shamt (2'd2),
    .out   (d_left_rshifter_out)
    );

    // right extension
    // q mux
    logic [31:0] q_right_mux_out;
    logic [31:0] q_right_lshifter_out;
    logic        q_right_mux_sel;

    vc_Mux2#(32) q_right_mux
    (
    .sel (q_right_mux_sel), //ctrl signal
    .in0 (q_right_lshifter_out),
    .in1 (query_right),
    .out (q_right_mux_out)
    );

    // d mux
    logic [31:0] d_right_mux_out;
    logic [31:0] d_right_lshifter_out;
    logic        d_right_mux_sel; 

    vc_Mux2#(32) d_right_mux
    (
    .sel (d_right_mux_sel), //ctrl signal
    .in0 (d_right_lshifter_out),
    .in1 (database_right),
    .out (d_right_mux_out)
    );

    // q register
    logic [31:0] q_right_reg_out;
    vc_Reg#(32) q_right_reg
    (
    .clk (clk),
    .d   (q_right_mux_out),
    .q   (q_right_reg_out)
    );

    // d register
    logic [31:0] d_right_reg_out;
    vc_Reg#(32) d_right_reg
    (
    .clk (clk),
    .d   (d_right_mux_out),
    .q   (d_right_reg_out)
    );

    // cmp_right
    logic eq_out_right;
    logic [1:0] q_right_cmp;
    logic [1:0] d_right_cmp;
    //q_right_reg_out[idx_q_right*2 + 1 : idx_q_right*2
    // d_right_reg_out[idx_d_right*2 + 1 : idx_d_right*2]
    assign q_right_cmp =( q_right_reg_out >> 32'd30) & 2'b11; 
    assign d_right_cmp =( d_right_reg_out >> 32'd30) & 2'b11; 
    vc_EqComparator #(2) right_comp
    (
        .in0 (q_right_cmp),
        .in1 (d_right_cmp),
        .out (eq_out_right)
    );

    // right_zero_mux
    logic [31:0] right_zero_mux_out;
    logic        right_zero_mux_sel;
    vc_Mux2#(32) right_zero_mux
    (
    .sel (right_zero_mux_sel), //ctrl signal
    .in0 ((eq_out_right)? 1 : -3),
    .in1 (0),
    .out (right_zero_mux_out)
    );

    // lshift_q
    vc_LeftLogicalShifter#(32,2) q_lshifter
    (
    .in    (q_right_reg_out),
    .shamt (2'd2),
    .out   (q_right_lshifter_out)
    );   

    // lshift_d
    vc_LeftLogicalShifter#(32,2) d_lshifter
    (
    .in    (d_right_reg_out),
    .shamt (2'd2),
    .out   (d_right_lshifter_out)
    );  

    // result mux
    logic [31:0] result_mux_out;
    logic [31:0] add_mux_out;
    logic        result_mux_sel;
    vc_Mux2#(32) result_mux
    (
    .sel (result_mux_sel), //ctrl signal
    .in0 (add_mux_out),
    .in1 (kmer),
    .out (result_mux_out)
    );

    // result register
    logic [31:0] result_reg_out;
    logic        result_en;
    vc_EnReg #(32) result_reg
    (
        .clk(clk),
        .reset(reset),
        .en(result_en),  // ctrl signal
        .d(result_mux_out),
        .q(result_reg_out)
    );

    // adder_left
    logic [31:0] add_left_out;
    vc_SimpleAdder#(32) add_left
    (
    .in0 (result_reg_out),
    .in1 (left_zero_mux_out),
    .out (add_left_out)
    );
    // adder_right
    logic [31:0] add_right_out;
    vc_SimpleAdder#(32) add_right
    (
    .in0 (add_left_out),
    .in1 (right_zero_mux_out),
    .out (add_right_out)
    );

    // add_mux
    logic        add_mux_sel;
    vc_Mux2#(32) add_mux
    (
    .sel (add_mux_sel), //ctrl signal
    .in0 (add_right_out),
    .in1 (result_reg_out),
    .out (add_mux_out)
    );

    //====================== ctrl ========================= 
    //Function for Updating the control signal for data path

  task cs    
  (
    input cs_istream_rdy,
    input cs_ostream_val,
    input cs_q_left_mux_sel,
    input cs_d_left_mux_sel,
    input cs_q_right_mux_sel,
    input cs_d_right_mux_sel,
    input cs_result_mux_sel,
    input cs_result_en,
    input cs_add_mux_sel,
    input cs_left_zero_mux_sel,
    input cs_right_zero_mux_sel
  );

  begin
    istream_rdy = cs_istream_rdy;
    ostream_val = cs_ostream_val;
    q_left_mux_sel = cs_q_left_mux_sel;
    d_left_mux_sel = cs_d_left_mux_sel;
    q_right_mux_sel = cs_q_right_mux_sel;
    d_right_mux_sel = cs_d_right_mux_sel;
    result_mux_sel = cs_result_mux_sel;
    result_en = cs_result_en;
    add_mux_sel = cs_add_mux_sel;
    left_zero_mux_sel = cs_left_zero_mux_sel;
    right_zero_mux_sel = cs_right_zero_mux_sel;
  end
  endtask
    
  localparam STATE_IDLE = 2'd0;
  localparam STATE_CALC = 2'd1;
  localparam STATE_DONE = 2'd2;

  logic [1:0] state_reg;
  logic [1:0] state_next;
  logic [31:0] lshift_cnt;
  logic [31:0] rshift_cnt;
  logic [31:0] lshift_cnt_next;
  logic [31:0] rshift_cnt_next;
  logic left_shift_done;
  logic right_shift_done;
  logic thre_break;
  logic left_shift_done_next;
  logic right_shift_done_next;
  logic thre_break_next;
  logic [31:0] current_score;
  logic [31:0] score_max;
  logic [31:0] lshift_cnt_max;
  logic [31:0] rshift_cnt_max;  
  logic [31:0] score_next;
  logic [31:0] score_max_next;
  logic [31:0] lshift_cnt_max_next;
  logic [31:0] rshift_cnt_max_next;

  // detect if shift is done test
  // assign left_shift_done = (idx_q_left + lshift_cnt == (query_len - 1)) || (idx_d_left + lshift_cnt == (database_len - 1)) || thre_break || (hit_pos_reg == (query_len - 1)) || (hit_pos_reg == (database_len - 1));
  // assign right_shift_done = (idx_q_right - rshift_cnt == 0 ) || (idx_d_right - rshift_cnt == 0) || thre_break || (hit_pos_reg == 0) || (hit_pos_reg == 0);
  
  // assign thre_break = (score_gap > thre);

  

  always_ff @(posedge clk) begin
    if (reset) begin
      state_reg <= STATE_IDLE;
      lshift_cnt <= 32'd0;
      rshift_cnt <= 32'd0;
      thre_break <= 32'd0;
      left_shift_done <= 32'd0;
      right_shift_done <= 32'd0;
      score_max <= 32'd0;
      current_score <= kmer;
      lshift_cnt_max <= 32'd0;
      rshift_cnt_max <= 32'd0;
      hit_pos_reg <= 32'd0;
      addr_reg <= 128'd0;
      seq_len_reg <= 32'd0;
      d_start_reg <= 32'd0;
      q_start_reg <= 32'd0;

    end 
    else begin
      state_reg <= state_next;
      if (state_reg == STATE_IDLE) begin
        if (istream_val && istream_rdy) begin
          hit_pos_reg <= hit_pos;
          addr_reg <= addr;
          seq_len_reg <= seq_len;
          d_start_reg <= d_start;
          q_start_reg <= q_start;

          idx_q_left_reg <= idx_q_left;
          idx_q_right_reg <= idx_q_right;
          idx_d_left_reg <= idx_d_left;
          idx_d_right_reg <= idx_d_right;

          query_left_reg     <= query_left ;
          query_right_reg    <= query_right ;
          database_left_reg  <= database_left ;
          database_right_reg <= database_right ;
        end
      end

      if (state_reg == STATE_CALC) begin
        lshift_cnt <= lshift_cnt_next;
        rshift_cnt <= rshift_cnt_next;
        thre_break <= thre_break_next;
        left_shift_done <= left_shift_done_next;
        right_shift_done <= right_shift_done_next;
        current_score <= score_next;
        score_max <= score_max_next;
        lshift_cnt_max <= lshift_cnt_max_next;
        rshift_cnt_max <= rshift_cnt_max_next;
      end
      else if (state_reg == STATE_DONE) begin
        if (ostream_rdy) begin
        lshift_cnt <= 32'd0;
        rshift_cnt <= 32'd0;
        thre_break <= 32'd0;
        left_shift_done <= 32'd0;
        right_shift_done <= 32'd0;
        current_score <= 32'd0;
        score_max <= 32'd0;
        lshift_cnt_max <= 32'd0;
        rshift_cnt_max <= 32'd0;

        hit_pos_reg <= 32'd0;
        addr_reg <= 128'd0;
        seq_len_reg <= 32'd0;
        d_start_reg <= 32'd0;
        q_start_reg <= 32'd0;
        idx_q_left_reg <= 32'd0;  
        idx_q_right_reg <= 32'd0;
        idx_d_left_reg <= 32'd0;
        idx_d_right_reg <= 32'd0;
        query_left_reg     <= 32'd0;
        query_right_reg    <= 32'd0;
        database_left_reg  <= 32'd0;
        database_right_reg <= 32'd0;

        end

      end
    end
  end


  logic [31:0] score_gap;

  always @(*) begin  
    left_shift_done_next = 32'd0;
    right_shift_done_next = 32'd0;
    thre_break_next = 32'd0;
    score_next = 32'd0;
    score_max_next = 32'd0;
    lshift_cnt_next = 32'd0;
    rshift_cnt_next = 32'd0;
    rshift_cnt_max_next = 32'd0;
    lshift_cnt_max_next = 32'd0;

    state_next = state_reg;
    score_next = current_score;
    left_shift_done_next = left_shift_done;
    right_shift_done_next = right_shift_done;

    cs(0, 0, 1'dx, 1'dx, 1'dx, 1'dx, 1'dx, 0, 1'dx, 1'dx, 1'dx);
    case (state_reg)

      //input stream is ready to accpet data, and output stream does not have valid data yet. 
      STATE_IDLE: begin 
        cs(1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1);
        if (istream_val && istream_rdy) begin
          state_next = STATE_CALC;
        end
      end

      STATE_CALC: begin 
        score_next = add_mux_out;
        // detect if shift is done
        if ((idx_q_left_reg + lshift_cnt == (seq_len_reg - 1)) || (idx_d_left_reg + lshift_cnt == (seq_len_reg - 1)) || thre_break) begin
          left_shift_done_next = 1;
        end
        if ((idx_q_right_reg - rshift_cnt == 0 ) || (idx_d_right_reg - rshift_cnt == 0) || thre_break ) begin
          right_shift_done_next = 1;
        end

        // update count number
        if (!(left_shift_done) ) begin
          lshift_cnt_next = lshift_cnt + 32'd1;
        end
        else if (left_shift_done) begin
            lshift_cnt_next = lshift_cnt;
        end
        if (!(right_shift_done)  ) begin
          rshift_cnt_next = rshift_cnt + 32'd1;
        end
        else if (right_shift_done  ) begin
          rshift_cnt_next = rshift_cnt;
        end

        // detect if thre_break
        if ($signed(score_max) > $signed(add_right_out)) begin
          score_gap = score_max - add_right_out;
        end else begin
          score_gap = add_right_out - score_max;
        end
        
        if ((score_gap) > thre) begin
          thre_break_next = 1;
          right_shift_done_next = 1;
          left_shift_done_next = 1;
        end

        // update max value
        if ($signed(add_mux_out) >= $signed(score_max) )begin
          score_max_next = add_mux_out;
          // if (!(left_shift_done) ) begin
          //   lshift_cnt_max_next = lshift_cnt + 32'd1;
          // end
          // if (!(right_shift_done) ) begin
          //   rshift_cnt_max_next = rshift_cnt + 32'd1;
          // 
          // TRY
          lshift_cnt_max_next = lshift_cnt_next;
          rshift_cnt_max_next = rshift_cnt_next;
        end
        else begin
          score_max_next = score_max;
          lshift_cnt_max_next = lshift_cnt_max;
          rshift_cnt_max_next = rshift_cnt_max;
        end

        // ctrl signal

        if(left_shift_done && !right_shift_done) begin
          if (thre_break) begin
            cs(0,0,0,0,0,0,0,1,1,1,0);
          end
          else begin
            cs(0,0,0,0,0,0,0,1,0,1,0);
          end
          state_next = STATE_CALC;
        end
        else if ((right_shift_done && !left_shift_done) ) begin 
          if (thre_break) begin
            cs(0,0,0,0,0,0,0,1,1,0,1);
          end
          else begin
            cs(0,0,0,0,0,0,0,1,0,0,1);
          end
          state_next = STATE_CALC;
        end
        else if (left_shift_done && right_shift_done) begin
          state_next = STATE_DONE;
          if (thre_break) begin
            cs(0,0,0,0,0,0,0,1,1,1,1);
          end
          else begin
            cs(0,0,0,0,0,0,0,1,0,1,1);
          end
        end
        else begin
          if (thre_break) begin
            cs(0,0,0,0,0,0,0,1,1,0,0);
          end
          else begin
            cs(0,0,0,0,0,0,0,1,0,0,0);
          end
          state_next = STATE_CALC;
        end
      end 

      //output is read
      STATE_DONE: begin 
        cs(0,1,1'dx, 1'dx, 1'dx, 1'dx, 1'dx, 0, 1'dx, 1'dx, 1'dx);
        if (ostream_rdy == 1'b1) begin
          state_next = STATE_IDLE;
        end 	
      end

      default: cs(1'dx,1'dx,1'dx,1'dx,1'dx,1'dx,1'dx,1'dx,1'dx,1'dx,1'dx);
    endcase
  end
  

logic [31:0] score;
logic [31:0] len;
logic [31:0] q_start_out;
logic [31:0] d_start_out;


// assign pos_left_d = idx_d_left - 1 + lshift_cnt_max;
// assign pos_right_d = idx_d_right - rshift_cnt_max + 1;
// assign pos_left_q = idx_q_left -1  + lshift_cnt_max;
// assign pos_right_q = idx_q_right - rshift_cnt_max + 1;

assign score = score_max;
assign len = (lshift_cnt_max + rshift_cnt_max) & 32'hFFFFFFFF;
// assign len = (idx_q_left_reg + lshift_cnt_max) - (idx_d_left_reg + rshift_cnt_max);
assign q_start_out = q_start_reg - rshift_cnt_max ;
assign d_start_out = d_start_reg - rshift_cnt_max ;
assign addr_reg_out = addr_reg;

assign ostream_msg = { addr_reg_out, d_start_out[7:0], q_start_out[7:0], len[7:0], score[7:0] } & {160{ostream_val}};



  //----------------------------------------------------------------------
  // Line Tracing
  //----------------------------------------------------------------------

  `ifndef SYNTHESIS

  logic [`VC_TRACE_NBITS-1:0] str;
  integer f;
  `VC_TRACE_BEGIN
  begin

    // $sformat( str, "UGPE out: score=%x", ostream_msg[159:128] );
    // vc_trace.append_str( trace_str, str );


    // $sformat( str, "%x", istream_msg );
    // vc_trace.append_val_rdy_str( trace_str, istream_val, istream_rdy, str );

    // vc_trace.append_str( trace_str, "(" );

    // // ''' LAB TASK ''''''''''''''''''''''''''''''''''''''''''''''''''''''
    // // Add line tracing code here.
    // // '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''\/

    // $sformat(str, "hit_pos: %x ", hit_pos);
    // vc_trace.append_str( trace_str, str );
    // $sformat(str, "hit_pos_reg: %x ", hit_pos_reg);
    // vc_trace.append_str( trace_str, str );

    // $sformat(str, "rshift_cnt_max: %x ", rshift_cnt_max);
    // vc_trace.append_str( trace_str, str );


    // // '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''/\

    // vc_trace.append_str( trace_str, ")" );

    // $sformat( str, "%x", ostream_msg );
    // vc_trace.append_val_rdy_str( trace_str, ostream_val, ostream_rdy, str );

    case ( state_reg )
        STATE_IDLE:      vc_trace.append_str( trace_str, "I " );
        STATE_CALC:      vc_trace.append_str( trace_str, "CAL" );
        STATE_DONE:      vc_trace.append_str( trace_str, "D" );
        default:         vc_trace.append_str( trace_str, "? " );
    endcase

  end
  `VC_TRACE_END

  `endif /* SYNTHESIS */

endmodule // Project_BLASTN_UGPE_V2_V


`endif // PROJECT_BLASTN_UGPE_V2_V