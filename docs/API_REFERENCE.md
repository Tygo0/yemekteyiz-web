# REST API Reference (Phase 3)

Base URL: `http://localhost:5000/api`

All `POST` / `PUT` / `DELETE` endpoints (except `/auth/login`) require:
```
Authorization: Bearer <jwt-access-token>
```

## Auth

| Method | Path | Auth | Notes |
|--------|------|------|-------|
| POST | `/auth/login` | none | `{ "username": "...", "password": "..." }` → `{ access_token, admin }` |
| POST | `/auth/logout` | required | Stateless JWT — client just discards the token |
| GET  | `/auth/me` | required | Returns the current admin |

## Seasons

| Method | Path | Auth |
|--------|------|------|
| GET | `/seasons` | none |
| GET | `/seasons/{id}` | none |
| POST | `/seasons` | required |

## Weeks

| Method | Path | Auth | Notes |
|--------|------|------|-------|
| GET | `/weeks` | none | |
| GET | `/weeks/{id}` | none | |
| POST | `/weeks` | required | 409 if `week_number` already used in that `season_id` |
| PUT | `/weeks/{id}` | required | Setting `winner_id` validates that contestant belongs to this week |
| DELETE | `/weeks/{id}` | required | Cascades: deletes the week's contestants (and their episodes/dishes/scores) |

## Contestants

| Method | Path | Auth | Notes |
|--------|------|------|-------|
| GET | `/contestants?week_id=` | none | `week_id` filter optional |
| GET | `/contestants/{id}` | none | |
| POST | `/contestants` | required | |
| PUT | `/contestants/{id}` | required | |
| DELETE | `/contestants/{id}` | required | |

## Episodes

| Method | Path | Auth | Notes |
|--------|------|------|-------|
| GET | `/episodes?contestant_id=` | none | |
| GET | `/episodes/{id}` | none | |
| POST | `/episodes` | required | |

## Dishes

| Method | Path | Auth | Notes |
|--------|------|------|-------|
| GET | `/dishes?episode_id=` | none | |
| GET | `/dishes/{id}` | none | |
| POST | `/dishes` | required | `category` must be one of: soup, appetizer, main_course, dessert, beverage |
| PUT | `/dishes/{id}` | required | |
| DELETE | `/dishes/{id}` | required | |

## Scores

| Method | Path | Auth | Notes |
|--------|------|------|-------|
| GET | `/scores?episode_id=&contestant_id=` | none | |
| GET | `/scores/{id}` | none | |
| POST | `/scores` | required | `value` must be 1-10; `contestant_id` must match the episode's actual contestant |

## Statistics

| Method | Path | Auth |
|--------|------|------|
| GET | `/statistics` | none |

Returns:
```json
{
  "weekly_winners": [{ "week_id": 1, "week_number": 15, "winner_id": 3, "winner_name": "Ayşe" }],
  "average_score": 7.75,
  "highest_score_ever": { "score_id": 1, "value": 10, "contestant_id": 3, "contestant_name": "Ayşe", "judge_name": "Zuhal" },
  "most_common_dish": { "dish_name": "Mercimek Çorbası", "count": 2 },
  "most_successful_contestant": { "contestant_id": 3, "contestant_name": "Ayşe", "average_score": 9.0 },
  "average_weekly_score": [{ "week_id": 1, "week_number": 15, "average_score": 7.75 }],
  "score_distribution": { "1": 0, "2": 0, "...": "...", "10": 1 }
}
```

## Automation (stubbed — real pipeline is Phase 6)

| Method | Path | Auth | Current behavior |
|--------|------|------|-------------------|
| POST | `/automation/import` | required | Returns `501` placeholder |
| GET | `/automation/status` | none | Returns `{ status: "idle" }` |
| GET | `/automation/logs` | none | Returns `{ logs: [] }` |

## Error shape

All errors return JSON:
```json
{ "error": "Human-readable message" }
```
Validation errors additionally include field-level detail:
```json
{ "error": "Validation failed", "details": { "value": ["Must be greater than or equal to 1..."] } }
```
