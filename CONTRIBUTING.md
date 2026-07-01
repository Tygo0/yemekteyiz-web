# Contributing / Branch Strategy

## Branches

- `main` — stable, always deployable.
- `develop` — integration branch; feature branches merge here first.
- `feature/backend`
- `feature/frontend`
- `feature/database`
- `feature/auth`
- `feature/automation`
- `feature/ocr`
- `feature/vision`
- `feature/statistics`

## Workflow

1. Branch off `develop`: `git checkout -b feature/xxx develop`
2. Commit small, focused changes with clear messages.
3. Open a PR into `develop`. `main` only receives merges from `develop` at release points.
4. Never commit directly to `main`.

## Commit message convention

```
<type>: <short summary>

feat:     new feature
fix:      bug fix
docs:     documentation only
refactor: no behavior change
test:     adding/adjusting tests
chore:    tooling, deps, config
```

Example: `feat: add JWT login endpoint`
