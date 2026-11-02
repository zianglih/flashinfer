"""Observe nested host wall time without changing AUTO calls or tactic order.

No CUDA event, synchronization, logging, or serialization is added to calls.
The caller installs this only during a necessary native AUTO run, never merely
to repeat existing evidence. Compile means the cute.compile API boundary,
including its SDK cache lookup; this is not isolated compiler backend CPU time.
"""
from contextlib import contextmanager
from contextvars import ContextVar
from functools import wraps
from time import perf_counter_ns


class NestedTiming:
    def __init__(self):
        self.stack = ContextVar('sync_audit_wall_stack', default=())
        self.report = {
            'clock': 'perf_counter_ns',
            'groups': {},
            'boundary': 'Inclusive/exclusive host wall spans. cute.compile includes SDK cache work; profile excludes nested compile only in its exclusive column and still includes warmups, graph capture, GPU waits and measurement machinery. Import/native C++ build time is not classified as cute.compile. No extra GPU synchronization or changed calls/order.',
        }

    @contextmanager
    def span(self, kind):
        stack = self.stack.get()
        frame = [kind, 0]
        token = self.stack.set((*stack, frame))
        started = perf_counter_ns()
        failed = False
        try:
            yield
        except BaseException:
            failed = True
            raise
        finally:
            elapsed = perf_counter_ns() - started
            self.stack.reset(token)
            if stack:
                stack[-1][1] += elapsed
            scope = 'inside_context' if kind == 'context' or any(row[0] == 'context' for row in stack) else 'outside_context'
            key = f'{scope}/{kind}'
            row = self.report['groups'].setdefault(key, {
                'calls': 0, 'failed_calls': 0,
                'inclusive_wall_ns': 0, 'exclusive_wall_ns': 0,
            })
            row['calls'] += 1
            row['failed_calls'] += int(failed)
            row['inclusive_wall_ns'] += elapsed
            row['exclusive_wall_ns'] += elapsed - frame[1]

    def wrap(self, function, kind):
        @wraps(function)
        def observed(*args, **kwargs):
            with self.span(kind):
                return function(*args, **kwargs)
        return observed


def install(autotuner_class):
    import cutlass.cute as cute
    ledger = NestedTiming()
    cute.compile = ledger.wrap(cute.compile, 'cute_compile')
    autotuner_class._profile_single_kernel = ledger.wrap(
        autotuner_class._profile_single_kernel, 'profile_single_kernel')
    return ledger
