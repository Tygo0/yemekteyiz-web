def _create_season(client, auth_headers, year=2026):
    resp = client.post(
        "/api/seasons", json={"name": "Season 1", "year": year}, headers=auth_headers
    )
    assert resp.status_code == 201
    return resp.get_json()["id"]


def _create_week(client, auth_headers, season_id, week_number=15):
    resp = client.post(
        "/api/weeks",
        json={"season_id": season_id, "week_number": week_number},
        headers=auth_headers,
    )
    assert resp.status_code == 201
    return resp.get_json()["id"]


def _create_contestant(client, auth_headers, week_id, name="Ayşe"):
    resp = client.post(
        "/api/contestants",
        json={"week_id": week_id, "name": name, "age": 30, "city": "Ankara"},
        headers=auth_headers,
    )
    assert resp.status_code == 201
    return resp.get_json()["id"]


def _create_episode(client, auth_headers, contestant_id):
    resp = client.post(
        "/api/episodes",
        json={"contestant_id": contestant_id, "video_url": "https://youtube.com/x"},
        headers=auth_headers,
    )
    assert resp.status_code == 201
    return resp.get_json()["id"]


def test_full_chain_create_and_read(client, auth_headers):
    season_id = _create_season(client, auth_headers)
    week_id = _create_week(client, auth_headers, season_id)
    contestant_id = _create_contestant(client, auth_headers, week_id)
    episode_id = _create_episode(client, auth_headers, contestant_id)

    dish_resp = client.post(
        "/api/dishes",
        json={"episode_id": episode_id, "name": "Mercimek Çorbası", "category": "soup"},
        headers=auth_headers,
    )
    assert dish_resp.status_code == 201

    score_resp = client.post(
        "/api/scores",
        json={
            "episode_id": episode_id,
            "contestant_id": contestant_id,
            "judge_name": "Zuhal",
            "value": 9,
        },
        headers=auth_headers,
    )
    assert score_resp.status_code == 201

    # Public GETs require no auth
    assert client.get("/api/contestants").status_code == 200
    assert client.get(f"/api/contestants/{contestant_id}").status_code == 200
    assert client.get(f"/api/contestants?week_id={week_id}").status_code == 200
    assert len(client.get(f"/api/contestants?week_id={week_id}").get_json()) == 1


def test_duplicate_week_number_rejected(client, auth_headers):
    season_id = _create_season(client, auth_headers)
    _create_week(client, auth_headers, season_id, week_number=15)
    resp = client.post(
        "/api/weeks",
        json={"season_id": season_id, "week_number": 15},
        headers=auth_headers,
    )
    assert resp.status_code == 409


def test_week_for_nonexistent_season_rejected(client, auth_headers):
    resp = client.post(
        "/api/weeks", json={"season_id": 999, "week_number": 1}, headers=auth_headers
    )
    assert resp.status_code == 404


def test_score_out_of_range_rejected_by_schema(client, auth_headers):
    season_id = _create_season(client, auth_headers)
    week_id = _create_week(client, auth_headers, season_id)
    contestant_id = _create_contestant(client, auth_headers, week_id)
    episode_id = _create_episode(client, auth_headers, contestant_id)

    resp = client.post(
        "/api/scores",
        json={
            "episode_id": episode_id,
            "contestant_id": contestant_id,
            "judge_name": "Zuhal",
            "value": 99,
        },
        headers=auth_headers,
    )
    assert resp.status_code == 400


def test_score_contestant_mismatch_rejected(client, auth_headers):
    season_id = _create_season(client, auth_headers)
    week_id = _create_week(client, auth_headers, season_id)
    c1 = _create_contestant(client, auth_headers, week_id, name="Ayşe")
    c2 = _create_contestant(client, auth_headers, week_id, name="Mehmet")
    episode_id = _create_episode(client, auth_headers, c1)

    # Scoring c2 against c1's episode should be rejected — the score must
    # target the contestant that episode actually belongs to.
    resp = client.post(
        "/api/scores",
        json={
            "episode_id": episode_id,
            "contestant_id": c2,
            "judge_name": "Zuhal",
            "value": 8,
        },
        headers=auth_headers,
    )
    assert resp.status_code == 400


def test_dish_invalid_category_rejected(client, auth_headers):
    season_id = _create_season(client, auth_headers)
    week_id = _create_week(client, auth_headers, season_id)
    contestant_id = _create_contestant(client, auth_headers, week_id)
    episode_id = _create_episode(client, auth_headers, contestant_id)

    resp = client.post(
        "/api/dishes",
        json={"episode_id": episode_id, "name": "Mystery Dish", "category": "snacks"},
        headers=auth_headers,
    )
    assert resp.status_code == 400


def test_set_winner_must_belong_to_week(client, auth_headers):
    season_id = _create_season(client, auth_headers)
    week1 = _create_week(client, auth_headers, season_id, week_number=1)
    week2 = _create_week(client, auth_headers, season_id, week_number=2)
    outsider = _create_contestant(client, auth_headers, week2, name="Outsider")

    resp = client.put(
        f"/api/weeks/{week1}", json={"winner_id": outsider}, headers=auth_headers
    )
    assert resp.status_code == 400


def test_delete_week_cascades_to_contestants(client, auth_headers):
    season_id = _create_season(client, auth_headers)
    week_id = _create_week(client, auth_headers, season_id)
    contestant_id = _create_contestant(client, auth_headers, week_id)

    resp = client.delete(f"/api/weeks/{week_id}", headers=auth_headers)
    assert resp.status_code == 204
    assert client.get(f"/api/contestants/{contestant_id}").status_code == 404
