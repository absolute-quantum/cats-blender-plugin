"""Report bpy.ops references that do not exist in the running Blender."""

import ast
import importlib
import sys
from pathlib import Path

import bpy


repo_dir = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(repo_dir.parent))
addon = importlib.import_module(repo_dir.name)


def operator_name(node):
    if not isinstance(node, ast.Attribute):
        return None
    operation = node.attr
    category_node = node.value
    if not isinstance(category_node, ast.Attribute):
        return None
    category = category_node.attr
    ops_node = category_node.value
    if not (
        isinstance(ops_node, ast.Attribute)
        and ops_node.attr == "ops"
        and isinstance(ops_node.value, ast.Name)
        and ops_node.value.id == "bpy"
    ):
        return None
    return category, operation


def run():
    addon.register()
    referenced = set()
    for path in repo_dir.rglob("*.py"):
        relative = path.relative_to(repo_dir)
        if relative.parts[0] in {"tests", "compat_backup_installed_20260727"}:
            continue
        tree = ast.parse(path.read_text(encoding="utf-8-sig"), filename=str(path))
        for node in ast.walk(tree):
            name = operator_name(node)
            if name:
                referenced.add(name)

    missing = []
    for category, operation in sorted(referenced):
        try:
            getattr(getattr(bpy.ops, category), operation).get_rna_type()
        except (AttributeError, KeyError, RuntimeError):
            missing.append(f"{category}.{operation}")

    print("CATS_OPERATOR_REFERENCES", len(referenced))
    print("CATS_MISSING_OPERATORS", ",".join(missing))
    addon.unregister()


if __name__ == "__main__":
    run()
