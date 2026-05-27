# Show available project commands.
default:
    @just --list

# Install local git hooks.
install-hooks:
    @pre-commit install

# Run checks for tracked files.
check:
    @pre-commit run --all-files

# Run checks for tracked and untracked files before the initial commit.
check-worktree:
    @git ls-files --cached --others --exclude-standard | xargs pre-commit run --files

# Show the current git worktree state.
status:
    @git status --short
