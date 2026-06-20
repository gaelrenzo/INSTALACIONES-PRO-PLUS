"""Domain exceptions for the calculations module."""

from __future__ import annotations

from electra.dominio.shared.excepciones import ErrorDominio


class ErrorCalculo(ErrorDominio):
    """Base exception for calculation errors."""


class ParametroInvalido(ErrorCalculo):
    """Raised when a required parameter is invalid or missing."""
