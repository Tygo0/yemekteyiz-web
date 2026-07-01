# Phase 2 — Concepts & Reasoning (Meeting Prep Notes)

## 1. What is a migration, and why not just create tables by hand?

A migration is a version-controlled script that describes a *change* to the database
schema (e.g. "add a `dishes` table"). Instead of manually running `CREATE TABLE`
commands, Flask-Migrate (built on Alembic) generates this script for you by comparing
your SQLAlchemy models to the current database state, then tracks every change over
time. Benefits: schema changes are code-reviewable, reversible (every migration has an
`upgrade()` and a `downgrade()`), and reproducible — anyone on the team runs
`flask db upgrade` and gets an identical schema, in dev, staging, or production.

**Why it matters here specifically:** we didn't just write the migration — we ran it
against a real database, checked the tables were created correctly, then ran the
downgrade to prove it can be undone cleanly, then round-tripped real data through
every relationship. This isn't going through the motions — a migration that can't
downgrade is broken and doesn't reveal it until months later.

## 2. Why the circular-looking `Week.winner_id` → `Contestant.id` relationship?

A `Week` has many `Contestant`s (`week_id` on the `Contestant` table), but also needs
to point to *one specific* contestant as the winner. That means `Week` needs a column
pointing at `Contestant`, and `Contestant` needs a column pointing at `Week` — a
circular dependency. If you tried to create both tables normally, the database would
complain: "table `weeks` doesn't exist yet" when creating `contestants`, and vice versa.

The fix (`use_alter=True` + `post_update=True`) tells SQLAlchemy: create both tables
first without the winner constraint, then add that specific foreign key as a separate
step afterward. It's a standard pattern for "self-referencing-adjacent" relationships,
not something unusual to this project.

## 3. Why a database-level `CHECK` constraint on `Score.value` instead of only validating in Python?

Because Python-level validation can be bypassed — a raw SQL script, a bug in a future
service function, or a different application entirely (in years 2+) could insert bad
data if the *only* thing stopping it is application code. A `CHECK (value BETWEEN 1
AND 10)` constraint makes it structurally impossible for an invalid score to exist in
the table, regardless of what wrote it. We proved this works: an attempted
`Score(value=99)` raised `IntegrityError` and was rejected before commit.

This is a "belt and suspenders" idea worth naming in a meeting: **validate at the API
layer for good error messages, but also constrain at the DB layer for guaranteed
correctness.**

## 4. Why is `Dish.category` a DB enum instead of a plain string?

Same reasoning as above — a plain string column would accept `"Soup"`, `"soup "`,
`"SOUP"`, or a typo like `"soop"` with no complaint. A native enum type restricts the
column to a fixed, known set of values at the database level.

## 5. Why does `Score.judge_name` stay a string instead of becoming a `Judge` table?

Because in this show, judges *are* the other contestants plus Zuhal — there's no
separate pool of "judge" people. Creating a `Judge` entity would mean duplicating
every contestant's data into a second table, just to represent the same people in a
different role. We chose the simpler model on purpose; it's worth being able to
explain *why* we didn't over-engineer this, not just that we didn't.

## 6. Why generate the ER diagram in Mermaid instead of a picture file?

Mermaid diagrams are plain text (`.md` file) that GitHub renders automatically in the
browser — no separate image file to keep in sync with the actual schema, and it lives
right next to the code in version control. If the schema changes, the diagram is a
text edit away from being correct again, rather than a re-export from a separate design
tool.

## 7. Likely meeting questions & short answers

- **"How do you know the migration actually works?"** → We ran it against a real
  SQLite DB: upgrade created all 7 tables correctly, downgrade cleanly reversed it,
  and we inserted real linked data through every relationship to confirm it round-trips.
- **"What stops someone from putting `score: 15` in the database?"** → A DB-level
  CHECK constraint — proven by testing that it throws `IntegrityError`.
- **"Why is there a winner_id on Week pointing back to Contestant — isn't that circular?"**
  → Yes, intentionally: a week has many contestants, but also references one of them
  as winner. Resolved via `use_alter`/`post_update` so both tables can be created.
- **"Why no Judge table?"** → Judges are just contestants + Zuhal in this show;
  a separate table would duplicate contestant data for no benefit.
