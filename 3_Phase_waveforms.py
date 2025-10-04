# 3-phase sinewave with Plotly
# pip install numpy plotly

import numpy as np
import plotly.graph_objects as go

# ==== Parameters ====
freq_hz = 50.0           # fundamental frequency (Hz)
amplitude = 230.0          # peak amplitude after modulation scaling
cycles = 2               # how many cycles to show
samples_per_cycle = 400  # time resolution (increase for smoother curves)
third_harmonic_ratio = 1.0 / 6.0  # zero-sequence injection to maximize modulation depth
include_line_to_line = True       # toggle line-to-line voltage traces as a group

# ==== Time base ====
T = 1.0 / freq_hz
N = int(cycles * samples_per_cycle)
t = np.linspace(0, cycles * T, N, endpoint=False)

# ==== Phase angles (in radians) ====
phase_angles = {
    "Phase A": 0.0,                 # 0 deg
    "Phase B": -2.0 * np.pi / 3.0,  # -120 deg
    "Phase C":  2.0 * np.pi / 3.0,  # +120 deg
}

omega = 2.0 * np.pi * freq_hz
third_harmonic = third_harmonic_ratio * np.sin(3.0 * omega * t)

# Normalize so the injected waveform still hits the requested peak amplitude
max_modulation = 0.0
for phi in phase_angles.values():
    combined = np.sin(omega * t + phi) + third_harmonic
    max_modulation = max(max_modulation, np.max(np.abs(combined)))
scaling = amplitude / max_modulation if max_modulation else 1.0

# ==== Build figure ====
fig = go.Figure()
phase_waveforms = {}
legend_group_phases = "Phase Voltages"

for idx, (name, phi) in enumerate(phase_angles.items()):
    fundamental = np.sin(omega * t + phi)
    injected = scaling * (fundamental + third_harmonic)
    phase_waveforms[name] = injected
    fig.add_trace(
        go.Scatter(
            x=t,
            y=injected,
            mode="lines",
            name=name,
            legendgroup=legend_group_phases,
            legendgrouptitle_text="Phases" if idx == 0 else None,
        )
    )

if include_line_to_line:
    legend_group_line = "Line-to-Line Voltages"
    line_to_line_pairs = [
        ("Phase A", "Phase B", "Vab"),
        ("Phase B", "Phase C", "Vbc"),
        ("Phase C", "Phase A", "Vca"),
    ]
    for idx, (pos, neg, label) in enumerate(line_to_line_pairs):
        voltage = phase_waveforms[pos] - phase_waveforms[neg]
        fig.add_trace(
            go.Scatter(
                x=t,
                y=voltage,
                mode="lines",
                name=label,
                legendgroup=legend_group_line,
                legendgrouptitle_text="Line-to-Line" if idx == 0 else None,
                line=dict(dash="dash"),
            )
        )

fig.update_layout(
    title=f"Three-Phase Sine Waves with 3rd Harmonic Injection | f={freq_hz} Hz, A={amplitude}",
    xaxis_title="Time (s)",
    yaxis_title="Amplitude",
    legend_title="Phases",
    hovermode="x unified",
    template="plotly_white",
    legend=dict(groupclick="togglegroup"),  # click one trace to show/hide its entire group
)

fig.show()

# Optional: save to an HTML file you can open in a browser
# fig.write_html("three_phase_sine.html", include_plotlyjs="cdn")
