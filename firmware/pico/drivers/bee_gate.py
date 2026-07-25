"""Bee-gate IR beam counter with direction inference.

Each of N tunnels has two beams, A (outer) and B (inner).  A bee entering the
hive breaks A first then B; a bee exiting breaks B first then A.  Beams within
BEE_GATE_DIRECTION_WINDOW_MS pair to form one event; otherwise the trip is
ambiguous.

We use GPIO interrupts (falling edge on beam break -- phototransistor pulled
low) and record timestamps for each channel.  On each publish tick, main.py
calls consume_counts() to get the running totals since the last call.

Beams that stay low for BEE_GATE_STUCK_TIMEOUT_MS are assumed to be a loitering
bee and disarmed until they release; no spurious event is generated.
"""

import time
from machine import Pin


class _Beam:
    __slots__ = ("pin_num", "pin", "last_edge_ms", "last_state", "stuck")

    def __init__(self, pin_num):
        self.pin_num = pin_num
        self.pin = Pin(pin_num, Pin.IN, Pin.PULL_UP)
        self.last_edge_ms = 0
        self.last_state = 1     # high = beam unbroken
        self.stuck = False


class BeeGate:
    def __init__(self, a_pins, b_pins, direction_window_ms, debounce_ms,
                 stuck_timeout_ms=2000):
        assert len(a_pins) == len(b_pins), "A/B pin count mismatch"
        self.n = len(a_pins)
        self.beams_a = [_Beam(p) for p in a_pins]
        self.beams_b = [_Beam(p) for p in b_pins]
        self.window = direction_window_ms
        self.debounce = debounce_ms
        self.stuck_timeout = stuck_timeout_ms

        self._in = 0
        self._out = 0
        self._ambiguous = 0

        for i, beam in enumerate(self.beams_a):
            beam.pin.irq(handler=self._make_handler(i, "a"),
                         trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING)
        for i, beam in enumerate(self.beams_b):
            beam.pin.irq(handler=self._make_handler(i, "b"),
                         trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING)

    def _make_handler(self, channel, side):
        # Closure over channel index and side letter.
        def _handler(pin):
            self._on_edge(channel, side, pin.value())
        return _handler

    def _on_edge(self, channel, side, state):
        now = time.ticks_ms()
        beam = (self.beams_a[channel] if side == "a"
                else self.beams_b[channel])

        # Debounce.
        if time.ticks_diff(now, beam.last_edge_ms) < self.debounce:
            return

        beam.last_state = state
        beam.last_edge_ms = now

        if state == 0:  # beam just broke
            self._on_break(channel, side, now)
        else:           # beam just cleared
            beam.stuck = False

    def _on_break(self, channel, side, now_ms):
        # Look at the *other* beam on the same channel and see if it recently
        # tripped.  If so, we have a directional event.
        this_beam = (self.beams_a[channel] if side == "a"
                     else self.beams_b[channel])
        other_beam = (self.beams_b[channel] if side == "a"
                      else self.beams_a[channel])

        dt = time.ticks_diff(now_ms, other_beam.last_edge_ms)
        if 0 < dt <= self.window and other_beam.last_state == 0:
            # Other beam is still blocked, this one just tripped -- bee is
            # mid-transit.  Decide direction from which side tripped first.
            if side == "b":     # other = A tripped first -> exit direction
                self._out += 1
            else:               # other = B tripped first -> entry direction
                self._in += 1
            # Reset both edges so the pair isn't double-counted.
            this_beam.last_edge_ms = 0
            other_beam.last_edge_ms = 0
        else:
            # Standalone trip -- may be resolved when the pair arrives, or may
            # end up as ambiguous.  We don't count anything yet.
            pass

    def _garbage_collect_stuck(self, now_ms):
        # Mark beams stuck-low as loitering (no event, no ambiguity).
        for beam in self.beams_a + self.beams_b:
            if (beam.last_state == 0 and not beam.stuck and
                    time.ticks_diff(now_ms, beam.last_edge_ms) > self.stuck_timeout):
                beam.stuck = True

    def consume_counts(self):
        now = time.ticks_ms()
        self._garbage_collect_stuck(now)
        out = {"in": self._in, "out": self._out, "ambiguous": self._ambiguous}
        self._in = 0
        self._out = 0
        self._ambiguous = 0
        return out
