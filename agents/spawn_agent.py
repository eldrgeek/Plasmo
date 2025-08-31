#!/usr/bin/env python3
"""
General purpose agent spawner script
Usage: python spawn_agent.py <agent_template> [target_project_dir] [specialization] [context]
"""

import sys
import os
from pathlib import Path
from agent_spawner import AgentSpawner

def main():
    if len(sys.argv) < 2:
        print("Usage: python spawn_agent.py <agent_template> [target_project_dir] [specialization] [context]")
        print("\nAvailable agent templates:")
        
        # List available templates
        templates_dir = Path(__file__).parent / "agent_templates"
        if templates_dir.exists():
            for template in templates_dir.glob("*.md"):
                print(f"  - {template.stem}")
        else:
            print("  No templates found in agent_templates/")
        
        sys.exit(1)
    
    agent_template = sys.argv[1]
    target_project_dir = sys.argv[2] if len(sys.argv) > 2 else ""
    specialization = sys.argv[3] if len(sys.argv) > 3 else ""
    context = sys.argv[4] if len(sys.argv) > 4 else ""
    
    # Remove .md extension if provided
    if agent_template.endswith('.md'):
        agent_template = agent_template[:-3]
    
    spawner = AgentSpawner()
    
    print(f"🚀 Spawning {agent_template} agent...")
    if target_project_dir:
        print(f"   Target Directory: {target_project_dir}")
    if specialization:
        print(f"   Specialization: {specialization}")
    if context:
        print(f"   Context: {context}")
    
    result = spawner.spawn_agent(
        role=agent_template,
        specialization=specialization,
        project_context=context,
        target_project_dir=target_project_dir
    )
    
    if result.get("success"):
        print(f"✅ {result['message']}")
        print(f"Agent ID: {result['agent_id']}")
        print("\nThe agent should now be running in a new Terminal window.")
        print("It will have full Python execution capabilities via the MCP server.")
    else:
        print(f"❌ Error: {result.get('error')}")

if __name__ == "__main__":
    main()