# Contributing

## Development Setup

1. Install dependencies:

```bash
make install-dev
```

2. Apply migrations:

```bash
make migrate
```

3. Run quality checks:

```bash
make quality
```

## Pull Requests

- Keep PRs focused on one change set.
- Include migration files for schema updates.
- Ensure CI passes before requesting review.
- Update docs when behavior or APIs change.
