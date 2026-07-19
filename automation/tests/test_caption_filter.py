from automation.ocr.base import OcrResult
from automation.vision.caption_filter import filter_caption_like_fragments


def _frame(*lines: str) -> list[OcrResult]:
    return [OcrResult(frame_path="frame_0.jpg", text_lines=list(lines))]


def test_short_contestant_name_survives():
    result = filter_caption_like_fragments(_frame("Ayse Yilmaz"))
    assert result[0].text_lines == ["Ayse Yilmaz"]


def test_short_dish_name_survives():
    result = filter_caption_like_fragments(_frame("Mercimek Corbasi"))
    assert result[0].text_lines == ["Mercimek Corbasi"]


def test_single_word_judge_name_survives():
    result = filter_caption_like_fragments(_frame("Zuhal"))
    assert result[0].text_lines == ["Zuhal"]


def test_name_with_apostrophe_survives():
    result = filter_caption_like_fragments(_frame("Yusuf'a"))
    assert result[0].text_lines == ["Yusuf'a"]


def test_day_header_caption_is_dropped():
    # Real failure case: a 5-word day-header caption misread as a contestant name.
    result = filter_caption_like_fragments(_frame("4 GUN YARISMACISI AYSEL DEMIR"))
    assert result[0].text_lines == []


def test_quoted_judge_commentary_is_dropped():
    # Long enough to exceed the word-count threshold on its own -- the
    # quote/colon don't need to be treated as disqualifying in themselves.
    result = filter_caption_like_fragments(
        _frame('ABDULLAH: "ENGINAR VELOUTE CORBADA PATATES BASKIN OLMUS"')
    )
    assert result[0].text_lines == []


def test_prize_money_announcement_is_dropped():
    # Real failure case: this produced a hallucinated "score" of 200000.
    result = filter_caption_like_fragments(
        _frame("POLYANA TOPLAM 20 PUAN ALARAK 200.000 TL'YE VEDA EDIYOR")
    )
    assert result[0].text_lines == []


def test_short_score_reveal_with_colon_survives():
    # Deliberately not punctuation-based: a real score reveal reads exactly
    # like this ("Zuhal: 8"), so a colon must not be disqualifying on its own.
    result = filter_caption_like_fragments(_frame("Zuhal: 8"))
    assert result[0].text_lines == ["Zuhal: 8"]


def test_fragment_at_exact_word_limit_survives():
    result = filter_caption_like_fragments(_frame("Bir Iki Uc Dort"), max_words=4)
    assert result[0].text_lines == ["Bir Iki Uc Dort"]


def test_fragment_one_word_over_limit_is_dropped():
    result = filter_caption_like_fragments(_frame("Bir Iki Uc Dort Bes"), max_words=4)
    assert result[0].text_lines == []


def test_empty_lines_are_dropped():
    result = filter_caption_like_fragments(_frame("", "  ", "Ayse"))
    assert result[0].text_lines == ["Ayse"]


def test_day_header_compressed_under_word_limit_is_still_dropped():
    # Real failure case: OCR merged "2." into "2GUN", leaving only 4 words --
    # under the word-count threshold, but still clearly a day-header caption.
    result = filter_caption_like_fragments(_frame("2GUN YARISMACISI POLYANA HOROZ"))
    assert result[0].text_lines == []


def test_short_narration_sentence_without_day_header_is_dropped():
    # Real failure case: "Yusuf greets the contestants" -- only 3 words, no
    # day-header pattern, but still narration via the "karsiliyor" root.
    result = filter_caption_like_fragments(_frame("YUSUF YARISMACILARIMIZI KARSILIYOR"))
    assert result[0].text_lines == []


def test_menu_caption_is_dropped():
    result = filter_caption_like_fragments(_frame("YUSUF'UN FINE DINING MENUSU"))
    assert result[0].text_lines == []


def test_turkish_diacritics_are_folded_before_matching():
    # Same narration word, properly accented this time -- must still match.
    result = filter_caption_like_fragments(_frame("Yusuf Yarışmacılarımızı Karşılıyor"))
    assert result[0].text_lines == []


def test_real_place_name_containing_karsi_root_is_not_a_false_positive():
    # "Karsiyaka" (a real Izmir district) contains "karsi" but not the
    # "karsil" root used for "karsiliyor" -- must not be dropped.
    result = filter_caption_like_fragments(_frame("Karsiyaka"))
    assert result[0].text_lines == ["Karsiyaka"]


def test_short_fragment_without_narration_vocabulary_survives():
    result = filter_caption_like_fragments(_frame("Polyana Horoz"))
    assert result[0].text_lines == ["Polyana Horoz"]
