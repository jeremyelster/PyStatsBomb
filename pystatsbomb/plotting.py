import matplotlib.pyplot as plt
from matplotlib.patches import Arc
# import seaborn as sns

# Create figure
fig = plt.figure()
fig.set_size_inches(7, 5)
ax = fig.add_subplot(1, 1, 1)

# Pitch Outline & Centre Line
plt.plot([0, 0], [0, 80], color="black")
plt.plot([0, 120], [80, 80], color="black")
plt.plot([120, 120], [80, 0], color="black")
plt.plot([120, 0], [0, 0], color="black")
plt.plot([60, 60], [0, 80], color="black")

# Left Penalty Area
plt.plot([18, 18], [62, 18], color="black")
plt.plot([0, 18], [62, 62], color="black")
plt.plot([18, 0], [18, 18], color="black")

# Right Penalty Area
plt.plot([120, 102], [62, 62], color="black")
plt.plot([102, 102], [62, 18], color="black")
plt.plot([102, 120], [18, 18], color="black")

# Left 6-yard Box
plt.plot([0, 6], [50, 50], color="black")
plt.plot([6, 6], [50, 30], color="black")
plt.plot([6, 0], [30, 30], color="black")

# Right 6-yard Box
plt.plot([120, 114], [50, 50], color="black")
plt.plot([114, 114], [50, 30], color="black")
plt.plot([114, 120], [30, 30], color="black")

# Left Goal
plt.plot([0, -2], [44, 44], color="black")
plt.plot([-2, -2], [44, 36], color="black")
plt.plot([-2, 0], [36, 36], color="black")

# Right Goal
plt.plot([120, 122], [44, 44], color="black")
plt.plot([122, 122], [44, 36], color="black")
plt.plot([122, 120], [36, 36], color="black")

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
plt.axis('off')

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
plt.show()
