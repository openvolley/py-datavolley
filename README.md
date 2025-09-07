# py-datavolley

A Python package for parsing and analyzing volleyball scouting data from DataVolley files (\*.dvw).

Currently rebuilding [pydatavolley](https://github.com/openvolley/pydatavolley) with modern Python tooling ([Astral ecosystem](https://docs.astral.sh/)) for improved experience: UV for package management, Ruff for linting/formatting and [Ty](https://github.com/astral-sh/ty) for type checking.

#

If you want to clone, here's how to set up the development environment using UV:

[UV documentation](https://docs.astral.sh/uv/getting-started/installation/)

# Setup Development Environment

```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh
```

1. Clone the repository:

   ```bash
   git clone https://github.com/your-username/py-datavolley.git
   cd py-datavolley
   ```

2. Create and activate virtual environment:

   ```bash
   # UV automatically creates and manages virtual environments
   uv sync
   ```

3. Install development dependencies:
   ```bash
   # Development dependencies are defined in pyproject.toml
   uv sync --group dev
   ```
