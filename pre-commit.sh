set -e

for ufo in sources/masters/*.ufo; do
  env/bin/ufonormalizer "$ufo"
  git add "$ufo"
done
