#!/usr/bin/env bash
# Installs the blocker as a locked system service that starts on boot.
set -e
if [ "$EUID" -ne 0 ]; then echo "Run with sudo: sudo ./install-linux.sh"; exit 1; fi
if [ -e /opt/hard-blocker/blocker.py ]; then
  echo "Already installed. To change settings: sudo study edit (applies after 24h)."
  echo "To reinstall, run sudo ./uninstall-linux.sh first (takes 15 minutes)."
  exit 1
fi

python3 -c "import psutil" 2>/dev/null || apt-get install -y python3-psutil

mkdir -p /opt/hard-blocker /var/lib/hard-blocker
cp "$(dirname "$0")/blocker.py" "$(dirname "$0")/config.json" /opt/hard-blocker/
chmod 755 /opt/hard-blocker/blocker.py
chmod 644 /opt/hard-blocker/config.json

cat > /etc/systemd/system/hard-blocker.service <<UNIT
[Unit]
Description=Hard blocker (games and sites during study hours)
After=network.target

[Service]
ExecStart=/usr/bin/python3 /opt/hard-blocker/blocker.py run
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
UNIT

# Guard: every minute starts the blocker again if someone stopped it
cat > /etc/systemd/system/hard-blocker-guard.service <<UNIT
[Unit]
Description=Hard blocker guard

[Service]
Type=oneshot
ExecStart=/usr/bin/systemctl start hard-blocker.service
UNIT

cat > /etc/systemd/system/hard-blocker-guard.timer <<UNIT
[Unit]
Description=Hard blocker guard timer

[Timer]
OnBootSec=30
OnUnitActiveSec=60

[Install]
WantedBy=timers.target
UNIT

ln -sf /opt/hard-blocker/blocker.py /usr/local/bin/study
systemctl daemon-reload
systemctl enable --now hard-blocker.service hard-blocker-guard.timer

# Lock the files so they can't be edited or deleted (not even with sudo) without chattr -i
for f in /opt/hard-blocker/blocker.py /opt/hard-blocker/config.json \
         /etc/systemd/system/hard-blocker.service \
         /etc/systemd/system/hard-blocker-guard.service \
         /etc/systemd/system/hard-blocker-guard.timer; do
  chattr +i "$f"
done

echo "Installed and locked. Try: study status   or   study today"
