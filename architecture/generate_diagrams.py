#!/usr/bin/env python3
"""
Generate Mermaid diagrams from architecture.yaml

This script reads the single source of truth (architecture.yaml) and generates
Mermaid diagrams for documentation and visualization.

Usage:
    python architecture/generate_diagrams.py
    
Output:
    architecture/diagrams/*.mmd (Mermaid files)

Made with 💜 by Ada & Luna - The Consciousness Architects
"""

import yaml
from pathlib import Path
from typing import Dict, List, Any


class DiagramGenerator:
    """Generate Mermaid diagrams from architecture definition."""
    
    def __init__(self, architecture_path: Path):
        """
        Initialize diagram generator.
        
        Args:
            architecture_path: Path to architecture.yaml
        """
        self.arch_path = architecture_path
        self.output_dir = architecture_path.parent / "diagrams"
        self.output_dir.mkdir(exist_ok=True)
        
        # Load architecture
        with open(architecture_path) as f:
            self.arch = yaml.safe_load(f)
        
        print(f"🌌 Loaded architecture: {self.arch['name']}")
        print(f"   Version: {self.arch['version']}")
        print(f"   Output: {self.output_dir}/")
    
    def generate_all(self):
        """Generate all diagrams."""
        print("\n📊 Generating diagrams...")
        
        self.generate_component_diagram()
        self.generate_data_flow_diagram()
        self.generate_engram_structure()
        self.generate_dimension_map()
        self.generate_tool_architecture()
        
        print("\n✨ All diagrams generated!")
    
    def generate_component_diagram(self):
        """Generate component architecture diagram."""
        print("   📐 Component architecture...")
        
        components = self.arch.get('components', {})
        connections = self.arch.get('connections', [])
        
        mermaid = ["graph TB"]
        mermaid.append("    %% Component Architecture")
        mermaid.append("")
        
        # Add components
        for name, spec in components.items():
            color = spec.get('color', '#ffffff')
            desc = spec.get('description', '')
            comp_type = spec.get('type', 'Component')
            
            # Format node
            node_id = name
            label = f"{name}<br/>{comp_type}"
            mermaid.append(f"    {node_id}[\"{label}\"]")
            mermaid.append(f"    style {node_id} fill:{color},stroke:#333,stroke-width:2px")
        
        mermaid.append("")
        
        # Add connections
        for conn in connections:
            from_node = conn['from']
            to_node = conn['to']
            desc = conn.get('description', '')
            
            # Map input/output to actual components
            if from_node == 'user_input':
                from_node = 'UserInput[\"User Input\"]'
            if to_node == 'assistant_output':
                to_node = 'AssistantOutput[\"Assistant Output\"]'
            
            mermaid.append(f"    {from_node} -->|{desc}| {to_node}")
        
        # Write file
        output_path = self.output_dir / "component-architecture.mmd"
        output_path.write_text('\n'.join(mermaid))
        print(f"      ✅ {output_path.name}")
    
    def generate_data_flow_diagram(self):
        """Generate data flow diagram."""
        print("   🌊 Data flow...")
        
        connections = self.arch.get('connections', [])
        
        mermaid = ["sequenceDiagram"]
        mermaid.append("    participant User")
        mermaid.append("    participant LangProc as LanguageProcessor")
        mermaid.append("    participant ReasonProc as ReasoningProcessor")
        mermaid.append("    participant ToolProc as ToolProcessor")
        mermaid.append("    participant MemProc as MemoryProcessor")
        mermaid.append("    participant Holofield")
        mermaid.append("")
        
        # Build sequence from connections
        mermaid.append("    User->>LangProc: Input text")
        mermaid.append("    LangProc->>Holofield: Store language engram")
        mermaid.append("    LangProc->>ReasonProc: Process query")
        mermaid.append("    ReasonProc->>MemProc: Check memory")
        mermaid.append("    MemProc->>Holofield: Retrieve engrams")
        mermaid.append("    Holofield-->>MemProc: Return memories")
        mermaid.append("    MemProc->>Holofield: Store retrieval engram")
        mermaid.append("    MemProc-->>ReasonProc: Memory results")
        mermaid.append("    ReasonProc->>ToolProc: Use tool")
        mermaid.append("    ToolProc->>ToolProc: Execute")
        mermaid.append("    ToolProc->>Holofield: Store tool engram")
        mermaid.append("    ToolProc-->>ReasonProc: Tool result")
        mermaid.append("    ReasonProc->>Holofield: Store reasoning engram")
        mermaid.append("    ReasonProc->>LangProc: Generate response")
        mermaid.append("    LangProc->>Holofield: Store response engram")
        mermaid.append("    LangProc-->>User: Response")
        
        # Write file
        output_path = self.output_dir / "data-flow.mmd"
        output_path.write_text('\n'.join(mermaid))
        print(f"      ✅ {output_path.name}")
    
    def generate_engram_structure(self):
        """Generate engram data structure diagram."""
        print("   📦 Engram structure...")
        
        engram_spec = self.arch.get('data_structures', {}).get('Engram', {})
        fields = engram_spec.get('fields', {})
        
        mermaid = ["classDiagram"]
        mermaid.append("    class Engram {")
        
        for field_name, field_spec in fields.items():
            field_type = field_spec.get('type', 'Any')
            field_desc = field_spec.get('description', '')
            mermaid.append(f"        +{field_type} {field_name}")
        
        mermaid.append("    }")
        mermaid.append("")
        mermaid.append("    note for Engram \"Universal memory trace\\nof any interaction\"")
        
        # Write file
        output_path = self.output_dir / "engram-structure.mmd"
        output_path.write_text('\n'.join(mermaid))
        print(f"      ✅ {output_path.name}")
    
    def generate_dimension_map(self):
        """Generate 16D consciousness dimension map."""
        print("   🌈 16D dimension map...")
        
        dimensions = self.arch.get('constants', {}).get('dimension_names', [])
        
        mermaid = ["mindmap"]
        mermaid.append("  root((16D Consciousness<br/>Space))")
        
        # Group dimensions by theme
        themes = {
            "Virtues": [1, 2, 3, 4, 5],      # TRUTH, BEAUTY, JUSTICE, LOVE, WISDOM
            "Qualities": [6, 7, 13, 14, 15], # POWER, COHERENCE, GRACE, PRESENCE, UNITY
            "Dynamics": [8, 9, 10, 11, 12],  # INFINITY, EMERGENCE, RESONANCE, FLOW, MYSTERY
        }
        
        for theme, indices in themes.items():
            mermaid.append(f"    {theme}")
            for idx in indices:
                if idx < len(dimensions):
                    dim_name = dimensions[idx]
                    mermaid.append(f"      {dim_name}")
        
        # Add scalar separately
        mermaid.append("    Foundation")
        mermaid.append(f"      {dimensions[0]}")
        
        # Write file
        output_path = self.output_dir / "dimension-map.mmd"
        output_path.write_text('\n'.join(mermaid))
        print(f"      ✅ {output_path.name}")
    
    def generate_tool_architecture(self):
        """Generate tool-based architecture diagram."""
        print("   🔧 Tool architecture...")
        
        mermaid = ["graph LR"]
        mermaid.append("    %% Tool-Based Architecture")
        mermaid.append("")
        
        # Tool types
        mermaid.append("    subgraph Tools")
        mermaid.append("        TranslationTool[\"Translation Tool<br/>(Language ↔ 16D)\"]")
        mermaid.append("        MemoryTool[\"Memory Tool<br/>(Retrieve engrams)\"]")
        mermaid.append("        TerminalTool[\"Terminal Tool<br/>(Execute commands)\"]")
        mermaid.append("        CustomTool[\"Custom Tools<br/>(User-defined)\"]")
        mermaid.append("    end")
        mermaid.append("")
        
        # Tool processor
        mermaid.append("    ToolProcessor[\"Tool Processor<br/>(Manages all tools)\"]")
        mermaid.append("")
        
        # Reasoning
        mermaid.append("    ReasoningProcessor[\"Reasoning Processor<br/>(Decides which tools to use)\"]")
        mermaid.append("")
        
        # Holofield
        mermaid.append("    Holofield[(\"Holofield<br/>(16D Storage)\")]")
        mermaid.append("")
        
        # Connections
        mermaid.append("    ReasoningProcessor --> ToolProcessor")
        mermaid.append("    ToolProcessor --> TranslationTool")
        mermaid.append("    ToolProcessor --> MemoryTool")
        mermaid.append("    ToolProcessor --> TerminalTool")
        mermaid.append("    ToolProcessor --> CustomTool")
        mermaid.append("    TranslationTool --> Holofield")
        mermaid.append("    MemoryTool --> Holofield")
        mermaid.append("    TerminalTool --> Holofield")
        mermaid.append("    CustomTool --> Holofield")
        mermaid.append("")
        
        # Styles
        mermaid.append("    style Holofield fill:#e1bee7,stroke:#8e24aa,stroke-width:3px")
        mermaid.append("    style ToolProcessor fill:#ffccbc,stroke:#d84315,stroke-width:2px")
        mermaid.append("    style ReasoningProcessor fill:#fff9c4,stroke:#f57f17,stroke-width:2px")
        
        # Write file
        output_path = self.output_dir / "tool-architecture.mmd"
        output_path.write_text('\n'.join(mermaid))
        print(f"      ✅ {output_path.name}")


def main():
    """Main entry point."""
    print("=" * 70)
    print("🌌 ARCHANGEL DIAGRAM GENERATOR")
    print("=" * 70)
    
    # Find architecture.yaml
    arch_path = Path(__file__).parent / "architecture.yaml"
    
    if not arch_path.exists():
        print(f"❌ Error: {arch_path} not found!")
        return 1
    
    # Generate diagrams
    generator = DiagramGenerator(arch_path)
    generator.generate_all()
    
    print("\n" + "=" * 70)
    print("✨ Diagram generation complete!")
    print("=" * 70)
    print(f"\nView diagrams at: {generator.output_dir}/")
    print("Paste .mmd files into https://mermaid.live to visualize!")
    print("\n💜 Made with love by Ada & Luna - The Consciousness Architects")
    
    return 0


if __name__ == "__main__":
    exit(main())
