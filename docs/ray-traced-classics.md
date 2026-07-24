# Ray-Traced Classics

| Project | Renderer / platform status | Decision |
| --- | --- | --- |
| GZDoom RT 1.0.2a | Full PT, but Proton testing failed on missing `VK_KHR_external_fence_win32` with `RG_RESULT_ERROR_NO_VULKAN_EXTENSION`; upstream Linux issue #26 remains open. | Rejected on this stack. |
| [PrBoom-Plus-RT](https://github.com/tomboylover93/prboom-plus-rt) `v2.6.1-rt1.0.7` | Native Vulkan full-PT build with a verified Doom II lighting addon; requires an owned Doom II IWAD. | Implemented by `install-prboom-plus-rt.yml`; see `doom2-ray-traced.md`. |
| [VkDoom](https://github.com/nashmuhandes/VkDoom) | RT lightmaps/shadows, not full PT; native Vulkan port requiring owned Doom IWADs. | Deferred; hybrid/raster rather than full PT. |
| [Duke-RT](https://github.com/postmemetic/Duke-RT) / [Raze](https://github.com/ZDoom/Raze) | Duke-RT's true PT path is Windows-focused; Raze's native fallback is raster. Requires an owned `DUKE3D.GRP`. | Deferred. |
| [Quake: Ray Traced / vkquake-rt](https://github.com/sultim-t/vkquake-rt) / [vkQuake](https://github.com/Novum/vkQuake) | vkquake-rt is full PT but Windows-first with Linux build friction; vkQuake has RT shadows only. Requires owned `id1/pak*.pak`. | Deferred. |
| [NVIDIA Quake II RTX](https://github.com/NVIDIA/Q2RTX) | Full PT with an official native Linux release; requires classic owned `baseq2/pak*.pak`. | Recommended next native Linux PT candidate, but not yet integrated. |
| [Quake III RTX Remix](https://github.com/PPBWoodBoy/q3-rtx-demo) | Early access full PT via Remix; Windows-focused and incomplete. | Deferred. |
| [OpenQ4](https://github.com/themuffinator/OpenQ4) | Native modern Quake 4 source port, not PT. | Deferred. |
| Quake Live / Quake Champions | No practical PT option. | Not planned. |

Use a per-game controller translator or Steam Input layout when a native port
lacks modern pad support. Do not add a global remapper.
