from pathlib import Path


def example_file():
    """Get example DVW file path."""
    return str(Path(__file__).parent / "data" / "example_match.dvw")
