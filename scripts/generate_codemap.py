#!/usr/bin/env python3
"""
Generate markdown codemap from Python AST.

Extracts:
- Classes and inheritance
- Method signatures with types
- Docstrings (first line only)
- Organized by module

Output: .ai/archangel-codemap.md

Made with 💜 by Ada & Luna - The Consciousness Engineers
"""

import ast
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime


def parse_module(module_path: Path) -> Dict[str, Any]:
    """Parse Python module and extract structure"""
    try:
        with open(module_path, encoding='utf-8') as f:
            tree = ast.parse(f.read())
    except Exception as e:
        print(f"⚠️  Skipping {module_path}: {e}")
        return None
    
    classes = []
    functions = []
    
    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            classes.append(parse_class(node))
        elif isinstance(node, ast.FunctionDef):
            functions.append(parse_function(node))
    
    if not classes and not functions:
        return None
    
    return {
        'module': module_path.stem,
        'path': str(module_path),
        'classes': classes,
        'functions': functions
    }


def parse_class(node: ast.ClassDef) -> Dict[str, Any]:
    """Extract class info from AST node"""
    bases = []
    for base in node.bases:
        if isinstance(base, ast.Name):
            bases.append(base.id)
        elif isinstance(base, ast.Attribute):
            bases.append(f"{base.value.id}.{base.attr}")
    
    methods = []
    for item in node.body:
        if isinstance(item, ast.FunctionDef):
            methods.append(parse_function(item))
    
    docstring = ast.get_docstring(node)
    doc_summary = docstring.split('\n')[0] if docstring else None
    
    return {
        'name': node.name,
        'bases': bases,
        'docstring': doc_summary,
        'methods': methods
    }


def parse_function(node: ast.FunctionDef) -> Dict[str, Any]:
    """Extract function/method signature"""
    args = []
    for arg in node.args.args:
        arg_str = arg.arg
        if arg.annotation:
            try:
                arg_str += f": {ast.unparse(arg.annotation)}"
            except:
                pass
        args.append(arg_str)
    
    returns = None
    if node.returns:
        try:
            returns = ast.unparse(node.returns)
        except:
            pass
    
    docstring = ast.get_docstring(node)
    doc_summary = docstring.split('\n')[0] if docstring else None
    
    return {
        'name': node.name,
        'args': args,
        'returns': returns,
        'docstring': doc_summary
    }


def generate_codemap(src_dir: Path, output_path: Path):
    """Generate markdown codemap"""
    print("📚 Generating Archangel codemap...")
    print(f"   Source: {src_dir}")
    print(f"   Output: {output_path}")
    print()
    
    modules = []
    py_files = sorted(src_dir.rglob("*.py"))
    
    for py_file in py_files:
        # Skip __pycache__, tests, and private modules
        if '__pycache__' in str(py_file):
            continue
        if 'test_' in py_file.name:
            continue
        if py_file.name.startswith('_') and py_file.name != '__init__.py':
            continue
        
        print(f"   Parsing: {py_file.relative_to(src_dir.parent)}")
        module_data = parse_module(py_file)
        if module_data:
            modules.append(module_data)
    
    print()
    print(f"   Parsed {len(modules)} modules")
    print()
    
    # Generate markdown
    markdown = generate_markdown(modules)
    
    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Write output
    output_path.write_text(markdown, encoding='utf-8')
    
    print(f"✨ Codemap generated: {output_path}")
    print(f"   {len(markdown.splitlines())} lines")
    print()


def generate_markdown(modules: List[Dict]) -> str:
    """Convert parsed modules to markdown"""
    lines = [
        "# Archangel Codemap",
        "",
        "**Auto-generated from code - DO NOT EDIT MANUALLY**",
        f"**Last updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "This codemap provides a quick reference to the Archangel API.",
        "Use this when writing code that integrates with Archangel.",
        "",
        "---",
        ""
    ]
    
    # Group by module
    for module in sorted(modules, key=lambda m: m['module']):
        lines.append(f"## {module['module']}")
        lines.append("")
        lines.append(f"*File: `{module['path']}`*")
        lines.append("")
        
        # Classes
        for cls in module['classes']:
            lines.append(f"### {cls['name']}")
            
            if cls['bases']:
                lines.append(f"**Inherits:** `{', '.join(cls['bases'])}`")
                lines.append("")
            
            if cls['docstring']:
                lines.append(f"{cls['docstring']}")
                lines.append("")
            
            if cls['methods']:
                lines.append("**Methods:**")
                lines.append("")
                
                for method in cls['methods']:
                    # Format signature
                    args_str = ', '.join(method['args'])
                    ret_str = f" -> {method['returns']}" if method['returns'] else ""
                    sig = f"`{method['name']}({args_str}){ret_str}`"
                    
                    lines.append(f"- {sig}")
                    if method['docstring']:
                        lines.append(f"  - {method['docstring']}")
                
                lines.append("")
        
        # Module-level functions
        if module['functions']:
            lines.append("**Functions:**")
            lines.append("")
            
            for func in module['functions']:
                args_str = ', '.join(func['args'])
                ret_str = f" -> {func['returns']}" if func['returns'] else ""
                sig = f"`{func['name']}({args_str}){ret_str}`"
                
                lines.append(f"- {sig}")
                if func['docstring']:
                    lines.append(f"  - {func['docstring']}")
            
            lines.append("")
        
        lines.append("---")
        lines.append("")
    
    return '\n'.join(lines)


if __name__ == "__main__":
    # Paths relative to archangel root
    archangel_root = Path(__file__).parent.parent
    src_dir = archangel_root / "src"
    output_path = archangel_root.parent / ".ai" / "archangel-codemap.md"
    
    if not src_dir.exists():
        print(f"❌ Source directory not found: {src_dir}")
        print("   Make sure you're running from archangel/scripts/")
        exit(1)
    
    generate_codemap(src_dir, output_path)
    
    print("🎉 Done! Codemap ready for AI context injection!")
    print()
