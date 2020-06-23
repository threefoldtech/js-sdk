import bisect
import hashlib
import itertools

from jumpscale.loader import j


def binary_search(a, x, lo=0, hi=None):  # can't use a to specify default for hi
    hi = hi if hi is not None else len(a)  # hi defaults to len(a)
    pos = bisect.bisect_left(a, x, lo, hi)  # find insertion position
    return pos if pos != hi and a[pos] == x else -1  # don't walk off the end


def to_entropy(words, english):
    if not isinstance(words, list):
        words = words.split(" ")
    if len(words) not in [12, 15, 18, 21, 24]:
        raise j.core.exceptions.Value(
            "Number of words must be one of the following: [12, 15, 18, 21, 24], but it is not (%d)." % len(words)
        )
    # Look up all the words in the list and construct the
    # concatenation of the original entropy and the checksum.
    concatLenBits = len(words) * 11
    concatBits = [False] * concatLenBits
    wordindex = 0
    use_binary_search = True
    for word in words:
        # Find the words index in the wordlist
        ndx = binary_search(english, word) if use_binary_search else english.index(word)
        if ndx < 0:
            raise j.core.exceptions.NotFound('Unable to find "%s" in word list.' % word)
        # Set the next 11 bits to the value of the index.
        for ii in range(11):
            concatBits[(wordindex * 11) + ii] = (ndx & (1 << (10 - ii))) != 0
        wordindex += 1
    checksumLengthBits = concatLenBits // 33
    entropyLengthBits = concatLenBits - checksumLengthBits
    # Extract original entropy as bytes.
    entropy = bytearray(entropyLengthBits // 8)
    for ii in range(len(entropy)):
        for jj in range(8):
            if concatBits[(ii * 8) + jj]:
                entropy[ii] |= 1 << (7 - jj)
    # Take the digest of the entropy.
    hashBytes = hashlib.sha256(entropy).digest()
    hashBits = list(itertools.chain.from_iterable(([c & (1 << (7 - i)) != 0 for i in range(8)] for c in hashBytes)))
    # Check all the checksum bits.
    for i in range(checksumLengthBits):
        if concatBits[entropyLengthBits + i] != hashBits[i]:
            raise j.core.exceptions.Value("Failed checksum.")
    return bytes(entropy)
