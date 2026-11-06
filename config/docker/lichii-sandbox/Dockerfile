FROM archlinux@sha256:b1c2fe6e717bfd5673af8fc217e1e1c3ce0dcbb1d53c3414c8425e7ce79fc6d9

# The AppImage bundles Lichii/Qt. These are the host-facing X11, Vulkan and
# font libraries it still expects. GPU driver libraries come from --gpus all.
RUN pacman -Syu --noconfirm --needed \
      alsa-lib fontconfig fribidi harfbuzz libglvnd libpulse libx11 libxcb \
      libxkbcommon-x11 noto-fonts noto-fonts-emoji ttf-dejavu \
      xcb-util-cursor \
    && pacman -Scc --noconfirm

ARG DG_UID
ARG DG_GID
RUN test -n "$DG_UID" && test -n "$DG_GID" \
    && groupadd -g "$DG_GID" gamer \
    && useradd -u "$DG_UID" -g "$DG_GID" -M -d /game-home gamer
USER gamer
ENV APPIMAGE_EXTRACT_AND_RUN=1 QT_QPA_PLATFORM=xcb
