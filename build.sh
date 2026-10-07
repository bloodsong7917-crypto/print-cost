#!/usr/bin/env bash
# Сборка .apk (Android) и .exe (Windows). Инструменты лежат в ~/print-cost-build-tools.
# Использование: ./build.sh [android|win|all]
set -euo pipefail
SRC="$(cd "$(dirname "$0")" && pwd)"
T="${PRINT_COST_TOOLS:-$HOME/print-cost-build-tools}"
P="$T/project"
export PATH="$T/node/bin:$T/jdk/bin:$PATH"
export JAVA_HOME="$T/jdk" ANDROID_HOME="$T/android-sdk" ANDROID_SDK_ROOT="$T/android-sdk"
WHAT="${1:-all}"
VERSION="$(node -p "require('$SRC/package.json').version")"

mkdir -p "$P" "$SRC/dist"
rm -rf "$P/www" "$P/desktop"
cp -a "$SRC/www" "$SRC/desktop" "$SRC/package.json" "$SRC/capacitor.config.json" "$P/"
cd "$P"
npm install --no-audit --no-fund

if [[ "$WHAT" == all || "$WHAT" == android ]]; then
  [[ -d android ]] || npx cap add android
  python3 "$SRC/tools/android-icons.py" "$P/android"
  npx cap sync android
  # Ключ подписи создаётся один раз; сохраните папку keys, иначе обновления не встанут поверх старой версии.
  K="$T/keys"
  if [[ ! -f "$K/release.jks" ]]; then
    mkdir -p "$K"; chmod 700 "$K"
    head -c 24 /dev/urandom | base64 | tr -d '/+=' > "$K/password.txt"; chmod 600 "$K/password.txt"
    keytool -genkeypair -keystore "$K/release.jks" -alias printcost -keyalg RSA -keysize 2048 -validity 10000 \
      -storepass "$(cat "$K/password.txt")" -keypass "$(cat "$K/password.txt")" -dname "CN=Print Cost" >/dev/null
  fi
  PW="$(cat "$K/password.txt")"
  (cd android && ./gradlew --no-daemon -q assembleRelease \
    -Pandroid.injected.signing.store.file="$K/release.jks" -Pandroid.injected.signing.store.password="$PW" \
    -Pandroid.injected.signing.key.alias=printcost -Pandroid.injected.signing.key.password="$PW")
  cp android/app/build/outputs/apk/release/app-release.apk "$SRC/dist/PrintCost-$VERSION.apk"
fi

if [[ "$WHAT" == all || "$WHAT" == win ]]; then
  rm -rf dist-win
  npx electron-builder --win --x64
  cp dist-win/*.exe "$SRC/dist/"
fi
ls -lh "$SRC/dist"
