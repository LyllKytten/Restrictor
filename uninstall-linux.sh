#!/usr/bin/env bash
# Removing the blocker takes 15 minutes on purpose. Go solve a problem instead :)
set -e
if [ "$EUID" -ne 0 ]; then echo "Run with sudo: sudo ./uninstall-linux.sh"; exit 1; fi

PHRASE="I am giving up on my olympiad and my exams"
echo "To remove the blocker, type exactly:"
echo "  $PHRASE"
read -r answer
if [ "$answer" != "$PHRASE" ]; then echo "Wrong. Blocker stays."; exit 1; fi

echo "OK. Waiting 15 minutes. Close this window to cancel (good choice)."
for ((left = 15; left > 0; left--)); do
  echo "  $left minutes left..."
  sleep 60
done

for f in /opt/hard-blocker/* /var/lib/hard-blocker/* /etc/systemd/system/hard-blocker*; do
  [ -e "$f" ] && chattr -i "$f" || true
done
systemctl disable --now hard-blocker-guard.timer hard-blocker.service || true
python3 /opt/hard-blocker/blocker.py clear || true
rm -f /etc/systemd/system/hard-blocker.service /etc/systemd/system/hard-blocker-guard.* /usr/local/bin/study
rm -rf /opt/hard-blocker /var/lib/hard-blocker
systemctl daemon-reload
echo "Removed."
