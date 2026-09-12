"""
flatten_xacro.py
-----------------
A minimal, purpose-built processor that expands the specific subset of
xacro features used in 4dof_arm.urdf.xacro (xacro:property, ${...} math
expressions, and simple xacro:macro calls for inertial blocks) into a
plain, standard URDF file.

This exists ONLY because the sandbox used to build this project has no
network access to install the real `xacro` ROS package for a local
smoke-test. In a real ROS 2 workstation, use the actual xacro tool:

    ros2 run xacro xacro 4dof_arm.urdf.xacro -o 4dof_arm.urdf

or let `launch/display.launch.py` invoke xacro automatically at launch
time (this is the normal, recommended workflow and is what the launch
file in this package does).
"""

import re
import sys
import copy
import xml.etree.ElementTree as ET

XACRO_NS = "http://www.ros.org/wiki/xacro"


def qname(tag):
    return f"{{{XACRO_NS}}}{tag}"


def safe_eval(expr, scope):
    # Only allow arithmetic - properties are all numeric in this file.
    allowed = {"__builtins__": {}}
    allowed.update(scope)
    return eval(expr, allowed)


def substitute_expressions(text, scope):
    if text is None:
        return None

    def repl(m):
        val = safe_eval(m.group(1), scope)
        if isinstance(val, float) and val == int(val):
            return str(val)
        return str(val)

    return re.sub(r"\$\{([^}]+)\}", repl, text)


def substitute_attribs(elem, scope):
    for k, v in list(elem.attrib.items()):
        elem.set(k, substitute_expressions(v, scope))


def process(root):
    scope = {}
    macros = {}

    # First pass at top level: collect properties & macros, in document order,
    # so later properties can reference earlier ones.
    new_children = []
    for child in list(root):
        if child.tag == qname("property"):
            name = child.get("name")
            value_str = child.get("value")
            value_str_sub = substitute_expressions(value_str, scope)
            try:
                scope[name] = float(value_str_sub)
            except ValueError:
                scope[name] = value_str_sub
        elif child.tag == qname("macro"):
            macros[child.get("name")] = child
        else:
            new_children.append(child)

    # Recursively expand macro calls and substitute expressions everywhere else.
    def expand(elem, local_scope):
        tag = elem.tag
        if tag.startswith(f"{{{XACRO_NS}}}"):
            macro_name = tag.split("}")[1]
            if macro_name in macros:
                macro_def = macros[macro_name]
                params = macro_def.get("params", "").split()
                call_scope = dict(local_scope)
                for p in params:
                    if p in elem.attrib:
                        v = substitute_expressions(elem.get(p), local_scope)
                        try:
                            v = float(v)
                        except ValueError:
                            pass
                        call_scope[p] = v
                expanded_nodes = []
                for sub in list(macro_def):
                    expanded_nodes.append(expand(copy.deepcopy(sub), call_scope))
                return expanded_nodes  # list of elements to splice in
            else:
                raise ValueError(f"Unknown xacro macro: {macro_name}")
        else:
            substitute_attribs(elem, local_scope)
            if elem.text:
                elem.text = substitute_expressions(elem.text, local_scope)
            new_kids = []
            for c in list(elem):
                result = expand(c, local_scope)
                if isinstance(result, list):
                    new_kids.extend(result)
                else:
                    new_kids.append(result)
            elem[:] = new_kids
            return elem

    final_children = []
    for c in new_children:
        result = expand(c, scope)
        if isinstance(result, list):
            final_children.extend(result)
        else:
            final_children.append(result)

    out_root = ET.Element("robot", {"name": root.get("name")})
    out_root[:] = final_children
    return out_root


def main(in_path, out_path):
    tree = ET.parse(in_path)
    root = tree.getroot()
    out_root = process(root)
    out_tree = ET.ElementTree(out_root)
    ET.indent(out_tree, space="  ")
    out_tree.write(out_path, xml_declaration=True, encoding="UTF-8")
    print(f"Wrote flattened URDF to {out_path}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
