#=========================================================================
# 06-synopsys-pt-pwr/run.tcl
#=========================================================================

#-------------------------------------------------------------------------
# Initial setup
#-------------------------------------------------------------------------

# We need to include the db files for the standard cells and any
# generated SRAMs.

set_app_var target_library [list \
  "$env(ECE6745_STDCELLS)/stdcells.db" \
  {% for sram in srams | default([]) -%}
  "../00-openram-memgen/{{sram}}.db" \
  {% endfor %}
]

set_app_var link_library [concat "*" $target_library]

set_app_var power_enable_analysis true

#-------------------------------------------------------------------------
# Inputs
#-------------------------------------------------------------------------

read_verilog ../04-cadence-innovus-pnr/post-pnr.v
current_design {{design_name}}
link_design

read_saif ../05-synopsys-vcs-baglsim/$env(EVALNAME).saif -strip_path Top/DUT
read_parasitics -format spef ../04-cadence-innovus-pnr/post-pnr.spef

#-------------------------------------------------------------------------
# Timing constraints
#-------------------------------------------------------------------------

create_clock clk -name ideal_clock1 -period {{clock_period}}

#-------------------------------------------------------------------------
# Power Analysis
#-------------------------------------------------------------------------

update_power

#-------------------------------------------------------------------------
# Outputs
#-------------------------------------------------------------------------

report_power            > $env(EVALNAME)-summary.rpt
report_power -hierarchy > $env(EVALNAME)-detailed.rpt

exit
