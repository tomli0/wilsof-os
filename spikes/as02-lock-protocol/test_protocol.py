"""No compositor, services, credentials, IPC, disk devices or native locks."""
from protocol import Protocol
from legacy_boolean import LegacyBoolean


def ready(cls=Protocol):
    p = cls()
    assert p.baseline_idle(p.token, 0)
    assert p.ack_closed(p.token, p.ui_epoch)
    return p


def test_delayed_release_cannot_clear_new_intent():
    p = ready()
    a = p.begin()
    assert p.ack_closed(a, p.ui_epoch)
    assert p.start(a)
    p.event("locked", a, 1)
    b = p.begin()
    assert b.generation > a.generation
    p.event("released", a, 2)
    assert not p.can_open(), "release A reopened the gate after lock intent B"


def test_password_start_requires_current_ui_lockdown_ack():
    p = ready()
    a = p.begin()
    assert not p.start(a), "password interface may start before confirmed UI lockdown"
    assert not p.ack_closed(a, p.ui_epoch, closed=False)
    assert not p.start(a)
    assert p.ack_closed(a, p.ui_epoch)
    assert p.start(a)


def test_negative_control_reproduces_rejected_boolean_race():
    p = ready(LegacyBoolean)
    a = p.begin()
    p.event("locked", a, 1)
    p.begin()
    p.event("released", a, 2)
    assert p.can_open(), "negative control must actually expose the stale-release race"


def locked():
    p = ready()
    t = p.begin()
    p.ack_closed(t, p.ui_epoch)
    p.start(t)
    p.event("locked", t, 1)
    return p, t


def test_normal_lock_unlock_recovers_without_locker_exit():
    p, t = locked()
    assert not p.open_request()
    assert p.event("released", t, 2)
    assert p.open_request()


def test_wrong_password_and_every_process_exit_are_not_unlock():
    p, t = locked()
    # Wrong password generates no compositor release; boolean and rc cannot substitute.
    for code in (0, 1, 23, 128 + 15, 128 + 9):
        assert not p.locker_exit(code)
        p.boolean_notification(False)
        assert not p.can_open()
    assert p.event("released", t, 2)
    assert p.can_open()


def test_locker_crash_remains_closed_until_real_release():
    p, _ = locked()
    p.locker_exit(137)
    assert p.state == "LOCKED"
    assert not p.can_open()


def test_immediate_relock_drains_old_slot_without_reopening():
    p, a = locked()
    b = p.begin()
    p.ack_closed(b, p.ui_epoch)
    assert not p.start(b)
    p.event("released", a, 2)
    assert not p.can_open()
    assert p.start(b)
    p.event("locked", b, 3)
    assert not p.can_open()
    p.event("released", b, 4)
    assert p.can_open()


def test_concurrent_intents_invalidate_stale_ack_and_never_double_start():
    p = ready()
    a = p.begin()
    b = p.begin()  # controlled serialization of two simultaneous requests
    assert not p.ack_closed(a, p.ui_epoch)
    assert not p.start(a)
    assert p.ack_closed(b, p.ui_epoch)
    assert p.start(b)
    assert not p.start(b)


def test_session_change_rejects_previous_epoch_and_requires_baseline():
    p, a = locked()
    old_generation = p.token.generation
    p.change_session("boot/other-logind/other-compositor")
    assert p.token.generation > old_generation
    assert not p.event("released", a, 2)
    assert not p.can_open()
    assert p.baseline_idle(p.token, 0)
    assert not p.can_open()
    assert p.ack_closed(p.token, p.ui_epoch)
    assert p.can_open()


def test_dms_restart_before_start_invalidates_old_ack():
    p = ready()
    t = p.begin()
    old_ui = p.ui_epoch
    p.ack_closed(t, old_ui)
    p.ui_restart()
    assert not p.start(t)
    assert not p.ack_closed(t, old_ui)
    assert p.ack_closed(t, p.ui_epoch)
    assert p.start(t)


def test_dms_restart_during_lock_defaults_closed_and_can_recover():
    p, t = locked()
    old_ui = p.ui_epoch
    p.ui_restart()
    p.event("released", t, 2)
    assert not p.can_open()
    assert not p.ack_closed(t, old_ui)
    assert p.ack_closed(t, p.ui_epoch)
    assert p.can_open()


def test_disconnect_rejects_queued_release_and_reconnect_does_not_guess():
    p, t = locked()
    p.disconnect()
    assert not p.event("released", t, 2)
    assert not p.can_open()
    p.reconnect()
    assert not p.event("released", t, 2)
    assert not p.baseline_idle(p.token, 0), "pending lock cannot be silently abandoned"
    assert not p.can_open()  # explicit unresolved liveness boundary


def test_idle_reconnect_requires_new_causal_baseline_and_ui_ack():
    p = ready()
    old = p.token
    p.disconnect()
    p.reconnect()
    assert not p.baseline_idle(old, 0)
    assert not p.can_open()
    assert p.baseline_idle(p.token, 0)
    assert not p.can_open()
    p.ack_closed(p.token, p.ui_epoch)
    assert p.can_open()


def test_open_and_lazy_activation_during_every_transition_are_denied():
    p = ready()
    t = p.begin()
    assert not p.open_request()
    p.ack_closed(t, p.ui_epoch)
    assert not p.open_request()
    p.start(t)
    assert not p.open_request()
    p.event("locked", t, 1)
    assert not p.open_request()


def test_release_before_secured_and_sequence_gap_quarantine():
    p = ready()
    t = p.begin()
    p.ack_closed(t, p.ui_epoch)
    p.start(t)
    assert not p.event("released", t, 1)
    assert not p.can_open()
    p, t = locked()
    assert not p.event("released", t, 3)
    assert not p.event("released", t, 2)
    assert not p.can_open()


def test_stale_ui_ack_and_boolean_cannot_open_initial_unknown():
    p = Protocol()
    p.boolean_notification(False)
    p.ack_closed(p.token, p.ui_epoch)
    assert not p.can_open()


def test_new_intent_after_release_but_before_ui_ack_stays_closed():
    p, a = locked()
    p.ui_restart()
    p.event("released", a, 2)
    b = p.begin()
    assert not p.ack_closed(a, p.ui_epoch)
    assert not p.can_open()
    assert p.ack_closed(b, p.ui_epoch)
    assert not p.can_open()


def test_untagged_histories_are_indistinguishable():
    # Same visible input: True, False. In H1 False releases A; in H2 it is
    # delayed A while unobserved B is active. No receiver-only boolean rule can
    # both reopen H1 and refuse H2 without another authority/fence.
    h1 = {"seen": (True, False), "actually_locked": False}
    h2 = {"seen": (True, False), "actually_locked": True}
    assert h1["seen"] == h2["seen"]
    assert h1["actually_locked"] != h2["actually_locked"]


def test_limit_start_permission_survives_ui_restart_in_external_caller():
    # Executable counterexample to the native handshake claim, NOT a safe adapter.
    p = ready()
    t = p.begin()
    p.ack_closed(t, p.ui_epoch)
    retained_launch_permission = p.start(t)
    p.ui_restart()
    assert retained_launch_permission, "a previously returned bool cannot be revoked"
    assert p.ack is None, "replacement UI has never acknowledged lockdown"
    assert not p.can_open()
    # An external caller can still launch using retained_launch_permission.
    # There is deliberately no real launch and no assertion that this is safe.


def test_limit_new_process_reuses_session_authority_identity():
    first = ready()
    old = first.begin()
    second = ready()
    new = second.begin()
    assert old == new, "in-memory counters do not prevent cross-process replay"
    assert second.ack_closed(old, first.ui_epoch), "old ack token is indistinguishable"


def test_out_of_band_lock_is_only_detected_after_notification():
    p = ready()
    assert p.can_open(), "model has no pre-notification knowledge of external lock"
    assert not p.event("locked", p.token, 1)
    assert not p.can_open()


def test_bounded_adversarial_schedules():
    from itertools import product
    actions = ("begin", "ack", "start", "locked", "released", "false", "restart", "disconnect", "open")
    for schedule in product(actions, repeat=4):
        p = ready()
        for action in schedule:
            if action == "begin":
                p.begin()
            elif action == "ack":
                p.ack_closed(p.token, p.ui_epoch)
            elif action == "start":
                before_ack = p.ack
                old_ui = p.ui_epoch
                started = p.start(p.token)
                if started:
                    assert before_ack == (p.token, old_ui), schedule
            elif action in ("locked", "released"):
                p.event(action, p.physical or p.token, p.sequence + 1)
            elif action == "false":
                p.boolean_notification(False)
            elif action == "restart":
                p.ui_restart()
            elif action == "disconnect":
                p.disconnect()
            else:
                assert p.open_request() == p.can_open()
            if p.pending or p.physical is not None or not p.connected or not p.synced:
                assert not p.can_open(), schedule
