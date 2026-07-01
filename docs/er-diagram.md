# Entity-Relationship Diagram

This reflects the actual SQLAlchemy models in `backend/app/models/`, verified via a
real Alembic migration (`migrations/versions/..._initial_schema...py`).

```mermaid
erDiagram
    SEASON ||--o{ WEEK : "has"
    WEEK ||--o{ CONTESTANT : "has"
    WEEK }o--|| CONTESTANT : "winner (nullable)"
    CONTESTANT ||--o{ EPISODE : "has"
    EPISODE ||--o{ DISH : "has"
    EPISODE ||--o{ SCORE : "has"
    CONTESTANT ||--o{ SCORE : "receives"

    SEASON {
        int id PK
        string name
        int year
    }

    WEEK {
        int id PK
        int season_id FK
        int week_number
        date air_date
        string youtube_url
        int winner_id FK "nullable, -> contestants.id"
        text notes
    }

    CONTESTANT {
        int id PK
        int week_id FK
        string name
        int age
        string profession
        string city
        text biography
        string photo_url
    }

    EPISODE {
        int id PK
        int contestant_id FK
        date broadcast_date
        string video_url
    }

    DISH {
        int id PK
        int episode_id FK
        string name
        enum category "soup/appetizer/main_course/dessert/beverage"
    }

    SCORE {
        int id PK
        int episode_id FK
        int contestant_id FK "who is being scored"
        string judge_name "who gave the score"
        int value "CHECK 1-10"
    }

    ADMIN {
        int id PK
        string username
        string password_hash
    }
```

## Notes on modeling decisions

- **`Week.winner_id`** is a nullable self-referencing-style FK to `Contestant`
  (a contestant belongs to a week, but a week also points back to one contestant as
  the winner). This creates a circular dependency between the two tables, resolved
  with SQLAlchemy's `use_alter` + `post_update` so Alembic can create both tables
  without a chicken-and-egg problem.
- **`Score.judge_name`** is a plain string, not a FK to a `Judge` table. In this show
  the judges *are* the other contestants plus Zuhal — a separate `Judge` entity would
  just duplicate `Contestant` for no real benefit at this stage.
- **`Dish.category`** is a native DB enum (`DishCategory`), so invalid categories are
  rejected at the database level, not just in application code.
- **`Score.value`** has a `CHECK (value >= 1 AND value <= 10)` constraint — verified
  directly: an out-of-range score raises `IntegrityError` and is rejected before it
  can be committed.
- **`Admin`** wasn't in the original blueprint's entity list but is required for JWT
  login (Phase 3) — stores only a bcrypt/werkzeug password hash, never plaintext.
