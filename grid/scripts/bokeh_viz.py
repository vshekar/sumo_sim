#Bokeh viz
from bokeh.plotting import figure, show, curdoc
from bokeh.layouts import widgetbox
from bokeh.models.widgets.inputs import MultiSelect
from bokeh.layouts import layout
import pickle
import bokeh.palettes
from random import randint

lines ={}


def text_ip_handler(attr, old, new):
    #print(palette)
    #print("Old : " + str(old))
    #print("New : " + str(new))
    for label in old:
        lines[label].visible = False
    for label in new:
        lines[label].visible = True
        i = randint(0, 5)
        print(label, palette[i])
        lines[label].glyph.line_color = palette[i]


f = open('../output/result_list', 'rb')

result_list = pickle.load(f)
palette = bokeh.palettes.all_palettes['Viridis'][5]


p = figure(plot_width=1600, plot_height=800)

for label in result_list.keys():
    lines[label] = p.step(result_list[label]['trip_id'], result_list[label]['t_cost'], color="navy")
    lines[label].visible = False

#p.legend.location = "top_left"
#p.legend.click_policy = "hide"

text_input = MultiSelect(value=list(result_list.keys()),
                         options=list(zip(list(result_list.keys()), list(result_list.keys()))))

text_input.on_change("value", text_ip_handler)
curdoc().add_root(layout(text_input, p))