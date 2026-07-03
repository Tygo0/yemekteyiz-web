def _create_season(client, auth_headers, year=2026):
    resp = client.post(
        "/api/seasons", json={"name": "Season 1", "year": year}, headers=auth_headers
    )
    return resp.get_json()["id"]


def _create_week(client, auth_headers, season_id, week_number=15):
    resp = client.post(
        "/api/weeks",
        json={"season_id": season_id, "week_number": week_number},
        headers=auth_headers,
    )
    return resp.get_json()["id"]


def _create_contestant(client, auth_headers, week_id, name="Ayşe"):
    resp = client.post(
        "/api/contestants",
        json={"week_id": week_id, "name": name},
        headers=auth_headers,
    )
    return resp.get_json()["id"]


def _create_episode(client, auth_headers, contestant_id):
    resp = client.post(
        "/api/episodes", json={"contestant_id": contestant_id}, headers=auth_headers
    )
    return resp.get_json()["id"]


def test_update_season(client, auth_headers):
    season_id = _create_season(client, auth_headers)
    resp = client.put(
        f"/api/seasons/{season_id}", json={"name": "Season One"}, headers=auth_headers
    )
    assert resp.status_code == 200
    assert resp.get_json()["name"] == "Season One"
    # year untouched by partial update
    assert resp.get_json()["year"] == 2026


def test_update_season_requires_auth(client, auth_headers):
    season_id = _create_season(client, auth_headers)
    resp = client.put(f"/api/seasons/{season_id}", json={"name": "x"})
    assert resp.status_code == 401


def test_update_episode(client, auth_headers):
    season_id = _create_season(client, auth_headers)
    week_id = _create_week(client, auth_headers, season_id)
    contestant_id = _create_contestant(client, auth_headers, week_id)
    episode_id = _create_episode(client, auth_headers, contestant_id)

    resp = client.put(
        f"/api/episodes/{episode_id}",
        json={"video_url": "https://youtube.com/updated"},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    assert resp.get_json()["video_url"] == "https://youtube.com/updated"
    # contestant_id cannot be changed via update — not in the update schema
    assert resp.get_json()["contestant_id"] == contestant_id


def test_delete_episode(client, auth_headers):
    season_id = _create_season(client, auth_headers)
    week_id = _create_week(client, auth_headers, season_id)
    contestant_id = _create_contestant(client, auth_headers, week_id)
    episode_id = _create_episode(client, auth_headers, contestant_id)

    resp = client.delete(f"/api/episodes/{episode_id}", headers=auth_headers)
    assert resp.status_code == 204
    assert client.get(f"/api/episodes/{episode_id}").status_code == 404


def test_update_score_value_and_judge(client, auth_headers):
    season_id = _create_season(client, auth_headers)
    week_id = _create_week(client, auth_headers, season_id)
    contestant_id = _create_contestant(client, auth_headers, week_id)
    episode_id = _create_episode(client, auth_headers, contestant_id)

    score_resp = client.post(
        "/api/scores",
        json={
            "episode_id": episode_id,
            "contestant_id": contestant_id,
            "judge_name": "Zuhal",
            "value": 7,
        },
        headers=auth_headers,
    )
    score_id = score_resp.get_json()["id"]

    resp = client.put(f"/api/scores/{score_id}", json={"value": 9}, headers=auth_headers)
    assert resp.status_code == 200
    assert resp.get_json()["value"] == 9
    assert resp.get_json()["judge_name"] == "Zuhal"  # untouched


def test_update_score_out_of_range_rejected(client, auth_headers):
    season_id = _create_season(client, auth_headers)
    week_id = _create_week(client, auth_headers, season_id)
    contestant_id = _create_contestant(client, auth_headers, week_id)
    episode_id = _create_episode(client, auth_headers, contestant_id)

    score_resp = client.post(
        "/api/scores",
        json={
            "episode_id": episode_id,
            "contestant_id": contestant_id,
            "judge_name": "Zuhal",
            "value": 7,
        },
        headers=auth_headers,
    )
    score_id = score_resp.get_json()["id"]

    resp = client.put(f"/api/scores/{score_id}", json={"value": 15}, headers=auth_headers)
    assert resp.status_code == 400


def test_delete_score(client, auth_headers):
    season_id = _create_season(client, auth_headers)
    week_id = _create_week(client, auth_headers, season_id)
    contestant_id = _create_contestant(client, auth_headers, week_id)
    episode_id = _create_episode(client, auth_headers, contestant_id)

    score_resp = client.post(
        "/api/scores",
        json={
            "episode_id": episode_id,
            "contestant_id": contestant_id,
            "judge_name": "Zuhal",
            "value": 7,
        },
        headers=auth_headers,
    )
    score_id = score_resp.get_json()["id"]

    resp = client.delete(f"/api/scores/{score_id}", headers=auth_headers)
    assert resp.status_code == 204
    assert client.get(f"/api/scores/{score_id}").status_code == 404


def test_update_contestant_full_fields(client, auth_headers):
    """Confirms bio/photo_url — required for a usable public profile — are
    actually editable, not just name/age/city as the create form used to
    suggest."""
    season_id = _create_season(client, auth_headers)
    week_id = _create_week(client, auth_headers, season_id)
    contestant_id = _create_contestant(client, auth_headers, week_id)

    resp = client.put(
        f"/api/contestants/{contestant_id}",
        json={
            "biography": "Started cooking with her grandmother in Ankara.",
            "photo_url": "https://example.com/ayse.jpg",
        },
        headers=auth_headers,
    )
    assert resp.status_code == 200
    assert resp.get_json()["biography"].startswith("Started cooking")
    assert resp.get_json()["photo_url"] == "https://example.com/ayse.jpg"


def test_update_week_sets_winner(client, auth_headers):
    season_id = _create_season(client, auth_headers)
    week_id = _create_week(client, auth_headers, season_id)
    contestant_id = _create_contestant(client, auth_headers, week_id)

    resp = client.put(
        f"/api/weeks/{week_id}", json={"winner_id": contestant_id}, headers=auth_headers
    )
    assert resp.status_code == 200
    assert resp.get_json()["winner_id"] == contestant_id
