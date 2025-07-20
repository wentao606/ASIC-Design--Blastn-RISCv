#=========================================================================
# 04-cadence-innovus-pnr/run.tcl
#=========================================================================

#-------------------------------------------------------------------------
# Initial Setup
#-------------------------------------------------------------------------

# We need to include the lef files for the routing technology,
# standard cells, and any generated SRAMs.

set lef_files [list \
  "$env(ECE6745_STDCELLS)/rtk-tech.lef" \
  "$env(ECE6745_STDCELLS)/stdcells.lef" \
  {% for sram in srams | default([]) -%}
  "../00-openram-memgen/{{sram}}.lef" \
  {% endfor %}
]

set init_mmmc_file "setup-timing.tcl"
set init_verilog   "../02-synopsys-dc-synth/post-synth.v"
set init_top_cell  "{{design_name}}"
set init_lef_file  $lef_files

# The standard cells use VDD/VSS but OpenRAM uses vdd/gnd

set init_pwr_net   {VDD vdd}
set init_gnd_net   {VSS gnd}

init_design

# Set the process node to 45nm for technology-specific optimizations

setDesignMode -process 45

# Turn off signal integrity analysis (i.e., signal cross-talk)

setDelayCalMode -SIAware false

# Turn off useful clock skew (i.e., the tools will try to reduce the
# clock skew across all flip-flops)

setOptMode -usefulSkew false

# Add in additional hold target slack to force Cadence Innovus to
# work harder; this way if it misses by a little we will still end up
# with positive hold slack.

setOptMode -holdTargetSlack 0.010

# Specify which standard cells to use when fixing hold time violations

setOptMode -holdFixingCells {
  BUF_X1 BUF_X1 BUF_X2 BUF_X4 BUF_X8 BUF_X16 BUF_X32
}

# Increase the number of significant digits in reports

set report_precision 4

#-------------------------------------------------------------------------
# Floorplanning
#-------------------------------------------------------------------------
# There are two primary floorplanning options: automatic and fixed.
#
# The automatic floorplan option will determine the overall dimensions
# given a target aspect ratio and placement density. Here is an
# example which targets an aspect ratio of 1.0 and placement density
# of 70% with a 4um border around the outside of the core area for the
# power ring.
#
#  floorPlan -r 1.0 0.70 4.0 4.0 4.0 4.0
#
# The fixed floorplan option uses a given width and height. Here is an
# example which targets a width of 200um and height of 100um with a
# 4um border around the outside of the core are for the power ring.
#
#  floorPlan -d 200 100 4.0 4.0 4.0 4.0
#

floorPlan {{ floorplan | default("-r 1.0 0.70 4.0 4.0 4.0 4.0") }}

#-------------------------------------------------------------------------
# Placement
#-------------------------------------------------------------------------

# Add a small halo around all SRAMs to help with congestion

addHaloToBlock 4.8 4.8 4.8 4.8 -allMacro

{% if srams is defined %}
# Preliminary concurrent placement of standard cells and SRAMs

set_macro_place_constraint -pg_resource_model {metal1 0.2}
place_design -concurrent_macros
refine_macro_place

{% endif %}
# Place and optimize the design 

place_opt_design

# Add tiehi/tielo cells which are used to connect constant values to
# either vdd or ground.

addTieHiLo -cell "LOGIC1_X1 LOGIC0_X1"

# Try to place the input/output pins so they are close to the
# standard-cells they are connected to

assignIoPins -pin *

#-------------------------------------------------------------------------
# Power Routing
#-------------------------------------------------------------------------

globalNetConnect VDD -type pgpin -pin VDD -all -verbose
globalNetConnect VSS -type pgpin -pin VSS -all -verbose

globalNetConnect VDD -type pgpin -pin vdd -all -verbose
globalNetConnect VSS -type pgpin -pin gnd -all -verbose

globalNetConnect VDD -type tiehi -pin VDD -all -verbose
globalNetConnect VSS -type tielo -pin VSS -all -verbose

# Route the M1 tracks for each row of standard cells

sroute -nets {VDD VSS}

# Route a power ring on M8 and M9 around the outside of the core area

addRing \
  -nets {VDD VSS} -width 0.8 -spacing 0.8 \
  -layer [list top 9 bottom 9 left 8 right 8]

# Route horizontal stripes on M9 for the power grid

addStripe \
  -nets {VSS VDD} -layer 9 -direction horizontal \
  -width 0.8 -spacing 4.8 \
  -set_to_set_distance 11.2 -start_offset 2.4

# Route vertical stripes on M for the power grid

addStripe \
  -nets {VSS VDD} -layer 8 -direction vertical \
  -width 0.8 -spacing 4.8 \
  -set_to_set_distance 11.2 -start_offset 2.4

#-------------------------------------------------------------------------
# Clock-Tree Synthesis
#-------------------------------------------------------------------------

# Create the clock tree specification from the timing constraints

create_ccopt_clock_tree_spec

# Control an optimization that allows Cadence Innovus to decide to add
# non-zero clock insertion source latency. Turning this on will
# complicate back-annotated gate-level simulation, but may enable
# closing timing for larger blocks.

set_ccopt_property update_io_latency {{ update_io_latency | default("false") }}

# Synthesize the clock tree

clock_opt_design

# Fix setup time violations by reducing the delay of the slow paths

optDesign -postCTS -setup

# Fix hold time violations by increasing the delay of the fast paths

optDesign -postCTS -hold

#-------------------------------------------------------------------------
# Routing
#-------------------------------------------------------------------------

# Route the design

routeDesign

# Fix setup time violations by reducing the delay of the slow paths

optDesign -postRoute -setup

# Fix hold time violations by increasing the delay of the fast paths

optDesign -postRoute -hold

# Fix design rule violations

optDesign -postRoute -drv

# Extract the interconnect parasitics

extractRC

#-------------------------------------------------------------------------
# Finishing
#-------------------------------------------------------------------------

# Add filler cells to complete each row of standard cells

setFillerMode -core {FILLCELL_X4 FILLCELL_X2 FILLCELL_X1}
addFiller

# Check the final physical design

verifyConnectivity
verify_drc

#-------------------------------------------------------------------------
# Outputs
#-------------------------------------------------------------------------

# Output the design which can be loaded into Cadence Innovus later

saveDesign post-pnr.enc

# Output the post-pnr gate-level netlist

saveNetlist post-pnr.v

# Output the interconnect parasitics in SPEF format for power analsys

rcOut -rc_corner typical -spef post-pnr.spef

# Output the timing delays in SDF format for back-annotated gate-level sim

write_sdf post-pnr.sdf

# Output the SDC file so we can check for clock source insertion latency

write_sdc post-pnr.sdc

# Merge the standard-cell layout with the place and routed design to
# stream out the final layout for the block; note that we need to
# include the gds files for the standard cells and any generated
# SRAMs.

set gds_files [list \
  "$env(ECE6745_STDCELLS)/stdcells.gds" \
  {% for sram in srams | default([]) -%}
  "../00-openram-memgen/{{sram}}.gds" \
  {% endfor %}
]

streamOut post-pnr.gds -merge $gds_files \
  -mapFile "$env(ECE6745_STDCELLS)/rtk-stream-out.map"

# Report the critical path (i.e., setup-time constraint)

report_timing -late  -path_type full_clock -net > timing-setup.rpt

# Report the short path (i.e., hold-time constraint)

report_timing -early -path_type full_clock -net > timing-hold.rpt

# Report the area broken down by module

report_area > area.rpt

exit
