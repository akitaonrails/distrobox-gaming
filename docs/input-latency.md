# Input Latency on Linux — findings vs. our setup

Study of a click-to-photon input-latency report and how it maps to this
box. Source: Marco Nett, *"Measuring input latency on Linux: X11 vs
Wayland, VRR, DXVK"*
(<https://marco-nett.de/blog/measuring-input-latency-on-linux-x11-vs-wayland-vrr-dxvk/>).

**Bottom line: no changes were applied.** Our architecture already
avoids the report's single biggest pitfall (desktop XWayland), and every
remaining optimization is either handled at a layer we already
configure, or a sub-millisecond gain that needs measurement hardware to
validate and per-game tuning to apply safely. Details below.

## The report in brief

Custom click-to-photon meter (Adafruit QT Py RP2040 1000 Hz HID mouse +
photodiode, ~24 µs sampling), measuring *Diabotical* (D3D11) via
Proton. Rig: Ryzen 5800X3D, **RTX 4070 SUPER, NVIDIA**, QD-OLED
**500 Hz**, CachyOS + **KDE Plasma Wayland**. Numbers are medians.

Ranked by effect size:

1. **Avoid XWayland — by far the biggest factor.** Native Wayland vs
   XWayland: **+1.12 ms** with dxvk-low-latency, **+3.13 ms** without —
   "more than all the other effects combined." Corroborated by two
   other independent meters (m2p-latency, Open-Source-LDAT).
2. **VRR — biggest *deliberate* win: −0.26 to −0.45 ms**, and it
   flattens jitter (p95–p5 spread 2.1–2.2 ms with VRR vs 2.6–3.0 ms
   without). For VRR they cap fps *just under* refresh
   (`dxgi.maxFrameRate = 497` / `480` at 500 Hz) to stay in the VRR
   window.
3. **dxvk-low-latency fork: −0.10 to −0.29 ms** capped, **−0.84 ms**
   uncapped (at a cost of ~45 fps). Enabled via `PROTON_DXVK_LOWLATENCY=1`
   with `dxvk.framePace = "low-latency-vrr-500"`,
   `dxvk.lowLatencyOffset`, etc. Keeps the GPU at 95–97 % instead of
   100 %, preventing render-queue buildup.
4. **X11 vs native Wayland: a wash — X11 wins by only 0.14–0.22 ms.**
   Not worth switching desktops for.

Optimal combo (X11 + VRR + dxvk-low-latency) moved the median down
~0.72 ms vs plain Wayland.

## How it maps to this box

Our host is **Omarchy/Arch + Hyprland (Wayland)**, RTX 5090, dual 4K
(Samsung Odyssey G8 on DP-1 = 240 Hz VRR/G-Sync-compatible, a 60 Hz
panel on DP-2). Games run two ways: **wine + DXVK inside `gamescope`**
(nested in Hyprland) for the box library, and **host Steam + GE-Proton**
for a few titles.

The report measures *desktop-fullscreen* games on KDE. We run games in
**gamescope**, Valve's purpose-built micro-compositor — a different (and
generally lower-latency) presentation path. So the findings translate as
follows:

| Report finding | Our status |
|---|---|
| **Avoid XWayland (−3.13 ms)** | **Already handled.** Box games present via DXVK's Vulkan WSI into gamescope's own compositor, not the desktop XWayland server. gamescope does direct scanout and bypasses Hyprland's desktop composite path. This is the recommended low-latency route and we already use it everywhere in the box. |
| **VRR (−0.26–0.45 ms + less jitter)** | **Enabled at the right layer.** Hyprland `misc:vrr = 2` (fullscreen-only) + `__GL_VRR_ALLOWED=1`. In *nested* gamescope, Hyprland — not gamescope — owns the physical panel's VRR, and engages it when the gamescope window is fullscreen on the G8. `hyprctl monitors` shows `vrr=false` at idle, which is correct for `vrr=2` (it flips on only for a fullscreen game). We do **not** pass gamescope `--adaptive-sync`; in nested mode that targets gamescope's virtual output, not the monitor, so it's not the lever here. |
| **X11 vs Wayland (0.14–0.22 ms)** | Not actionable / not worth it. gamescope abstracts this and the host is Wayland by design (the monitor-scale and windowrule setup depends on it). |
| **dxvk-low-latency (−0.1–0.84 ms)** | **Not in use.** Box games use stock DXVK via `winetricks dxvk`; host games use GE-Proton's bundled DXVK. The low-latency fork / `dxvk.framePace` pacing isn't wired up. |
| **fps cap just under refresh (for VRR)** | Not set. gamescope caps to the game's mode, not a VRR-window cap. |

## Candidate tweaks — documented, deliberately NOT applied

None of these cleared the "only change if very confident" bar: they're
sub-millisecond, unverifiable without a photon meter, and risk
regressions on our nested/dual-monitor (one non-VRR) layout.

1. **Confirm VRR actually engages** on the G8 during a fullscreen
   gamescope game (`hyprctl monitors | grep vrr` while playing). If it
   stays `false`, VRR — the report's biggest deliberate win — isn't
   reaching the panel through the game→gamescope→Hyprland chain, and
   *then* it's worth investigating (e.g. gamescope `--adaptive-sync`,
   or running specific titles without the nested gamescope layer).
2. **fps cap ~2–3 below 240** for VRR titles (e.g. `dxgi.maxFrameRate`
   in a per-game `dxvk.conf`, or gamescope `-r 237`) to keep frames
   inside the VRR window. Only meaningful once (1) confirms VRR is live,
   and only for games that actually exceed 240 fps (few of our arcade/
   racing titles do at 4K).
3. **dxvk-low-latency** for a latency-sensitive title: a newer DXVK
   build with `dxvk.framePace = "low-latency"` (or GE-Proton's
   `PROTON_DXVK_LOWLATENCY=1` for host games). Per-prefix DXVK swap +
   testing; revisit if a specific game feels laggy.
4. **Host Steam Proton on Wayland**: GE-Proton supports
   `PROTON_ENABLE_WAYLAND=1` — would avoid XWayland for host titles
   (the −1 to −3 ms finding). Experimental; only relevant to the handful
   of host-Steam games, and those had their own issues (see DiRT notes).

## Practical-relevance caveat

The report optimizes a **500 Hz competitive twitch FPS**, where 0.2 ms
is meaningful. Our library is **emulators + arcade/rally racers on a
240 Hz panel**; at that cadence one frame is ~4.2 ms and these
sub-millisecond deltas are below perceptible threshold for the genres we
run. The one finding that *does* matter at any refresh — avoid XWayland
— we already satisfy via gamescope. So the honest conclusion is that the
box is already near-optimal for its use case, and the remaining knobs
are worth touching only if a specific game demonstrably feels laggy.
