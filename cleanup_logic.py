import re
def clean(code):
    # Remove non-ascii non-printable characters
    code = "".join(c for c in code if c.isprintable() or c in "\n\r\t")
    # Basic sanity check: if it's too broken, use a placeholder
    if "def " not in code or "return" not in code:
        code = "def synthesized_func(**kwargs):\n    return 'SYNTH_FALLBACK: Logic too chaotic'"
    return code
