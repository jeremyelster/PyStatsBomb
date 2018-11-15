import numpy as np
from bokeh.layouts import widgetbox, row, column
from bokeh.models import (
    ColumnDataSource, RangeSlider, Select, HoverTool, LabelSet)
from bokeh.models import Span, Label, Panel
from bokeh.plotting import figure
from bokeh.palettes import Spectral6, Viridis10
from bokeh.transform import factor_cmap
from bokeh.models.widgets import CheckboxGroup


def player_tab(passing_model):

    positions = list(passing_model.Position.unique())
    position_details = list(passing_model.Position_Detail.unique())
    position_color = factor_cmap(
        'Position_Detail', palette=Viridis10, factors=position_details)
    select = Select(title="Position:", value="Midfield", options=positions)

    max_passes = int(passing_model["Passes"].max())
    pass_slider = RangeSlider(
        start=0, end=max_passes, value=(70, max_passes),
        step=5, title="Number of Passes")

    def make_dataset(select_value, pass_slider_min, pass_slider_max):
        source = ColumnDataSource(
            data=passing_model.loc[
                (passing_model["Position"] == select_value) &
                (passing_model["Passes"] >= pass_slider_min) &
                (passing_model["Passes"] <= pass_slider_max), :])
        source.data["Pass_Size"] = source.data["Passes"] / 10
        source.data["xP_Mean_mean"] = np.repeat(source.data["xP_Mean"].mean(), len(source.data["Passes"]))
        source.data["xP_Rating_mean"] = np.repeat(source.data["xP_Rating"].mean(), len(source.data["Passes"]))
        return source

    def make_plot(source):
        """Need to return the span so we can update them in callback (I think)
        """
        # Set up Plot Figure
        plot_size_and_tools = {
            'plot_height': 100, 'plot_width': 1000,
            'x_range': (source.data["xP_Rating"].min() * .8, source.data["xP_Rating"].max() * 1.2),
            'y_range': (source.data["xP_Mean"].min() * .8, source.data["xP_Mean"].max() * 1.2)}
        plot = figure(tools=["tap", "pan", "wheel_zoom",'box_select', 'reset', 'help'], title="Expected Passes v. Pass Difficulty")
        plot.y_range.flipped = True

        # Get Means and Ranges and Top n% for Labels
        xp_ms = source.data["xP_Mean_mean"][0]
        xp_mean_span = Span(location=xp_ms,
                                dimension='width', line_color="black",
                                line_dash='solid', line_width=3, line_alpha=.2)
        plot.add_layout(xp_mean_span)

        xp_rs = source.data["xP_Rating_mean"][0]
        xp_rating_span = Span(location=xp_rs,
                                dimension='height', line_color="black",
                                line_dash='solid', line_width=3, line_alpha=.2)
        plot.add_layout(xp_rating_span)

        renderer = plot.circle("xP_Rating", "xP_Mean", size="Pass_Size",
                               color=position_color,
                               legend="Position_Detail",

                               source=source,

                               # set visual properties for selected glyphs
                               selection_color=Spectral6[5],
                               #color="Position_Detail",

                               # set visual properties for non-selected glyphs
                               nonselection_fill_alpha=0.1,
                               nonselection_fill_color=Spectral6[0],
                               nonselection_line_color=Spectral6[5],
                               nonselection_line_alpha=1.0)
        plot.legend.location = (10,50)
        plot.legend.border_line_width = 3
        plot.legend.border_line_color = "black"
        plot.legend.border_line_alpha = 0.5

        labels = LabelSet(x='xP_Rating', y='xP_Mean', text='Player', level='glyph',
                          text_font_size='10pt', x_offset=-2, y_offset=2, source=source, render_mode='canvas')
        plot.add_layout(labels)


        # Hover tool with vline mode
        hover = HoverTool(tooltips=[('Team', '@Team'),
                                    ('Player', '@Player'),
                                    ('Position', '@Position_Detail'),
                                    ('Expected Pass Rating', '@xP_Rating'),
                                    ('Total Passes', '@Passes')],
                          mode='vline')
        plot.add_tools(hover)

        # Add Labels in the corners
        citation1 = Label(x=10, y=10, x_units='screen', y_units='screen',
                     text='Easier Passes, Poorly Executed', render_mode='css',
                     border_line_color='black', border_line_alpha=1.0,
                     background_fill_color='white', background_fill_alpha=1.0)
        # Add Labels in the corners
        citation2 = Label(x=10, y=510, x_units='screen', y_units='screen',
                     text='Harder Passes, Poorly Executed', render_mode='css',
                     border_line_color='black', border_line_alpha=1.0,
                     background_fill_color='white', background_fill_alpha=1.0)
        # Add Labels in the corners
        citation3 = Label(x=625, y=10, x_units='screen', y_units='screen',
                     text='Easier Passes, Well Executed', render_mode='css',
                     border_line_color='black', border_line_alpha=1.0,
                     background_fill_color='white', background_fill_alpha=1.0)
        # Add Labels in the corners
        citation4 = Label(x=625, y=510, x_units='screen', y_units='screen',
                     text='Easier Passes, Well Executed', render_mode='css',
                     border_line_color='black', border_line_alpha=1.0,
                     background_fill_color='white', background_fill_alpha=1.0)
        plot.add_layout(citation1)
        plot.add_layout(citation2)
        plot.add_layout(citation3)
        plot.add_layout(citation4)

        return plot, xp_mean_span, xp_rating_span

    def callback(attr, old, new):

        # Pass Slider
        range_start = pass_slider.value[0]
        range_end = pass_slider.value[1]

        # Select
        position_val = select.value

        # Update Title
        plot.title.text = select.value

        # Update Dataset
        new_df = make_dataset(position_val, range_start, range_end)
        source.data.update(new_df.data)

        # Update Averages
        xp_ms = source.data["xP_Mean_mean"][0]
        xp_mean_span.location = xp_ms
        xp_rs = source.data["xP_Rating_mean"][0]
        xp_rating_span.location = xp_rs

    source = make_dataset(
        select.value, pass_slider.value[0], pass_slider.value[1])

    plot, xp_mean_span, xp_rating_span = make_plot(source)

    inputs = widgetbox(select, pass_slider)

    select.on_change('value', callback)
    pass_slider.on_change('value', callback)

    # Create a row layout
    layout = column(inputs, plot)

    # Make a tab with the layout
    tab = Panel(child=layout, title='Player Passing Model')

    return tab



def team_tab(passing_model):
    result = [
      "Group Stage", "Round of 16", "Quarter-finals", "Semi-finals", "Final"]
    #position_details = list(passing_model.Position_Detail.unique())
    result_color = factor_cmap(
        'Round', palette=Spectral6, factors=result)
    checkbox = CheckboxGroup(
      labels=result, active=[0,1,2,3,4])
    rounds = [checkbox.labels[i] for i in checkbox.active]
    #max_passes = int(passing_model["Passes"].max())
    #pass_slider = RangeSlider(
    #    start=0, end=max_passes, value=(70, max_passes),
    #    step=5, title="Number of Passes")

    def make_dataset(rounds):
        source = ColumnDataSource(
            data=passing_model.loc[
                passing_model["Round"].isin(rounds), :] ) #&
                #(passing_model["Passes"] >= pass_slider_min) &
                #(passing_model["Passes"] <= pass_slider_max), :])
        source.data["Pass_Size"] = source.data["Passes"] / 50
        source.data["xP_Mean_mean"] = np.repeat(source.data["xP_Mean"].mean(), len(source.data["Passes"]))
        source.data["xP_Rating_mean"] = np.repeat(source.data["xP_Rating"].mean(), len(source.data["Passes"]))
        return source


    def make_plot(source):
        """Need to return the span so we can update them in callback (I think)"""
        # Set up Plot Figure
        plot_size_and_tools = {
            'plot_height': 100, 'plot_width': 1000,
            'x_range': (source.data["xP_Rating"].min() * .8, source.data["xP_Rating"].max() * 1.2),
            'y_range': (source.data["xP_Mean"].min() * .8, source.data["xP_Mean"].max() * 1.2)}
        plot = figure(tools=["tap", "pan", "wheel_zoom",'box_select', 'reset', 'help'], title="Expected Passes v. Pass Difficulty")
        plot.y_range.flipped = True

        # Get Means and Ranges and Top n% for Labels
        xp_ms = source.data["xP_Mean_mean"][0]
        xp_mean_span = Span(location=xp_ms,
                                dimension='width', line_color="black",
                                line_dash='solid', line_width=3, line_alpha=.2)
        plot.add_layout(xp_mean_span)

        xp_rs = source.data["xP_Rating_mean"][0]
        xp_rating_span = Span(location=xp_rs,
                                dimension='height', line_color="black",
                                line_dash='solid', line_width=3, line_alpha=.2)
        plot.add_layout(xp_rating_span)

        renderer = plot.circle("xP_Rating", "xP_Mean", size="Pass_Size",
                               color=result_color,
                               legend="Round",

                               source=source,

                               # set visual properties for selected glyphs
                               selection_color=Spectral6[5],
                               #color="Position_Detail",

                               # set visual properties for non-selected glyphs
                               nonselection_fill_alpha=0.1,
                               nonselection_fill_color=Spectral6[0],
                               nonselection_line_color=Spectral6[5],
                               nonselection_line_alpha=1.0)
        plot.legend.location = (10,50)
        plot.legend.border_line_width = 3
        plot.legend.border_line_color = "black"
        plot.legend.border_line_alpha = 0.5

        labels = LabelSet(x='xP_Rating', y='xP_Mean', text='Team', level='glyph',
                          text_font_size='10pt', x_offset=-2, y_offset=2, source=source, render_mode='canvas')
        plot.add_layout(labels)


        # Hover tool with vline mode
        hover = HoverTool(tooltips=[('Team', '@Team'),
                                    ('Result', '@Round'),
                                    #('Position', '@Position_Detail'),
                                    ('Expected Pass Rating', '@xP_Rating'),
                                    ('Total Passes', '@Passes')],
                          mode='vline')
        plot.add_tools(hover)

        # Add Labels in the corners
        citation1 = Label(x=10, y=10, x_units='screen', y_units='screen',
                     text='Easier Passes, Poorly Executed', render_mode='css',
                     border_line_color='black', border_line_alpha=1.0,
                     background_fill_color='white', background_fill_alpha=1.0)
        # Add Labels in the corners
        citation2 = Label(x=10, y=510, x_units='screen', y_units='screen',
                     text='Harder Passes, Poorly Executed', render_mode='css',
                     border_line_color='black', border_line_alpha=1.0,
                     background_fill_color='white', background_fill_alpha=1.0)
        # Add Labels in the corners
        citation3 = Label(x=625, y=10, x_units='screen', y_units='screen',
                     text='Easier Passes, Well Executed', render_mode='css',
                     border_line_color='black', border_line_alpha=1.0,
                     background_fill_color='white', background_fill_alpha=1.0)
        # Add Labels in the corners
        citation4 = Label(x=625, y=510, x_units='screen', y_units='screen',
                     text='Easier Passes, Well Executed', render_mode='css',
                     border_line_color='black', border_line_alpha=1.0,
                     background_fill_color='white', background_fill_alpha=1.0)
        plot.add_layout(citation1)
        plot.add_layout(citation2)
        plot.add_layout(citation3)
        plot.add_layout(citation4)

        return plot, xp_mean_span, xp_rating_span

    def callback(attr, old, new):

        new_rounds = [checkbox.labels[i] for i in checkbox.active]

        # Update Dataset
        new_df = make_dataset(new_rounds)
        source.data.update(new_df.data)

        # Update Averages
        xp_ms = source.data["xP_Mean_mean"][0]
        xp_mean_span.location = xp_ms
        xp_rs = source.data["xP_Rating_mean"][0]
        xp_rating_span.location = xp_rs

    source = make_dataset(rounds)

    plot, xp_mean_span, xp_rating_span = make_plot(source)

    inputs = widgetbox(checkbox)

    checkbox.on_change('active', callback)
    #pass_slider.on_change('value', callback)

    # Create a row layout
    layout = column(inputs, plot)
    #layout = row(plot)

    # Make a tab with the layout
    tab = Panel(child=layout, title='Team Passing Model')

    return tab
