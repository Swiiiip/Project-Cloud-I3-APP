# Split-service smoke and stress tests

This package contains scenario-based smoke/stress checks for the Blurmoji split architecture.

Scenarios:
- `queue_delay`: checks whether render calls experience queueing delay >= threshold
- `concurrent_sessions`: validates isolation for at least 100 concurrent sessions
- `gateway_restrictions`: confirms public users can use gateway routes but not internal routes
- `stress`: mixed high-load calls with error-rate and latency SLO gates
- `connectivity`: verifies gateway/internal health and Redis/MySQL/Azurite reachability

Run all scenarios:

```powershell
python -m src.tests.smoke.run_suite
```

Run one scenario:

```powershell
python -m src.tests.smoke.run_suite --scenario stress
```

Quick local harness against embedded mock gateway:

```powershell
python -m src.tests.smoke.mock_stack
```

