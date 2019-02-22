set display_name {Calibration}

set core [ipx::current_core]

set_property DISPLAY_NAME $display_name $core
set_property DESCRIPTION $display_name $core

set_property VENDOR {PSFC} $core
set_property VENDOR_DISPLAY_NAME {PSFC} $core
set_property COMPANY_URL {https://www.psfc.mit.edu/} $core
