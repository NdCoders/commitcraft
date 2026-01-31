# Commitcraft

A pre-commit hook to automatically add ticket info to commit messages based on branch name. The ticket info is added in the form of a prefix to the commit message subject and can also be added in the body of the commit message.

## Features

- **Ticket prefix**: Automatically prepends ticket number to commit subject
- **Body content**: Optionally adds Jira links to commit body (renders in PR descriptions)
- **Flexible regex**: Customize ticket pattern matching
- **Smart skipping**: Ignores fixup/squash/merge commits and existing tickets

## Installation

Add to your `.pre-commit-config.yaml`:

```yaml
default_install_hook_types:
  - pre-commit
  - prepare-commit-msg

repos:
  - repo: https://github.com/ndcoders/commitcraft
    rev: v0.1.0
    hooks:
      - id: commitcraft
        args:
          - '--regex=(?P<ticket>NDC-[0-9]+|PIL-[0-9]+)'
          - '--format={ticket} {commit_msg}'
          - '--body=Ticket: [{ticket}](https://ndcoders.atlassian.net/browse/{ticket})'
        stages: [prepare-commit-msg]
```

Then install the hooks:

```bash
pre-commit install --hook-type prepare-commit-msg
```

## Usage

### Arguments

| Argument | Default | Description |
|----------|---------|-------------|
| `--regex` | `[A-Z]+-\d+` | Regex pattern to extract ticket from branch name |
| `--format` | `{ticket} {commit_msg}` | Template for commit subject |
| `--body` | None | Template for commit body (optional) |

### Placeholders

- `{ticket}` - First matched ticket (e.g., `NDC-123`)
- `{tickets}` - All matched tickets, comma-separated (e.g., `NDC-123, NDC-456`)
- `{commit_msg}` - Original commit message (subject only)

### Example

Branch: `NDC-123_fix-auth-bug`

Commit: `fix: add authentication timeout`

Result:
```
NDC-123 fix: add authentication timeout

Ticket: [NDC-123](https://ndcoders.atlassian.net/browse/NDC-123)
```

## Development

```bash
# Clone and install
git clone https://github.com/ndcoders/commitcraft.git
cd commitcraft
uv sync --all-extras

# Run lint, type-check and tests
pre-commit run --all-files
```

## License

MIT
