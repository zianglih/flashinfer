# Graph edge metadata limitation

CPU-only artifact/source audit, 2026-10-25. No additional graph capture, replay, CUDA query, or GPU work. The executed `graph_metadata.py` and raw trace files remain unchanged. This note does not repair or replace raw values.

## Confirmed result

`decode/raw/T128.json` contains invalid first-edge annotations in both arms:

|Arm|Edge|type|from_port|to_port|
|---|---|---:|---:|---:|
|control|topk → sort|16|211|159|
|publisher|topk → sort|195|45|9|

The installed CUDA 13.2 header defines dependency types 0/1, source ports 0/1/2, and requires destination port 0 (`cuda.h:2042–2095`). These records cannot describe valid edges. The helper reads fields without validation (`graph_metadata.py:106–120`); its `complete = not errors` at123 only reflects query failures. Therefore raw `complete=true` and empty `errors` do **not** establish valid metadata. Derived summaries must mark `PARTIAL_INVALID_EDGE_DATA`, exclude first-edge type/ports from interpretation, and preserve the original raw values as evidence.

The remaining four edges in each arm report `1/1/0`. Those fields are within the documented domain; this does not independently establish their correctness or prove the corruption was confined to the first record.

Both DOT files (`decode/raw/T128-{control,publisher}.dot:70–74`) confirm the same six-kernel linear topology: topk → sort → preparation → FC1 → FC2 → finalizer. Every edge has only `headlabel=0`. DOT supplies no dependency-type/source-port annotation, so it cannot recover the corrupt first edge or independently validate the other `1/1/0` annotations. Do not replace the first edge with either `0/0/0` or `1/1/0` by inference.

No material capture ownership or module-dispatch defect was found: `probe_graph.py:153–160` freezes CPU expected bytes and clears observer-held tensors;169–194 retains graph/output owners through metadata and postchecks;89–99 switches core/cache/auxiliary identities. Candidate DOT kernel names corroborate candidate dispatch. Timestamp-based overlap findings are separate evidence and do not depend on decoding these edge structs.

## Unconfirmed cause

The helper obtains native edge objects at44–46, performs several node/parameter/name queries at74–104, and only then converts edge fields to Python integers at117–119. Buffer reuse during that interval is a plausible explanation, **not a confirmed diagnosis**.

Installed `cuda/bindings/driver.pxd:1208–1209` declares both an inline `CUgraphEdgeData_st _pvt_val` and a `CUgraphEdgeData_st* _pvt_ptr`. That declaration does not establish which storage the edge-enumeration wrapper uses or its ownership. The installed distribution has no implementation `.pyx` source for inspection. Consequently, immediate integer copying before later node calls may reduce exposure but is not proven sufficient: a returned wrapper could already reference invalid storage when the API call returns. CPU stubs used before the trace tested tuple shapes/error handling, not native ownership.

## Future owner-buffer-safe approach; not executed

Use caller-owned `ctypes` arrays with the explicitly exported **`cuGraphGetEdges_v2`** driver symbol, then copy all fields to Python integers while those arrays remain alive. The installed header maps the current five-argument C name through a macro (`cuda.h:167,20954`); the raw unsuffixed `cuGraphGetEdges` symbol is the legacy four-argument API. A Python `ctypes` lookup does not apply the C macro.

```c
CUresult cuGraphGetEdges_v2(
    CUgraph graph, CUgraphNode *from, CUgraphNode *to,
    CUgraphEdgeData *edgeData, size_t *numEdges);
```

Use `c_void_p` for handles, `c_int` for the result, `POINTER(c_size_t)` for the count, and this structure:

```python
class EdgeData(ctypes.Structure):
    _fields_ = [
        ("from_port", ctypes.c_ubyte),
        ("to_port", ctypes.c_ubyte),
        ("type", ctypes.c_ubyte),
        ("reserved", ctypes.c_ubyte * 5),
    ]
```

CPU layout check passed: size8, alignment1, offsets0/1/2/3, matching `cydriver.pxd:1063–1069` and the header. `libcuda.so.1` and its `_v2` symbol were found by read-only library/symbol lookup; no driver function was invoked. First query count with null arrays, allocate both handle arrays plus `EdgeData[count]`, fill them, check the result/count, and immediately materialize their contents. Keep the Torch graph alive throughout. This avoids dependence on ownership of Cython-returned struct wrappers; it has not been validated on a live graph.

A future reader must append explicit per-edge validation errors and set `complete=false` for invalid fields: type outside {0,1}, source port outside {0,1,2}, destination port not0, nonzero reserved bytes, missing endpoints, or documented incompatible type/port/node-kind combinations. In particular type1 requires kernel endpoints and source port1 or2; port1 is associated with programmatic dependencies. Preserve raw invalid fields, do not coerce them, and do not classify API success as metadata validity. Launch-only attribute6 remains unsuitable as a required graph-node query.

## Identity receipt

|File|SHA256|
|---|---|
|executed `graph_metadata.py`|`59eb135dfe6575564b3ed935b780b8b2ad83739c982e495c6d0df457921b87fe`|
|`decode/raw/T128.json`|`2843c3e228e31362ff18766da05e4740d78869113a2f35753af4d9146c415049`|
|`decode/raw/T128-control.dot`|`c94f210810bbff859e74da753120617642347b0b2fc1137ed85d216491ff086e`|
|`decode/raw/T128-publisher.dot`|`755802708e8a752ddd3d3670b2487538a4d9476683caef2a215b9c62d1d0c90c`|
|installed `cuda/bindings/driver.pxd`|`eb417e0bcccedc3451b43c49c18aff1f5c1b60794b4c9c7527f9d770fd2a84cb`|
|installed `cuda/bindings/cydriver.pxd`|`67bc96b7f5101eec5552ad68eb4487a512b247475792ad8acbf68fd98964c88c`|
|installed `cuda.h`|`673873a292718591d75ea3c2e65330b1f8f8278eac3c96b32245418fb0817851`|

Installed package/API context and exact signatures are recorded in `GRAPH_METADATA_API.md`. No QMD timestamp interpretation was attempted: the parent confirmed all three queried QMD fields are null for both shapes/arms.
