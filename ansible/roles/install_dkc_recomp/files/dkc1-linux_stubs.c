/* linux_stubs.c — Linux implementations of the macOS presenter / picker /
 * display-link API used by sdl_host.c. Everything answers "not available",
 * which routes the host onto its portable SDL renderer + SDL timing paths
 * (the same fallbacks used on macOS when the Metal presenter is disabled).
 * Maintained by the distrobox-gaming install_dkc_recomp role. */
#include <stddef.h>
#include <string.h>
#include <SDL.h>

#include "macos_file_picker.h"
#include "macos_metal_presenter.h"
#include "macos_pause_menu.h"
#include "macos_controls.h"

int Dkc1MacMetalPresenterStart(void *native_window, double preferred_hz,
                               Dkc1MacFullscreenScaling scaling,
                               int fullscreen) {
  (void)native_window; (void)preferred_hz; (void)scaling; (void)fullscreen;
  return 0;
}
void Dkc1MacMetalPresenterQueueFrame(
    const uint32_t *pixels, int width, int height, int presentation_width,
    const Dkc1MacPresentationFrameInfo *info) {
  (void)pixels; (void)width; (void)height; (void)presentation_width; (void)info;
}
void Dkc1MacMetalPresenterSetGeometry(int presentation_width, int fullscreen) {
  (void)presentation_width; (void)fullscreen;
}
void Dkc1MacMetalPresenterSetScaling(Dkc1MacFullscreenScaling scaling) {
  (void)scaling;
}
void Dkc1MacMetalPresenterSetActive(int active) { (void)active; }
void Dkc1MacMetalPresenterStop(void) {}

char *Dkc1MacChooseRom(void) { return NULL; }
char *Dkc1MacChooseBabyKongRom(void) { return NULL; }
char *Dkc1MacSavedBabyKongRom(void) { return NULL; }
void Dkc1MacSetBabyKongRom(const char *path) { (void)path; }
int Dkc1MacSavedBabyKongEnabled(void) { return 0; }
void Dkc1MacSetBabyKongEnabled(int enabled) { (void)enabled; }

char *Dkc1MacChooseMsu1(void) { return NULL; }
char *Dkc1MacSavedMsu1(void) { return NULL; }
void Dkc1MacClearMsu1(void) {}

Dkc1MacFullscreenScaling Dkc1MacSavedFullscreenScaling(void) {
  return kDkc1MacFullscreenSharpBilinear; /* documented default */
}
void Dkc1MacSetFullscreenScaling(Dkc1MacFullscreenScaling scaling) {
  (void)scaling;
}

Dkc1EdgePolicy Dkc1MacSavedWidescreenEdge(void) {
  return kDkc1EdgeGlide; /* documented default */
}
void Dkc1MacSetWidescreenEdge(Dkc1EdgePolicy policy) { (void)policy; }

void Dkc1MacInstallMenu(void) {}
void Dkc1MacUpdateMenuState(int paused, int fullscreen,
                            Dkc1MacFullscreenScaling fullscreen_scaling,
                            Dkc1VideoAspect aspect, Dkc1EdgePolicy edge,
                            unsigned char layer_mask, int provenance,
                            int replacement_music, int baby_kong_enabled,
                            int baby_kong_ready) {
  (void)paused; (void)fullscreen; (void)fullscreen_scaling; (void)aspect;
  (void)edge; (void)layer_mask; (void)provenance; (void)replacement_music;
  (void)baby_kong_enabled; (void)baby_kong_ready;
}

int Dkc1MacDisplayLinkStart(void *native_window, double preferred_fps) {
  (void)native_window; (void)preferred_fps;
  return 0;
}
int Dkc1MacDisplayLinkWait(unsigned long long after_callback_number,
                           double timeout_seconds, double *timestamp,
                           double *target_timestamp, double *duration,
                           unsigned long long *callback_number) {
  (void)after_callback_number; (void)timeout_seconds; (void)timestamp;
  (void)target_timestamp; (void)duration; (void)callback_number;
  return 0;
}
void Dkc1MacDisplayLinkStop(void) {}

/* v0.0.10 (e873d89) added a native Cocoa/Metal in-game pause + graphics/controls
 * settings menu. None of it exists on Linux; these route to no-ops so the port
 * keeps its SDL fullscreen + env-driven settings. Dkc1MacShowPauseMenu returns 1
 * ("resume") so the pause key simply unpauses instead of opening a dead menu.
 * (ApplyGraphics/AssistEnabled/PauseMenuController/HostStatus/MenuCommand are
 * NOT stubbed here — sdl_host.c already defines them on the non-Apple path.) */
/* macOS loads persisted graphics/audio settings here (falling back to
 * defaults). On Linux there's no plist, so populate the portable defaults —
 * critically audio_enabled=1 / volume=100. A no-op would leave the static
 * s_graphics zero-initialised, and sdl_host.c gates output on
 * `s_graphics.audio_enabled ? s_graphics.volume : 0` → dead silence. */
void Dkc1MacLoadGraphics(Dkc1GraphicsSettings *settings) {
  Dkc1GraphicsDefault(settings);
}
void Dkc1MacSaveGraphics(const Dkc1GraphicsSettings *settings) { (void)settings; }
int Dkc1MacPauseMenuIsOpen(void) { return 0; }
int Dkc1MacShowPauseMenu(void *window, Dkc1GraphicsSettings *settings,
                         Dkc1Controls *controls, int graphics_page) {
  (void)window; (void)settings; (void)controls; (void)graphics_page;
  return 1; /* resume */
}

void Dkc1MacSaveControls(const Dkc1Controls *controls) { (void)controls; }
/* macOS loads persisted controls here, seeding macos_controls.m's Defaults()
 * first. On Linux there are no prefs, so apply those same defaults verbatim —
 * P1 = keyboard + gamepad, the SNES-button -> SDL-pad map, deadzone 25, assist
 * on the triggers. A no-op left the static s_controls zero-initialised
 * (source=None, empty pad bindings) so the gamepad was ignored entirely. */
void Dkc1MacLoadControls(Dkc1Controls *c) {
  memset(c, 0, sizeof *c);
  c->source[0] = kDkc1InputSourceBoth;
  const int keys[12] = {SDL_SCANCODE_UP, SDL_SCANCODE_DOWN,
    SDL_SCANCODE_LEFT, SDL_SCANCODE_RIGHT, SDL_SCANCODE_S, SDL_SCANCODE_Z,
    SDL_SCANCODE_A, SDL_SCANCODE_X, SDL_SCANCODE_Q, SDL_SCANCODE_W,
    SDL_SCANCODE_RETURN, SDL_SCANCODE_RSHIFT};
  const int pads[12] = {12, 13, 14, 15, 2, 1, 4, 3, 10, 11, 7, 5};
  memcpy(c->keys[0], keys, sizeof keys);
  for (int p = 0; p < 2; p++) {
    c->deadzone[p] = 25;
    memcpy(c->pads[p], pads, sizeof pads);
  }
  c->assist_keys[0] = SDL_SCANCODE_BACKSPACE;
  c->assist_keys[1] = SDL_SCANCODE_TAB;
  c->assist_pads[0] = DKC1_PAD_AXIS(SDL_CONTROLLER_AXIS_TRIGGERLEFT, 1);
  c->assist_pads[1] = DKC1_PAD_AXIS(SDL_CONTROLLER_AXIS_TRIGGERRIGHT, 1);
  /* distrobox-gaming: upstream defaults leave assist_enabled=0 (the toggle
   * lives in the macOS pause menu, which Linux has no equivalent of), gating
   * off ALL pad assist bindings — rewind/FF on the triggers included. Enable
   * it here, and bind save/load state to Select+L1 / Select+R1 chords
   * (DKC1_PAD_CHORD is our addition from dkc1-linux-port.patch). */
  c->assist_enabled = 1;
  c->assist_pads[2] = DKC1_PAD_CHORD(SDL_CONTROLLER_BUTTON_BACK,
                                     SDL_CONTROLLER_BUTTON_LEFTSHOULDER);
  c->assist_pads[3] = DKC1_PAD_CHORD(SDL_CONTROLLER_BUTTON_BACK,
                                     SDL_CONTROLLER_BUTTON_RIGHTSHOULDER);
}
int Dkc1MacEditControls(Dkc1Controls *controls) { (void)controls; return 0; }

void Dkc1MacMetalPresenterFlush(void) {}
void Dkc1MacMetalPresenterSetGraphics(const Dkc1GraphicsSettings *settings) {
  (void)settings;
}

void Dkc1MacUpdateGraphicsMenuState(int display, int upscaler, int screen) {
  (void)display; (void)upscaler; (void)screen;
}
