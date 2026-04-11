#!/usr/bin/env sh
set -eu

DG_PROJECT_ROOT="${DG_PROJECT_ROOT:-$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)}"
. "$DG_PROJECT_ROOT/lib/paths.sh"
. "$DG_PROJECT_ROOT/lib/common.sh"

esde_dir="$DG_BOX_HOME/ES-DE/custom_systems"
esde_xml="$esde_dir/es_systems.xml"
ensure_dir "$esde_dir"
backup_once "$esde_xml"

log "Writing ES-DE custom systems"
cat > "$esde_xml" <<EOF
<?xml version="1.0"?>
<systemList>
    <system>
        <name>switch</name>
        <fullname>Nintendo Switch</fullname>
        <path>%ROMPATH%/switch</path>
        <extension>.nca .NCA .nro .NRO .nso .NSO .nsp .NSP .xci .XCI</extension>
        <command label="Eden (Standalone)">env -u QT_STYLE_OVERRIDE eden %ROM%</command>
        <command label="Ryujinx (Standalone)">%EMULATOR_RYUJINX% %ROM%</command>
        <platform>switch</platform>
        <theme>switch</theme>
    </system>

    <system>
        <name>psx</name>
        <fullname>Sony PlayStation</fullname>
        <path>%ROMPATH%/psx</path>
        <extension>.bin .BIN .cbn .CBN .ccd .CCD .chd .CHD .cue .CUE .ecm .ECM .exe .EXE .img .IMG .iso .ISO .m3u .M3U .mdf .MDF .mds .MDS .minipsf .MINIPSF .pbp .PBP .psexe .PSEXE .psf .PSF .toc .TOC .z .Z .znx .ZNX .7z .7Z .zip .ZIP</extension>
        <command label="DuckStation (Standalone)">duckstation-qt -batch %ROM%</command>
        <command label="Beetle PSX HW">%EMULATOR_RETROARCH% -L %CORE_RETROARCH%/mednafen_psx_hw_libretro.so %ROM%</command>
        <command label="Beetle PSX">%EMULATOR_RETROARCH% -L %CORE_RETROARCH%/mednafen_psx_libretro.so %ROM%</command>
        <platform>psx</platform>
        <theme>psx</theme>
    </system>

    <system>
        <name>ps2</name>
        <fullname>Sony PlayStation 2</fullname>
        <path>%ROMPATH%/ps2</path>
        <extension>.bin .BIN .chd .CHD .ciso .CISO .cso .CSO .dump .DUMP .elf .ELF .gz .GZ .m3u .M3U .mdf .MDF .img .IMG .iso .ISO .isz .ISZ .ngr .NRG .zso .ZSO</extension>
        <command label="PCSX2 (Standalone)">pcsx2-qt -batch %ROM%</command>
        <command label="PCSX2 (RetroArch)">%EMULATOR_RETROARCH% -L %CORE_RETROARCH%/pcsx2_libretro.so %ROM%</command>
        <platform>ps2</platform>
        <theme>ps2</theme>
    </system>

    <system>
        <name>dreamcast</name>
        <fullname>Sega Dreamcast</fullname>
        <path>%ROMPATH%/dreamcast</path>
        <extension>.cdi .CDI .chd .CHD .cue .CUE .dat .DAT .elf .ELF .gdi .GDI .iso .ISO .lst .LST .m3u .M3U .7z .7Z .zip .ZIP</extension>
        <command label="Flycast (Standalone)">$DG_BOX_HOME/bin/flycast-hires %ROM%</command>
        <command label="Flycast (RetroArch)">%EMULATOR_RETROARCH% -L %CORE_RETROARCH%/flycast_libretro.so %ROM%</command>
        <platform>dreamcast</platform>
        <theme>dreamcast</theme>
    </system>

    <system>
        <name>gc</name>
        <fullname>Nintendo GameCube</fullname>
        <path>%ROMPATH%/gc</path>
        <extension>.ciso .CISO .dff .DFF .dol .DOL .elf .ELF .gcm .GCM .gcz .GCZ .iso .ISO .json .JSON .m3u .M3U .rvz .RVZ .tgc .TGC .wad .WAD .wbfs .WBFS .wia .WIA .7z .7Z .zip .ZIP</extension>
        <command label="Dolphin (Standalone)">dolphin-emu -b -e %ROM%</command>
        <command label="Dolphin (RetroArch)">%EMULATOR_RETROARCH% -L %CORE_RETROARCH%/dolphin_libretro.so %ROM%</command>
        <platform>gc</platform>
        <theme>gc</theme>
    </system>

    <system>
        <name>wii</name>
        <fullname>Nintendo Wii</fullname>
        <path>%ROMPATH%/wii</path>
        <extension>.ciso .CISO .dff .DFF .dol .DOL .elf .ELF .gcm .GCM .gcz .GCZ .iso .ISO .json .JSON .m3u .M3U .rvz .RVZ .tgc .TGC .wad .WAD .wbfs .WBFS .wia .WIA .7z .7Z .zip .ZIP</extension>
        <command label="Dolphin (Standalone)">dolphin-emu -b -e %ROM%</command>
        <command label="Dolphin (RetroArch)">%EMULATOR_RETROARCH% -L %CORE_RETROARCH%/dolphin_libretro.so %ROM%</command>
        <platform>wii</platform>
        <theme>wii</theme>
    </system>

    <system>
        <name>psp</name>
        <fullname>Sony PlayStation Portable</fullname>
        <path>%ROMPATH%/psp</path>
        <extension>.chd .CHD .cso .CSO .elf .ELF .iso .ISO .pbp .PBP .prx .PRX .7z .7Z .zip .ZIP</extension>
        <command label="PPSSPP (Standalone)">PPSSPPQt %ROM%</command>
        <command label="PPSSPP (RetroArch)">%EMULATOR_RETROARCH% -L %CORE_RETROARCH%/ppsspp_libretro.so %ROM%</command>
        <platform>psp</platform>
        <theme>psp</theme>
    </system>

    <system>
        <name>ps4</name>
        <fullname>Sony PlayStation 4</fullname>
        <path>%ROMPATH%/ps4/$DG_SHADPS4_TITLE_ID</path>
        <extension>.bin .BIN</extension>
        <command label="shadPS4 Driveclub (Standalone)">$DG_SHADPS4_BIN -g %ROM% -p $DG_SHADPS4_PATCH_XML -f true</command>
        <platform>ps4</platform>
        <theme>ps4</theme>
    </system>

    <system>
        <name>xbox</name>
        <fullname>Microsoft Xbox</fullname>
        <path>%ROMPATH%/xbox</path>
        <extension>.iso .ISO .xiso .XISO</extension>
        <command label="xemu (Standalone)">xemu -dvd_path %ROM%</command>
        <platform>xbox</platform>
        <theme>xbox</theme>
    </system>

    <system>
        <name>model3</name>
        <fullname>Sega Model 3</fullname>
        <path>%ROMPATH%/model3</path>
        <extension>.zip .ZIP</extension>
        <command label="Supermodel (Standalone)">supermodel %ROM%</command>
        <platform>arcade</platform>
        <theme>model3</theme>
    </system>

    <system>
        <name>naomi</name>
        <fullname>Sega NAOMI</fullname>
        <path>%ROMPATH%/naomi</path>
        <extension>.bin .BIN .cdi .CDI .chd .CHD .cue .CUE .dat .DAT .elf .ELF .gdi .GDI .iso .ISO .lst .LST .zip .ZIP .7z .7Z</extension>
        <command label="Flycast (Standalone)">$DG_BOX_HOME/bin/flycast-hires %ROM%</command>
        <command label="Flycast (RetroArch)">%EMULATOR_RETROARCH% -L %CORE_RETROARCH%/flycast_libretro.so %ROM%</command>
        <platform>arcade</platform>
        <theme>naomi</theme>
    </system>
</systemList>
EOF

log "ES-DE configuration completed: $esde_xml"
