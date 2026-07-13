# Challenge 33 — Study Checklist

To solve this challenge, you should understand:
- Layered/clean/hexagonal architecture and the inward-dependency rule
- The Dependency Inversion Principle (ports and adapters)
- Why interfaces live with their consumers, implementations with details
- The `ast` module: `parse`, `walk`, `Import`, `ImportFrom` nodes
- Why static analysis beats importing or regex for this job
- `pathlib.Path.rglob` for walking a package
- CI enforcement (exit codes); the `import-linter` tool
