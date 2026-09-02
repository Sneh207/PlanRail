---
trigger: always_on
---

# PlanRail Safety Rules

## Never Automatically

Do not:

* delete files
* delete directories
* force push Git
* reset Git history
* overwrite unrelated work
* modify files outside the PlanRail workspace
* expose secrets
* commit `.env`
* commit passwords
* commit API keys
* drop database tables
* delete production data

## Before Destructive Operations

Always explain:

1. What will be changed.
2. Why it is necessary.
3. What could be lost.

Wait for explicit user approval.

## Git

Never run:

git push --force

git reset --hard

unless the user explicitly requests it.

Do not modify another developer's branch.

## Database

Never execute destructive SQL such as:

DROP DATABASE
DROP TABLE
TRUNCATE

without explicit confirmation.

## Dependencies

Before installing a new dependency:

1. Explain why it is needed.
2. Check whether an existing dependency can solve the problem.
3. Ask for approval if the dependency significantly changes the architecture.
