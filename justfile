# === Settings ===
# Use bash (or pwsh on Windows)
# set shell := ["bash", "-c"]
cd set shell := ["pwsh", "-c"]
# set shell := ["fish", "-c"]

# === Default Task ===
# List available tasks
default:
    @just --list

# === Main Tasks ===

# Lint all template files (Jinja, YAML) and Python test code
lint: lint-jinja lint-yaml lint-py

# Format all files
format: format-jinja format-py

# Run the template's pytest suite
test:
    @echo "Running template generation tests..."
    @pdm run pytest tests/

# Do a quick test-generation into a temp folder
generate:
    @echo "Generating test project in ./temp-test-build..."
    @pdm run copier copy . ./temp-test-build --force --vcs-ref=HEAD

# Remove temporary build files
clean:
    @echo "Removing ./temp-test-build..."
    @rm -rf ./temp-test-build

# === Sub-Tasks ===
lint-jinja:
    @echo "Checking Jinja templates..."
    @pdm run djlint --check .

lint-yaml:
    @echo "Checking YAML files..."
    @pdm run yamllint .

lint-py:
    @echo "Checking Python test code..."
    @pdm run ruff check tests/

format-jinja:
    @echo "Formatting Jinja templates..."
    @pdm run djlint --reformat .

format-py:
    @echo "Formatting Python test code..."
    @pdm run ruff format tests/