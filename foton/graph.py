"""Core Graph implementation for EditGraph."""

from typing import Any, Dict, List, Optional, Union
from collections import defaultdict, deque

from .base import Node, Wire, NodeOutput


class ExecutionResult:
    """Result of graph execution."""

    def __init__(
        self, outputs: Dict[str, NodeOutput], execution_order: List[str]
    ) -> None:
        self.outputs = outputs
        self.execution_order = execution_order

    def get_node_output(self, node_name: str) -> Optional[NodeOutput]:
        """Get output from a specific node."""
        return self.outputs.get(node_name)

    def __getitem__(self, key: str) -> NodeOutput:
        return self.outputs[key]


class Graph:
    """Main graph class for building and executing image processing pipelines."""

    def __init__(self) -> None:
        self.nodes: Dict[str, Node] = {}
        self.wires: List[Wire] = []
        self._execution_cache: Optional[ExecutionResult] = None

    def add(self, name: str, node: Node) -> "Graph":
        """Add a node to the graph.

        Args:
            name: Unique name for the node
            node: Node instance to add

        Returns:
            Self for method chaining
        """
        if name in self.nodes:
            raise ValueError(f"Node with name '{name}' already exists")

        node.name = name
        self.nodes[name] = node
        self._execution_cache = None
        return self

    def wire(self, connection: str) -> "Graph":
        """Add a wire connection between nodes.

        Args:
            connection: Connection string like "source.output -> target.input"

        Returns:
            Self for method chaining
        """
        if "->" not in connection:
            raise ValueError(f"Invalid connection format: {connection}")

        source, target = connection.split("->", 1)
        source = source.strip()
        target = target.strip()

        # Handle multiple inputs (comma-separated)
        if "," in source:
            sources = [s.strip() for s in source.split(",")]
            for src in sources:
                wire = Wire(src, target)
                self.wires.append(wire)
        else:
            wire = Wire(source, target)
            self.wires.append(wire)

        self._execution_cache = None
        return self

    def _build_dependency_graph(self) -> Dict[str, List[str]]:
        """Build dependency graph for topological sorting."""
        dependencies = defaultdict(list)

        # All nodes start with no dependencies
        for node_name in self.nodes:
            dependencies[node_name] = []

        # Add dependencies based on wires
        for wire in self.wires:
            if wire.target_node not in dependencies:
                dependencies[wire.target_node] = []
            if wire.source_node not in dependencies[wire.target_node]:
                dependencies[wire.target_node].append(wire.source_node)

        return dependencies

    def _topological_sort(self) -> List[str]:
        """Perform topological sort to determine execution order."""
        dependencies = self._build_dependency_graph()

        # Count incoming edges
        in_degree = {node: len(deps) for node, deps in dependencies.items()}

        # Find nodes with no dependencies
        queue = deque([node for node, degree in in_degree.items() if degree == 0])
        result = []

        while queue:
            node = queue.popleft()
            result.append(node)

            # Remove this node from other nodes' dependencies
            for target_node, deps in dependencies.items():
                if node in deps:
                    in_degree[target_node] -= 1
                    if in_degree[target_node] == 0:
                        queue.append(target_node)

        if len(result) != len(self.nodes):
            raise ValueError("Circular dependency detected in graph")

        return result

    def _propagate_data(self, execution_outputs: Dict[str, NodeOutput]) -> None:
        """Propagate data through wires to set node inputs."""
        print(self.wires)
        for wire in self.wires:
            # Get source output
            try:
                source_output = execution_outputs[wire.source_node]
                output_value = source_output.get(wire.source_output)

                if output_value is None:
                    raise ValueError(
                        f"Source node '{wire.source_node}' has no output '{wire.source_output}'"
                    )

                # Set target input
                target_node = self.nodes[wire.target_node]
                target_node.set_input(wire.target_input, output_value)
            except Exception as e:
                pass

    def run(self) -> ExecutionResult:
        """Execute the graph and return results.

        Returns:
            ExecutionResult containing outputs from all nodes
        """
        if not self.nodes:
            raise ValueError("Cannot run empty graph")

        # Get execution order
        execution_order = self._topological_sort()

        # Execute nodes in order
        execution_outputs: Dict[str, NodeOutput] = {}

        for node_name in execution_order:
            node = self.nodes[node_name]

            # Propagate data from previous executions
            if execution_outputs:
                self._propagate_data(execution_outputs)

            # Execute node
            try:
                output = node.execute(**node.inputs)
                execution_outputs[node_name] = output
            except Exception as e:
                raise RuntimeError(
                    f"Error executing node '{node_name}': {str(e)}"
                ) from e

        result = ExecutionResult(execution_outputs, execution_order)
        self._execution_cache = result
        return result

    def get_node(self, name: str) -> Optional[Node]:
        """Get a node by name."""
        return self.nodes.get(name)

    def list_nodes(self) -> List[str]:
        """List all node names."""
        return list(self.nodes.keys())

    def __repr__(self) -> str:
        return f"Graph(nodes={len(self.nodes)}, wires={len(self.wires)})"
