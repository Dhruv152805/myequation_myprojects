"""
validate_urdf_structure.py
---------------------------
Static structural validation of a URDF file, independent of ROS 2 /
urdfdom (useful in environments where those tools aren't installed).
Checks performed:

  1. Every joint's parent/child link is declared as a <link>.
  2. The link graph is a single connected tree (no cycles, no orphans).
  3. Exactly one root link (a link that is never a joint's child).
  4. Every revolute joint declares an <axis> and a <limit> with
     lower < upper.
  5. Every link has both <visual> and <collision> geometry (per the
     assignment requirement), except purely structural placeholder
     links with no geometry (none expected here).

Usage: python3 validate_urdf_structure.py path/to/robot.urdf
"""

import sys
import xml.etree.ElementTree as ET


def validate(path):
    tree = ET.parse(path)
    root = tree.getroot()
    assert root.tag == "robot", "Root element must be <robot>"

    links = {l.get("name"): l for l in root.findall("link")}
    joints = root.findall("joint")

    errors = []
    warnings = []

    children_of = {}
    parent_of = {}
    all_child_links = set()

    for j in joints:
        name = j.get("name")
        jtype = j.get("type")
        parent_el = j.find("parent")
        child_el = j.find("child")
        if parent_el is None or child_el is None:
            errors.append(f"Joint '{name}' missing <parent> or <child>")
            continue
        parent = parent_el.get("link")
        child = child_el.get("link")

        if parent not in links:
            errors.append(f"Joint '{name}': parent link '{parent}' not declared")
        if child not in links:
            errors.append(f"Joint '{name}': child link '{child}' not declared")

        if child in all_child_links:
            errors.append(f"Link '{child}' is the child of more than one joint "
                           f"(tree structure violated)")
        all_child_links.add(child)
        children_of.setdefault(parent, []).append(child)
        parent_of[child] = parent

        if jtype == "revolute":
            axis = j.find("axis")
            limit = j.find("limit")
            if axis is None:
                errors.append(f"Revolute joint '{name}' missing <axis>")
            if limit is None:
                errors.append(f"Revolute joint '{name}' missing <limit>")
            else:
                lo, hi = float(limit.get("lower")), float(limit.get("upper"))
                if not (lo < hi):
                    errors.append(f"Revolute joint '{name}': limit lower({lo}) "
                                   f"must be < upper({hi})")

    # root link(s): declared links that are never a child
    roots = [name for name in links if name not in all_child_links]
    if len(roots) != 1:
        errors.append(f"Expected exactly 1 root link, found {len(roots)}: {roots}")
    else:
        root_link = roots[0]

    # connectivity / cycle check via BFS from root
    if len(roots) == 1:
        visited = set()
        stack = [roots[0]]
        while stack:
            n = stack.pop()
            if n in visited:
                errors.append(f"Cycle detected in kinematic tree at link '{n}'")
                continue
            visited.add(n)
            stack.extend(children_of.get(n, []))
        unreached = set(links.keys()) - visited
        if unreached:
            errors.append(f"Links not connected to root: {sorted(unreached)}")

    # visual / collision presence (skip the abstract 'world' frame)
    for name, link_el in links.items():
        if name == "world":
            continue
        if link_el.find("visual") is None:
            warnings.append(f"Link '{name}' has no <visual> geometry")
        if link_el.find("collision") is None:
            warnings.append(f"Link '{name}' has no <collision> geometry")

    return errors, warnings, links, joints, parent_of, roots


def print_tree(link, children_of, depth=0):
    print("  " * depth + f"- {link}")
    for c in children_of.get(link, []):
        print_tree(c, children_of, depth + 1)


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "4dof_arm.urdf"
    errors, warnings, links, joints, parent_of, roots = validate(path)

    print(f"Validating: {path}")
    print(f"Links: {len(links)}   Joints: {len(joints)}")
    print(f"Revolute joints: {sum(1 for j in joints if j.get('type') == 'revolute')}")
    print(f"Fixed joints:    {sum(1 for j in joints if j.get('type') == 'fixed')}")

    print("\n--- Kinematic tree ---")
    children_of = {}
    for c, p in parent_of.items():
        children_of.setdefault(p, []).append(c)
    if roots:
        print_tree(roots[0], children_of)

    print("\n--- Errors ---")
    if errors:
        for e in errors:
            print("  [ERROR]", e)
    else:
        print("  None. Structure is a valid single-root tree.")

    print("\n--- Warnings ---")
    if warnings:
        for w in warnings:
            print("  [WARN]", w)
    else:
        print("  None.")

    sys.exit(1 if errors else 0)
