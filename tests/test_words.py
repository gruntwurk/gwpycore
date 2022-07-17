from gwpycore import (standardize_keywords, CONNECTIVE_WORDS)


def test_standardize_keywords():

    hashtag_synonyms = {
        "": CONNECTIVE_WORDS,
        "gratitude": ["thanks", "thx"],
        }

    tags = "The quick brown fox jumped over the lazy dog".lower().split()
    new_tags = " ".join(standardize_keywords(tags, hashtag_synonyms))
    assert new_tags == "quick brown fox jumped over lazy dog"

    tags = "No thanks I regret that I have but one life to give to my country".lower().split()
    new_tags = " ".join(standardize_keywords(tags, hashtag_synonyms))
    assert new_tags == "gratitude regret one life give country"

