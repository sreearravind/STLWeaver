"""Minimal security validation scaffold."""


class SecurityValidator:
    """Placeholder for static validation and sandbox execution checks."""

    ALLOWED_IMPORTS: set[str] = {"build123d", "math", "typing"}
    DANGEROUS_MODULES: set[str] = {"os", "sys", "subprocess", "socket"}

    def validate_code(self, code: str) -> tuple[bool, list[str]]:
        """Perform a shallow placeholder validation step."""
        if not code.strip():
            return False, ["No code provided."]
        return True, []

