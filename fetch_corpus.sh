#!/bin/sh
# Fetch the tuning corpus (shallow clones, gitignored).
set -eu
cd "$(dirname "$0")"
mkdir -p corpus
for r in anthropics/skills obra/superpowers mattpocock/skills growthbook/skills; do
  n=$(echo "$r" | tr '/' '_')
  if [ ! -d "corpus/$n" ]; then
    git clone --depth 1 "https://github.com/$r.git" "corpus/$n"
  else
    echo "$n already present"
  fi
done
