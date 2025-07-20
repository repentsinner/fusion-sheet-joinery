"""
Invoke tasks for Fusion Sheet Joinery development
"""

from invoke import task


@task
def lint(c):
    """Run ruff linter on the codebase"""
    c.run("ruff check src/")


@task
def format(c):
    """Format code with ruff"""
    c.run("ruff format src/")


@task
def lint_fix(c):
    """Run ruff linter with auto-fix"""
    c.run("ruff check --fix src/")


@task
def typecheck(c):
    """Run pyright type checker"""
    c.run("pyright src/")


@task
def check(c):
    """Run all code quality checks"""
    print("Running ruff linter...")
    c.run("ruff check src/")
    print("\nRunning ruff formatter check...")
    c.run("ruff format --check src/")
    print("\nRunning pyright type checker...")
    c.run("pyright src/")
    print("\nAll checks passed!")