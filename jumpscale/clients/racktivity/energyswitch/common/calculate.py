import math


def getTHD(harmonics, offset=1):
    """
    returns the thd as calculated from harmonics according to the formula:
    THD = sqrt(sum of squares from second to 39th) / first harmonic
    @param harmonics: list
    @param offset: how many elements omit on start
    """
    # Beware that the first value in the list is ignored because for some reason this is not the first harmonic value
    # most probably because of a firmware bug?
    divideBy = harmonics[offset]
    if divideBy == 0:
        return None
    harmonicVals = harmonics[offset + 1 : offset + 40]

    # Use only the first 39 current amplitudes to calculate THD
    harmonicsSquareSum = 0
    for harmonic in harmonicVals:
        harmonicsSquareSum += harmonic ** 2

    return math.sqrt(harmonicsSquareSum) * 100.0 / divideBy
