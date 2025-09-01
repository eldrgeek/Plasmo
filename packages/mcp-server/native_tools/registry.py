"""
Tool Registry Management
=======================

Manages the loading, parsing, and querying of tools from the tools.yaml registry.
Supports hot reload via file watching and provides AI-friendly tool discovery.
"""

import yaml
import os
import time
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)

class ToolRegistry:
    """Manages the native tool registry with hot reload capabilities."""
    
    def __init__(self, registry_path: str = "tools.yaml"):
        self.registry_path = Path(registry_path)
        self.tools: Dict[str, Dict[str, Any]] = {}
        self.last_modified = 0
        self.load_registry()
    
    def load_registry(self) -> bool:
        """Load tools from the YAML registry file."""
        try:
            if not self.registry_path.exists():
                logger.warning(f"Registry file not found: {self.registry_path}")
                return False
            
            # Check if file was modified
            current_modified = self.registry_path.stat().st_mtime
            if current_modified <= self.last_modified:
                return True  # No changes
            
            with open(self.registry_path, 'r', encoding='utf-8') as f:
                # Use safe_load for security
                data = yaml.safe_load(f)
            
            if not data or 'tools' not in data:
                logger.error("Invalid registry format: missing 'tools' section")
                return False
            
            self.tools = data['tools']
            self.last_modified = current_modified
            
            logger.info(f"Loaded {len(self.tools)} tools from registry")
            return True
            
        except yaml.YAMLError as e:
            logger.error(f"YAML parsing error: {e}")
            return False
        except Exception as e:
            logger.error(f"Failed to load registry: {e}")
            return False
    
    def get_tool(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """Get a specific tool by name."""
        self.load_registry()  # Auto-reload
        return self.tools.get(tool_name)
    
    def list_tools(self, category: str = "all", include_status: bool = False) -> List[Dict[str, Any]]:
        """List available tools, optionally filtered by category."""
        self.load_registry()  # Auto-reload
        
        result = []
        for name, tool in self.tools.items():
            if category != "all" and tool.get("category") != category:
                continue
            
            tool_info = {
                "name": name,
                "description": tool.get("description", ""),
                "category": tool.get("category", "uncategorized"),
                "keywords": tool.get("keywords", []),
                "supports_persistent": tool.get("supports_persistent", False),
                "requires_review": tool.get("requires_review", False)
            }
            
            if include_status:
                # Add runtime status information
                tool_info["status"] = self._get_tool_status(name, tool)
            
            result.append(tool_info)
        
        return result
    
    def search_by_keywords(self, keywords: List[str]) -> List[Dict[str, Any]]:
        """Search tools by keywords."""
        self.load_registry()  # Auto-reload
        
        matching_tools = []
        for name, tool in self.tools.items():
            tool_keywords = tool.get("keywords", [])
            
            # Check if any search keyword matches tool keywords
            if any(keyword.lower() in [tk.lower() for tk in tool_keywords] for keyword in keywords):
                matching_tools.append({
                    "name": name,
                    "description": tool.get("description", ""),
                    "keywords": tool_keywords,
                    "match_score": self._calculate_match_score(keywords, tool_keywords)
                })
        
        # Sort by match score
        matching_tools.sort(key=lambda x: x["match_score"], reverse=True)
        return matching_tools
    
    def search_by_use_case(self, intent: str) -> List[Dict[str, Any]]:
        """Search tools by user intent/use case."""
        self.load_registry()  # Auto-reload
        
        intent_lower = intent.lower()
        matching_tools = []
        
        for name, tool in self.tools.items():
            use_cases = tool.get("use_cases", [])
            
            # Check if intent matches any use case
            for use_case in use_cases:
                if intent_lower in use_case.lower():
                    matching_tools.append({
                        "name": name,
                        "description": tool.get("description", ""),
                        "matched_use_case": use_case,
                        "confidence": self._calculate_intent_confidence(intent_lower, use_case.lower())
                    })
                    break
        
        # Sort by confidence
        matching_tools.sort(key=lambda x: x["confidence"], reverse=True)
        return matching_tools
    
    def get_tool_categories(self) -> List[str]:
        """Get all available tool categories."""
        self.load_registry()  # Auto-reload
        
        categories = set()
        for tool in self.tools.values():
            categories.add(tool.get("category", "uncategorized"))
        
        return sorted(list(categories))
    
    def _get_tool_status(self, name: str, tool: Dict[str, Any]) -> str:
        """Get runtime status of a tool."""
        # This would be expanded to check if scripts exist, dependencies available, etc.
        script = tool.get("script")
        if script and not Path(script).exists():
            return "script_missing"
        
        return "available"
    
    def _calculate_match_score(self, search_keywords: List[str], tool_keywords: List[str]) -> float:
        """Calculate keyword match score (0.0 to 1.0)."""
        if not search_keywords or not tool_keywords:
            return 0.0
        
        matches = sum(1 for sk in search_keywords 
                     if any(sk.lower() in tk.lower() for tk in tool_keywords))
        
        return matches / len(search_keywords)
    
    def _calculate_intent_confidence(self, intent: str, use_case: str) -> float:
        """Calculate intent matching confidence (0.0 to 1.0)."""
        # Simple word overlap scoring
        intent_words = set(intent.split())
        use_case_words = set(use_case.split())
        
        if not intent_words or not use_case_words:
            return 0.0
        
        overlap = len(intent_words & use_case_words)
        return overlap / len(intent_words | use_case_words)
