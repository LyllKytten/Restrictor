# Hard Blocker

A study blocker for Linux and Windows. During study hours it closes games and blocks distracting sites. It also shows your daily plan. It's built to be **hard to switch off**, so "just 5 minutes of Roblox" doesn't turn into 3 hours.

## What it does

- **Kills games** every 15 seconds during blocked hours: Steam and everything installed through it, Minecraft and TLauncher, Valorant/Riot, Roblox (including Sober on Linux), and the Epic and GOG launchers
- **Blocks sites** through the system `hosts` file: TikTok, YouTube, Twitch, movie and anime sites, game stores, torrent sites and browser game sites
- **Shows your plan:** `study today` prints the day and marks what you should be doing now
- **Lock mode**, so you can't cheat in a weak moment:
  - Config changes start working **24 hours** after you make them
  - On Linux, the files are locked with `chattr +i`, so even `sudo` can't edit them directly
  - A watchdog restarts the blocker within a minute if it gets stopped
  - Uninstalling means typing a sentence and then waiting **15 minutes**

## Install

### Ubuntu / Linux

```bash
sudo ./install-linux.sh
```

The installer copies everything to `/opt/hard-blocker` and starts the `hard-blocker` systemd service, along with a guard timer that restarts it.

### Windows

1. Install [Python](https://www.python.org/downloads/). Tick "Add Python to PATH" during setup.
2. Open PowerShell **as Administrator** in this folder and run:

```powershell
powershell -ExecutionPolicy Bypass -File install-windows.ps1
```

The installer copies everything to `C:\ProgramData\HardBlocker` and creates two scheduled tasks: `HardBlocker` and `HardBlockerGuard`.

> After blocking starts, restart your browser. Browsers remember sites for a few minutes.

## Usage

| Command | What it does |
|---|---|
| `study status` | Is blocking on right now, and what you should be doing |
| `study today` | Today's full plan |
| `sudo study edit` | Edit the config (applies after 24 hours) |

On Windows, use `python C:\ProgramData\HardBlocker\blocker.py <command>` instead of `study`.

## Config

Everything lives in `config.json`:

- `block_hours`: when games and sites are blocked, per day (`mon` to `sun`)
- `kill_process_names`: process names to kill (no `.exe` needed)
- `kill_if_path_contains`: kill any process whose path or command line contains this text (for example `steamapps` catches every Steam game)
- `blocked_sites`: domains to block (the `www.` version is added automatically)
- `plan`: your daily schedule for `weekday` and `weekend`, shown by `study today`

Edit `config.json` **before** installing to set things up the way you want. After installing, any change takes 24 hours to apply.

## Uninstall

```bash
sudo ./uninstall-linux.sh                                              # Linux
powershell -ExecutionPolicy Bypass -File uninstall-windows.ps1         # Windows (as Admin)
```

You'll have to type `I am giving up on my olympiad and my exams` and then wait 15 minutes. That's on purpose.

## Limits

- Someone who knows the system well can still get around it. The goal is to make cheating slow and annoying, not impossible.
- `hosts` can't block wildcards. Sites with lots of mirror domains (kinogo, anime sites) need a browser extension like [LeechBlock NG](https://www.proginosko.com/leechblock/) with rules like `*kinogo*` and `*anime*`.
- The Windows scripts haven't been tested yet.

## Phone (Android)

You can't run this blocker on a phone. Use these instead:

1. **[NextDNS](https://nextdns.io):** go to Parental Control, add the services and set Recreation Time to your free hours. Put the extra sites in the Denylist. Then on the phone, go to Settings → Network & internet → Private DNS and enter your NextDNS address.
2. **Stay Focused** or **AppBlock** with **Strict mode**, to block game apps and stop you changing the Private DNS setting.
3. Hardest option: **Google Family Link**, managed by a parent.

## Olympiad prep

See [ROADMAP.md](ROADMAP.md) for an 8-week C++ olympiad plan (city level).
