import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ----------------------------
# Parameters
# ----------------------------
R = 2.0
r = 0.7

N = 90
num_frames = 81

phi = np.linspace(0, 2*np.pi, N)
theta = np.linspace(0, 2*np.pi, N)

Phi, Theta = np.meshgrid(phi, theta)

# Torus embedding
X = (R + r*np.cos(Theta)) * np.cos(Phi)
Y = (R + r*np.cos(Theta)) * np.sin(Phi)
Z = r * np.sin(Theta)

# Morse function
F = np.cos(Phi) + np.cos(Theta)

# Slider values
t_values = np.linspace(-2, 2, num_frames)

# ----------------------------
# Discrete color array
# 0 = outside sublevel set
# 1 = inside sublevel set
# 2 = near level curve f = t
# ----------------------------
def color_data(t):
    C = np.zeros_like(F)

    # Sublevel set
    C[F <= t] = 1

    # Level curve band
    eps = 0.045
    C[np.abs(F - t) < eps] = 2

    return C

# Discrete colorscale
colorscale = [
    [0.00, "lightgray"],
    [0.32, "lightgray"],

    [0.33, "royalblue"],
    [0.66, "royalblue"],

    [0.67, "black"],
    [1.00, "black"],
]

# ----------------------------
# Critical points
# ----------------------------
critical_points = [
    (np.pi, np.pi, "min<br>index 0<br>f=-2"),
    (0, np.pi, "saddle<br>index 1<br>f=0"),
    (np.pi, 0, "saddle<br>index 1<br>f=0"),
    (0, 0, "max<br>index 2<br>f=2"),
]

def torus_point(ph, th):
    x = (R + r*np.cos(th)) * np.cos(ph)
    y = (R + r*np.cos(th)) * np.sin(ph)
    z = r * np.sin(th)
    return x, y, z

crit_x, crit_y, crit_z, crit_text = [], [], [], []

for ph, th, label in critical_points:
    x, y, z = torus_point(ph, th)
    crit_x.append(x)
    crit_y.append(y)
    crit_z.append(z)
    crit_text.append(label)

# ----------------------------
# Figure with 3D torus + 2D parameter square
# ----------------------------
fig = make_subplots(
    rows=1,
    cols=2,
    specs=[[{"type": "scene"}, {"type": "xy"}]],
    subplot_titles=[
        r"Sublevel set on the torus",
        r"Parameter space $(\phi,\theta)$"
    ],
    column_widths=[0.58, 0.42]
)

t0 = t_values[0]
C0 = color_data(t0)

# 3D torus surface
fig.add_trace(
    go.Surface(
        x=X,
        y=Y,
        z=Z,
        surfacecolor=C0,
        cmin=0,
        cmax=2,
        colorscale=colorscale,
        showscale=False,
        lighting=dict(
            ambient=0.7,
            diffuse=0.6,
            specular=0.2,
            roughness=0.8
        ),
        name="torus"
    ),
    row=1,
    col=1
)

# 2D parameter-space heatmap
fig.add_trace(
    go.Heatmap(
        x=phi,
        y=theta,
        z=C0,
        zmin=0,
        zmax=2,
        colorscale=colorscale,
        showscale=False,
        name="parameter space"
    ),
    row=1,
    col=2
)

# Critical points on 3D torus
fig.add_trace(
    go.Scatter3d(
        x=crit_x,
        y=crit_y,
        z=crit_z,
        mode="markers+text",
        marker=dict(size=5, color="red"),
        text=["min", "saddle", "saddle", "max"],
        textposition="top center",
        hovertext=crit_text,
        hoverinfo="text",
        name="critical points"
    ),
    row=1,
    col=1
)

# Critical points in parameter space
fig.add_trace(
    go.Scatter(
        x=[p[0] for p in critical_points],
        y=[p[1] for p in critical_points],
        mode="markers+text",
        marker=dict(size=9, color="red"),
        text=["min", "saddle", "saddle", "max"],
        textposition="top center",
        hovertext=[p[2] for p in critical_points],
        hoverinfo="text",
        name="critical points"
    ),
    row=1,
    col=2
)

# ----------------------------
# Animation frames
# ----------------------------
frames = []

for t in t_values:
    C = color_data(t)

    frames.append(
        go.Frame(
            data=[
                go.Surface(surfacecolor=C),
                go.Heatmap(z=C),
            ],
            traces=[0, 1],
            name=f"{t:.2f}",
            layout=go.Layout(
                title_text=rf"Morse function $f(\phi,\theta)=\cos\phi+\cos\theta$ &nbsp;&nbsp; Level/time $t={t:.2f}$"
            )
        )
    )

fig.frames = frames

# ----------------------------
# Slider
# ----------------------------
slider_steps = []

for t in t_values:
    slider_steps.append(
        dict(
            method="animate",
            label=f"{t:.2f}",
            args=[
                [f"{t:.2f}"],
                dict(
                    mode="immediate",
                    frame=dict(duration=0, redraw=True),
                    transition=dict(duration=0)
                )
            ]
        )
    )

sliders = [
    dict(
        active=0,
        currentvalue=dict(
            prefix="level/time t = ",
            font=dict(size=16)
        ),
        pad=dict(t=45),
        steps=slider_steps
    )
]

# ----------------------------
# Play/pause buttons
# ----------------------------
buttons = [
    dict(
        label="Play",
        method="animate",
        args=[
            None,
            dict(
                frame=dict(duration=80, redraw=True),
                transition=dict(duration=0),
                fromcurrent=True,
                mode="immediate"
            )
        ]
    ),
    dict(
        label="Pause",
        method="animate",
        args=[
            [None],
            dict(
                frame=dict(duration=0, redraw=False),
                transition=dict(duration=0),
                mode="immediate"
            )
        ]
    )
]

# ----------------------------
# Layout
# ----------------------------
fig.update_layout(
    title=rf"Morse function $f(\phi,\theta)=\cos\phi+\cos\theta$ &nbsp;&nbsp; Level/time $t={t0:.2f}$",
    width=1200,
    height=650,
    sliders=sliders,
    updatemenus=[
        dict(
            type="buttons",
            buttons=buttons,
            direction="left",
            x=0.1,
            y=0,
            xanchor="right",
            yanchor="top"
        )
    ],
    scene=dict(
        xaxis=dict(title="x"),
        yaxis=dict(title="y"),
        zaxis=dict(title="z"),
        aspectmode="data",
        camera=dict(
            eye=dict(x=1.6, y=1.6, z=0.9)
        )
    )
)

fig.update_xaxes(
    title_text=r"$\phi$",
    tickvals=[0, np.pi, 2*np.pi],
    ticktext=["0", "π", "2π"],
    row=1,
    col=2
)

fig.update_yaxes(
    title_text=r"$\theta$",
    tickvals=[0, np.pi, 2*np.pi],
    ticktext=["0", "π", "2π"],
    scaleanchor="x",
    scaleratio=1,
    row=1,
    col=2
)

fig.show()