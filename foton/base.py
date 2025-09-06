"""Base classes for EditGraph."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass, field


@dataclass
class NodeOutput:
    """Represents the output of a node execution."""
    data: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __getitem__(self, key: str) -> Any:
        return self.data[key]
    
    def __setitem__(self, key: str, value: Any) -> None:
        self.data[key] = value
    
    def get(self, key: str, default: Any = None) -> Any:
        return self.data.get(key, default)


class Node(ABC):
    """Base class for all nodes in the EditGraph pipeline."""
    
    def __init__(self, name: Optional[str] = None, **kwargs: Any) -> None:
        self.name = name or self.__class__.__name__.lower()
        self.config = kwargs
        self.inputs: Dict[str, Any] = {}
        
    @abstractmethod
    def execute(self, **inputs: Any) -> NodeOutput:
        """Execute the node with given inputs.
        
        Args:
            **inputs: Input data for the node
            
        Returns:
            NodeOutput containing the results
        """
        pass
    
    def set_input(self, key: str, value: Any) -> None:
        """Set an input value for the node."""
        self.inputs[key] = value
    
    def get_input(self, key: str, default: Any = None) -> Any:
        """Get an input value for the node."""
        return self.inputs.get(key, default)
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name={self.name})"


class Wire:
    """Represents a connection between nodes."""
    
    def __init__(self, source: str, target: str) -> None:
        """Initialize a wire.
        
        Args:
            source: Source specification (e.g., "node1.output")
            target: Target specification (e.g., "node2.input" or just "node2")
        """
        self.source = source
        self.target = target
        
        # Parse source
        if '.' in source:
            self.source_node, self.source_output = source.split('.', 1)
        else:
            raise ValueError(f"Source must specify output: {source}")
        
        # Parse target
        if '.' in target:
            self.target_node, self.target_input = target.split('.', 1)
        else:
            # If no input specified, use the output name as input name
            self.target_node = target
            self.target_input = self.source_output
    
    def __repr__(self) -> str:
        return f"Wire({self.source} -> {self.target})"