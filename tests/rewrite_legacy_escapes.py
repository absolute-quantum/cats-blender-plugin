"""One-shot source migration for Python 3.13 invalid escape warnings."""

import ast
import re
from pathlib import Path


repo_dir = Path(__file__).resolve().parents[1]
targets = (
    repo_dir / "tools" / "armature.py",
    repo_dir / "tools" / "armature_bones.py",
    repo_dir / "extern_tools" / "mmd_tools_local" / "operators" / "fileio.py",
)


for path in targets:
    before = path.read_text(encoding="utf-8")
    after = re.sub(r"(?<!\\)\\([Ll.])", r"\\\\\1", before)
    if before == after:
        continue

    # Doubling these invalid escapes must preserve every parsed value and all
    # executable semantics. Refuse to write if the AST differs.
    before_ast = ast.dump(ast.parse(before), include_attributes=False)
    after_ast = ast.dump(ast.parse(after), include_attributes=False)
    if before_ast != after_ast:
        raise RuntimeError(f"Escape rewrite changed semantics: {path}")
    path.write_text(after, encoding="utf-8", newline="")
    print(f"REWROTE {path.relative_to(repo_dir)}")
