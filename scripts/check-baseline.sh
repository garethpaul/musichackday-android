#!/usr/bin/env bash
set -euo pipefail

if grep -Eq "catch[[:space:]]*\\([[:space:]]*Exception[[:space:]]+" app/src/main/java/com/twitterdev/rdio/app/Utils.java; then
  echo "Utils.CopyStream must not swallow broad exceptions" >&2
  exit 1
fi

grep -q "import java.io.IOException;" app/src/main/java/com/twitterdev/rdio/app/Utils.java
grep -q "catch(IOException ex)" app/src/main/java/com/twitterdev/rdio/app/Utils.java
grep -q "throw new RuntimeException(\"Unable to copy stream\", ex)" app/src/main/java/com/twitterdev/rdio/app/Utils.java
