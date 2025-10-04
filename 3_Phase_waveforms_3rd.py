# 3-phase inverter references with third-harmonic injection
# pip install numpy plotly

import numpy as np
import plotly.graph_objects as go

# ==== Parameters ====
freq_hz = 50.0                 # fundamental frequency (Hz)
phase_leg_peak_v = 230.0       # max per-phase voltage reference (V)
cycles = 2                     # how many cycles to show
samples_per_cycle = 400        # time resolution (increase for smoother curves)
third_harmonic_ratio = 1.0 / 6.0  # zero-sequence gain that maximizes modulation depth
include_line_to_line = True       # toggle line-to-line voltage traces as a group
show_metrics_annotation = True    # display fundamental and boost metrics on the chart

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
fundamental_waves = {
    name: np.sin(omega * t + phi)
    for name, phi in phase_angles.items()
}
third_harmonic = third_harmonic_ratio * np.sin(3.0 * omega * t)

# Combine with zero-sequence injection and scale to respect phase-leg limits
combined_waveforms = {
    name: wave + third_harmonic
    for name, wave in fundamental_waves.items()
}
max_modulation = max(np.max(np.abs(wave)) for wave in combined_waveforms.values())
scaling = phase_leg_peak_v / max_modulation if max_modulation else 1.0

# ==== Build figure ====
fig = go.Figure()
phase_waveforms = {}
legend_group_phases = "Phase Voltages (THI)"

for idx, (name, raw_wave) in enumerate(combined_waveforms.items()):
    injected = scaling * raw_wave
    phase_waveforms[name] = injected
    fig.add_trace(
        go.Scatter(
            x=t,
            y=injected,
            mode="lines",
            name=name,
            legendgroup=legend_group_phases,
            legendgrouptitle_text="Phases w/ THI" if idx == 0 else None,
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

# ==== Compute and display fundamental metrics ====
fundamental_peak = scaling  # fundamental component magnitude per phase (peak)
line_to_line_peak = np.sqrt(3.0) * fundamental_peak
line_to_line_rms = line_to_line_peak / np.sqrt(2.0)
baseline_line_to_line_peak = np.sqrt(3.0) * phase_leg_peak_v
boost_ratio = line_to_line_peak / baseline_line_to_line_peak if baseline_line_to_line_peak else float("nan")
boost_percent = (boost_ratio - 1.0) * 100.0

if show_metrics_annotation:
    metrics = (
        f"Phase fundamental peak: {fundamental_peak:.1f} V\n"
        f"Line-line fundamental RMS: {line_to_line_rms:.1f} V\n"
        f"Boost vs pure sinusoid: {boost_percent:+.1f}%"
    )
    fig.add_annotation(
        x=0.02,
        y=0.98,
        xref="paper",
        yref="paper",
        text=metrics,
        align="left",
        showarrow=False,
        bordercolor="#444",
        borderwidth=1,
        borderpad=6,
        bgcolor="rgba(255,255,255,0.85)",
    )

fig.update_layout(
    title=(
        "Three-Phase References with Third Harmonic Injection | "
        f"f={freq_hz} Hz, phase limit={phase_leg_peak_v} V"
    ),
    xaxis_title="Time (s)",
    yaxis_title="Voltage (V)",
    legend_title="Traces",
    hovermode="x unified",
    template="plotly_white",
    legend=dict(groupclick="togglegroup"),  # click one trace to show/hide its entire group
)

fig.show()

# Optional: save to an HTML file you can open in a browser
# fig.write_html("three_phase_sine_third_harmonic.html", include_plotlyjs="cdn")
