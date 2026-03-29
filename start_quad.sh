#!/bin/bash

export XDG_RUNTIME_DIR=/run/user/1000
export WAYLAND_DISPLAY=wayland-0

pkill chromium 2>/dev/null
sleep 1

chromium \
  --ozone-platform=wayland \
  --kiosk \
  --noerrdialogs \
  --disable-infobars \
  --disable-session-crashed-bubble \
  --user-data-dir=/tmp/chromium-monitor \
  file:///home/pi/monitoring/quad.html
