"""Read-only NVML sampling around a command; no CUDA context or clock writes.

Uses CUPTI get_timestamp for the same timestamp domain as activity records.
The child command and its environment are unchanged. Polling makes these runs
clock diagnostics, not replacement retention timings.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time

import pynvml as nvml
from cupti import cupti


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--gpu', required=True, help='Physical NVML index or UUID')
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--interval-ms', type=float, default=2.0)
    parser.add_argument('command', nargs=argparse.REMAINDER)
    args = parser.parse_args()
    command = args.command[1:] if args.command[:1] == ['--'] else args.command
    assert command and args.interval_ms >= 1.0
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=False)
    nvml.nvmlInit()
    handle = (nvml.nvmlDeviceGetHandleByIndex(int(args.gpu)) if args.gpu.isdecimal()
              else nvml.nvmlDeviceGetHandleByUUID(args.gpu))
    reason_bits = {name: int(getattr(nvml, name)) for name in dir(nvml)
                   if name.startswith('nvmlClocksEventReason') and
                   isinstance(getattr(nvml, name), int)}
    receipt = dict(complete=False, started=time.time(), command=command,
                   uuid=nvml.nvmlDeviceGetUUID(handle), interval_ms=args.interval_ms,
                   reason_bits=reason_bits, pid=os.getpid(),
                   helper_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                   boundary='Read-only NVML plus CUPTI get_timestamp only. No CUDA context, activity collection, clock, power, or benchmark changes. Diagnostic polling may affect host scheduling.')
    errors = {}

    def read(name, fn):
        try:
            return fn()
        except nvml.NVMLError as exc:
            errors.setdefault(name, str(exc))
            return None

    def stamp():
        # get_timestamp needs no CUPTI activity initialization or GPU context.
        before = time.perf_counter_ns()
        value = int(cupti.get_timestamp())
        return dict(perf_before_ns=before, cupti_ns=value,
                    perf_after_ns=time.perf_counter_ns(), wall_ns=time.time_ns())

    def save():
        receipt['unsupported_fields'] = errors
        (out / 'receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')

    # Warm get_timestamp once to exclude lazy library initialization in samples.
    receipt['clock_calibration'] = [stamp() for _ in range(5)]
    save()
    process = None
    count = 0
    try:
        with (out / 'samples.jsonl').open('w', buffering=1) as stream:
            process = subprocess.Popen(command)
            receipt['child_pid'] = process.pid
            save()
            deadline = time.perf_counter()
            while True:
                start = stamp()
                util = read('utilization', lambda: nvml.nvmlDeviceGetUtilizationRates(handle))
                record = dict(index=count, start=start,
                    sm_mhz=read('sm', lambda: nvml.nvmlDeviceGetClockInfo(handle, nvml.NVML_CLOCK_SM)),
                    graphics_mhz=read('graphics', lambda: nvml.nvmlDeviceGetClockInfo(handle, nvml.NVML_CLOCK_GRAPHICS)),
                    memory_mhz=read('memory', lambda: nvml.nvmlDeviceGetClockInfo(handle, nvml.NVML_CLOCK_MEM)),
                    pstate=read('pstate', lambda: nvml.nvmlDeviceGetPerformanceState(handle)),
                    clocks_event_reasons=read('events', lambda: nvml.nvmlDeviceGetCurrentClocksEventReasons(handle)),
                    power_mw=read('power', lambda: nvml.nvmlDeviceGetPowerUsage(handle)),
                    temperature_c=read('temperature', lambda: nvml.nvmlDeviceGetTemperature(handle, nvml.NVML_TEMPERATURE_GPU)),
                    gpu_util_pct=None if util is None else util.gpu,
                    memory_util_pct=None if util is None else util.memory,
                    end=stamp())
                stream.write(json.dumps(record, separators=(',', ':')) + '\n')
                count += 1
                result = process.poll()
                if result is not None:
                    receipt['returncode'] = result
                    break
                deadline += args.interval_ms / 1000.0
                now = time.perf_counter()
                if deadline < now:
                    deadline = now
                time.sleep(max(0, deadline - now))
        receipt.update(complete=True, sample_count=count, finished=time.time(),
                       final_clock_calibration=[stamp() for _ in range(5)])
        save()
        return receipt['returncode']
    finally:
        if process is not None and process.poll() is None:
            process.terminate()
            process.wait(timeout=30)
        receipt.update(sample_count=count, finished=time.time())
        save()
        nvml.nvmlShutdown()


if __name__ == '__main__':
    sys.exit(main())
