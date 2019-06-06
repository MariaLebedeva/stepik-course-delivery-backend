a = int(input())
b = int(input())


def nod(aa, bb):
    r = aa % bb
    rp = bb
    rpp = r
    while rp % rpp != 0:
        r = rp % rpp
        rp = rpp
        rpp = r
    return rpp


def ev(aa, bb):
    n = nod(aa, bb)
    x = aa // n
    y = bb // n
    return x * y * n


if a == b:
    print(a)
elif a > b:
    print(ev(a, b))
else:
    print(ev(b, a))
