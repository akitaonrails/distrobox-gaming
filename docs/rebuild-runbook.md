# Rebuild Runbook

Use this when recreating the gaming distrobox from scratch.

1. Configure paths:

   ```sh
   cp config/distrobox-gaming.env.example config/distrobox-gaming.env
   $EDITOR config/distrobox-gaming.env
   ```

2. Check host paths and permissions:

   ```sh
   ./bin/dg check
   ```

3. Create the distrobox:

   ```sh
   ./bin/dg create
   ```

4. Install packages:

   ```sh
   ./bin/dg bootstrap
   ```

5. Apply configuration:

   ```sh
   ./bin/dg configure
   ```

6. Verify:

   ```sh
   ./bin/dg verify
   ```

The scripts are intended to be idempotent. Re-run individual phases after
changing config paths or templates.

Do not run cleanup commands against ROM, BIOS, save, firmware, or game-data
directories from these scripts.

