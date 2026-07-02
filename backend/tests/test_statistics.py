def _build_scored_week(client, auth_headers):
    season_id = client.post(
        "/api/seasons", json={"name": "Season 1", "year": 2026}, headers=auth_headers
    ).get_json()["id"]
    week_id = client.post(
        "/api/weeks",
        json={"season_id": season_id, "week_number": 1},
        headers=auth_headers,
    ).get_json()["id"]

    c1 = client.post(
        "/api/contestants",
        json={"week_id": week_id, "name": "Ayşe"},
        headers=auth_headers,
    ).get_json()["id"]
    c2 = client.post(
        "/api/contestants",
        json={"week_id": week_id, "name": "Mehmet"},
        headers=auth_headers,
    ).get_json()["id"]

    e1 = client.post(
        "/api/episodes", json={"contestant_id": c1}, headers=auth_headers
    ).get_json()["id"]
    e2 = client.post(
        "/api/episodes", json={"contestant_id": c2}, headers=auth_headers
    ).get_json()["id"]

    client.post(
        "/api/dishes",
        json={"episode_id": e1, "name": "Mercimek Çorbası", "category": "soup"},
        headers=auth_headers,
    )
    client.post(
        "/api/dishes",
        json={"episode_id": e2, "name": "Mercimek Çorbası", "category": "soup"},
        headers=auth_headers,
    )

    for judge, value in [("Zuhal", 10), ("Mehmet", 8)]:
        client.post(
            "/api/scores",
            json={"episode_id": e1, "contestant_id": c1, "judge_name": judge, "value": value},
            headers=auth_headers,
        )
    for judge, value in [("Zuhal", 6), ("Ayşe", 7)]:
        client.post(
            "/api/scores",
            json={"episode_id": e2, "contestant_id": c2, "judge_name": judge, "value": value},
            headers=auth_headers,
        )

    client.put(f"/api/weeks/{week_id}", json={"winner_id": c1}, headers=auth_headers)
    return {"week_id": week_id, "c1": c1, "c2": c2}


def test_statistics_endpoint_is_public(client):
    resp = client.get("/api/statistics")
    assert resp.status_code == 200


def test_statistics_values(client, auth_headers):
    ids = _build_scored_week(client, auth_headers)
    stats = client.get("/api/statistics").get_json()

    # average of 10, 8, 6, 7 = 7.75
    assert stats["average_score"] == 7.75

    assert stats["highest_score_ever"]["value"] == 10
    assert stats["highest_score_ever"]["contestant_id"] == ids["c1"]

    assert stats["most_common_dish"]["dish_name"] == "Mercimek Çorbası"
    assert stats["most_common_dish"]["count"] == 2

    # c1 avg = (10+8)/2 = 9, c2 avg = (6+7)/2 = 6.5 -> c1 most successful
    assert stats["most_successful_contestant"]["contestant_id"] == ids["c1"]
    assert stats["most_successful_contestant"]["average_score"] == 9.0

    assert stats["score_distribution"]["10"] == 1
    assert stats["score_distribution"]["6"] == 1

    winners = stats["weekly_winners"]
    assert len(winners) == 1
    assert winners[0]["winner_id"] == ids["c1"]

    weekly_avgs = stats["average_weekly_score"]
    assert len(weekly_avgs) == 1
    assert weekly_avgs[0]["average_score"] == 7.75
