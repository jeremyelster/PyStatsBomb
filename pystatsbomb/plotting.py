import matplotlib.pyplot as plt
from matplotlib.patches import Arc
import matplotlib.cm as cm
import seaborn as sns
import numpy as np
import pandas as pd
from bokeh.plotting import figure
from bokeh.io import show

# import seaborn as sns


def plotpitch(display=False, size=(7,5)):
    # Create figure
    fig = plt.figure()
    fig.set_size_inches(size)
    ax = fig.add_subplot(1, 1, 1)

    # Pitch Outline & Centre Line
    ax.plot([0, 0], [0, 80], color="black")
    ax.plot([0, 120], [80, 80], color="black")
    ax.plot([120, 120], [80, 0], color="black")
    ax.plot([120, 0], [0, 0], color="black")
    ax.plot([60, 60], [0, 80], color="black")

    # Left Penalty Area
    ax.plot([18, 18], [62, 18], color="black")
    ax.plot([0, 18], [62, 62], color="black")
    ax.plot([18, 0], [18, 18], color="black")

    # Right Penalty Area
    ax.plot([120, 102], [62, 62], color="black")
    ax.plot([102, 102], [62, 18], color="black")
    ax.plot([102, 120], [18, 18], color="black")

    # Left 6-yard Box
    ax.plot([0, 6], [50, 50], color="black")
    ax.plot([6, 6], [50, 30], color="black")
    ax.plot([6, 0], [30, 30], color="black")

    # Right 6-yard Box
    ax.plot([120, 114], [50, 50], color="black")
    ax.plot([114, 114], [50, 30], color="black")
    ax.plot([114, 120], [30, 30], color="black")

    # Left Goal
    ax.plot([0, -2], [44, 44], color="black")
    ax.plot([-2, -2], [44, 36], color="black")
    ax.plot([-2, 0], [36, 36], color="black")

    # Right Goal
    ax.plot([120, 122], [44, 44], color="black")
    ax.plot([122, 122], [44, 36], color="black")
    ax.plot([122, 120], [36, 36], color="black")

    # Prepare Circles
    centreCircle = plt.Circle((60, 40), 10, color="black", fill=False, lw=2)
    centreSpot = plt.Circle((60, 40), 0.8, color="black")
    leftPenSpot = plt.Circle((12, 40), 0.8, color="black")
    rightPenSpot = plt.Circle((108, 40), 0.8, color="black")

    # Draw Circles
    ax.add_patch(centreCircle)
    ax.add_patch(centreSpot)
    ax.add_patch(leftPenSpot)
    ax.add_patch(rightPenSpot)

    # Prepare Arcs
    leftArc = Arc((12, 40), height=20, width=20, angle=0,
                  theta1=310, theta2=50, color="black", lw=2)
    rightArc = Arc((108, 40), height=20, width=20, angle=0,
                   theta1=130, theta2=230, color="black", lw=2)

    # Draw Arcs
    ax.add_patch(leftArc)
    ax.add_patch(rightArc)

    # Tidy Axes
    ax.axis('off')

    # sns.regplot(df_shot["x"],df_shot["y"], fit_reg=False)#,
    # shade=True,n_levels=50)
    # team1 = df_shot[df_shot.team == 'Chelsea LFC']
    # team2 = df_shot[df_shot.team != 'Chelsea LFC']

    # sns.kdeplot(team1["x"], team1["y"], shade=False,
    #            shade_lowest=False, n_levels=50, cmap="Reds", ax=ax)
    # sns.kdeplot(team2["x"], team2["y"], shade=False,
    #            shade_lowest=False, n_levels=50, cmap="Blues", ax=ax)
    # sns.regplot(team1["x"], team1["y"], fit_reg=False, color="red", ax=ax)
    # sns.regplot(team2["x"], team2["y"], fit_reg=False, color="blue", ax=ax)

    plt.ylim(-5, 85)
    plt.xlim(-5, 125)


    # Display Pitch
    if display:
        plt.show()
    else:
        return fig, ax





def plotpitch_bokeh(display=False, line_color="black", background="green"):

    plot = figure(title="Pitch Baseplot", x_range=(-5,125), y_range=(-5,85), plot_width=600, plot_height=400)

    # Styling
    color = line_color
    plot.background_fill_color = background
    plot.background_fill_alpha = 0.1
    plot.grid.grid_line_color = None
    plot.xaxis.axis_line_color = None
    plot.yaxis.axis_line_color = None
    plot.xaxis.major_tick_line_color = None
    plot.xaxis.minor_tick_line_color = None
    plot.yaxis.major_tick_line_color = None
    plot.yaxis.minor_tick_line_color = None
    plot.xaxis.major_label_text_font_size = '0pt'
    plot.yaxis.major_label_text_font_size = '0pt'

    # Outline and Midline
    plot.multi_line(
        [[0, 0], [0, 120], [120, 120], [120, 0], [60, 60]],
        [[0, 80], [80, 80], [80, 0], [0, 0], [0, 80]], color=color, name="outline")

    # Left Penalty Area
    plot.multi_line(
        [[18, 18], [0, 18], [18, 0]],
        [[62, 18], [62, 62], [18, 18]], color=color, name="left_penalty_area")

    # Right Penalty Area
    plot.multi_line(
        [[120, 102], [102, 102], [102, 120]],
        [[62, 62], [62, 18], [18, 18]], color=color, name="right_penalty_area")


    # Left 6-yard Box
    plot.multi_line(
        [[0, 6], [6, 6], [6, 0]],
        [[50, 50], [50, 30], [30, 30]], color=color, name="left_6")


    # Right 6-yard Box
    plot.multi_line(
        [[120, 114], [114, 114], [114, 120]],
        [[50, 50], [50, 30], [30, 30]], color=color, name="right_6")

    # Left Goal
    plot.multi_line(
        [[0, -2], [-2, -2], [-2, 0]],
        [[44, 44], [44, 36], [36, 36]], color=color, name="left_goal")

    # Right Goal
    plot.multi_line(
        [[120, 122], [122, 122], [122, 120]],
        [[44, 44], [44, 36], [36, 36]], color=color, name="right_goal")

    # Circles and Arcs
    plot.circle(60, 40, radius=10, fill_alpha=0, color=color, name="center_cirle")
    plot.circle(60, 40, size=5, color=color, name="center_dot")
    plot.circle(12, 40, size=5, color=color, name="left_pen_dot")
    plot.circle(108, 40, size=5 ,color=color, name="right_pen_dot")

    plot.arc(12, 40, radius=10, start_angle=307, end_angle=53, start_angle_units='deg', end_angle_units="deg", color=color, name="left_pen_circle")
    plot.arc(108, 40, radius=10, start_angle=127, end_angle=233, start_angle_units='deg', end_angle_units="deg", color=color, name="right_pen_circle")

    # Display Pitch
    if display:
        show(plot)
    else:
        return plot


def pass_rose(df_passes, palette=None):
    """Based from https://gist.github.com/phobson/41b41bdd157a2bcf6e14"""

    if "pass_angle_deg" in df_passes.columns:
        pass
    else:
        print("Adding Pass Angle Degrees")
        df_passes['pass_angle_deg'] = (
            df_passes['pass_angle'].apply(pass_angle_deg))

    total_count = df_passes.shape[0]
    print('{} total observations'.format(total_count))

    dir_bins = np.arange(-7.5, 370, 15)
    dir_labels = (dir_bins[:-1] + dir_bins[1:]) / 2

    rosedata = (
        df_passes
        .assign(PassAngle_bins=lambda df: (
            pd.cut(
                df['pass_angle_deg'],
                bins=dir_bins,
                labels=dir_labels,
                right=False))))

    rosedata.loc[rosedata["PassAngle_bins"] == 360., "PassAngle_bins"] = 0.
    rosedata["PassAngle_bins"].cat.remove_categories([360], inplace=True)

    rosedata = (
        rosedata
        .groupby(by=['PassAngle_bins'])
        .agg({"pass_length": "size"})
        # .unstack(level='PassAngle_bins')
        .fillna(0)
        .sort_index(axis=0)
        #.applymap(lambda x: x / total_count * 100)
    )

    pass_dirs = np.arange(0, 360, 15)

    if palette is None:
        palette = sns.color_palette('inferno', n_colors=rosedata.shape[1])

    bar_dir, bar_width = _convert_dir(pass_dirs)

    fig, ax = plt.subplots(figsize=(5, 5), subplot_kw=dict(polar=True))
    ax.set_theta_direction('clockwise')
    ax.set_theta_zero_location('N')

    c1 = "pass_length"
    colors = cm.viridis(rosedata[c1].values / float(max(rosedata[c1].values)))
    print(len(bar_dir))
    print(len(rosedata[c1].values))
    # first column only
    ax.bar(
        bar_dir,
        rosedata[c1].values,
        width=bar_width,
        color=colors,
        edgecolor='none',
        label=c1,
        linewidth=0)

    leg = ax.legend(loc=(0.75, 0.95), ncol=2)
    #xtl = ax.set_xticklabels(['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW'])

    # return fig




def _convert_dir(directions, N=None):
    if N is None:
        N = directions.shape[0]
    barDir = directions * np.pi/180. # np.pi/N
    barWidth = 2 * np.pi / N
    return barDir, barWidth

def dist_labels(bins, units):
    labels = []
    for left, right in zip(bins[:-1], bins[1:]):
        if np.isinf(right):
            labels.append('>{} {}'.format(left, units))
        else:
            labels.append('{} - {} {}'.format(left, right, units))

    return list(labels)

def pass_angle_deg(x):
    """Convert negative angles to positive radians from 0 to 2pi clockwise"""
    if x >= 0:
        return x * 180. / np.pi
    else:
        return (2 * np.pi + x) * 180. / np.pi

def getArrow(start, end, color, qualifier=None, viz="mpl"):
    x = start[0]
    y = start[1]
    if viz == "mpl":
        dx = end[0] - start[0]
        dy = end[1] - start[1]
    elif viz == "bokeh":
        dx = end[0]
        dy = end[1]
    else:
        print("please choose mpl or bokeh")
    if color == qualifier:
        color = 'blue'
    else:
        color = 'red'
    return x, y, dx, dy, color
