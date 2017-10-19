# adpated to Python from segment.js of https://github.com/mapbox/linematch

def match_segment(seg1, seg2, r, result):
    a = seg1[0]
    b = seg1[1]
    c = seg2[0]
    d = seg2[1]
    length = len(result)

    ap = close_point(a, c, d, r)
    bp = close_point(b, c, d, r)

    #     a----b
    # c---ap---bp---d
    if ((ap is not None) and (bp is not None)):
        return True  # fully covered

    cp = close_point(c, a, b, r)
    dp = close_point(d, a, b, r)

    if ((cp is not None) and (cp == dp)):
        return False  # degenerate case, no overlap

    if ((cp is not None) and (dp is not None)):
        cpp = seg_point(a, b, cp)
        dpp = seg_point(a, b, dp)

        if (equals(cpp, dpp)):
            return False  # degenerate case

        # a---cp---dp---b
        #     c----d
        if (cp < dp):
            if (not equals(a, cpp)):
                result.insert(0, [a, cpp])
            if (not equals(dpp, b)):
                result.insert(0, [dpp, b])

        # a---dp---cp---b
        #     d----c
        else:
            if (not equals(a, dpp)):
                result.insert(0, [a, dpp])
            if (not equals(cpp, b)):
                result.insert(0, [cpp, b])

    elif (cp is not None):
        cpp = seg_point(a, b, cp)

        #     a----cp---b
        # d---ap---c
        if ((ap is not None) and not equals(a, cpp)):
            result.insert(0, [cpp, b])

        # a---cp---b
        #     c----bp---d
        elif ((bp is not None) and (not equals(cpp, b))):
            result.insert(0, [a, cpp])

    elif (dp is not None):
        dpp = seg_point(a, b, dp)

        # a---dp---b
        #     d----bp---c
        if ((bp is not None) and (not equals(dpp, b))):
            result.insert(0, [a, dpp])

        #     a----dp---b
        # c---ap---d
        elif ((ap is not None) and (not equals(a, dpp))):
            result.insert(0, [dpp, b])

    if len(result) != length:
        return True
    else:
        return False


def seg_point(a, b, t):
    return [a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t]


# find a closest point from a given point p to a segment [a, b]
# if it's within given square distance r
def close_point(p, a, b, r):
    x = a[0]
    y = a[1]
    dx = b[0] - x
    dy = b[1] - y

    if (dx != 0) or (dy != 0):
        t = ((p[0] - x) * dx + (p[1] - y) * dy) / (dx * dx + dy * dy)

        if (t >= 1):
            x = b[0]
            y = b[1]
            t = 1
        elif (t > 0):
            x += dx * t
            y += dy * t
        else:
            t = 0

    dx = p[0] - x
    dy = p[1] - y

    if (dx * dx + dy * dy) < (r * r):
        return t
    else:
        return None


def equals(a, b):
    return (abs(a[0] - b[0]) < 1e-12) and (abs(a[1] - b[1]) < 1e-12)
