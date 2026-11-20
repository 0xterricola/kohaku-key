#!/usr/bin/env bash
set -euo pipefail

for name in ANT_JAVACARD_JAR KEYCARD_JC_SDK KEYCARD_MATH_HOME; do
    if [[ -z "${!name:-}" ]]; then
        printf 'Missing: %s\n' "$name" >&2
        exit 1
    fi
done

[[ -f "$ANT_JAVACARD_JAR" ]] || {
    echo "ant-javacard JAR missing" >&2
    exit 1
}
[[ -d "$KEYCARD_JC_SDK" ]] || {
    echo "JavaCard SDK missing" >&2
    exit 1
}
[[ -f "$KEYCARD_MATH_HOME/keycard-math.jar" ]] || {
    echo "keycard-math JAR missing" >&2
    exit 1
}

cd "$(dirname "$0")"
exec ant -f build.xml cap
