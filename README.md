# astro2 

A remake of my first major Python project, nine years later.

# Setup

Requires Python3.8.

On Windows, after installing Python, you may need to make some aliases to be able to use it in Git Bash. After first opening Git Bash, run `touch ~/.bashrc`, open the created file, and paste the following into it:

```bash
alias python='winpty python'
alias python3='winpty python'
```

Install tox with pip if necessary.

```bash
pip install tox
```

Make sure to change directory to wherever you cloned the Git repo.

## Running unit tests

```bash
tox
```

## Running the game

```bash
tox -e app
```
