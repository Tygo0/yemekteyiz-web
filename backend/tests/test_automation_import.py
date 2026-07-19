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
    assert entry["dishes"][0]["category"] == "soup"
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


def test_import_accepts_non_four_contestant_count(client, auth_headers):
    # Real weeks don't always have exactly 4 contestants (e.g. week 215 has
    # 5) -- an unusual count on its own isn't a rejection reason.
    season_id = _create_season(client, auth_headers)
    week_id = _create_week(client, auth_headers, season_id)
    payload = {"week_id": week_id, "contestants": [_contestant_payload(n) for n in "ABC"]}
    resp = client.post("/api/automation/import", json=payload, headers=auth_headers)
    assert resp.status_code == 201
    assert len(resp.get_json()["contestants"]) == 3


def test_import_rejects_empty_contestant_list(client, auth_headers):
    season_id = _create_season(client, auth_headers)
    week_id = _create_week(client, auth_headers, season_id)
    payload = {"week_id": week_id, "contestants": []}
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


def test_successful_import_is_logged(client, auth_headers):
    season_id = _create_season(client, auth_headers)
    week_id = _create_week(client, auth_headers, season_id)
    payload = {
        "week_id": week_id,
        "contestants": [_contestant_payload(n) for n in ["Ayşe", "Mehmet", "Fatma", "Ali"]],
    }
    resp = client.post("/api/automation/import", json=payload, headers=auth_headers)
    assert resp.status_code == 201

    logs = client.get(f"/api/automation/logs?week_id={week_id}").get_json()["logs"]
    assert len(logs) == 1
    assert logs[0]["status"] == "success"
    assert logs[0]["contestant_count"] == 4
    assert logs[0]["error_message"] is None


def test_failed_import_is_logged_with_error_message(client, auth_headers):
    payload = {"week_id": 999, "contestants": [_contestant_payload(n) for n in "ABCD"]}
    resp = client.post("/api/automation/import", json=payload, headers=auth_headers)
    assert resp.status_code == 404

    logs = client.get("/api/automation/logs?week_id=999").get_json()["logs"]
    assert len(logs) == 1
    assert logs[0]["status"] == "failure"
    assert "999" in logs[0]["error_message"]


def test_logs_endpoint_requires_no_auth_and_lists_all_by_default(client, auth_headers):
    season_id = _create_season(client, auth_headers)
    week_id = _create_week(client, auth_headers, season_id)
    payload = {
        "week_id": week_id,
        "contestants": [_contestant_payload(n) for n in ["Ayşe", "Mehmet", "Fatma", "Ali"]],
    }
    client.post("/api/automation/import", json=payload, headers=auth_headers)

    resp = client.get("/api/automation/logs")
    assert resp.status_code == 200
    assert len(resp.get_json()["logs"]) == 1


def test_report_failure_logs_a_client_side_rejection(client, auth_headers):
    season_id = _create_season(client, auth_headers)
    week_id = _create_week(client, auth_headers, season_id)

    resp = client.post(
        "/api/automation/logs",
        json={
            "week_id": week_id,
            "error_message": "Vision model determined this video is not a cooking competition episode",
            "contestant_count": 0,
        },
        headers=auth_headers,
    )
    assert resp.status_code == 201
    body = resp.get_json()
    assert body["status"] == "failure"
    assert body["week_id"] == week_id

    logs = client.get(f"/api/automation/logs?week_id={week_id}").get_json()["logs"]
    assert len(logs) == 1
    assert logs[0]["status"] == "failure"
    assert "not a cooking competition" in logs[0]["error_message"]


def test_report_failure_requires_auth(client):
    resp = client.post(
        "/api/automation/logs",
        json={"week_id": 1, "error_message": "x"},
    )
    assert resp.status_code == 401
