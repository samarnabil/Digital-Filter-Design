# Bokeh Libraries
from functools import partial
from bokeh.models.layouts import Spacer
from bokeh.models.widgets.markups import Div
from AllPassFilter import AllPass
from bokeh.io import output_file, curdoc
from bokeh.models import Circle,TapTool, CustomJS, ColumnDataSource, TextInput, HoverTool,Button,CheckboxButtonGroup, BoxEditTool, renderers
from bokeh.models.glyphs import Scatter
from bokeh.models.tools import PointDrawTool
from bokeh.models.widgets.groups import CheckboxGroup
from bokeh.plotting import figure, show, reset_output
from bokeh.events import DoubleTap,ButtonClick, MouseLeave, PanStart, Tap, PanEnd
from bokeh.layouts import grid, row,column,layout, gridplot
from Test import *
from AllPassFilter import *


# My x-y coordinate data
unit_source = ColumnDataSource(data=dict(x=[0],y=[0]))
zeros_source = ColumnDataSource(data=dict(x=[],y=[]))
poles_source = ColumnDataSource(data=dict(x=[],y=[]))
mg_source = ColumnDataSource(data=dict(x=[],y=[]))
phase_source = ColumnDataSource(data=dict(x=[],y=[]))

#sources
fil1_poles_source = ColumnDataSource(data=dict(x=[0.3,1],y=[-0.6,1]))
fil1_phase_source = ColumnDataSource(data=dict(x=[],y=[]))
fil1_zeros_source = ColumnDataSource(data=dict(x=[],y=[]))
fil2_poles_source = ColumnDataSource(data=dict(x=[0.36],y=[0.73]))
fil2_zeros_source = ColumnDataSource(data=dict(x=[],y=[]))
fil2_phase_source = ColumnDataSource(data=dict(x=[],y=[]))

TOOLTIPS = [("index", "$index"),("(x,y)", "($x, $y)")]

# Create a figure
fig = figure(title='My Coordinates',
            tools="tap", tooltips=TOOLTIPS,
            x_range=[-2.5, 2.5], y_range=[-2.5, 2.5],
            toolbar_location='above')

fig2 = figure(title='Magnitude',
            tools="tap,reset,pan", tooltips=TOOLTIPS,
            plot_height=300,plot_width=600,
            y_range=[0, 10],
            toolbar_location='above')

fig3 = figure(title='Phase',
            tools="tap,reset,pan", tooltips=TOOLTIPS,
            plot_height=300,plot_width=600,
            toolbar_location='above')

# Draw the coordinates as circles
unit_circle = fig.circle(0, 0, radius = 1,
           line_color='gold', fill_alpha=0, line_width=2)

zeros = fig.circle('x', 'y', source= zeros_source,
           line_color='blue', size=15, fill_alpha=0, line_width=2)

poles = fig.x('x', 'y', source= poles_source,
           line_color='blue', size=15, line_width=3)

# Selection
selected_circle = Circle(fill_alpha=1, fill_color='red', line_color='red')
nonselected_circle = Circle(fill_alpha=0, line_color='blue', line_width=2)
zeros.selection_glyph = selected_circle
zeros.nonselection_glyph = nonselected_circle


# Selection
selected_pole = Scatter(marker='cross', fill_alpha=1, fill_color='red', line_color='red',line_width=3)
nonselected_pole = Scatter(marker='cross', fill_alpha=0, line_color='blue', line_width=3)
poles.selection_glyph = selected_pole
poles.nonselection_glyph = nonselected_pole

zero_mode = False
poles_mode = False
zero_index = None
poles_index = None



def update():
    mg_source.data['x'],mg_source.data['y'] = z_transform.PlotMagnitude()
    phase_source.data['x'],phase_source.data['y'] = z_transform.PlotPhase()
    fig2.line(source= mg_source)
    fig3.line(source= phase_source)
    
isZero = False 
def get_clicked_point(attr, old, new):
    global zero_index,poles_index, isZero
    if len(zeros_source.selected.indices)>0:
        zero_index = zeros_source.selected.indices[0]
        isZero = True
    if  len(poles_source.selected.indices)>0:
        poles_index = poles_source.selected.indices[0]
        isZero = False
    


def clear_zeros():
    zeros_source.data['x'].clear()
    zeros_source.data['y'].clear()
    new_data = {'x' : zeros_source.data['x'],'y' : zeros_source.data['y'],}
    zeros_source.data = new_data
    z_transform.update_zeros([])
    update()
    
def clear_poles():
    poles_source.data['x'].clear()
    poles_source.data['y'].clear()
    new_data = {'x' : poles_source.data['x'],'y' : poles_source.data['y'],}
    poles_source.data = new_data
    z_transform.update_poles([])
    update()
    
def delete_selected_point():
    print("filter:",z_transform.get_AllPassFilter())
    global zero_index,poles_index,conjugate_mode
    print("applied:",z_transform.getAppliedIndex())
    if len(zeros_source.selected.indices)>0:
        conj_X_Zeros = (zeros_source.data['x'][zero_index])
        conj_Y_Zeros = -(zeros_source.data['y'][zero_index])
        zeros_source.data['x'].pop(zero_index)
        zeros_source.data['y'].pop(zero_index)

        # find and delete conjugate
        if conjugate_mode.active == [0]:
            zeros_source.data['x'].remove(conj_X_Zeros)
            zeros_source.data['y'].remove(conj_Y_Zeros)
        
        zeros_source.selected.indices=[]
        zero_index=None
        new_data = {'x' : zeros_source.data['x'],'y' : zeros_source.data['y'],}
        zeros_source.data = new_data
        z_transform.update_zeros([])
        for x,y in zip(zeros_source.data['x'],zeros_source.data['y']):
            z_transform.setZero(x,y)
        update()

    if len(poles_source.selected.indices)>0:
        conj_X_Poles = (poles_source.data['x'][poles_index])
        conj_Y_Poles = -(poles_source.data['y'][poles_index])
        poles_source.data['x'].pop(poles_index)
        poles_source.data['y'].pop(poles_index)

        # find and delete conjugate
        if conjugate_mode.active == [0]:
            poles_source.data['x'].remove(conj_X_Poles)
            poles_source.data['y'].remove(conj_Y_Poles)

        poles_source.selected.indices=[]
        poles_index=None
        new_data = {'x' : poles_source.data['x'],'y' : poles_source.data['y'],}
        poles_source.data = new_data
        z_transform.update_poles([])
        for x,y in zip(poles_source.data['x'],poles_source.data['y']):
            z_transform.setPole(x,y)
        update()
    
    



# zeros_source.on_change('value', get_clicked_point)
zeros_source.selected.on_change('indices', get_clicked_point)
poles_source.selected.on_change('indices', get_clicked_point)

# Add
def add(event):
    new_x = event.x
    new_y = event.y
    new_data = {'x' : [new_x],'y' : [new_y],}
    conj_new_data = {'x' : [new_x], 'y': [-new_y]}
    if zero_mode:
        if conjugate_mode.active == [0]:
            zeros_source.stream(conj_new_data)
        zeros_source.stream(new_data)
        z_transform.setZero(new_x,new_y)
    if poles_mode:
        if conjugate_mode.active == [0]:
            poles_source.stream(conj_new_data)
        poles_source.stream(new_data)
        z_transform.setPole(new_x,new_y)
    
    update()
 
def toggle_mode_poles(event):
    global poles_mode,zero_mode
    zero_mode = False
    poles_mode = not(poles_mode)


temp=[]

def toggle_mode(active):
    global zero_mode,poles_mode,temp
    if active == [0]:
        temp =[0]
        poles_mode = not(poles_mode)

    if active ==[1]:
        temp = [1]
        zero_mode = not(poles_mode)

    if active ==[]:
        temp = []
        zero_mode = False
        poles_mode = False

    if active == [0,1]:

        if temp == [1]:
            checkbox_button_group.active = [0]
            zero_mode = False
            poles_mode = True
        else:
            checkbox_button_group.active = [1]
            zero_mode = True
            poles_mode = False
            
conj_isChecked = False
def toggle_conj_mode(active):
    global conj_isChecked
    conj_isChecked = not(conj_isChecked)

    clear_zeros()
    clear_poles()

drag_index_zero =None
drag_index_pole =None
x_value_zero = None
y_value_zero = None
x_value_pole = None
y_value_pole = None

def catch_drag(event):
    global drag_index_zero, x_value_zero, y_value_zero, x_value_pole, y_value_pole, drag_index_pole, zero_index
    #zeros
    if isZero:
        x_value_zero = zeros_source.data['x'][zero_index]
        y_value_zero = zeros_source.data['y'][zero_index]
        drag_index_zero = zeros_source.data['y'].index(-y_value_zero)
    #poles
    else:
        x_value_pole = poles_source.data['x'][poles_index]
        y_value_pole = poles_source.data['y'][poles_index]
        drag_index_pole = poles_source.data['y'].index(-y_value_pole)

def update_drag(event):
    global zero_index, poles_index, drag_index_pole, drag_index_zero
    if conj_isChecked == True:
        #zeros
        if isZero:
            new_x = zeros_source.data['x'][zero_index]
            new_y = -zeros_source.data['y'][zero_index]
            zeros_source.data['x'].pop(drag_index_zero)
            zeros_source.data['y'].pop(drag_index_zero)
            new_node = {'x' : [new_x],'y' : [new_y]}
            zeros_source.stream(new_node)
            z_transform.setZero(zeros_source.data['x'][zero_index],-zeros_source.data['y'][zero_index])
            new_data = {'x' : zeros_source.data['x'],'y' : zeros_source.data['y'],}
            zeros_source.data = new_data
        #poles
        else:
            new_x = poles_source.data['x'][poles_index]
            new_y = -poles_source.data['y'][poles_index]
            poles_source.data['x'].pop(drag_index_pole)
            poles_source.data['y'].pop(drag_index_pole)
            new_node = {'x' : [new_x],'y' : [new_y]}
            poles_source.stream(new_node)
            z_transform.setZero(poles_source.data['x'][poles_index],-poles_source.data['y'][poles_index])
            new_data = {'x' : poles_source.data['x'],'y' : poles_source.data['y'],}
            poles_source.data = new_data


    else:
        z_transform.update_zeros([])
        for x,y in zip(zeros_source.data['x'],zeros_source.data['y']):
            z_transform.setZero(x,y)

        z_transform.update_poles([])
        for x,y in zip(poles_source.data['x'],poles_source.data['y']):
            z_transform.setPole(x,y)

    update()

fig.on_event(DoubleTap,add)
fig.on_event(PanEnd,update_drag)
fig.on_event(PanStart,catch_drag)


#Drag
drag_tool = BoxEditTool(renderers=[zeros, poles],)
fig.add_tools(drag_tool)


# draw_tool = PointDrawTool(renderers=[zeros, poles], empty_value='black')
# fig.add_tools(draw_tool)


LABELS = ["Poles", "Zeros"]

checkbox_button_group = CheckboxButtonGroup(labels=LABELS, active=[])
checkbox_button_group.on_click(toggle_mode)

delete_button = Button(label="Delete", button_type="danger")
delete_button.on_click(delete_selected_point)

delete_zeros_button = Button(label="clear zeros", button_type="warning")
delete_zeros_button.on_click(clear_zeros)

delete_poles_button = Button(label="clear poles", button_type="warning")
delete_poles_button.on_click(clear_poles)

CHECK_LABELS = ["Conjugate"]
conjugate_mode = CheckboxGroup(labels=CHECK_LABELS , active=[])
conjugate_mode.on_click(toggle_conj_mode)
z_transform= ZTransform()


#################################### ALL-PASS ##########################################

#functions
def draw_filter(pole_source,zero_source):
    filter = AllPass()
    z_transform.get_AllPassFilter().append(filter)
    for x,y in zip(pole_source.data['x'],pole_source.data['y']):
        filter.SetPole(x, y)

    new_data = {'x' : [x.getReal() for x in filter.GetZero()],'y' : [x.getImaginary() for x in filter.GetZero()],}
    zero_source.stream(new_data)

def draw_filter_phase(phase_source,phase_fig,index):
    phase_source.data['x'],phase_source.data['y'] = z_transform.PlotAllPassPhase_V2(index)
    phase_fig.line(source= phase_source)
    

def addFilter(btn_name):
    print("attr",btn_name)
    global zeros_source_to_be_printed,poles_source_to_be_printed
    if btn_name == "add_filter1":
        z_transform.setAppliedIndex(0)
        zeros_source_to_be_printed.data = dict(fil1_zeros_source.data)
        poles_source_to_be_printed.data = dict(fil1_poles_source.data)
    if btn_name == "add_filter2":
        z_transform.setAppliedIndex(1)
        zeros_source_to_be_printed.data = dict(fil2_zeros_source.data)
        poles_source_to_be_printed.data = dict(fil2_poles_source.data)
    update()    
        
    

def remove_filter():
    global zeros_source_to_be_printed,poles_source_to_be_printed
    zeros_source_to_be_printed.data.clear()
    poles_source_to_be_printed.data.clear()
    z_transform.setAppliedIndex(None)
    # z_transform.getZeros()
    update()    



#### filter 1
allPass_fig1 = figure(title='Filter 1',tools="tap,reset", tooltips=TOOLTIPS,
            x_range = [-2.5,2.5], y_range = [-2.5,2.5],
            plot_height=250,plot_width=250,toolbar_location=None)
filter1_circle = allPass_fig1.circle(0, 0, radius = 1,line_color='gold', fill_alpha=0, line_width=2)
filter1_phase = figure(title='Phase',tools="tap,reset", tooltips=TOOLTIPS,
            plot_height=250,plot_width=350,toolbar_location=None)

draw_filter(fil1_poles_source,fil1_zeros_source)
draw_filter_phase(fil1_phase_source,filter1_phase,0)

zeros_source_to_be_printed = ColumnDataSource(data=dict(x=[],y=[]))
poles_source_to_be_printed = ColumnDataSource(data=dict(x=[],y=[]))

zeros_filter_to_be_addeed = fig.circle('x', 'y', source= zeros_source_to_be_printed,
        line_color='black', size=15, fill_alpha=0, line_width=5,name='polpol')
poles_filter_to_be_addeed = fig.x('x', 'y', source= poles_source_to_be_printed,
        line_color='black', size=15, fill_alpha=0, line_width=5,name='polpol')

#zeros
filter1_zeros = allPass_fig1.circle('x', 'y', source= fil1_zeros_source,
           line_color='blue', size=7, fill_alpha=0, line_width=2)
#poles
filter1_poles = allPass_fig1.x('x', 'y', source= fil1_poles_source,
           line_color='blue', size=10, line_width=3)

add_filter1 = Button(label="Apply", button_type="success")
remove_filter1 = Button(label="Remove", button_type="danger")
add_filter1.on_click(partial(addFilter, btn_name="add_filter1"))
remove_filter1.on_click(remove_filter)


#### filter 2
allPass_fig2 = figure(title='Filter 2',tools="tap,reset", tooltips=TOOLTIPS,
            x_range = [-2.5,2.5], y_range = [-2.5,2.5],
            plot_height=250,plot_width=250,toolbar_location=None)
filter2_circle = allPass_fig2.circle(0, 0, radius = 1,line_color='gold', fill_alpha=0, line_width=2)
filter2_phase = figure(title='Phase',tools="tap,reset", tooltips=TOOLTIPS,
            plot_height=250,plot_width=350,toolbar_location=None)


draw_filter(fil2_poles_source,fil2_zeros_source)
draw_filter_phase(fil2_phase_source,filter2_phase,1)

#zeros
filter2_zeros = allPass_fig2.circle('x', 'y', source= fil2_zeros_source,
           line_color='blue', size=7, fill_alpha=0, line_width=2)
#poles
filter2_poles = allPass_fig2.x('x', 'y', source= fil2_poles_source,
           line_color='blue', size=10, line_width=3)
add_filter2 = Button(label="Apply", button_type="success")
remove_filter2= Button(label="Remove", button_type="danger")
add_filter2.on_click(partial(addFilter, btn_name="add_filter2"))
remove_filter2.on_click(remove_filter)


########################################################################################

######################### Custom Filter ############################
custom_unit_source = ColumnDataSource(data=dict(x=[0],y=[0]))
custom_zeros_source = ColumnDataSource(data=dict(x=[],y=[]))
custom_poles_source = ColumnDataSource(data=dict(x=[],y=[]))
custom_phase_source = ColumnDataSource(data=dict(x=[],y=[]))

custom_fig = figure(title='My Custom Filter',
            tools="tap", tooltips=TOOLTIPS,
            plot_height=400,plot_width=400,
            x_range=[-2.5, 2.5], y_range=[-2.5, 2.5],
            toolbar_location='above')

custom_phase_fig = figure(title='Phase',
            tools="tap,reset", tooltips=TOOLTIPS,
            plot_height=400,plot_width=600,
            toolbar_location=None)

custom_unit_circle = custom_fig.circle(0, 0, radius = 1,
           line_color='gold', fill_alpha=0, line_width=2)

custom_zeros = custom_fig.circle('x', 'y', source= custom_zeros_source,
           line_color='blue', size=15, fill_alpha=0, line_width=2)

custom_poles = custom_fig.x('x', 'y', source= custom_poles_source,
           line_color='blue', size=15, line_width=3)


custom_zero_mode = False
custom_poles_mode = False
custom_zero_index = None
custom_poles_index = None
custom_filter = AllPass()


custom_temp=[]
def custom_toggle_mode(active):
    global custom_zero_mode,custom_poles_mode,custom_temp
    if active == [0]:
        custom_temp =[0]
        custom_poles_mode = not(custom_poles_mode)

    if active ==[1]:
        custom_temp = [1]
        custom_zero_mode = not(custom_poles_mode)

    if active ==[]:
        custom_temp = []
        custom_zero_mode = False
        custom_poles_mode = False

    if active == [0,1]:

        if custom_temp == [1]:
            custom_checkbox_button_group.active = [0]
            custom_zero_mode = False
            custom_poles_mode = True
        else:
            custom_checkbox_button_group.active = [1]
            custom_zero_mode = True
            custom_poles_mode = False

def draw_custom_phase():
    custom_phase_source.data['x'],custom_phase_source.data['y'] = z_transform.PlotCustomPhase(custom_filter)
    custom_phase_fig.line(source= custom_phase_source)

def custom_add(event):
    global custom_filter
    new_x = event.x
    new_y = event.y
    
    if custom_poles_mode:
        new_data = {'x' : [new_x],'y' : [new_y],}
        custom_poles_source.stream(new_data)
        custom_filter.SetPole(round(new_x,2), round(new_y,2))

        
        new_zero = {'x' : [x.getReal() for x in custom_filter.GetZero()],'y' : [x.getImaginary() for x in custom_filter.GetZero()],}
        custom_zeros_source.stream(new_zero)

    if custom_zero_mode:
        new_data = {'x' : [new_x],'y' : [new_y],}
        custom_zeros_source.stream(new_data)
        custom_filter.SetZero(round(new_x,2), round(new_y,2))
        new_pole = {'x' : [x.getReal() for x in custom_filter.GetPole()],'y' : [x.getImaginary() for x in custom_filter.GetPole()],}
        custom_poles_source.stream(new_pole)

    draw_custom_phase()   
   

def custom_clear():
    global zeros_source_to_be_printed,poles_source_to_be_printed
    custom_poles_source.data['x'].clear()
    custom_poles_source.data['y'].clear()
    new_data1 = {'x' : custom_poles_source.data['x'],'y' : custom_poles_source.data['y'],}
    custom_poles_source.data = dict(new_data1)
    custom_zeros_source.data['x'].clear()
    custom_zeros_source.data['y'].clear()
    new_data2 = {'x' : custom_zeros_source.data['x'],'y' : custom_zeros_source.data['y'],}
    custom_zeros_source.data = dict(new_data2)
    custom_filter.ClearAll()
    zeros_source_to_be_printed.data.clear()
    poles_source_to_be_printed.data.clear()
    z_transform.setAppliedIndex(None)
    draw_custom_phase()
    update()

applied = False
def add_custom_filter():
    global zeros_source_to_be_printed,poles_source_to_be_printed, applied
    applied = True
    z_transform.setAppliedIndex(2)
    zeros_source_to_be_printed.data = dict(custom_zeros_source.data)
    poles_source_to_be_printed.data = dict(custom_poles_source.data)
    z_transform.get_AllPassFilter().append(custom_filter)
    update()    



def remove_custom_filter():
    global zeros_source_to_be_printed,poles_source_to_be_printed,applied
    if applied:
        zeros_source_to_be_printed.data.clear()
        poles_source_to_be_printed.data.clear()
        z_transform.setAppliedIndex(None)
        z_transform.get_AllPassFilter().pop()
        custom_clear()
    applied = False  

    
custom_fig.on_event(DoubleTap,custom_add)
CUSTOM_LABELS = ["Poles", "Zeros"]
custom_checkbox_button_group = CheckboxButtonGroup(labels=CUSTOM_LABELS, active=[])
custom_checkbox_button_group.on_click(custom_toggle_mode)

custom_clear_button = Button(label="Clear", button_type="danger")
custom_clear_button.on_click(custom_clear)

add_custom_filter_button = Button(label="Apply", button_type="success")
remove_custom_filter_button = Button(label="Remove", button_type="danger")
add_custom_filter_button.on_click(add_custom_filter)
remove_custom_filter_button.on_click(remove_custom_filter)

####################################################################

f1 = column(fig)
f2 = column(fig2,fig3)
f3 = row(checkbox_button_group)
f4=row(delete_button)
f5 =row(delete_zeros_button,delete_poles_button)
#all pass
#filter1
f6 = row (allPass_fig1,filter1_phase)
f1btn = row(add_filter1,remove_filter1)
fil1 = column(f6,f1btn)
#filter2
f7 = row (allPass_fig2,filter2_phase)
f2btn = row(add_filter2,remove_filter2)
fil2 = column(f7,f2btn)
#custom
custom_unit = column(custom_fig)
custom_col = column(custom_phase_fig)
cst_ad = row(custom_checkbox_button_group)
cst_clr = row(custom_clear_button)
ad_rm = row(add_custom_filter_button,remove_custom_filter_button)
#spaces
top = Spacer(width=1, height=15)
header_spacer = Spacer(width=30, height=0)
middle = Spacer(width=30, height=0)
button_space = Spacer(width=45, height=0)
division = Spacer(width=1, height=40)

#headers
Header1 = Div(text='<h1 style="color: black">Pole-Zero Placement</h1>')
Header2 = Div(text='<h1 style="color: black">All Pass Library</h1>')
Header3 = Div(text='<h1 style="color: black">Customize your Filter!</h1>')

x= layout([
    [Header1],
    [middle,fig,middle,f2],
    [button_space,f3, f4,conjugate_mode],
    [button_space,f5],
    [division],
    [Header2],
    [middle,fil1 ,middle, fil2],
    [division],
    [Header3],
    [middle,custom_unit,middle,custom_col],
    [button_space,cst_ad,add_custom_filter_button],
    [button_space,custom_clear_button,remove_custom_filter_button],
])

curdoc().add_root(x)