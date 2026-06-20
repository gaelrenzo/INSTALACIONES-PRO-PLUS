"""Excepciones del dominio compartido."""

from __future__ import annotations


class ErrorDominio(Exception):
    """Base de todas las excepciones de dominio."""


class ValorInvalido(ErrorDominio):
    """Un valor no cumple las reglas de dominio."""
