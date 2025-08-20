"""
Metrics collection for NAICS classification service.
"""
import time
from collections import defaultdict
from typing import Dict, Any


class MetricsCollector:
    def __init__(self):
        # Store counters and timings
        self.counters = defaultdict(int)
        self.timings = defaultdict(list)

    def inc(self, metric_name: str, amount: int = 1):
        """Increment a counter metric."""
        self.counters[metric_name] += amount

    def observe(self, metric_name: str, value: float):
        """Record a timing/observation value."""
        self.timings[metric_name].append(value)

    def start_timer(self) -> float:
        """Get a start timestamp for measuring elapsed time."""
        return time.perf_counter()

    def stop_timer(self, start_time: float, metric_name: str):
        """Record an elapsed time for a given metric."""
        elapsed = time.perf_counter() - start_time
        self.observe(metric_name, elapsed)
        return elapsed

    def get_metrics(self) -> Dict[str, Any]:
        """Return all current metrics as a dict."""
        return {
            "counters": dict(self.counters),
            "timings": {k: {
                "count": len(v),
                "avg": sum(v) / len(v) if v else 0,
                "min": min(v or [0]),
                "max": max(v or [0])
            } for k, v in self.timings.items()}
        }

    def reset(self):
        """Reset all metrics."""
        self.counters.clear()
        self.timings.clear()


# Optionally create a global collector instance
metrics_collector = MetricsCollector()
