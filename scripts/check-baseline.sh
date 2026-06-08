#!/usr/bin/env bash
set -euo pipefail

if grep -R "catch(Exception ex){}" -n app/src/main/java/com/twitterdev/rdio/app/Utils.java; then
  echo "Utils.CopyStream must not swallow broad exceptions" >&2
  exit 1
fi

grep -q "catch(IOException ex)" app/src/main/java/com/twitterdev/rdio/app/Utils.java
grep -q "throw new RuntimeException(\"Unable to copy stream\", ex)" app/src/main/java/com/twitterdev/rdio/app/Utils.java
