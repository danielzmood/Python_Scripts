# 3-phase sinewave with Plotly
# pip install numpy plotly

import numpy as np
import plotly.graph_objects as go

# ==== Parameters ====
freq_hz = 50.0          # signal frequency (Hz)
amplitude = 1.0         # peak amplitude
cycles = 2              # how many cycles to show
samples_per_cycle = 400 # time resolution (increase for smoother curves)

# ==== Time base ====
T = 1.0 / freq_hz
N = int(cycles * samples_per_cycle)
t = np.linspace(0, cycles * T, N, endpoint=False)

# ==== Phase angles (in radians) ====
phase_angles = {
    "Phase A": 0.0,
    "Phase B": -2.0 * np.pi / 3.0,  # -120°
    "Phase C":  2.0 * np.pi / 3.0,  # +120°
}

# ==== Build figure ====
fig = go.Figure()

for name, phi in phase_angles.items():
    y = amplitude * np.sin(2.0 * np.pi * freq_hz * t + phi)
    fig.add_trace(go.Scatter(x=t, y=y, mode="lines", name=name))

fig.update_layout(
    title=f"Three-Phase Sine Waves — f={freq_hz} Hz, A={amplitude}",
    xaxis_title="Time (s)",
    yaxis_title="Amplitude",
    legend_title="Phases",
    hovermode="x unified",
    template="plotly_white",
)

fig.show()

# Optional: save to an HTML file you can open in a browser
# fig.write_html("three_phase_sine.html", include_plotlyjs="cdn")
