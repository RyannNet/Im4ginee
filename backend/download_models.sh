#!/usr/bin/env bash
set -euo pipefail

MODELS_DIR=${MODELS_DIR:-"/workspace/backend/models"}
mkdir -p "$MODELS_DIR"

# Example: download Real-ESRGAN weights placeholder
mkdir -p "$MODELS_DIR/realesrgan"
if [ ! -f "$MODELS_DIR/realesrgan/weights.pth" ]; then
  echo "Placing placeholder Real-ESRGAN weights (provide real weights for production)"
  dd if=/dev/zero of="$MODELS_DIR/realesrgan/weights.pth" bs=1 count=1024 >/dev/null 2>&1 || true
fi

echo "Models directory prepared at $MODELS_DIR"
