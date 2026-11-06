# Installed graph metadata API receipt

CPU/read-only inspection on `fi-w4a4-narrow-1025`, C1/ziangli, 2026-10-25. Used managed `/usr/local/bin/h` after verifying `command -v h`; sourced `/workspace/flashinfer-w4a4-split-dynamic-n/scripts/recovery442/env_candidate.sh` in each remote shell. No CUDA API was invoked during inspection: only installed source/docstrings and Python handle/struct construction were read. No GPU allocation, capture, instantiation, launch, or replay was performed by this reviewer.

Installed packages: Torch `2.12.0a0+5aff3928d8.nv26.5.50603568`, cuda-bindings `13.2.0`.

## Graph ownership

`/usr/local/lib/python3.12/dist-packages/torch/cuda/graphs.py:69–86,93–94,128–135,167–179`:

- Construct with `torch.cuda.CUDAGraph(keep_graph=True)` before the caller's capture.
- After capture, `raw_cuda_graph() -> int` exposes the retained `cudaGraph_t`. Default `keep_graph=False` instantiates and destroys that original graph at capture end, so an exec handle is not a substitute.
- `instantiate()` preserves the retained graph. Call it before measured replay to exclude first-replay instantiation overhead.
- Keep the Torch owner alive during metadata inspection; the helper must not destroy its graph or modify node-owned parameter storage.

Source SHA256: `1f4cf2183a1ef1897787c0dc6d13d5afe3ab57de1dd76bb9345323fd64b742b0`.

## Exact installed driver binding signatures

|Call|Return tuple|
|---|---|
|`cuGraphGetNodes(hGraph, numNodes=0)`|`(CUresult, nodes, numNodes)`|
|`cuGraphGetEdges(hGraph, numEdges=0)`|`(CUresult, from_nodes, to_nodes, edgeData, numEdges)`|
|`cuGraphNodeGetType(hNode)`|`(CUresult, CUgraphNodeType)`|
|`cuGraphKernelNodeGetParams(hNode)`|`(CUresult, CUDA_KERNEL_NODE_PARAMS)`|
|`cuFuncGetName(hfunc)`|`(CUresult, name_bytes)`|
|`cuKernelGetName(hfunc)`|`(CUresult, name_bytes)`|
|`cuGraphKernelNodeGetAttribute(hNode, attr)`|`(CUresult, CUkernelNodeAttrValue)`|
|`cuGraphNodeGetDependencies(hNode, numDependencies=0)`|`(CUresult, dependencies, edgeData, numDependencies)`|
|`cuGraphChildGraphNodeGetGraph(hNode)`|`(CUresult, CUgraph)`|

Use two calls for enumeration: zero capacity to obtain count, then that capacity to obtain arrays. The unsuffixed13.2 `cuGraphGetEdges` already includes edge data; there is **no** Python `cuGraphGetEdges_v2` symbol. Runtime `cudaGraphGetNodes`/`cudaGraphGetEdges` expose equivalent tuples with `cudaError_t`; runtime `_v2` is likewise absent. Do not use an older edge API that discards nondefault data; lossy queries can return `CUDA_ERROR_LOSSY_QUERY`/`cudaErrorLossyQuery`.

`drv.CUgraph(raw_integer)` and `int(handle)` were verified with a null Python wrapper without CUDA calls. `CUgraphEdgeData.type/from_port/to_port` return Python integers in this install, despite the generated docstring describing them as bytes. `CUDA_KERNEL_NODE_PARAMS` exposes `func`, gridDimXYZ, blockDimXYZ, sharedMemBytes, and optional `kern`/`ctx`; the helper reads identity/geometry only, not kernel argument pointers.

Driver extension: `/usr/local/lib/python3.12/dist-packages/cuda/bindings/driver.cpython-312-x86_64-linux-gnu.so`, SHA256 `80a758631923dbdd7d81dedeb391ad8cea12d266041ccc39578d343b96dca10a`.

## PDL metadata distinction

Installed `/usr/local/cuda/include/cuda.h:2209–2219` declares `CU_LAUNCH_ATTRIBUTE_PROGRAMMATIC_STREAM_SERIALIZATION=6` **valid for launches**, unlike attributes explicitly valid for graph nodes. The shared `CUkernelNodeAttrID` enum exposes6 and its union exposes `programmaticStreamSerializationAllowed`, but that does not make a required node-attribute query valid. The helper deliberately does not query it; an `INVALID_VALUE` result would not establish that PDL was disabled.

Read edge annotations instead (`cuda.h:2042–2095`):

- Type0/default, from_port0, to_port0: full upstream completion with memory visibility.
- Type1/programmatic: supports downstream `cudaGridDependencySynchronize`; allowed between kernel nodes with from_port1 or2.
- From port1/programmatic: activated once all upstream blocks have triggered programmatic completion or terminated.
- From port2/launch order: activated once all upstream blocks began execution.
- To port must currently be0.

Header SHA256: `673873a292718591d75ea3c2e65330b1f8f8278eac3c96b32245418fb0817851`. Its current full edge declaration at20954 includes `CUgraphEdgeData*`; a legacy declaration is separately guarded near26967.

## Helper and boundary

`graph_metadata.py:inspect_graph(torchgraph)` performs only metadata queries on an already captured, retained graph. It returns JSON-safe node handles/types, kernel names/grid/block/shared bytes, and every top-level edge's type/ports. It preserves per-node query errors and marks the result incomplete; graph enumeration errors raise. Node enumeration order is not execution order. Child graph nodes are identified but not expanded; if present, their internals need separate inspection before making whole-pipeline claims.

The caller can run `metadata = inspect_graph(g)` after its capture/instantiate/debug-dump setup and serialize it with `json.dumps(metadata, indent=2)`. No PDL semantics are inferred solely from names, launch API presence, or a missing attribute. Graph dependencies describe permitted ordering; Nsight timestamps are still needed to establish actual kernel overlap or gaps. The helper received syntax/CPU-stub checks only in this audit, not a live captured-graph invocation.
