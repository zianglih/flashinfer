# C2 container hostname resolution

The bare host-network container initially had only localhost entries in its Kubernetes-managed `/etc/hosts`. `socket.gethostname()` returned `hu-pdx-38`, and `socket.getaddrinfo()` failed. The EP4 torchrun rendezvous retried before starting worker tests.

Added `127.0.0.1 hu-pdx-38` to this container's `/etc/hosts`, then verified resolution. All distributed workers in this task are on the same node. This is environment setup only; no repository or test change. The original launcher log retains the initial resolution warnings.
