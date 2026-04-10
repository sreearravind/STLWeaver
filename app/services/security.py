"""Minimal security validation scaffold."""


class SecurityValidator:
    """Placeholder for static validation and sandbox execution checks."""

    ALLOWED_IMPORTS: set[str] = {"build123d", "math", "typing"}
    DANGEROUS_MODULES: set[str] = {"os", "sys", "subprocess", "socket"}

    def validate_code(self, code: str) -> dict[str, object]:
        """Perform a shallow placeholder validation step."""
        if not code.strip():
            return {"is_safe": False, "violations": ["No code provided."]}
        return {"is_safe": True, "violations": []}
