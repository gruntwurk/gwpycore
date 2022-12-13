def is_palindrome(word):
    w = word.lower().replace(" ", "")
    return w == w[::-1]
