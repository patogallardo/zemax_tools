echo "Make sure OpticStudio is running."
SET MY_PATH=C:\Users\pgall\OneDrive - The University of Chicago\Github\zemax_tools\ZOS_API_scripts\export_lenses_info

python "%MY_PATH%\S4cam_export_lens_cads.py"
python "%MY_PATH%\S4cam_export_lens_surfaces.py"
python "%MY_PATH%\S4cam_export_lens_surfaces2.py"
python "%MY_PATH%\S4cam_plot_lens_shape_and_mk_table.py"

if not exist "CAD\tables_and_cad" mkdir "CAD\tables_and_cad"

xcopy /Y "CAD\*.stp" "CAD\tables_and_cad"

xcopy /Y "CAD\sag_tables\*.png" "CAD\tables_and_cad"
xcopy /Y "CAD\sag_tables\*.pdf" "CAD\tables_and_cad"

xcopy /Y "CAD\surface_definitions\lensDef_L1\*.png" "CAD\tables_and_cad"
xcopy /Y "CAD\surface_definitions\lensDef_L1\*.pdf" "CAD\tables_and_cad"

xcopy /Y "CAD\surface_definitions\lensDef_L2\*.png" "CAD\tables_and_cad"
xcopy /Y "CAD\surface_definitions\lensDef_L2\*.png" "CAD\tables_and_cad"

xcopy /Y "CAD\surface_definitions\lensDef_L3\*.png" "CAD\tables_and_cad"
xcopy /Y "CAD\surface_definitions\lensDef_L3\*.png" "CAD\tables_and_cad"

xcopy /Y "%MY_PATH%\lens_prescription_formulas\*.png" "CAD\tables_and_cad"
