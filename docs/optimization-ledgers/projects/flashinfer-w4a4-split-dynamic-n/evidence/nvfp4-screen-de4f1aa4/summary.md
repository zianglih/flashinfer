# NVFP4 candidate de4f1aa4 screen

Single baseline/candidate pair; diagnostic screen only, not the final ABBA comparison. Same GPU0, token grid, histograms, timing method and deterministic unfused finalize. Tokens1/2 shown but excluded from retention. Candidate is not retained.

|Tokens|Baseline us|Candidate us|Before/after|
|---:|---:|---:|---:|
|1|27.439|28.992|0.946x|
|2|37.184|39.072|0.952x|
|4|52.512|57.792|0.909x|
|8|69.792|75.359|0.926x|
|16|79.200|84.367|0.939x|
|32|111.120|122.496|0.907x|
|64|143.999|157.984|0.911x|
|128|147.648|162.672|0.908x|
|256|154.928|172.000|0.901x|
|512|157.408|175.455|0.897x|
|4096|208.463|290.463|0.718x|
|8192|297.456|483.503|0.615x|
|16384|472.464|915.070|0.516x|

decode: 0.912117x.

prefill: 0.610884x.

retention: 0.817657x.
