#!/usr/bin/env python3
"""Generate TeknoParrot UserProfiles for a roms_rare/TeknoParrot collection and
wire ES-DE .tp launch stubs. Matches descriptively-named game folders to
TeknoParrot GameIds via the shipped Metadata (game_name + platform), sets each
UserProfile's <GamePath> to the game exe as a Wine Z: path, moves console-backed
games (PS2/PS3/Xbox/GC) to the archive dir, and writes one <GameId>.tp stub +
gamelist.xml for ES-DE.

Usage: tp_generate_profiles.py GAMES_DIR INSTALL_DIR LAUNCHERS_DIR ARCHIVE_DIR
Idempotent. Prints a summary; exits 0.
"""
import os, re, sys, json, glob, shutil
import xml.etree.ElementTree as ET

GAMES, INSTALL, LAUNCHERS, ARCHIVE = sys.argv[1:5]
META=os.path.join(INSTALL,"Metadata"); PROF=os.path.join(INSTALL,"GameProfiles"); USER=os.path.join(INSTALL,"UserProfiles")
SKIP_FOLDER={"TPBootstrapper","initdexp-chd","initd-chd"}
SUPPORTED={"OpenParrot","TeknoParrot","ElfLdr2","N2","TeknoMacaw","TeknoViper","TeknoVegas"}
CONSOLE={"pcsx2x6","cxbxr","RPCS3","Dolphin","CrediarDolphin","Play"}

def norm(s): return re.sub(r'[^a-z0-9]','',(s or '').lower())
def strip_suffix(n): return re.sub(r'\s*\([^)]*\)\s*$','',re.sub(r'\s*\([^)]*\)\s*$','',n)).strip()
def winpath(p): return "Z:\\"+p.lstrip("/").replace("/","\\")
def parse_folder(name):
    n=re.sub(r'\s*\[TP\]\s*$','',name).strip()
    br=re.findall(r'\[([^\]]+)\]',n)
    m=re.search(r'[\(\[]',n)
    return (n[:m.start()] if m else n).strip(), (br[-1].strip() if br else '')
REGION={'export':'export','world':'export','usa':'export','us':'export','japan':'japan','jpn':'japan','jp':'japan','japanese':'japan'}
def region_of(t):
    t=t.lower()
    for k,v in REGION.items():
        if re.search(r'\b'+k+r'\b',t): return v
    return ''

idx={}
for f in glob.glob(os.path.join(META,"*.json")):
    gid=os.path.splitext(os.path.basename(f))[0]
    try: d=json.load(open(f))
    except: continue
    gn=d.get("game_name","")
    for k in (norm(strip_suffix(gn)), norm(gn)):
        idx.setdefault(k,[]).append((gid,gn,d.get("platform","")))
def score(fp,fr,c):
    gid,gn,pl=c; s=0
    if norm(fp) and (norm(fp) in norm(pl) or norm(pl) in norm(fp)): s+=3
    cr=region_of(gn)
    if fr and cr: s+= 3 if fr==cr else -2
    if 'elf' in gid.lower(): s+=1
    return s
def prof(gid):
    p=os.path.join(PROF,gid+".xml")
    if not os.path.isfile(p): return None
    try: r=ET.parse(p).getroot()
    except: return None
    return {"exe":r.findtext("ExecutableName") or "", "emu":r.findtext("EmulatorType") or ""}
# Non-game exes to ignore when a GameProfile leaves ExecutableName empty.
_NONGAME=re.compile(r'openparrot|budgieloader|parrotloader|unins|vc_?redist|'
                    r'dxsetup|directx|redist|dotnet|crashreport|prerequisite|'
                    r'^setup\.exe$|vcredist', re.I)
def find_exe(folder,exe):
    # NB: os.walk, not glob — folder names contain [brackets] which glob treats
    # as character classes and silently fails to match.
    root=os.path.join(GAMES,folder)
    if exe:
        for dp,_,fs in os.walk(root):
            for f in fs:
                if f.lower()==exe.lower(): return os.path.join(dp,f)
        return None
    # empty ExecutableName: prefer game.exe, else the largest non-helper .exe
    cands=[]
    for dp,_,fs in os.walk(root):
        for f in fs:
            if f.lower().endswith(".exe") and not _NONGAME.search(f):
                p=os.path.join(dp,f)
                try: cands.append((os.path.getsize(p),p,f))
                except OSError: pass
    if not cands: return None
    g=[c for c in cands if c[2].lower()=="game.exe"]
    if g: return g[0][1]
    cands.sort(reverse=True)
    return cands[0][1]

os.makedirs(USER,exist_ok=True); os.makedirs(LAUNCHERS,exist_ok=True); os.makedirs(ARCHIVE,exist_ok=True)
written=[]; archived=[]; skipped=[]
for folder in sorted(os.listdir(GAMES)):
    if not os.path.isdir(os.path.join(GAMES,folder)) or folder in SKIP_FOLDER: continue
    gname,plat=parse_folder(folder); fr=region_of(folder)
    cands=idx.get(norm(gname))
    if not cands:
        direct=[os.path.splitext(os.path.basename(x))[0] for x in glob.glob(os.path.join(PROF,'*.xml')) if norm(os.path.splitext(os.path.basename(x))[0])==norm(gname)]
        cands=[(direct[0],gname,plat)] if len(direct)==1 else None
    if not cands: skipped.append((folder,"unmatched")); continue
    uniq={c[0]:c for c in cands}; cands=list(uniq.values())
    if len(cands)==1: gid=cands[0][0]
    else:
        sc=sorted(cands,key=lambda c:score(plat,fr,c),reverse=True)
        if score(plat,fr,sc[0])==score(plat,fr,sc[1]): skipped.append((folder,"ambiguous")); continue
        gid=sc[0][0]
    info=prof(gid)
    if not info: skipped.append((folder,"no-profile")); continue
    if info["emu"] in CONSOLE:
        dst=os.path.join(ARCHIVE,folder)
        if os.path.isdir(os.path.join(GAMES,folder)) and not os.path.exists(dst):
            shutil.move(os.path.join(GAMES,folder),dst); archived.append((folder,info["emu"]))
        continue
    if info["emu"] not in SUPPORTED: skipped.append((folder,"emu:"+info["emu"])); continue
    ep=find_exe(folder,info["exe"])
    if not ep: skipped.append((folder,"exe-not-found:"+repr(info["exe"]))); continue
    t=ET.parse(os.path.join(PROF,gid+".xml")); r=t.getroot()
    gp=r.find("GamePath")
    if gp is None: gp=ET.SubElement(r,"GamePath")
    gp.text=winpath(ep)
    t.write(os.path.join(USER,gid+".xml"),encoding="utf-8",xml_declaration=True)
    written.append(gid)

# ES-DE .tp stubs + gamelist
for f in glob.glob(os.path.join(LAUNCHERS,"*.tp")): os.remove(f)
gl=['<?xml version="1.0"?>','<gameList>']
for gid in sorted(set(written)):
    open(os.path.join(LAUNCHERS,gid+".tp"),"w").close()
    name=gid; mp=os.path.join(META,gid+".json")
    if os.path.exists(mp):
        try: name=json.load(open(mp)).get("game_name",gid)
        except: pass
    gl.append(f"  <game>\n    <path>./{gid}.tp</path>\n    <name>{name}</name>\n  </game>")
gl.append("</gameList>")
open(os.path.join(LAUNCHERS,"gamelist.xml"),"w").write("\n".join(gl))

print(f"UserProfiles written: {len(set(written))}")
print(f"console games archived: {len(archived)}")
print(f"skipped (unmatched/exe-missing/console-emu/ambiguous): {len(skipped)}")
for folder,why in skipped: print(f"  SKIP [{why}] {folder}")
