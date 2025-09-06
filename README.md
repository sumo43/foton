# Foton

A LangChain-style Python library for building image generation and editing pipelines.


Supports test time scaling using iterative refinement 
Only supports nano banana

## Features

- **Graph-based Pipeline**: Build complex image processing workflows using a graph structure
- **Node System**: Modular nodes for different image operations
- **Method Chaining**: Fluent API for building pipelines
- **Extensible**: Easy to add custom nodes and operations
- **AI Integration**: Built-in support for AI models like SAM2, diffusion models, and super-resolution

## Installation

```bash
# Basic installation
pip install -e .
```

## Quick Start

```python
from foton import Image, Graph, nodes as N

# Create a processing pipeline
g = Graph() \
  .add("load", N.Load(path="input.png")) \
  .add("edit", N.Edit(prompt="make him an astronaut")) \
  .add("refine", N.IterativeRefinement(
        "make the image more realistic",
        steps=30)) 
  .add("export", N.Export(path="output.png", embed_recipe=True))

# Wire nodes together
g.wire("load.image -> edit.image")
g.wire("edit.image -> refine.image")
g.wire("refine.image -> export.image")

# Execute the pipeline
result = g.run()
```

## Available Nodes

### Input/Output
- **Load**: Load images from file
- **Export**: Save images with optional recipe embedding

### AI-Powered Processing
- **Edit**: Edit stuff with nano banana

