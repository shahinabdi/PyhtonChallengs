"""Challenge 35 — Finite state machine driven by a transition table."""

from enum import StrEnum


class State(StrEnum):
    DRAFT = "draft"
    REVIEW = "review"
    APPROVED = "approved"
    PUBLISHED = "published"


class Event(StrEnum):
    SUBMIT = "submit"
    APPROVE = "approve"
    REJECT = "reject"
    PUBLISH = "publish"


class InvalidTransition(Exception):
    def __init__(self, state: State, event: Event) -> None:
        super().__init__(f"cannot {event!s} while in state {state!s}")
        self.state = state
        self.event = event


class Document:
    """States: draft -> review -> approved -> published
                        review -> draft (reject)
       Illegal transitions raise InvalidTransition."""

    # The whole behavior in one data structure — adding a state/event is
    # a table edit, not new control flow. (state, event) -> next state.
    TRANSITIONS: dict[tuple[State, Event], State] = {
        (State.DRAFT, Event.SUBMIT): State.REVIEW,
        (State.REVIEW, Event.APPROVE): State.APPROVED,
        (State.REVIEW, Event.REJECT): State.DRAFT,
        (State.APPROVED, Event.PUBLISH): State.PUBLISHED,
    }

    def __init__(self, title: str) -> None:
        self.title = title
        self.state = State.DRAFT
        self.history: list[str] = []

    def dispatch(self, event: Event) -> State:
        try:
            new_state = self.TRANSITIONS[(self.state, event)]
        except KeyError:
            raise InvalidTransition(self.state, event) from None

        old_state, self.state = self.state, new_state
        self.history.append(f"{old_state}--{event}->{new_state}")

        # Hook discovery via getattr: if the subclass/instance defines
        # on_enter_<state>, call it — no if/elif, no registry to maintain.
        hook = getattr(self, f"on_enter_{new_state}", None)
        if callable(hook):
            hook(old_state, event)
        return new_state

    # ---- per-transition hooks (found by name) ---------------------------
    def on_enter_review(self, old: State, event: Event) -> None:
        self.history.append(f"[hook] notifying reviewers of {self.title!r}")

    def on_enter_published(self, old: State, event: Event) -> None:
        self.history.append("[hook] purging CDN cache")


if __name__ == "__main__":
    doc = Document("Q3 report")

    assert doc.dispatch(Event.SUBMIT) == State.REVIEW      # hook fires
    assert doc.dispatch(Event.REJECT) == State.DRAFT       # review -> draft
    assert doc.dispatch(Event.SUBMIT) == State.REVIEW
    assert doc.dispatch(Event.APPROVE) == State.APPROVED
    assert doc.dispatch(Event.PUBLISH) == State.PUBLISHED  # hook fires

    assert "[hook] notifying reviewers of 'Q3 report'" in doc.history
    assert "[hook] purging CDN cache" in doc.history

    # Illegal transition: publishing from draft.
    fresh = Document("memo")
    try:
        fresh.dispatch(Event.PUBLISH)
    except InvalidTransition as exc:
        print(f"blocked: {exc}")
        assert exc.state is State.DRAFT and exc.event is Event.PUBLISH

    # Terminal state: nothing is legal from published.
    try:
        doc.dispatch(Event.SUBMIT)
    except InvalidTransition:
        print("published is terminal, as designed")

    print("\n".join(doc.history))
    print("ok")
