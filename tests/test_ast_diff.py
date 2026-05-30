from sin_code_ibd.ast_diff import ASTDiff
from sin_code_ibd.intent_summarizer import IntentSummarizer


def test_signature_change():
    ad = ASTDiff()
    a = b"def foo(x): pass"
    b = b"def foo(x, y): pass"
    changes = ad.diff_strings(a, b)
    assert any(c.change_type == "signature_changed" for c in changes)


def test_added_symbol():
    ad = ASTDiff()
    a = b"def foo(): pass"
    b = b"def foo(): pass\ndef bar(): pass"
    changes = ad.diff_strings(a, b)
    assert any(c.change_type == "added" for c in changes)


def test_intent_summarizer():
    ad = ASTDiff()
    changes = ad.diff_strings(b"def foo(x): pass", b"def foo(x, y): pass")
    ism = IntentSummarizer()
    intents = ism.summarize(changes)
    assert any(i.category == "api_change" for i in intents)
