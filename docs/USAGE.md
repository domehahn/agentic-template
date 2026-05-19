# Usage

## Initialize

```bash
agentic-template init --target .
```

## Preview

```bash
agentic-template bake default --target . --dry-run
```

## Apply

```bash
agentic-template bake default --target . --write
```

## Validate

```bash
agentic-template validate --target .
```

## List targets

```bash
agentic-template list-targets --target .
```

## Force overwrite

Only use this when you intentionally want to overwrite unmanaged or locally modified files:

```bash
agentic-template bake default --target . --write --force
```
