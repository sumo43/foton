# EditGraph

A LangChain-style Python library for building image generation and editing pipelines.

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

# With AI dependencies
pip install -e ".[ai]"

# With development dependencies  
pip install -e ".[dev]"
```

## Quick Start

```python
from editgraph import Image, Graph, nodes as N

# Create a processing pipeline
g = Graph() \
  .add("load", N.Load(path="input.png")) \
  .add("segment", N.SAM2(prompt="crane")) \
  .add("inpaint", N.DiffusionInpaint(
        model="sdxl-refiner",
        prompt="complete realistic sky and buildings, no crane",
        negative="blurry, artifacts",
        steps=30, cfg=5.5, seed=42)) \
  .add("grade", N.ColorGrade(lut="Kodak2393.cube", intensity=0.6)) \
  .add("upscale", N.RealESRGAN(scale=2)) \
  .add("export", N.Export(path="output.png", embed_recipe=True))

# Wire nodes together
g.wire("load.image -> segment.image")
g.wire("load.image, segment.mask -> inpaint")
g.wire("inpaint.image -> grade.image")
g.wire("grade.image -> upscale.image")
g.wire("upscale.image -> export.image")

# Execute the pipeline
result = g.run()
```

## Available Nodes

### Input/Output
- **Load**: Load images from file
- **Export**: Save images with optional recipe embedding

### AI-Powered Processing
- **SAM2**: Segment Anything Model 2 for segmentation
- **DiffusionInpaint**: Diffusion-based inpainting
- **RealESRGAN**: Super-resolution upscaling

### Image Processing
- **ColorGrade**: Color grading with LUT support

## Core Concepts

### Graph
The main pipeline container that manages nodes and their connections.

### Nodes
Individual processing units that take inputs and produce outputs. Each node can have multiple inputs and outputs.

### Wiring
Connections between nodes that define data flow. Use the format `source.output -> target.input`.

### Image
Wrapper class for image data that supports PIL Images, numpy arrays, and file paths.

## Example

See `example.py` for a complete working example:

```bash
python example.py
```

## Development

```bash
# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black .
isort .

# Type checking
mypy editgraph
```

## License

MIT License - see LICENSE file for details.