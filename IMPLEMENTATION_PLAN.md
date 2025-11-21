# MIDI Event Accumulation - Implementation Plan

## Overview

This document provides a detailed implementation plan for adding MIDI event
accumulation to midi2cmd. This plan is designed to be used for delegating
implementation tasks to development agents.

## Current Architecture Analysis

### Key Components

1. **console.py** (src/midi2cmd/console.py)
   - Entry point with Typer CLI
   - `process_messages()` function: Main message loop (lines 90-94)
   - `msg_to_simple_cmd_mapper()`: Current 1:1 message-to-command handler (lines 101-104)
   - Uses handler pattern with `MessageHandler` type

2. **midi_reader.py** (src/midi2cmd/midi_reader.py)
   - `ConfigTxt` dataclass: Holds port and commands
   - `MessageDict`: Custom dict that normalizes messages (ignores time, value, pitch)
   - `_normalize()` method: Already handles control_change and pitchwheel types
   - Config parsing in `read()` method

3. **utils.py** (src/midi2cmd/utils.py)
   - `get_value()`: Extracts value from messages
   - `runcmd()`: Executes commands with environment variables

### Current Message Flow

```
MIDI Port → process_messages() → msg_to_simple_cmd_mapper() → runcmd()
                                        ↓
                                  ConfigTxt.commands[message]
```

## Implementation Strategy

### Phase 1: Configuration Parsing (Low Risk)

**Goal**: Add support for parsing `accumulate_window` from config file.

**Changes Required**:

1. **Modify ConfigTxt dataclass** (midi_reader.py)
   - Add field: `accumulate_window: float = 0.5`
   - Update `read()` method to parse `accumulate_window: <seconds>` line
   - Add validation: must be positive number

**Implementation Details**:

```python
@dataclass
class ConfigTxt:
    port: str = ""
    accumulate_window: float = 0.5  # seconds
    commands: MessageDict = field(default_factory=MessageDict)

    def read(self, txt: IO[str]) -> None:
        for line in txt:
            # ... existing parsing ...
            if line.startswith("accumulate_window:"):
                value_str = line.split(":", 1)[1].strip()
                # Parse value (handle "0.5" or "500ms")
                self.accumulate_window = parse_time_value(value_str)
```

**Testing**:

- Unit tests for parsing various time formats
- Test default value when not specified
- Test validation of negative/invalid values
- Update existing config file tests

**Files to Modify**:

- `src/midi2cmd/midi_reader.py`
- `tests/test_midi_reader.py`

---

### Phase 2: Accumulator Core Logic (Medium Risk)

**Goal**: Implement event accumulation without threading (synchronous approach).

**New Component**: Create `accumulator.py` module

**Accumulator Class Design**:

```python
@dataclass
class EventSeries:
    """Represents a series of accumulated MIDI events."""
    start_value: int
    end_value: int
    event_count: int
    first_timestamp: float
    message_template: Message  # Normalized message for identification

    def delta(self) -> int:
        """Calculate absolute change with sign."""
        return self.end_value - self.start_value

    def percent_change(self) -> float:
        """Calculate percentage change based on message type."""
        if self.message_template.type == "pitchwheel":
            return (self.delta() / 16383) * 100
        else:  # control_change
            return (self.delta() / 127) * 100


class EventAccumulator:
    """Accumulates MIDI events over a time window."""

    def __init__(self, window_seconds: float):
        self.window_seconds = window_seconds
        self.current: EventSeries | None = None

    def add_event(self, message: Message, current_time: float) -> EventSeries | None:
        """
        Add event to accumulator. Returns flushed event series if window expired or control changed.

        Strategy:
        1. If no current accumulation, start new one
        2. If message is different control, flush current and start new
        3. If message is same control but window expired, flush and start new
        4. Otherwise, add to current accumulation
        """
        normalized = MessageDict._normalize(message)
        value = get_value(message)

        # No current accumulation - start new
        if self.current is None:
            self.current = EventSeries(
                start_value=value,
                end_value=value,
                event_count=1,
                first_timestamp=current_time,
                message_template=normalized
            )
            return None

        # Different control - flush current, start new
        if normalized != self.current.message_template:
            flushed = self.current
            self.current = EventSeries(
                start_value=value,
                end_value=value,
                event_count=1,
                first_timestamp=current_time,
                message_template=normalized
            )
            return flushed

        # Same control - check if window expired
        if (current_time - self.current.first_timestamp) > self.window_seconds:
            flushed = self.current
            self.current = EventSeries(
                start_value=value,
                end_value=value,
                event_count=1,
                first_timestamp=current_time,
                message_template=normalized
            )
            return flushed

        # Same control within window - accumulate
        self.current.end_value = value
        self.current.event_count += 1
        return None

    def flush(self) -> EventSeries | None:
        """Flush current accumulation (called on program exit)."""
        flushed = self.current
        self.current = None
        return flushed
```

**Implementation Details**:

- Use `time.monotonic()` for timestamps (not affected by system time changes)
- Only accumulate `control_change` and `pitchwheel` types (validated in add_event)
- Single active accumulator at any time (one control being accumulated)
- Stateless between different controls (automatic flush on control change)

**Testing**:

- Unit tests for single event (no accumulation)
- Unit tests for multiple events within window
- Unit tests for window expiration
- Unit tests for control change triggering flush
- Unit tests for both control_change and pitchwheel
- Unit tests for EventSeries.percent_change() calculation (both ranges)
- Test edge case: flush with no current accumulation

**Files to Create**:

- `src/midi2cmd/accumulator.py`
- `tests/test_accumulator.py`

---

### Phase 3: Integration with Message Handler (Medium Risk)

**Goal**: Replace simple mapper with accumulating mapper.

**Changes Required**:

1. **Create new handler function** (console.py)

```python
def msg_to_accumulating_cmd_mapper(
    cfg: ConfigTxt,
    accumulator: EventAccumulator,
    message: Message
) -> None:
    """Handle message with accumulation support."""
    # Only accumulate control_change and pitchwheel
    if message.type not in ["control_change", "pitchwheel"]:
        # Non-accumulating types: execute immediately
        cmd = cfg.commands[message]
        if cmd:
            runcmd(cmd, MIDI_VALUE=get_value(message))
        return

    # Add to accumulator
    current_time = time.monotonic()
    flushed_event = accumulator.add_event(message, current_time)

    # If we got a flushed event, execute its command
    if flushed_event:
        execute_accumulated_command(cfg, flushed_event)


def execute_accumulated_command(cfg: ConfigTxt, events: EventSeries) -> None:
    """Execute command with accumulated event data."""
    # Reconstruct message to look up command
    message = events.message_template.copy()
    message.value = events.end_value  # Or pitch for pitchwheel

    cmd = cfg.commands[message]
    if not cmd:
        return

    # Prepare environment variables
    delta = events.delta()
    percent = events.percent_change()

    runcmd(
        cmd,
        MIDI_VALUE=events.end_value,
        MIDI_START_VALUE=events.start_value,
        MIDI_END_VALUE=events.end_value,
        MIDI_DELTA=f"{delta:+d}",  # With sign prefix
        MIDI_PERCENT_CHANGE=f"{percent:+.2f}",  # With sign prefix
        MIDI_EVENT_COUNT=events.event_count,
    )
```

2. **Modify run() command** (console.py)

```python
@app.command()
def run(
    config_path: str = typer.Option(...),
    port: str = typer.Option(None, ...),
) -> None:
    """Run the MIDI command processor."""
    cfg = load_config_txt(config_path)
    port = port or cfg.port
    validate_midi_port(port)

    # Create accumulator
    accumulator = EventAccumulator(cfg.accumulate_window)

    # Create handler with accumulator
    cmd_handler = partial(msg_to_accumulating_cmd_mapper, cfg, accumulator)

    process_messages(port, handlers=[cmd_handler])
```

**Implementation Details**:

- No cleanup needed on program exit - pending events are discarded
- Keep backward compatibility: single events work exactly as before
- Environment variables include all values even for single events (delta=0, count=1)
- Sign prefix required: `+` or `-` for MIDI_DELTA and MIDI_PERCENT_CHANGE

**Testing**:

- Unit tests for execute_accumulated_command with mock runcmd (passing EventSeries events)
- Unit tests for msg_to_accumulating_cmd_mapper with various scenarios
- Test that non-accumulating types bypass accumulation
- Test environment variable values and formatting

**Files to Modify**:

- `src/midi2cmd/console.py`
- `tests/test_console.py`

---

### Phase 4: Integration Tests (Low Risk)

**Goal**: Add end-to-end tests demonstrating accumulation behavior.

**Test Scenarios**:

1. **Test: Multiple events within window**
   - Send 5 control_change events rapidly (within window)
   - Verify command executes once with aggregated EventSeries values
   - Check MIDI_EVENT_COUNT=5, MIDI_DELTA, MIDI_PERCENT_CHANGE

2. **Test: Window expiration**
   - Send 3 events within window
   - Wait for window to expire
   - Send 3 more events
   - Verify 2 separate command executions with separate EventSeries

3. **Test: Control change triggers flush**
   - Send 3 events for control A
   - Send 1 event for control B (triggers flush of A)
   - Verify control A executed with EventSeries of 3 events
   - Verify control B starts new EventSeries

4. **Test: Single event behavior**
   - Send 1 event, wait for flush
   - Verify EventSeries has MIDI_START_VALUE == MIDI_END_VALUE
   - Verify MIDI_DELTA = +0 or -0
   - Verify MIDI_EVENT_COUNT = 1

5. **Test: Pitchwheel range calculation**
   - Send pitchwheel events with large delta
   - Verify EventSeries.percent_change() uses 16383 range

6. **Test: Exit without flush**
   - Send events and immediately terminate process
   - Verify pending events are discarded (no command execution on exit)

**Implementation Details**:

- Extend virtual_midi_device.py if needed to support timed sequences
- Create new integration test config with accumulate_window setting
- Use signal mode for precise control over message timing
- Capture stdout to verify environment variable values

**Files to Modify/Create**:

- `tests/test_integration.py` (add new tests)
- `tests/fixtures/accumulation.config.txt` (new config)
- Possibly `virtual_midi_device.py` (if timing features needed)

---

### Phase 5: Documentation and Examples (Low Risk)

**Goal**: Update documentation with accumulation feature.

**Changes Required**:

1. **Update README.md**
   - Add section on accumulation feature
   - Explain time window configuration
   - Document all new environment variables
   - Add example use cases from FEATURE_SPEC.md

2. **Add example configs** to the README
   - Add volume control example
   - Add scrolling example
   - Add brightness control example

3. **Update CLI help text**
   - Ensure `midi2cmd run --help` mentions accumulation
   - Document config file format

**Files to Modify/Create**:

- `README.md`

---

## Implementation Order

### Recommended Sequence

1. **Phase 1: Configuration Parsing** (1-2 hours)
   - Low risk, no behavior changes
   - Foundation for other phases
   - Easy to test in isolation

2. **Phase 2: Accumulator Core** (3-4 hours)
   - Core logic, needs careful testing
   - Completely isolated, no integration yet
   - Can be thoroughly unit tested

3. **Phase 3: Handler Integration** (2-3 hours)
   - Medium risk, changes message processing
   - Requires phases 1 and 2 complete
   - Should maintain backward compatibility

4. **Phase 4: Integration Tests** (2-3 hours)
   - Validates entire feature
   - Can be done in parallel with Phase 5
   - Requires phases 1-3 complete

5. **Phase 5: Documentation** (1-2 hours)
   - Low risk, no code changes
   - Can be done in parallel with Phase 4
   - Final polish before release

**Total Estimated Time**: 9-14 hours

---

## Key Design Decisions

### 1. Synchronous vs Threaded Accumulation

**Decision**: Synchronous (no threads)

**Rationale**:

- Simpler implementation and debugging
- No race conditions or locking needed
- Window expiration checked on next event (lazy)
- Trade-off: If no new events arrive, accumulator waits until next event or exit
- Acceptable for intended use case (continuous control adjustments)

### 2. Global vs Per-Command Window

**Decision**: Global window configuration

**Rationale**:

- Simpler configuration
- Consistent behavior across all controls
- Per-spec requirement
- Can be extended later if needed

### 3. Single Active Accumulator

**Decision**: Only one control accumulates at a time

**Rationale**:

- Users typically adjust one control at a time
- Automatic flush when switching controls
- Simpler state management
- Per-spec requirement

### 4. Environment Variable Naming

**Decision**: Use `MIDI_` prefix for all variables

**Rationale**:

- Consistent with existing `MIDI_VALUE`
- Clear namespace separation
- Easy to filter in shell scripts

### 5. Sign Prefix for Delta Values

**Decision**: Always include `+` or `-` prefix

**Rationale**:

- Makes direction explicit
- Easier to use in commands (pactl, xdotool)
- Per-spec requirement

---

## Testing Strategy

### Unit Tests

- **test_midi_reader.py**: Config parsing, window validation
- **test_accumulator.py**: Core accumulation logic (extensive)
- **test_console.py**: Handler functions, environment variables
- **test_utils.py**: Any new utility functions

### Integration Tests

- **test_integration.py**: End-to-end scenarios using virtual device
- Focus on timing, flushing, and command execution
- Verify environment variables in actual command execution

### Type Checking

- All new code must pass `mypy` type checking
- Add type annotations to all functions
- Use proper types from `mido` library

---

## Potential Issues and Mitigations

### Issue 1: Timing Precision

**Risk**: Window expiration timing may be imprecise

**Mitigation**:

- Use `time.monotonic()` for reliable intervals
- Document that window is a minimum, not exact
- Integration tests validate timing behavior

### Issue 2: Pending Events on Exit

**Risk**: Events pending in accumulator at exit time are lost

**Mitigation**:

- This is intentional per specification
- Document that only completed accumulations execute commands
- Pending events are simply discarded on exit (no special handling needed)

### Issue 3: Large Event Counts

**Risk**: Rapidly moving control could accumulate thousands of events

**Mitigation**:

- No maximum count limit per spec
- Memory usage is minimal (only storing start/end values)
- Command executes after window regardless of count

### Issue 4: Backward Compatibility

**Risk**: Changing handler could break existing configs

**Mitigation**:

- Keep default window at 500ms (reasonable for most use cases)
- Single events work identically (all env vars still set)
- New env vars don't break existing scripts (ignored if not used)

---

## Success Criteria Checklist

Per FEATURE_SPEC.md:

- [ ] Global accumulation window can be configured in config file
- [ ] All `control_change` and `pitchwheel` messages automatically use accumulation
- [ ] Accumulated values (start, end, delta, percent, count) are passed to commands
- [ ] Accumulation flushes on different control type or window expiration
- [ ] Integration tests demonstrate accumulation behavior
- [ ] Documentation updated with examples

Additional criteria:

- [ ] All unit tests pass
- [ ] All integration tests pass
- [ ] Type checking passes (`mypy`)
- [ ] Pre-commit hooks pass
- [ ] Examples directory created with working configs
- [ ] README updated with complete feature documentation

---

## Agent Task Delegation

### Task 1: Configuration Parser Agent

**Responsibility**: Implement Phase 1
**Skills Required**: Python, dataclasses, parsing
**Entry Point**: `src/midi2cmd/midi_reader.py`
**Exit Criteria**: Unit tests pass, config parsing works

### Task 2: Accumulator Logic Agent

**Responsibility**: Implement Phase 2
**Skills Required**: Python, algorithms, timing
**Entry Point**: Create `src/midi2cmd/accumulator.py`
**Exit Criteria**: Unit tests pass, all edge cases covered

### Task 3: Integration Agent

**Responsibility**: Implement Phase 3
**Skills Required**: Python, refactoring, integration
**Entry Point**: `src/midi2cmd/console.py`
**Exit Criteria**: Unit tests pass, backward compatible

### Task 4: Testing Agent

**Responsibility**: Implement Phase 4
**Skills Required**: Python, pytest, integration testing
**Entry Point**: `tests/test_integration.py`
**Exit Criteria**: Integration tests pass, full coverage

### Task 5: Documentation Agent

**Responsibility**: Implement Phase 5
**Skills Required**: Technical writing, Markdown
**Entry Point**: `README.md`, `examples/`
**Exit Criteria**: Complete documentation, working examples

---

## Notes

- Follow conventional commits specification
- Use `uv` for all package management
- Run `just test` before marking task complete
- Keep functions small and focused (single responsibility)
- Add docstrings to all public functions
- Use dataclasses over regular classes where appropriate
