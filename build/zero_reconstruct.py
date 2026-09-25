#!/usr/bin/env python3
"""
Reconstruction du zero non barre pour la police Temoin.

Principe : dans Atkinson Hyperlegible Next, la barre du zero n'est pas un
contour ajoute. Elle est un vide : la contreforme ovale du zero a ete
decoupee en deux morceaux par une bande diagonale. Il n'y a donc rien a
supprimer, il faut recoudre l'ovale.

Les deux morceaux de contreforme sont des sous-courbes exactes de l'ovale
d'origine. On peut donc retrouver l'ovale par le calcul, sans redessiner :
pour chaque coupure, on connait le debut d'une courbe de Bezier et sa fin,
et on resout les deux parametres de decoupe. La reconstruction est verifiee
par le residu du systeme (doit etre nul a l'unite pres).
"""

import math
import numpy as np
from scipy.optimize import least_squares


# ---------------------------------------------------------------- geometrie

def bez(p0, c1, c2, p3, u):
    m = 1.0 - u
    return (m * m * m * np.asarray(p0)
            + 3 * m * m * u * np.asarray(c1)
            + 3 * m * u * u * np.asarray(c2)
            + u * u * u * np.asarray(p3))


def split_left(p0, c1, c2, p3, t):
    """Points de controle de la sous-courbe [0, t]."""
    p0, c1, c2, p3 = map(np.asarray, (p0, c1, c2, p3))
    a1 = p0 + t * (c1 - p0)
    a2 = p0 + 2 * t * (c1 - p0) + t * t * (c2 - 2 * c1 + p0)
    a3 = bez(p0, c1, c2, p3, t)
    return p0, a1, a2, a3


def split_right(p0, c1, c2, p3, t):
    """Points de controle de la sous-courbe [t, 1]."""
    p0, c1, c2, p3 = map(np.asarray, (p0, c1, c2, p3))
    s = 1.0 - t
    b3 = p3
    b2 = p3 + s * (c2 - p3)
    b1 = p3 + 2 * s * (c2 - p3) + s * s * (c1 - 2 * c2 + p3)
    b0 = bez(p0, c1, c2, p3, t)
    return b0, b1, b2, b3


def rejoin(piece1, piece2):
    """
    piece1 = (P0, A1, A2, A3) : debut de la courbe d'origine, coupee en t1
    piece2 = (B0, B1, B2, P3) : fin de la meme courbe, coupee en t2

    Retourne (C1, C2, t1, t2, residu) pour la courbe d'origine P0 -> P3.
    """
    P0 = np.asarray(piece1[0], float)
    A1 = np.asarray(piece1[1], float)
    A2 = np.asarray(piece1[2], float)
    B1 = np.asarray(piece2[1], float)
    B2 = np.asarray(piece2[2], float)
    P3 = np.asarray(piece2[3], float)

    d1 = A1 - P0          # = t1 * (C1 - P0)
    d2 = B2 - P3          # = (1-t2) * (C2 - P3)

    def unpack(x):
        t1, s = x                       # s = 1 - t2
        t1 = min(max(t1, 1e-6), 1 - 1e-6)
        s = min(max(s, 1e-6), 1 - 1e-6)
        C1 = P0 + d1 / t1
        C2 = P3 + d2 / s
        return t1, s, C1, C2

    def residuals(x):
        t1, s, C1, C2 = unpack(x)
        t2 = 1.0 - s
        _, _, a2, _ = split_left(P0, C1, C2, P3, t1)
        _, b1, _, _ = split_right(P0, C1, C2, P3, t2)
        return np.concatenate([a2 - A2, b1 - B1])

    best = None
    for guess in ((0.4, 0.4), (0.2, 0.2), (0.6, 0.6), (0.5, 0.3), (0.3, 0.5)):
        sol = least_squares(residuals, guess, bounds=([1e-6, 1e-6], [1 - 1e-6, 1 - 1e-6]))
        if best is None or sol.cost < best.cost:
            best = sol
    t1, s, C1, C2 = unpack(best.x)
    return C1, C2, t1, 1.0 - s, float(np.max(np.abs(residuals(best.x))))


# ------------------------------------------------------- chemins glyphs

def segments(path):
    """Decoupe un GSPath ferme en segments ('line'|'curve', p0, [ctrl...], p3)."""
    nodes = list(path.nodes)
    oncurve = [n for n in nodes if n.type != 'offcurve']
    if not oncurve:
        return []
    start = nodes.index(oncurve[-1])          # on part du dernier oncurve
    order = nodes[start:] + nodes[:start]
    segs, pending, prev = [], [], _pt(order[0])
    for n in order[1:] + [order[0]]:
        if n.type == 'offcurve':
            pending.append(_pt(n))
            continue
        if n.type == 'line':
            segs.append(('line', prev, [], _pt(n)))
        else:
            segs.append(('curve', prev, pending, _pt(n)))
        pending, prev = [], _pt(n)
    return segs


def _pt(node):
    return (float(node.position.x), float(node.position.y))


def area(pts):
    a = 0.0
    for i in range(len(pts)):
        x1, y1 = pts[i]
        x2, y2 = pts[(i + 1) % len(pts)]
        a += x1 * y2 - x2 * y1
    return a / 2.0


def open_arc(path):
    """Retire le segment droit (la coupe de la barre) et retourne les segments restants."""
    segs = segments(path)
    idx = [i for i, s in enumerate(segs) if s[0] == 'line']
    if len(idx) != 1:
        raise ValueError(f"attendu 1 segment droit, trouve {len(idx)}")
    i = idx[0]
    return segs[i + 1:] + segs[:i]


def merge_counters(pathA, pathB):
    """Recoud les deux moities de contreforme en un ovale unique."""
    a, b = open_arc(pathA), open_arc(pathB)
    recon = []
    diag = []
    for first, second in ((a, b), (b, a)):
        p1 = first[-1]
        p2 = second[0]
        piece1 = (p1[1], p1[2][0], p1[2][1], p1[3])
        piece2 = (p2[1], p2[2][0], p2[2][1], p2[3])
        C1, C2, t1, t2, res = rejoin(piece1, piece2)
        recon.append(('curve', piece1[0], [tuple(C1), tuple(C2)], piece2[3]))
        diag.append((t1, t2, res))
    merged = a[1:-1] + [recon[0]] + b[1:-1] + [recon[1]]
    return merged, diag
