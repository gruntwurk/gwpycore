# ############################################################################
#                                                            KEYWORDS/HASHTAGS
# ############################################################################

CONNECTIVE_WORDS = [
    "a", "an", "the",
    "and", "but", "or", "nor", "not", "true", "false",
    "of", "to", "from",
    "i", "you", "he", "she", "them", "they", "my", "our", "ours", "your", "yours", "mine",
    "if", "then", "else", "that", "otherwise",
    "yes", "no", "have"]


def standardize_keywords(keywords, dictionary):
    """
    Standardizes a list of strings (keywords, hashtags, index entries, etc.)
    by comparing each word in the `keywords` list with the given `dictionary`.

    :param keywords: The list to be standardized.

    :param dictionary: The dictionary keys are the preferred keywords. The
    corresponding values are each a list of the sub-optimal keyword variations.

    :returns: A copy of the `keywords` list, but with any matches replaced
    by their preferred versions. In the special case of the dictionary key
    being blank (an empty string), the original keyword is simply suppressed,
    as opposed being replaced by the empty string.
    """
    results = []
    for candidate in keywords:
        for kwd in dictionary:
            if candidate in dictionary[kwd]:
                if kwd:
                    results.append(kwd)
                break
        else:
            results.append(candidate)
    return results


__all__ = [
    "standardize_keywords",
    "CONNECTIVE_WORDS",
]