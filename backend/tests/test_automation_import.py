def _create_season(client, auth_headers, year=2026):
    resp = client.post("/api/seasons", json={"name": "Season 1", "year": year}, headers=auth_headers)
    assert resp.status_code == 201
    return resp.get_json()["id"]


def _create_week(client, auth_headers, season_id, week_number=15):
    resp = client.post(
        "/api/weeks", json={"season_id": season_id, "week_number": week_number}, headers=auth_headers
    )
    assert resp.status_code == 201
    return resp.get_json()["id"]


def _contestant_payload(name):
    return {
        "name": name,
        "age": 30,
        "profession": "Chef",
        "city": "Istanbul",
        "biography": "Bio",
        "photo_url": "https://example.com/p.jpg",
        "broadcast_date": "2026-01-05",
        "video_url": "https://youtube.com/watch?v=abc",
        "dishes": [{"name": "Mercimek Çorbası", "category": "soup"}],
        "scores": [{"judge_name": "Zuhal", "value": 8}],
    }


def test_import_full_week_creates_everything(client, auth_headers):
    season_id = _create_season(client, auth_headers)
    week_id = _create_week(client, auth_headers, season_id)

    payload = {
        "week_id": week_id,
        "contestants": [
            _contestant_payload("Ayşe"),
            _contestant_payload("Mehmet"),
            _contestant_payload("Fatma"),
            _contestant_payload("Ali"),
        ],
    }
    resp = client.post("/api/automation/import", json=payload, headers=auth_headers)
    assert resp.status_code == 201
    body = resp.get_json()
    assert body["status"] == "imported"
    assert len(body["contestants"]) == 4
    entry = body["contestants"][0]
    assert entry["contestant"]["name"] == "Ayşe"
    assert len(entry["dishes"]) == 1
    assert len(entry["scores"]) == 1

    assert len(client.get(f"/api/contestants?week_id={week_id}").get_json()) == 4


def test_import_requires_auth(client, auth_headers):
    season_id = _create_season(client, auth_headers)
    week_id = _create_week(client, auth_headers, season_id)
    payload = {"week_id": week_id, "contestants": [_contestant_payload(n) for n in "ABCD"]}
    resp = client.post("/api/automation/import", json=payload)
    assert resp.status_code == 401


def test_import_rejects_nonexistent_week(client, auth_headers):
    payload = {"week_id": 999, "contestants": [_contestant_payload(n) for n in "ABCD"]}
    resp = client.post("/api/automation/import", json=payload, headers=auth_headers)
    assert resp.status_code == 404


def test_import_rejects_wrong_contestant_count(client, auth_headers):
    season_id = _create_season(client, auth_headers)
    week_id = _create_week(client, auth_headers, season_id)
    payload = {"week_id": week_id, "contestants": [_contestant_payload(n) for n in "ABC"]}
    resp = client.post("/api/automation/import", json=payload, headers=auth_headers)
    assert resp.status_code == 400


def test_import_rejects_duplicate_names_in_payload(client, auth_headers):
    season_id = _create_season(client, auth_headers)
    week_id = _create_week(client, auth_headers, season_id)
    payload = {
        "week_id": week_id,
        "contestants": [_contestant_payload("Ayşe")] * 4,
    }
    resp = client.post("/api/automation/import", json=payload, headers=auth_headers)
    assert resp.status_code == 409


def test_import_rejects_contestant_already_in_week(client, auth_headers):
    season_id = _create_season(client, auth_headers)
    week_id = _create_week(client, auth_headers, season_id)
    resp = client.post(
        "/api/contestants",
        json={"week_id": week_id, "name": "Ayşe"},
        headers=auth_headers,
    )
    assert resp.status_code == 201

    payload = {
        "week_id": week_id,
        "contestants": [
            _contestant_payload("Ayşe"),
            _contestant_payload("Mehmet"),
            _contestant_payload("Fatma"),
            _contestant_payload("Ali"),
        ],
    }
    resp = client.post("/api/automation/import", json=payload, headers=auth_headers)
    assert resp.status_code == 409


def test_import_rejects_score_out_of_range(client, auth_headers):
    season_id = _create_season(client, auth_headers)
    week_id = _create_week(client, auth_headers, season_id)
    contestants = [_contestant_payload(n) for n in ["Ayşe", "Mehmet", "Fatma", "Ali"]]
    contestants[0]["scores"] = [{"judge_name": "Zuhal", "value": 99}]
    payload = {"week_id": week_id, "contestants": contestants}
    resp = client.post("/api/automation/import", json=payload, headers=auth_headers)
    assert resp.status_code == 400
