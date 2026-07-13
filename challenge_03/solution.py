"""Challenge 03 — Dict dispatch rewritten with structural pattern matching."""


def handle_event(event: dict) -> str:
    match event:
        # Guard `if approved` reproduces the original *truthiness* check;
        # the literal pattern `"approved": True` would only match the exact
        # singleton True (literal True/False/None patterns compare with `is`).
        case {"type": "deploy", "env": "prod", "approved": approved,
              "service": service} if approved:
            return f"deploying {service} to prod"
        case {"type": "deploy"}:
            return "deploy blocked"
        case {"type": "rollback", "service": service}:
            return f"rolling back {service}"
        case {"type": "rollback"}:
            return "rolling back unknown"
        # int(n) is a class pattern: matches if replicas is an int and binds n.
        case {"type": "scale", "replicas": int(n)} if n > 0:
            return f"scaling to {n}"
        case _:
            return "ignored"


if __name__ == "__main__":
    cases = [
        ({"type": "deploy", "env": "prod", "approved": True, "service": "auth"},
         "deploying auth to prod"),
        ({"type": "deploy", "env": "prod", "approved": False, "service": "auth"},
         "deploy blocked"),
        ({"type": "deploy", "env": "staging", "approved": True, "service": "auth"},
         "deploy blocked"),
        ({"type": "rollback", "service": "billing"}, "rolling back billing"),
        ({"type": "rollback"}, "rolling back unknown"),
        ({"type": "scale", "replicas": 4}, "scaling to 4"),
        ({"type": "scale", "replicas": 0}, "ignored"),
        ({"type": "scale", "replicas": "many"}, "ignored"),
        ({"type": "noop"}, "ignored"),
        ({}, "ignored"),
    ]
    for event, expected in cases:
        got = handle_event(event)
        assert got == expected, (event, got, expected)
    print("ok")
