from automation.vision.cluster_fusion import fuse_cluster_extractions


def _partial(name=None, age=None, profession=None, city=None, dishes=None, scores=None):
    return {
        "name": name,
        "age": age,
        "profession": profession,
        "city": city,
        "dishes": dishes or [],
        "scores": scores or [],
    }


def test_empty_partials_yield_no_contestants():
    assert fuse_cluster_extractions([]) == []


def test_none_partials_are_skipped():
    assert fuse_cluster_extractions([None, None]) == []


def test_single_name_cluster_creates_one_contestant():
    result = fuse_cluster_extractions([_partial(name="Ayse", city="Istanbul")])
    assert len(result) == 1
    assert result[0]["name"] == "Ayse"
    assert result[0]["city"] == "Istanbul"


def test_dish_only_cluster_attaches_to_most_recently_named_contestant():
    dish = {"name": "Mercimek Corbasi", "category": "soup"}
    result = fuse_cluster_extractions([
        _partial(name="Ayse"),
        _partial(dishes=[dish]),  # separate dish overlay, no name of its own
    ])
    assert len(result) == 1
    assert result[0]["dishes"] == [dish]


def test_score_only_cluster_attaches_to_most_recently_named_contestant():
    score = {"judge_name": "Zuhal", "value": 8}
    result = fuse_cluster_extractions([
        _partial(name="Ayse"),
        _partial(scores=[score]),
    ])
    assert result[0]["scores"] == [score]


def test_dish_before_any_name_is_established_is_dropped_not_guessed():
    dish = {"name": "Mercimek Corbasi", "category": "soup"}
    result = fuse_cluster_extractions([_partial(dishes=[dish])])
    assert result == []


def test_reappearing_name_variant_merges_into_existing_contestant_not_a_duplicate():
    # Same person, OCR'd slightly differently on a later card (e.g. at judging
    # time vs. their intro card).
    result = fuse_cluster_extractions([
        _partial(name="Ayse Yilmaz", city="Istanbul"),
        _partial(name="Ayse Yilmz"),  # OCR typo variant of the same name
    ])
    assert len(result) == 1
    assert result[0]["city"] == "Istanbul"


def test_distinct_names_produce_separate_contestants():
    result = fuse_cluster_extractions([_partial(name="Ayse"), _partial(name="Mehmet")])
    assert len(result) == 2
    assert {c["name"] for c in result} == {"Ayse", "Mehmet"}


def test_switching_back_to_an_earlier_contestant_attaches_to_the_right_one():
    dish_a = {"name": "Soup", "category": "soup"}
    dish_b = {"name": "Dessert", "category": "dessert"}
    result = fuse_cluster_extractions([
        _partial(name="Ayse"),
        _partial(name="Mehmet"),
        _partial(dishes=[dish_b]),  # attaches to Mehmet (currently active)
        _partial(name="Ayse"),      # re-mentioned -- becomes current again
        _partial(dishes=[dish_a]),  # now attaches to Ayse
    ])
    ayse = next(c for c in result if c["name"] == "Ayse")
    mehmet = next(c for c in result if c["name"] == "Mehmet")
    assert ayse["dishes"] == [dish_a]
    assert mehmet["dishes"] == [dish_b]


def test_missing_fields_fill_in_from_a_later_cluster_without_overwriting():
    result = fuse_cluster_extractions([
        _partial(name="Ayse", city="Istanbul"),
        _partial(name="Ayse", city="Ankara", profession="Ogretmen"),
    ])
    # First-seen city wins, doesn't get clobbered by a possibly-noisier re-read.
    assert result[0]["city"] == "Istanbul"
    assert result[0]["profession"] == "Ogretmen"
