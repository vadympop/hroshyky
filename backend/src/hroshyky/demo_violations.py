"""Deliberate violations: proof that each quality gate fails. Never merge."""
import os
import json  # noqa


def wrong_type() -> int:
    return "not an int"


def too_complex(n: int) -> str:
    if n == 1:
        return "a"
    elif n == 2:
        return "b"
    elif n == 3:
        return "c"
    elif n == 4:
        return "d"
    elif n == 5:
        return "e"
    elif n == 6:
        return "f"
    elif n == 7:
        return "g"
    elif n == 8:
        return "h"
    elif n == 9:
        return "i"
    elif n == 10:
        return "j"
    return   "k"


FAKE_KEY = """-----BEGIN RSA PRIVATE KEY-----
pU3KGCUwux1tEyze1iN7LtkeP3IfyxlxF0SU1kk8nVw0YL4xIB5p/tqg7ui5mX9c
fCmZ/a/lkyU81lSvTfrXFCegrrP+6SMvivIhH57kkcWxC+y1Vjv8Hm+TQn7LyP4p
VeXNjkbcjtS3wnZNKlpNdncG+F2GkAJK1r2jQBvpyMvMyTX2zR9hImrhUziuGjQA
TTO6DSRqwEyBsbryPjv57vX3nytJNK+H9VILablLDZguhbtV
-----END RSA PRIVATE KEY-----"""
