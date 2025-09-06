#!/usr/bin/env python3
"""Example usage of EditGraph library."""

from tkinter import W
from foton import Image, Graph, nodes as N


def main() -> None:
    """Run the example EditGraph pipeline."""

    # Create a new graph
    g = Graph()
    # Add nodes to the pipeline
    g.add("load", N.Load(path="demo_image.jpg")).add(
        "edit", N.Edit(prompt="Make him an astronaut")
    ).add("export", N.Export(path="one.jpg"))

    # .add("upscale", N.RealESRGAN(scale=2))

    # Wire the nodes together
    g.wire("load.image -> edit.image")
    g.wire("edit.image -> export.image")

    # Print graph information
    print(f"Created graph: {g}")
    print(f"Nodes: {g.list_nodes()}")
    print(f"Wires: {len(g.wires)}")

    # Execute the pipeline (would fail without actual input.png)
    result = g.run()
    print(f"Pipeline executed successfully!")
    print(f"Execution order: {result.execution_order}")

    # Create a new graph
    g = Graph()
    # Add nodes to the pipeline
    g.add("load", N.Load(path="artem.jpg")).add(
        "refine", N.IterativeRefinement(prompt="Make him an astronaut", steps=10)
    ).add("export", N.Export(path="out.jpg"))

    # .add("upscale", N.RealESRGAN(scale=2))

    # Wire the nodes together
    g.wire("load.image -> refine.image")
    g.wire("refine.image -> export.image")

    # Print graph information
    print(f"Created graph: {g}")
    print(f"Nodes: {g.list_nodes()}")
    print(f"Wires: {len(g.wires)}")

    # Execute the pipeline (would fail without actual input.png)
    result = g.run()
    print(f"Pipeline executed successfully!")
    print(f"Execution order: {result.execution_order}")

    # Access specific node outputs
    final_output = result.get_node_output("export")
    if final_output:
        print(f"Final output saved to: {final_output['path']}")


def demo_simple_pipeline() -> None:
    """Demo a simpler pipeline that can actually run."""
    print("\n--- Simple Demo (creates a test image) ---")

    from PIL import Image as PILImage
    import numpy as np

    # Create a test image
    test_array = np.random.randint(0, 256, (200, 200, 3), dtype=np.uint8)
    test_pil = PILImage.fromarray(test_array)
    test_pil.save("demo_input.png")

    # Create a simple pipeline
    g = Graph()
    g.add("load", N.Load(path="demo_input.png")).add(
        "export", N.Export(path="demo_output.png")
    )

    g.wire("load.image -> grade.image")
    g.wire("grade.image -> export.image")

    # Run the pipeline
    try:
        result = g.run()
        print("Simple demo completed successfully!")
        print(f"Input: demo_input.png")
        print(f"Output: demo_output.png")

        # Clean up
        import os

        os.remove("demo_input.png")

    except Exception as e:
        print(f"Demo error: {e}")


if __name__ == "__main__":
    main()
    demo_simple_pipeline()
