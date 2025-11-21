# Feature Specification: MIDI Event Accumulation

## Overview

Currently, midi2cmd has a 1:1 mapping between MIDI events and commands. Each
MIDI event triggers an immediate command execution. This feature request adds
support for **accumulating multiple MIDI events** over a configurable time
window before executing a command with aggregated values.

## Current Behavior

When a user adjusts a MIDI control (e.g., a slider or knob), the system:

1. Receives one MIDI event per increment/decrement
2. Immediately executes the mapped command for each event
3. Passes the individual event value to the command via `MIDI_VALUE`

**Example**: Turning a volume knob from position 50 to 70 generates 20 separate
events, executing the volume command 20 times.

## Desired Behavior

Add an **accumulation mode** where the system:

1. Collects multiple MIDI events for the same control over a short time window
   (e.g., 500ms)
2. Aggregates these events before executing the command once
3. Provides both absolute values and relative change information to the command

**Example**: Turning a volume knob from position 50 to 70 generates 20 events,
but the command executes only once with aggregated information about the
change.

## Requirements

### 1. Event Accumulation (Simplified - No Threading)

- Collect consecutive events for the same MIDI control within a **globally
configured** time window (default: 500ms)
- Track timestamp of first event to determine window expiration
- Execute accumulated command when **either**:
  - A different control/message type is received (flush previous accumulator)
  - Time window expires (checked synchronously when next event of same control
  arrives)
- Reset accumulator after command execution
- On program exit, discard any pending accumulator (do not flush)
- **No maximum event count limit** - only time-based window constraint

### 2. Aggregated Value Calculation

The command should receive multiple pieces of information:

- **Start Value**: The value from the first event in the accumulation window
- **End Value**: The value from the last event in the accumulation window
- **Total Events**: Number of events accumulated
- **Absolute Change**: `end_value - start_value`
- **Percent Change**: Change relative to the control's total range
  - For standard MIDI controls (0-127): `(absolute_change / 127) * 100`
  - For pitchwheel controls (-8192 to 8191): `(absolute_change / 16383) * 100`

### 3. Configuration Syntax

Add a global accumulation window setting at the top of the config file:

```
port: My MIDI Device
accumulate_window: 0.5

control_change channel=10 control=9: echo "Volume changed by $MIDI_DELTA"
pitchwheel channel=10: volume_control.sh
```

- `accumulate_window` is optional (default: 500ms if not specified)
- All `control_change` and `pitchwheel` commands automatically use accumulation
- Format: `<number>` (in seconds, e.g., `0.5` for 500ms)

### 4. Environment Variables

When executing commands, provide these environment variables:

- `MIDI_VALUE`: Final/end value
- `MIDI_START_VALUE`: First value in the accumulation window
- `MIDI_END_VALUE`: Last value in the accumulation window (same as MIDI_VALUE)
- `MIDI_DELTA`: Absolute change (end - start)
- `MIDI_PERCENT_CHANGE`: Percentage change relative to control range
- `MIDI_EVENT_COUNT`: Number of events accumulated

For single events (not accumulated), all values still work:

- `MIDI_START_VALUE` and `MIDI_END_VALUE` will be the same
- `MIDI_DELTA` will be 0
- `MIDI_EVENT_COUNT` will be 1

Both `MIDI_DELTA` and `MIDI_PERCENT_CHANGE` must be prefixed by the sign (`+`
or `-`) to indicate direction of change.

### 5. Supported Message Types

- Accumulation mode **only** supports: `control_change` and `pitchwheel`
- Other message types (note_on, note_off, etc.) are not supported for accumulation
- Commands configured with accumulation for unsupported types should error or warn

### 6. Default Behavior

- Accumulation is enabled by default for all `control_change` and `pitchwheel` messages
- The global time window applies to all supported message types
- No per-command configuration needed - accumulation happens automatically

## Use Cases

### Use Case 1: Volume Control

**Goal**: Adjust system volume based on how much the knob moved, not individual increments

**Config**:

```
port: My MIDI Device
accumulate_window: 500ms

control_change channel=10 control=9: adjust_volume.sh
```

**Script** (`adjust_volume.sh`):

```bash
#!/bin/bash
# Adjust volume by percentage change
pactl set-sink-volume @DEFAULT_SINK@ "${MIDI_PERCENT_CHANGE}%"
```

### Use Case 2: Smooth Scrolling

**Goal**: Scroll a specific number of lines based on accumulated wheel movement

**Config**:

```
port: My MIDI Device
accumulate_window: 300ms

control_change channel=10 control=12: scroll_content.sh
```

**Script** (`scroll_content.sh`):

```bash
#!/bin/bash
# Scroll by the absolute change amount
xdotool click --repeat $MIDI_DELTA 4  # scroll up by delta amount
```

### Use Case 3: Brightness Control

**Goal**: Set brightness to exact value after user stops adjusting

**Config**:

```
port: My MIDI Device
accumulate_window: 600ms

control_change channel=10 control=15: set_brightness.sh
```

**Script** (`set_brightness.sh`):

```bash
#!/bin/bash
# Set brightness to final value
brightnessctl set "$((MIDI_END_VALUE * 100 / 127))%"
```

## Technical Considerations

### Simplified Accumulation (No Threading)

**Accumulation Strategy:**

- **No timers or threads** - time checking is done synchronously when events arrive
- Accumulate events for a given control until **either**:
  1. Time window expires (checked when next event of same control arrives)
  2. A different control/message type is received (flush previous accumulator immediately)

**Implementation approach:**

- Track timestamp of first event in accumulation window
- On each new event:
  - If it's a different control than currently accumulating: flush the old
    accumulator and start new one
  - If it's the same control: check if time window expired since first event
    - If expired: flush accumulator and start new accumulation
    - If not expired: add to current accumulation
- On program exit: discard any pending accumulator (no flush)

### Per-Control Accumulators

- Each unique MIDI control has its own accumulator state
- Only one accumulator can be "active" at a time
- When switching controls, the previous accumulator is flushed automatically
- Example: Moving from volume knob to brightness slider flushes volume accumulator

### Edge Cases

- Single event within window: Should still execute when flushed
- Program exit: Flush any pending accumulator
- First event after idle: Starts new accumulation window
- Same control after window expires: Flush old accumulation, start new one

## Success Criteria

- [ ] Global accumulation window can be configured in config file
- [ ] All `control_change` and `pitchwheel` messages automatically use accumulation
- [ ] Accumulated values (start, end, delta, percent, count) are passed to commands
- [ ] Accumulation flushes on different control type or window expiration
- [ ] Integration tests demonstrate accumulation behavior
- [ ] Documentation updated with examples

## Implementation Notes

- Time window is configured **globally** (applies to all accumulating commands)
- No maximum event count limit - only time-based constraints
- Pitchwheel range: -8192 to 8191 (total range: 16383)
- Only `control_change` and `pitchwheel` message types support accumulation
