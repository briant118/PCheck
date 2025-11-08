"""Custom password validators for the account app."""

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


class StrongPasswordValidator:
    """Ensure passwords meet basic strength requirements."""

    def __init__(
        self,
        min_length: int = 8,
        require_upper: bool = True,
        require_lower: bool = True,
        require_digit: bool = True,
    ) -> None:
        self.min_length = min_length
        self.require_upper = require_upper
        self.require_lower = require_lower
        self.require_digit = require_digit

    def validate(self, password: str, user=None) -> None:
        if len(password) < self.min_length:
            raise ValidationError(
                _(f"This password must contain at least {self.min_length} characters."),
                code="password_too_short",
            )

        if self.require_digit and not any(char.isdigit() for char in password):
            raise ValidationError(
                _("This password must contain at least one number."),
                code="password_no_number",
            )

        if self.require_upper and not any(char.isupper() for char in password):
            raise ValidationError(
                _("This password must contain at least one uppercase letter."),
                code="password_no_upper",
            )

        if self.require_lower and not any(char.islower() for char in password):
            raise ValidationError(
                _("This password must contain at least one lowercase letter."),
                code="password_no_lower",
            )

    def get_help_text(self) -> str:
        requirements = [f"at least {self.min_length} characters"]
        if self.require_digit:
            requirements.append("one number")
        if self.require_upper:
            requirements.append("one uppercase letter")
        if self.require_lower:
            requirements.append("one lowercase letter")

        return _(
            "Your password must contain " + ", ".join(requirements[:-1]) +
            (" and " + requirements[-1] if len(requirements) > 1 else "") + "."
        )

