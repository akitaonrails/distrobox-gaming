# Box Steam stuck on "waiting for network connection"

## Symptom

The **in-box** Steam (`gaming` distrobox, launched from the "Steam (gaming)"
menu entry → `bin/steam-launch`) opens, shows the spinning **"waiting for
network connection"** screen, and never reaches the login screen or library —
even though the network is completely fine (browsers work, other box apps reach
the internet).

## Root cause

Steam's newer client (2026 builds) monitors network state through the **system
D-Bus / NetworkManager**. The `gaming` distrobox has **no system D-Bus of its
own** — only a session bus — and its `/run` is a **tmpfs that is wiped on every
container restart**, so `/run/dbus/system_bus_socket` is absent.

Without that socket the client's network subsystem never initializes. In the CEF
logs you see:

```
CONSOLE: "SteamApp Init - Before Login - SystemNetworkStore - ERROR
          TypeError: SteamClient.System.Network.RegisterForDeviceChanges is not a function"
ERROR:bus.cc: Failed to connect to socket /run/dbus/system_bus_socket: No such file or directory
```

Steam therefore believes there is no network and spins forever. The login window
is even created, but off-screen/hidden, so nothing usable appears.

**Why it breaks "out of the blue":** nothing you change triggers it — a plain
**distrobox container restart** (which wipes the tmpfs `/run`) removes the socket.
The host does not need to reboot. Because the socket was historically never made
persistent, the next container restart surfaced the missing dependency.

Diagnosing pointers: it is **not** network, DNS, clock, auth, or the UI cache.
`connection_log.txt` shows the connectivity tests *passing* and then the client
hanging before it ever attempts a CM login; `cef_log.txt` shows the D-Bus error
above.

## The fix (reproducible)

`bin/steam-launch` (source: `ansible/roles/scripts_in_box/files/steam-launch`,
deployed by the `scripts_in_box` role) links the box's expected system-bus path
to the **host's** system bus (which has NetworkManager) right before it execs
Steam:

```sh
host_system_bus="/run/host/run/dbus/system_bus_socket"   # host bus, mounted into the box
box_system_bus="/run/dbus/system_bus_socket"
if [ ! -S "$box_system_bus" ] && [ -S "$host_system_bus" ]; then
  sudo -n mkdir -p /run/dbus
  sudo -n ln -sfn "$host_system_bus" "$box_system_bus"
fi
```

It is idempotent and runs on **every** launch, so it self-heals after any
container restart (the wrapper is the box Steam entry point, and sudo is
passwordless in the box). This complements the pre-existing **session**-bus
handling in the same script.

Deploy / re-apply:

```sh
cd ansible
ansible-playbook site.yml --tags scripts        # redeploys bin/steam-launch
# verify:
distrobox-enter -n gaming -- /mnt/data/distrobox/gaming/bin/steam-launch --diagnose
#   -> system_bus=ok  session_bus=ok
```

If Steam is still stuck, confirm the host actually has the system bus + NM:
`ls -l /run/dbus/system_bus_socket` and `pgrep -a NetworkManager` on the host.
