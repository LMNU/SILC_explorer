from os.path import dirname, join

import numpy as np
import pandas.io.sql as psql
import sqlite3 as sql
import pandas as pd

from bokeh.plotting import figure
from bokeh.layouts import layout, widgetbox
from bokeh.models import ColumnDataSource, HoverTool, Div, CustomJS, Range1d, CategoricalColorMapper
from bokeh.models.widgets import Slider, Select, TextInput, CheckboxGroup
from bokeh.io import curdoc
from bokeh.palettes import *

# read the csv
df = pd.read_csv(join(dirname(__file__), 'data/BE_2012_b1.txt'),sep="\t")

# read the html
desc = Div(text=open(join(dirname(__file__), "description.html")).read(), width=800)


# Create Column Data Source that will be used by the plot
source = ColumnDataSource(data=dict(x=[], y=[], grouped=[], lhw=[], yivwg=[],size=[]))


# define a function to select the data depending on certain values of a variable/column
def select_data():
    
    #start with the whole data frame
    selected = df
    
    # read values from the input controls
    selection_val = select_select.value
    selection_title = select_select.title
    
    # select the required rows from the data frame
    if selection_title == "Select gender":
        if (selection_val != "All"):
            selected = selected[selected.dgn == int(selection_val)]    
    elif selection_title == "Select education":
        if (selection_val != "All"):
            selected = selected[selected.deh == int(selection_val)]   
    
    # return the selected rows
    return selected


# define function to update the column data source depending on the selected data and the grouping variable
def update():
    
    # get the selected rows
    mydf = select_data()
    
    # read the values from the input controls
    x_name = axis_map[x_axis_select.value]
    y_name = axis_map[y_axis_select.value]
    group_val = groups_map[groupby_select.value]
    
    # calculate the requested means
    sumdf = pd.merge(mydf.groupby(group_val)["lhw","yivwg"].mean().reset_index(),
         mydf[group_val].value_counts().sort_index().reset_index().rename(columns={group_val:"counts","index":group_val}))
    
    # set the axis labels
    p.xaxis.axis_label = x_axis_select.value
    p.yaxis.axis_label = y_axis_select.value
    
    # set the axis ranges
    if y_axis_select.value == "Income":
        p.y_range = Range1d(0,35)
    
    # set the plot title
    p.title.text = "%d data selected" % len(mydf)
    
    # update the data attribute of the column data source
    source.data = dict(
        x=sumdf[x_name],
        y=sumdf[y_name],
        size=sumdf["counts"]/100,
        grouped=sumdf[group_val],
        lhw=sumdf["lhw"],
        yivwg=sumdf["yivwg"],
    )


# create mappings of variable names to column names
axis_map = {
    "Income": "lhw",
    "Working hours": "yivwg",
}
groups_map = {"Education": "deh",
              "Gender": "dgn"}


# create list of options to show in drop down menu's
gender_list = list(np.unique(df['dgn']))
education_list = list(np.unique(df['deh']))

gender_list_str = ["All"]+[str(x) for x in gender_list]
education_list_str = ["All"]+[str(x) for x in education_list]


# callback using custom javascript (but see instead easier way below)
## create callback function to change the / menu when selecting an option in the selection menu
#callback = CustomJS(args=dict(sselect=select_select), code="""
#        var gbselectvalue = cb_obj.get('value')
#        if (gbselectvalue == "Education"){
#            sselect.title = "Select gender";
#            sselect.options = ["All","0","1"];
#            sselect.value = "All";
#        } else {
#            sselect.title = "Select education";
#            sselect.options = ["All","0","1","2","3","4","5"];
#            sselect.value = "All";
#        }
#        source.trigger('change');
#    """)
#groupby_select = Select(title="Group by", options=sorted(groups_map.keys()), value="Education", callback=callback)


# Define a callback function
def callback(attr, old, new):
    if groupby_select.value == 'Education':
        select_select.title = "Select gender";
        select_select.options = gender_list_str;
        select_select.value = "All";
    else:
        select_select.title = "Select education";
        select_select.options = education_list_str;
        select_select.value = "All";

        
# create input controls
x_axis_select = Select(title="X Axis", options=sorted(axis_map.keys()), value="Working hours")
y_axis_select = Select(title="Y Axis", options=sorted(axis_map.keys()), value="Income")
select_select = Select(title="Select gender", options=gender_list_str, value = 'All')
groupby_select = Select(title="Group by", options=sorted(groups_map.keys()), value="Education")


# add callback to the groupby_select input control
groupby_select.on_change('value', callback)


# add input controls to list
controls = [x_axis_select, y_axis_select, groupby_select, select_select]


# add update function to on_change attribute of each input control 
for control in controls:
    control.on_change('value', lambda attr, old, new: update())

    
# add controls to widget box
inputs = widgetbox(*controls, sizing_mode='fixed')
    

# Create hover tools
hover = HoverTool(tooltips=[
    ("Group", "@grouped"),
    ("Income", "@lhw"),
    ("Working hours", "@yivwg"),
    ("Number of people","@size")
])


# Make a color mapper: color_mapper
color_mapper = CategoricalColorMapper(factors=education_list, palette=Spectral6)


# create plot
p = figure(plot_height=600, plot_width=700, title="", toolbar_location=None, tools=[hover])
p.circle(x="x", y="y", source=source, size="size", color=dict(field='grouped', transform=color_mapper), legend='grouped')


# Set the legend.location attribute of the plot to 'top_right'
p.legend.location = 'bottom_right'


# add all the elements to a layout
l = layout([
    [desc],
    [inputs, p],
], sizing_mode='fixed')


# initial load of the data
update()


# add layout to current document
curdoc().add_root(l)


# add title to current document
curdoc().title = "Experiment"