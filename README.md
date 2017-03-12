# SILC_explorer

main.py = python script containing the code for bokeh server
  To run:
  => in terminal / command line go to directory above SILC_explorer
  => type "bokeh serve --show SILC_explorer"
  
main.ipynb = same as above, but in notebook to explore

1_data_prep.ipynb = translation of STATA file "tryout graph.do" to python
  => includes non-interactive bokeh chart of two examples given in email
  
description.html = html file used by main.py to generate final webpage

.gitignore = file that includes names of files/directories to ignore
  => includes "data/" directory containing SILC data
  => in local folder: save SILC data in folder "data" in this directory
