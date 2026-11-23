"""Check data initialized by the same packaged app on an isolated CI runner."""
import json
import os
from pathlib import Path
import re
import sys

assert os.environ.get("CI") == "true", "isolated CI only"
evidence = Path(sys.argv[1])
source = Path("crates/openless-core/src")
original = json.loads((source / "builtin_styles/intent-reconstruction-v1.json").read_text())
rules = re.search(
    r'pub const DICTATION_REVISION_RULES: &str = "(.*?)";',
    (source / "style_packs.rs").read_text(),
    re.S,
).group(1)
path = Path.home() / "Library/Application Support/OpenLess/style-packs.json"
packs = json.loads(path.read_text())
pack = next(row for row in packs if row["id"] == "openless.intent-reconstruction")
assert pack["version"] == "1.2.0", pack["version"]
assert len(original["prompt"]) == 5671
assert len(original["selectionPrompt"]) == 3494
for key in ("prompt", "selectionPrompt"):
    assert pack[key] == original[key] + "\n\n" + rules, key
    assert pack[key].count(rules) == 1, key
(evidence / "initialized-intent-style.json").write_text(
    json.dumps(pack, ensure_ascii=False, indent=2) + "\n"
)
(evidence / "initialized-style-result.txt").write_text(
    "PASS: same packaged app initialized intent 1.2.0; complete original "
    "5671/3494 character prefixes and exactly one requested correction tail per prompt\n"
)
print("PASS initialized intent 1.2.0: complete original prefixes plus correction tails")
