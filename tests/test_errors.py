"""Tests for error mapping."""

from __future__ import annotations

import pytest

from tessera.errors import (
    AuthenticationError,
    BadRequestError,
    ForbiddenError,
    InternalServerError,
    NotFoundError,
    ServiceUnavailableError,
    TesseraAPIError,
    error_from_response,
)


@pytest.mark.parametrize(
    ("code", "expected"),
    [
        ("unauthorized", AuthenticationError),
        ("forbidden", ForbiddenError),
        ("not_found", NotFoundError),
        ("bad_request", BadRequestError),
        ("unavailable", ServiceUnavailableError),
        ("internal", InternalServerError),
    ],
)
def test_maps_error_code_to_exception(code: str, expected: type[TesseraAPIError]) -> None:
    exc = error_from_response(400, f'{{"error": "{code}"}}'.encode())
    assert isinstance(exc, expected)
    assert exc.code == code


def test_falls_back_to_status_when_body_missing() -> None:
    exc = error_from_response(404, None)
    assert isinstance(exc, NotFoundError)
    assert exc.code is None
    assert exc.status_code == 404


def test_falls_back_to_status_on_unparseable_body() -> None:
    exc = error_from_response(503, b"<html>gateway timeout</html>")
    assert isinstance(exc, ServiceUnavailableError)


def test_unknown_status_yields_base_api_error() -> None:
    exc = error_from_response(418, None)
    assert type(exc) is TesseraAPIError
    assert exc.status_code == 418
