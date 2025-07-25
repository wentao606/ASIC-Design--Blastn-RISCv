////////////////////////////////////////////////////////////////////////////////
//
//       This confidential and proprietary software may be used only
//     as authorized by a licensing agreement from Synopsys Inc.
//     In the event of publication, the following notice is applicable:
//
//                    (C) COPYRIGHT 2005 - 2024 SYNOPSYS INC.
//                           ALL RIGHTS RESERVED
//
//       The entire notice above must be reproduced on all authorized
//     copies.
//
// VERSION:   Verilog Simulation Model for FP adder/subtractor
//
// DesignWare_version: 1f8a0a99
// DesignWare_release: V-2023.12-DWBB_202312.5
//
////////////////////////////////////////////////////////////////////////////////
//-------------------------------------------------------------------------------
//
// ABSTRACT: Floating-point two-operand Adder/Subtractor
//           Computes the addition/subtraction of two FP numbers. 
//           The format of the FP numbers is defined by the number of bits 
//           in the significand (sig_width) and the number of bits in the 
//           exponent (exp_width).
//           The total number of bits in the FP number is sig_width+exp_width+1
//           since the sign bit takes the place of the MS bits in the significand
//           which is always 1 (unless the number is a denormal; a condition 
//           that can be detected testing the exponent value).
//           The output is a FP number and status flags with information about
//           special number representations and exceptions. 
//           Subtraction is forced when op=1.
//              parameters      valid values (defined in the DW manual)
//              ==========      ============
//              sig_width       significand size,  2 to 253 bits
//              exp_width       exponent size,     3 to 31 bits
//              ieee_compliance supports the IEEE Compliance 
//                              including NaN and denormal expressions.
//                              0 - IEEE 754 compatible without denormal support
//                                  (NaN becomes Infinity, Denormal becomes Zero)
//                              1 - IEEE 754 standard compatible
//                                  (NaN and denormal numbers are supported)
//                              2 - Reserved for future use
//                              3 - IEEE 754 standard compatible
//                                  (complying NaN and denormal numbers are supported)
//
//              Input ports     Size & Description
//              ===========     ==================
//              a               (sig_width + exp_width + 1)-bits
//                              Floating-point Number Input
//              b               (sig_width + exp_width + 1)-bits
//                              Floating-point Number Input
//              rnd             3 bits
//                              rounding mode
//              op              1 bit
//                              add/sub control: 0 for add - 1 for sub
//
//              Output ports    Size & Description
//              ===========     ==================
//              z               (sig_width + exp_width + 1) bits
//                              Floating-point Number result
//              status          byte
//                              info about FP results
//
// MODIFIED:
//
// 3/22/2021  RJK        Addressed STAR 3625874 involving accepting the value
//                       on the 'rnd' input at time 0
//
// 5/14/2020  Tawalbeh   Fixing STAR 3201667 - (TINY status bit)       
//
// 1/31/2020  Tawalbeh   Added ieee_compliance =3 functionality to match the DWFC in: behavior of NaN representation,
// 		         and mapping the rouding modes from six to four (4 and 5 will map to 0 and 1 in DWFC). 
//			 Added Warning messages when "rnd" value equals '4' or '5'
//
// 12/14/06  Kyung-Nam   Modifications based on code review by Kyung-Nam 
//
// 7/21/2006     	- includes manipulation of inexact bit
//           		- fixes value assigned to HugeInfinity when rnd=4 (up) RND_eval
//           		- fixes some special cases when rounding close to inf and zero
// 
//-------------------------------------------------------------------------------

module DW_fp_addsub (a, b, rnd, op, z, status);
parameter integer sig_width=23;
parameter integer exp_width=8;  
parameter integer ieee_compliance=0;                    

// declaration of inputs and outputs
input  [sig_width+exp_width:0] a,b;
input  [2:0] rnd;
input  op;
output [7:0] status;
output [sig_width+exp_width:0] z;

    // synopsys translate_off

  //-------------------------------------------------------------------------
  // Parameter legality check
  //-------------------------------------------------------------------------
  
 
  initial begin : parameter_check
    integer param_err_flg;

    param_err_flg = 0;
    
  
    if ( (sig_width < 2) || (sig_width > 253) ) begin
      param_err_flg = 1;
      $display(
	"ERROR: %m :\n  Invalid value (%d) for parameter sig_width (legal range: 2 to 253)",
	sig_width );
    end
  
    if ( (exp_width < 3) || (exp_width > 31) ) begin
      param_err_flg = 1;
      $display(
	"ERROR: %m :\n  Invalid value (%d) for parameter exp_width (legal range: 3 to 31)",
	exp_width );
    end
  
    if ( (ieee_compliance==2) || (ieee_compliance<0) || (ieee_compliance>3) ) begin
      param_err_flg = 1;
      $display(
	"ERROR: %m : Illegal value of ieee_compliance. ieee_compliance must be 0, 1, or 3" );
    end
  
    if ( param_err_flg == 1) begin
      $display(
        "%m :\n  Simulation halted due to invalid parameter value(s)");
      $finish;
    end

  end // parameter_check 




function [4-1:0] RND_eval;

  input [2:0] RND;
  input [0:0] Sign;
  input [0:0] L,R,STK;


  begin
  RND_eval[0] = 0;
  RND_eval[1] = R|STK;
  RND_eval[2] = 0;
  RND_eval[3] = 0;
  case (RND)
    3'b000:
    begin
      RND_eval[0] = R&(L|STK);
      RND_eval[2] = 1;
      RND_eval[3] = 0;
    end
    3'b001:
    begin
      RND_eval[0] = 0;
      RND_eval[2] = 0;
      RND_eval[3] = 0;
    end
    3'b010:
    begin
      RND_eval[0] = ~Sign & (R|STK);
      RND_eval[2] = ~Sign;
      RND_eval[3] = ~Sign;
    end
    3'b011:
    begin
      RND_eval[0] = Sign & (R|STK);
      RND_eval[2] = Sign;
      RND_eval[3] = Sign;
    end
    3'b100:
    begin
      RND_eval[0] = R;
      RND_eval[2] = 1;
      RND_eval[3] = 0;
    end
    3'b101:
    begin
      RND_eval[0] = R|STK;
      RND_eval[2] = 1;
      RND_eval[3] = 1;
    end
    default:
    begin
`ifndef DW_SUPPRESS_WARN
      if ($time > 0) begin
        $display ("WARNING: %m:\\n at time = %0t: Illegal rounding mode.", $time);
      end
`endif
    end
  endcase
  end

endfunction


// definitions used in the code

reg [8    -1:0] status_int;
reg [(exp_width + sig_width):0] z_temp,Large,Small;
reg [0:0] swap,subtract,STK;
reg [exp_width-1:0] E_Large,E_Small,E_Diff; // Exponents.
reg [sig_width-1:0] F_Large,F_Small;        // Fractions.
reg [exp_width+1:0] E_Comp;                 // The biggest possible exponent
reg [((sig_width + 3 + 3        ) - 2):0] M_Large,M_Small;       // The Mantissa numbers.
reg [((sig_width + 3 + 3        ) - 2):0] M_Z;                   // The Mantissa numbers.
reg [4-1:0] RND_val;         // Values returned by RND_eval function.
reg [(exp_width + sig_width):0] NaNFp;          // NaN FP number
reg [(exp_width + sig_width):0] b_int;          // internal value of b
reg Denormal_Large;                  // signals a denormal as a large operand
reg Denormal_Small;                  // signals a denormal as a small operand

// main process of information
always @(a or b or rnd or op)
  begin
    if (ieee_compliance == 3) 
      begin
        NaNFp = {1'b0,{exp_width{1'b1}},1'b1,{sig_width-1{1'b0}} } ;      
      end 
    else 
      begin
        NaNFp = {1'b0,{exp_width{1'b1}},{sig_width-1{1'b0}},1'b1};  
      end
 
  status_int = 0;
  b_int = b;
  b_int[(exp_width + sig_width)] = (op == 1)?~b[(exp_width + sig_width)]:b[(exp_width + sig_width)];
  subtract = a[(exp_width + sig_width)] ^ b_int[(exp_width + sig_width)];

  swap = a[((exp_width + sig_width) - 1):0] < b[((exp_width + sig_width) - 1):0];
  Large = swap ? b_int : a;
  Small = swap ? a : b_int;
  E_Large = Large[((exp_width + sig_width) - 1):sig_width];
  E_Small = Small[((exp_width + sig_width) - 1):sig_width];
  F_Large = Large[(sig_width - 1):0];
  F_Small = Small[(sig_width - 1):0];

  // 
  // NaN Input
  // 
  if ((((E_Large === ((((1 << (exp_width-1)) - 1) * 2) + 1)) && (F_Large !== 0)) ||
      ((E_Small === ((((1 << (exp_width-1)) - 1) * 2) + 1)) && (F_Large !== 0))) && ((ieee_compliance === 1) || (ieee_compliance === 3)))
    begin
      z_temp = NaNFp;
      status_int[2] = 1;
    end
  //
  // Infinity Input
  //
  else 
    if (E_Large === ((((1 << (exp_width-1)) - 1) * 2) + 1) && (F_Large === 0 || ieee_compliance === 0)) 
      begin
   	status_int[1] = 1;
        z_temp = Large;
        // zero out the fractional part
        z_temp[(sig_width - 1):0] = 0;
   	// Watch out for Inf-Inf !
   	if ( (E_Small === ((((1 << (exp_width-1)) - 1) * 2) + 1)) && (F_Large === 0 || ieee_compliance === 0) && (subtract === 1) )
    	  begin
            status_int[2] = 1;
            if ((ieee_compliance ===1) || (ieee_compliance === 3))   
              begin
                status_int[1] = 0;
                z_temp = NaNFp;
              end
            else
              z_temp[(exp_width + sig_width)] = 0;  // use positive inf. to represent NaN
   	  end
      end
    //
    // Zero Input (or denormal input when ieee_compliance == 0)
    //
    else 
      if (E_Small == 0 && ((ieee_compliance == 0) || (F_Small == 0)))
        begin
           z_temp = Large;
           // watch out for 0-0 !
	    if (E_Large === 0 && ((ieee_compliance == 0) || (F_Large == 0)))
      	     begin
      	       status_int[0] = 1;
               // Set the fraction to 000...
               z_temp = 0;
               if (subtract) 
                 if (rnd === 3'b011) z_temp[(exp_width + sig_width)] = 1;
                 else                z_temp[(exp_width + sig_width)] = 0;
               else                  z_temp[(exp_width + sig_width)] = a[(exp_width + sig_width)];
             end
// Check for large input being denormal, and set the Tiny bit
  if (E_Large == 0 && F_Large != 0 && (ieee_compliance == 1 || ieee_compliance == 3))
    status_int[3] =1;      
  end
      //
      // Normal Inputs
      //
      else
        begin
          // Detect the denormal input case
          if ((E_Large == 0) && (F_Large != 0)) 
            begin
              // M_Large contains the Mantissa of denormal value
              M_Large = {2'b00,F_Large,3'b000};
              Denormal_Large = 1'b1;
            end
          else
            begin
              // M_Large is the Mantissa for Large number
              M_Large = {2'b01,F_Large,3'b000};
              Denormal_Large = 1'b0;
            end
   
          if ((E_Small == 0) && (F_Small != 0)) 
            begin
              // M_Small contains the Mantissa of denormal value
              M_Small = {2'b00,F_Small,3'b000};
              Denormal_Small = 1'b1;
            end
          else
            begin
              // M_Small is the Mantissa for Small number
              M_Small = {2'b01,F_Small,3'b000};
              Denormal_Small = 1'b0;
            end

          // When one of the inputs is a denormal, we need to
          // compensate because the exponent for a denormal is
          // actually 1, and not 0.
          if ((Denormal_Large ^ Denormal_Small) == 1'b1) 
            E_Diff = E_Large - E_Small - 1;
	  else
            E_Diff = E_Large - E_Small;

          // Shift right by E_Diff for Small number: M_Small.
          STK = 0;
          while ( (M_Small != 0) && (E_Diff != 0) )
            begin
              STK = M_Small[0] | STK;
              M_Small = M_Small >> 1;
              E_Diff = E_Diff - 1;
            end
          M_Small[0] = M_Small[0] | STK;

          // Compute M_Z result: a +/- b
          if (subtract === 0) M_Z = M_Large + M_Small;
          else M_Z = M_Large - M_Small;

          // ----------------------------------------------------------
          //  Post Process
          // -----------------------------------------------------------
          E_Comp = {2'b00, E_Large};

          //
          // Exact 0 special case after the computation.
          //
            if (M_Z === 0)
              begin
                status_int[0] = 1;
                z_temp = 0;
                // If rounding mode is -Infinity, the sign bit is 1; 
                // otherwise the sign bit is 0.
                if (rnd === 3'b011) z_temp[(exp_width + sig_width)] = 1;
              end
            //
            // Normal case after the computation.
            //
            else
              begin
                // Normalize the Mantissa for computation overflow case.
                if (M_Z[((sig_width + 3 + 3        ) - 2)] === 1)
                  begin
                    E_Comp = E_Comp + 1;
                    STK = M_Z[0];
                    M_Z = M_Z >> 1;
                    M_Z[0] = M_Z[0] | STK;
                  end

                // Normalize the Mantissa for leading zero case.
                while ( (M_Z[((sig_width + 3 + 3        ) - 2)-1] === 0) && (E_Comp > 1) )
                  begin
                    E_Comp = E_Comp - 1;
                    M_Z = M_Z << 1;
                  end
	
                // test if the output of the normalization unit is still not normalized
                if (M_Z[((sig_width + 3 + 3        ) - 2):((sig_width + 3 + 3        ) - 2)-1] === 0)
	          if ((ieee_compliance == 1) || (ieee_compliance === 3)) 
                    begin
                      z_temp = {Large[(exp_width + sig_width)],{exp_width{1'b0}}, M_Z[((sig_width + 3 + 3        ) - 2)-2:3]};
		      status_int[3] = ~status_int[2] ; 
                      if ((STK == 1) || (M_Z[(3 - 1):0] != 0))
                        status_int[5] = 1;
                      if (M_Z[((sig_width + 3 + 3        ) - 2)-2:3] == 0) 
                        status_int[0] = 1; 
                    end
                  else // when denormal is not used --> becomes zero or minFP
                    begin
                      if ((rnd == 2 & ~Large[(exp_width + sig_width)]) | 
                          (rnd == 3 & Large[(exp_width + sig_width)]) | 
                          (rnd == 5)) 
                        begin
                          z_temp = {Large[(exp_width + sig_width)],{exp_width-1{1'b0}},{1'b1},{sig_width{1'b0}}};
                          status_int[0] = 0;
                        end
                      else
                        begin
                          z_temp = {Large[(exp_width + sig_width)],{exp_width{1'b0}}, {sig_width{1'b0}}};
                          status_int[0] = 1;
                        end
                      status_int[3] = 1;
                      status_int[5] = 1;
                    end
                else
                  begin
                    // Round M_Z according to the rounding mode (rnd). 
           	    if (ieee_compliance == 3) 
             	      begin
               		RND_val = RND_eval({1'b0, rnd[1:0]}, Large[(exp_width + sig_width)], M_Z[3], M_Z[(3 - 1)], (|{M_Z[1:0]})); 
             	      end  
           	    else
	     	      begin
               		RND_val = RND_eval(rnd, Large[(exp_width + sig_width)], M_Z[3], M_Z[(3 - 1)], (|{M_Z[1:0]}));      
             	      end

                  if (RND_val[0] === 1) M_Z = M_Z + (1<<3);
 
                    // Normalize the Mantissa for overflow case after rounding.
                    if ( (M_Z[((sig_width + 3 + 3        ) - 2)] === 1) )
                      begin
                        E_Comp = E_Comp + 1;
                        M_Z = M_Z >> 1;
                      end

                    //
                    // Huge
                    //
                    if (E_Comp >= ((((1 << (exp_width-1)) - 1) * 2) + 1))
                      begin
                        status_int[4] = 1;
                        status_int[5] = 1;
                        if(RND_val[2] === 1)
                          begin
                            // Infinity
                            M_Z[((sig_width + 3 + 3        ) - 2)-2:3] = 0;
                            E_Comp = ((((1 << (exp_width-1)) - 1) * 2) + 1);
                            status_int[1] = 1;
                          end
                        else
                          begin
                            // MaxNorm
                            E_Comp = ((((1 << (exp_width-1)) - 1) * 2) + 1) - 1;
                            M_Z[((sig_width + 3 + 3        ) - 2)-2:3] = -1;
                          end
                      end
                    //
                    // Tiny or Denormal
                    //
                    else 
                      if (E_Comp <= 0) E_Comp = 0 + 1;
    
                    //
                    // Normal  (continues)
                    //
                    status_int[5] = status_int[5] | RND_val[1];
                    // Reconstruct the floating point format.
                    z_temp = {Large[(exp_width + sig_width)],E_Comp[exp_width-1:0],M_Z[((sig_width + 3 + 3        ) - 2)-2:3]};
                  end //  result is normal value 
              end  // Normal computation case
        end    // non-special inputs
end

assign status = ((^(a ^ a) !== 1'b0) || (^(b ^ b) !== 1'b0) || (^(rnd ^ rnd) !== 1'b0) || (^(op ^ op) !== 1'b0)) ? {8'bx} : status_int;
assign z = ((^(a ^ a) !== 1'b0) || (^(b ^ b) !== 1'b0) || (^(rnd ^ rnd) !== 1'b0) || (^(op ^ op) !== 1'b0)) ? {sig_width+exp_width+1{1'bx}} : z_temp;

reg msg_rnd4_emitted_once;
reg msg_rnd5_emitted_once;
initial begin
  msg_rnd4_emitted_once = 1'b0;
  msg_rnd5_emitted_once = 1'b0;
end

generate
  if (ieee_compliance == 3) begin : GEN_IC_EQ_3
    always @ (rnd) begin : warning_alert_PROC
      if ((rnd == 3'b100) && (msg_rnd4_emitted_once !== 1'b1)) begin
        $display("############################################################");
        $display("############################################################");
        $display("##");
        $display("## At time: %d", $stime);
        $display("## Warning! : from %m");
        $display("##");
        $display("##      The rnd input was set to a value of 4 and with");
        $display("##      ieee_compliance set to 3 internal rounding will");
        $display("##      follow the same behavior as if rnd input is being");
        $display("##      set to 0.  That is, the IEEE standard rounding mode");
        $display("##      of 'round to nearest even' is used when rnd input");
        $display("##      is set to a value of 4.");
        $display("##");
        $display("############################################################");
        $display("############################################################");
        $display(" ");
        msg_rnd4_emitted_once = 1'b1;
      end

      if ((rnd == 3'b101) && (msg_rnd5_emitted_once !== 1'b1)) begin
        $display("############################################################");
        $display("############################################################");
        $display("##");
        $display("## At time: %d", $stime);
        $display("## Warning! : from %m");
        $display("##");
        $display("##      The rnd input was set to a value of 5 and with");
        $display("##      ieee_compliance set to 3 internal rounding will");
        $display("##      follow the same behavior as if rnd input is being");
        $display("##      set to 1.  That is, the IEEE standard rounding mode");
        $display("##      of 'round to zero' is used when rnd input is set");
        $display("##      to a value of 5.");
        $display("##");
        $display("############################################################");
        $display("############################################################");
        $display(" ");
        msg_rnd5_emitted_once = 1'b1;
      end
    end
  end  // GEN_IC_EQ_3
endgenerate

    // synopsys translate_on

endmodule

