import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import pytest
import transparency_crypto as tc

REPORT = b"# HW4 AI-usage log\n| 2026-10-14 | critique | attempt1, 3 gaps named |\n"


def test_roundtrip():
    sealed, opening = tc.seal(REPORT)
    assert tc.open_sealed(sealed, opening) == REPORT


def test_commitment_is_binding_to_report():
    sealed, opening = tc.seal(REPORT)
    other = REPORT + b"| extra |\n"
    assert tc.commit(other, opening.blinding) != sealed.commitment


def test_commitment_is_hiding_across_blindings():
    r1 = tc.sodium.crypto_core_ristretto255_scalar_random()
    r2 = tc.sodium.crypto_core_ristretto255_scalar_random()
    assert tc.commit(REPORT, r1) != tc.commit(REPORT, r2)


def test_wrong_key_fails():
    sealed, opening = tc.seal(REPORT)
    bad = tc.Opening(bytes(32), opening.blinding)
    with pytest.raises(ValueError, match="decryption failed"):
        tc.open_sealed(sealed, bad)


def test_wrong_blinding_fails_commitment_check():
    sealed, opening = tc.seal(REPORT)
    bad = tc.Opening(opening.key, tc.sodium.crypto_core_ristretto255_scalar_random())
    with pytest.raises(ValueError, match="commitment mismatch"):
        tc.open_sealed(sealed, bad)


def test_ciphertext_bound_to_commitment():
    sealed, opening = tc.seal(REPORT)
    other_c = tc.commit(REPORT, tc.sodium.crypto_core_ristretto255_scalar_random())
    forged = tc.Sealed(other_c, sealed.nonce, sealed.ciphertext)
    with pytest.raises(ValueError, match="decryption failed"):
        tc.open_sealed(forged, opening)


def test_text_encodings_roundtrip():
    sealed, opening = tc.seal(REPORT)
    tok = tc.encode_opening(opening)
    assert len(tok) == 64 + 1 + 64
    assert tc.decode_opening(" " + tok.upper() + "\n") == opening
    assert tc.decode_sealed(tc.encode_sealed(sealed)) == sealed
    assert tc.open_sealed(tc.decode_sealed(tc.encode_sealed(sealed)), tc.decode_opening(tok)) == REPORT


def test_generator_h_is_fixed_and_valid():
    h = tc.generator_h()
    assert h == tc.generator_h()
    assert tc.sodium.crypto_core_ristretto255_is_valid_point(h)
