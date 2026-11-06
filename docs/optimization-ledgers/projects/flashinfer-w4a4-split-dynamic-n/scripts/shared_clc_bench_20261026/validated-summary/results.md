# Shared FC1/FC2 CLC native AUTO comparison

A: independent FC1/FC2 scheduling (720 raw tactics). B: one shared on/off flag (360 raw tactics). Both perform fresh native AUTO on the same retained kernel. Four separate processes use A–B–B–A or B–A–A–B order. The first pair performs native AUTO outside public timed work; the reverse pair replays frozen winners. Each cell uses 10 warmups and100 cold-L2 CUDA-graph CUPTI samples. Speedup is sqrt(A1*A2/(B1*B2)); values below1 are regressions. NVFP4 includes input quantization. MX inputs are prequantized. Tokens1/2 and unchanged W4A16 are excluded from retention. No TRT rerun.

| Model | Backend | Decode GM | Prefill GM | All GM | Worst | Tokens | Points D/P |
|---|---|---:|---:|---:|---:|---:|---|
| kimi-k3 | CuteDSL MXFP4x8 | 1.00241x | 0.99746x | 1.00106x | 0.97508x | 16384 | 8/8 + 3/3 |
| kimi-k3 | CuteDSL MXFP8 | 1.00019x | 1.00028x | 1.00021x | 0.99872x | 32 | 8/8 + 3/3 |
| kimi-k3 | CuteDSL PER-TOKEN | 1.00093x | 1.00233x | 1.00131x | 0.99827x | 16 | 8/8 + 3/3 |
| kimi-k3 | CuteDSL W4A4 | 0.99899x | 1.00695x | 1.00116x | 0.99728x | 16 | 8/8 + 3/3 |
| v3 | CuteDSL MXFP4x8 | 0.99653x | 0.99496x | 0.99610x | 0.98755x | 16384 | 8/8 + 3/3 |
| v3 | CuteDSL MXFP8 | 1.00104x | 1.01059x | 1.00363x | 0.98727x | 8192 | 8/8 + 3/3 |
| v3 | CuteDSL PER-TOKEN | 0.99567x | 1.00049x | 0.99698x | 0.97510x | 4 | 8/8 + 3/3 |
| v3 | CuteDSL W4A4 | 0.99565x | 0.99985x | 0.99679x | 0.98342x | 16 | 8/8 + 3/3 |
| v41-flash | CuteDSL MXFP4x8 | 0.99851x | 0.99917x | 0.99869x | 0.98309x | 4 | 8/8 + 3/3 |
| v41-flash | CuteDSL MXFP8 | 1.00137x | 1.00032x | 1.00108x | 0.99661x | 8192 | 8/8 + 3/3 |
| v41-flash | CuteDSL PER-TOKEN | 1.00079x | 0.99402x | 0.99894x | 0.98530x | 4096 | 8/8 + 3/3 |
| v41-flash | CuteDSL W4A4 | 1.00180x | 0.99042x | 0.99869x | 0.98569x | 16384 | 8/8 + 3/3 |

| Model | Backend | Tokens | A us | B us | A/B | Pair1 | Pair2 | A CLC | B CLC |
|---|---|---:|---:|---:|---:|---:|---:|---|---|
| kimi-k3 | CuteDSL MXFP8 | 1 | 12.400 | 12.384 | 1.00131x | 1.00000x | 1.00263x | [(True, True)] | [(True, True)] |
| kimi-k3 | CuteDSL MXFP4x8 | 1 | 12.224 | 12.240 | 0.99870x | 1.00000x | 0.99740x | [(True, True)] | [(True, True)] |
| kimi-k3 | CuteDSL MXFP8 | 2 | 33.656 | 35.856 | 0.93865x | 0.93604x | 0.94127x | [(True, False)] | [(True, True)] |
| kimi-k3 | CuteDSL MXFP4x8 | 2 | 28.656 | 28.496 | 1.00561x | 1.00672x | 1.00449x | [(False, True)] | [(True, True)] |
| kimi-k3 | CuteDSL MXFP8 | 4 | 82.129 | 82.113 | 1.00020x | 0.99903x | 1.00137x | [(True, True)] | [(True, True)] |
| kimi-k3 | CuteDSL MXFP4x8 | 4 | 53.264 | 52.728 | 1.01016x | 1.01152x | 1.00881x | [(True, True)] | [(True, True)] |
| kimi-k3 | CuteDSL MXFP8 | 8 | 122.217 | 122.313 | 0.99921x | 0.99725x | 1.00118x | [(True, True)] | [(True, True)] |
| kimi-k3 | CuteDSL MXFP4x8 | 8 | 78.896 | 77.992 | 1.01159x | 1.00492x | 1.01832x | [(True, True)] | [(True, True)] |
| kimi-k3 | CuteDSL MXFP8 | 16 | 184.497 | 183.841 | 1.00357x | 1.00139x | 1.00576x | [(True, True)] | [(True, True)] |
| kimi-k3 | CuteDSL MXFP4x8 | 16 | 111.337 | 111.393 | 0.99950x | 0.99627x | 1.00274x | [(True, True)] | [(True, True)] |
| kimi-k3 | CuteDSL MXFP8 | 32 | 299.563 | 299.946 | 0.99872x | 0.99851x | 0.99894x | [(True, True)] | [(True, True)] |
| kimi-k3 | CuteDSL MXFP4x8 | 32 | 170.823 | 170.993 | 0.99901x | 0.99625x | 1.00177x | [(True, True)] | [(True, True)] |
| kimi-k3 | CuteDSL MXFP8 | 64 | 412.924 | 412.779 | 1.00035x | 0.99977x | 1.00093x | [(True, True)] | [(True, True)] |
| kimi-k3 | CuteDSL MXFP4x8 | 64 | 231.168 | 231.874 | 0.99696x | 0.99399x | 0.99993x | [(True, True)] | [(True, True)] |
| kimi-k3 | CuteDSL MXFP8 | 128 | 520.908 | 520.548 | 1.00069x | 0.99994x | 1.00145x | [(True, True)] | [(True, True)] |
| kimi-k3 | CuteDSL MXFP4x8 | 128 | 290.889 | 290.698 | 1.00066x | 0.99846x | 1.00286x | [(True, True)] | [(True, True)] |
| kimi-k3 | CuteDSL MXFP8 | 256 | 578.405 | 578.508 | 0.99982x | 1.00152x | 0.99812x | [(True, True)] | [(True, True)] |
| kimi-k3 | CuteDSL MXFP4x8 | 256 | 323.979 | 323.929 | 1.00015x | 1.00174x | 0.99857x | [(True, True)] | [(True, True)] |
| kimi-k3 | CuteDSL MXFP8 | 512 | 589.125 | 589.757 | 0.99893x | 0.99913x | 0.99873x | [(True, True)] | [(True, True)] |
| kimi-k3 | CuteDSL MXFP4x8 | 512 | 338.387 | 337.922 | 1.00137x | 1.00161x | 1.00114x | [(False, False)] | [(False, False)] |
| kimi-k3 | CuteDSL MXFP8 | 4096 | 651.174 | 650.326 | 1.00130x | 1.00286x | 0.99975x | [(False, False)] | [(False, False)] |
| kimi-k3 | CuteDSL MXFP4x8 | 4096 | 398.243 | 397.763 | 1.00121x | 1.00257x | 0.99984x | [(False, False)] | [(False, False)] |
| kimi-k3 | CuteDSL MXFP8 | 8192 | 766.247 | 766.721 | 0.99938x | 0.99645x | 1.00233x | [(False, False)] | [(False, False)] |
| kimi-k3 | CuteDSL MXFP4x8 | 8192 | 594.718 | 585.049 | 1.01653x | 1.00142x | 1.03186x | [(False, False)] | [(False, False)] |
| kimi-k3 | CuteDSL MXFP8 | 16384 | 1320.026 | 1319.833 | 1.00015x | 0.97299x | 1.02806x | [(False, False)] | [(False, False)] |
| kimi-k3 | CuteDSL MXFP4x8 | 16384 | 1098.355 | 1126.422 | 0.97508x | 1.03292x | 0.92049x | [(False, False)] | [(False, False)] |
| kimi-k3 | CuteDSL W4A4 | 1 | 12.624 | 13.696 | 0.92172x | 0.92308x | 0.92037x | [(False, True)] | [(True, True)] |
| kimi-k3 | CuteDSL PER-TOKEN | 1 | 16.112 | 14.432 | 1.11644x | 1.10911x | 1.12382x | [(True, True)] | [(False, False)] |
| kimi-k3 | CuteDSL W4A16 | 1 | 12.800 | 12.840 | 0.99685x | 0.99750x | 0.99620x | [] | [] |
| kimi-k3 | CuteDSL W4A4 | 2 | 28.736 | 28.728 | 1.00030x | 0.99669x | 1.00392x | [(True, True)] | [(True, True)] |
| kimi-k3 | CuteDSL PER-TOKEN | 2 | 31.448 | 30.561 | 1.02902x | 1.03082x | 1.02722x | [(True, True)] | [(True, True)] |
| kimi-k3 | CuteDSL W4A16 | 2 | 30.801 | 30.832 | 0.99898x | 1.00053x | 0.99742x | [] | [] |
| kimi-k3 | CuteDSL W4A4 | 4 | 54.304 | 54.328 | 0.99955x | 1.00205x | 0.99705x | [(True, True)] | [(True, True)] |
| kimi-k3 | CuteDSL PER-TOKEN | 4 | 57.400 | 57.384 | 1.00028x | 0.99889x | 1.00168x | [(True, True)] | [(True, True)] |
| kimi-k3 | CuteDSL W4A16 | 4 | 60.752 | 59.704 | 1.01755x | 1.02115x | 1.01396x | [] | [] |
| kimi-k3 | CuteDSL W4A4 | 8 | 81.568 | 81.321 | 1.00304x | 0.99961x | 1.00649x | [(True, True)] | [(True, True)] |
| kimi-k3 | CuteDSL PER-TOKEN | 8 | 85.712 | 85.440 | 1.00319x | 1.00244x | 1.00394x | [(True, True)] | [(True, True)] |
| kimi-k3 | CuteDSL W4A16 | 8 | 85.289 | 85.032 | 1.00302x | 1.00605x | 1.00001x | [] | [] |
| kimi-k3 | CuteDSL W4A4 | 16 | 114.944 | 115.257 | 0.99728x | 0.99265x | 1.00194x | [(True, True)] | [(True, True)] |
| kimi-k3 | CuteDSL PER-TOKEN | 16 | 120.353 | 120.561 | 0.99827x | 0.99536x | 1.00119x | [(True, True)] | [(True, True)] |
| kimi-k3 | CuteDSL W4A16 | 16 | 122.057 | 120.839 | 1.01008x | 1.01345x | 1.00672x | [] | [] |
| kimi-k3 | CuteDSL W4A4 | 32 | 176.318 | 176.729 | 0.99767x | 0.98916x | 1.00626x | [(True, True)] | [(True, True)] |
| kimi-k3 | CuteDSL PER-TOKEN | 32 | 182.832 | 182.609 | 1.00122x | 1.00632x | 0.99615x | [(True, True)] | [(True, True)] |
| kimi-k3 | CuteDSL W4A16 | 32 | 187.288 | 186.272 | 1.00546x | 0.99726x | 1.01372x | [] | [] |
| kimi-k3 | CuteDSL W4A4 | 64 | 238.241 | 238.482 | 0.99899x | 0.99684x | 1.00114x | [(True, True)] | [(True, True)] |
| kimi-k3 | CuteDSL PER-TOKEN | 64 | 246.953 | 246.786 | 1.00068x | 1.00565x | 0.99573x | [(True, True)] | [(True, True)] |
| kimi-k3 | CuteDSL W4A16 | 64 | 252.809 | 252.866 | 0.99977x | 0.99444x | 1.00513x | [] | [] |
| kimi-k3 | CuteDSL W4A4 | 128 | 296.250 | 296.794 | 0.99817x | 0.99650x | 0.99984x | [(True, True)] | [(True, True)] |
| kimi-k3 | CuteDSL PER-TOKEN | 128 | 307.721 | 307.347 | 1.00122x | 1.00610x | 0.99636x | [(True, True)] | [(True, True)] |
| kimi-k3 | CuteDSL W4A16 | 128 | 315.233 | 316.387 | 0.99635x | 0.99257x | 1.00015x | [] | [] |
| kimi-k3 | CuteDSL W4A4 | 256 | 330.434 | 330.834 | 0.99879x | 0.99918x | 0.99841x | [(True, True)] | [(True, True)] |
| kimi-k3 | CuteDSL PER-TOKEN | 256 | 339.844 | 339.499 | 1.00102x | 0.99996x | 1.00208x | [(True, True)] | [(True, True)] |
| kimi-k3 | CuteDSL W4A16 | 256 | 357.875 | 355.771 | 1.00591x | 1.00620x | 1.00563x | [] | [] |
| kimi-k3 | CuteDSL W4A4 | 512 | 338.571 | 339.091 | 0.99847x | 1.00033x | 0.99661x | [(True, True)] | [(True, True)] |
| kimi-k3 | CuteDSL PER-TOKEN | 512 | 363.954 | 363.386 | 1.00156x | 1.00229x | 1.00083x | [(False, False)] | [(False, False)] |
| kimi-k3 | CuteDSL W4A16 | 512 | 374.147 | 374.196 | 0.99987x | 0.99957x | 1.00017x | [] | [] |
| kimi-k3 | CuteDSL W4A4 | 4096 | 386.755 | 387.443 | 0.99822x | 0.99868x | 0.99777x | [(False, False)] | [(False, False)] |
| kimi-k3 | CuteDSL PER-TOKEN | 4096 | 446.500 | 446.211 | 1.00065x | 0.99814x | 1.00316x | [(False, False)] | [(False, False)] |
| kimi-k3 | CuteDSL W4A16 | 4096 | 660.706 | 618.541 | 1.06817x | 1.06998x | 1.06636x | [] | [] |
| kimi-k3 | CuteDSL W4A4 | 8192 | 499.996 | 501.213 | 0.99757x | 0.99623x | 0.99891x | [(False, False)] | [(False, False)] |
| kimi-k3 | CuteDSL PER-TOKEN | 8192 | 651.453 | 650.302 | 1.00177x | 1.00379x | 0.99975x | [(False, False)] | [(False, False)] |
| kimi-k3 | CuteDSL W4A16 | 8192 | 1221.555 | 1231.486 | 0.99194x | 1.00193x | 0.98204x | [] | [] |
| kimi-k3 | CuteDSL W4A4 | 16384 | 819.606 | 799.376 | 1.02531x | 1.03256x | 1.01811x | [(False, False)] | [(False, False)] |
| kimi-k3 | CuteDSL PER-TOKEN | 16384 | 1098.939 | 1093.944 | 1.00457x | 0.99160x | 1.01770x | [(False, False)] | [(False, False)] |
| kimi-k3 | CuteDSL W4A16 | 16384 | 2092.073 | 2206.106 | 0.94831x | 0.95041x | 0.94621x | [] | [] |
| v3 | CuteDSL MXFP8 | 1 | 35.112 | 33.528 | 1.04724x | 1.04826x | 1.04623x | [(False, True)] | [(False, False)] |
| v3 | CuteDSL MXFP4x8 | 1 | 29.352 | 28.144 | 1.04292x | 1.04447x | 1.04138x | [(False, True)] | [(False, False)] |
| v3 | CuteDSL MXFP8 | 2 | 46.648 | 46.640 | 1.00017x | 1.00206x | 0.99829x | [(True, True)] | [(True, True)] |
| v3 | CuteDSL MXFP4x8 | 2 | 33.968 | 34.296 | 0.99044x | 0.98975x | 0.99113x | [(False, True)] | [(True, True)] |
| v3 | CuteDSL MXFP8 | 4 | 68.657 | 68.720 | 0.99908x | 0.99954x | 0.99861x | [(False, True)] | [(True, True)] |
| v3 | CuteDSL MXFP4x8 | 4 | 47.040 | 47.168 | 0.99729x | 0.99999x | 0.99459x | [(False, True)] | [(True, True)] |
| v3 | CuteDSL MXFP8 | 8 | 93.072 | 92.960 | 1.00121x | 1.00345x | 0.99896x | [(True, True)] | [(True, True)] |
| v3 | CuteDSL MXFP4x8 | 8 | 60.592 | 61.136 | 0.99111x | 0.98541x | 0.99685x | [(False, True)] | [(True, True)] |
| v3 | CuteDSL MXFP8 | 16 | 111.616 | 111.601 | 1.00014x | 1.00000x | 1.00028x | [(True, True)] | [(True, True)] |
| v3 | CuteDSL MXFP4x8 | 16 | 68.553 | 68.784 | 0.99663x | 0.99629x | 0.99698x | [(False, True)] | [(True, True)] |
| v3 | CuteDSL MXFP8 | 32 | 165.993 | 165.896 | 1.00058x | 1.00029x | 1.00088x | [(True, True)] | [(True, True)] |
| v3 | CuteDSL MXFP4x8 | 32 | 100.249 | 100.472 | 0.99778x | 0.99778x | 0.99777x | [(True, True)] | [(True, True)] |
| v3 | CuteDSL MXFP8 | 64 | 222.218 | 221.273 | 1.00427x | 1.00152x | 1.00702x | [(False, True)] | [(True, True)] |
| v3 | CuteDSL MXFP4x8 | 64 | 131.905 | 131.001 | 1.00690x | 1.00499x | 1.00882x | [(False, True)] | [(True, True)] |
| v3 | CuteDSL MXFP8 | 128 | 226.545 | 226.858 | 0.99862x | 0.99823x | 0.99901x | [(True, True)] | [(True, True)] |
| v3 | CuteDSL MXFP4x8 | 128 | 135.001 | 135.889 | 0.99346x | 0.99282x | 0.99411x | [(False, True)] | [(True, True)] |
| v3 | CuteDSL MXFP8 | 256 | 244.473 | 243.290 | 1.00486x | 1.00935x | 1.00040x | [(False, True)] | [(True, True)] |
| v3 | CuteDSL MXFP4x8 | 256 | 143.457 | 145.217 | 0.98788x | 0.98581x | 0.98996x | [(False, True)] | [(False, False)] |
| v3 | CuteDSL MXFP8 | 512 | 246.226 | 246.338 | 0.99955x | 1.00026x | 0.99883x | [(False, True)] | [(True, True)] |
| v3 | CuteDSL MXFP4x8 | 512 | 146.961 | 146.769 | 1.00131x | 1.00317x | 0.99946x | [(False, False)] | [(False, False)] |
| v3 | CuteDSL MXFP8 | 4096 | 305.562 | 304.859 | 1.00231x | 1.00430x | 1.00031x | [(False, False)] | [(True, True)] |
| v3 | CuteDSL MXFP4x8 | 4096 | 225.545 | 225.361 | 1.00082x | 1.00369x | 0.99795x | [(True, False)] | [(False, False)] |
| v3 | CuteDSL MXFP8 | 8192 | 440.268 | 445.947 | 0.98727x | 0.98972x | 0.98482x | [(True, False)] | [(False, False)] |
| v3 | CuteDSL MXFP4x8 | 8192 | 375.641 | 376.939 | 0.99656x | 0.99123x | 1.00191x | [(False, False)] | [(False, False)] |
| v3 | CuteDSL MXFP8 | 16384 | 778.702 | 746.590 | 1.04301x | 1.05361x | 1.03252x | [(False, False)] | [(False, False)] |
| v3 | CuteDSL MXFP4x8 | 16384 | 684.625 | 693.254 | 0.98755x | 0.96559x | 1.01002x | [(True, False)] | [(False, False)] |
| v3 | CuteDSL W4A4 | 1 | 28.360 | 28.984 | 0.97846x | 0.98121x | 0.97572x | [(False, True)] | [(True, True)] |
| v3 | CuteDSL PER-TOKEN | 1 | 32.976 | 30.784 | 1.07121x | 1.07330x | 1.06913x | [(False, True)] | [(False, False)] |
| v3 | CuteDSL W4A16 | 1 | 34.336 | 35.160 | 0.97657x | 0.97635x | 0.97680x | [] | [] |
| v3 | CuteDSL W4A4 | 2 | 34.327 | 35.392 | 0.96990x | 0.97964x | 0.96025x | [(False, True)] | [(True, True)] |
| v3 | CuteDSL PER-TOKEN | 2 | 38.328 | 38.120 | 1.00544x | 1.00924x | 1.00167x | [(False, False)] | [(False, False)] |
| v3 | CuteDSL W4A16 | 2 | 40.128 | 39.968 | 1.00400x | 1.00480x | 1.00321x | [] | [] |
| v3 | CuteDSL W4A4 | 4 | 47.040 | 47.568 | 0.98889x | 0.98923x | 0.98855x | [(False, True)] | [(True, True)] |
| v3 | CuteDSL PER-TOKEN | 4 | 50.440 | 51.728 | 0.97510x | 0.97196x | 0.97826x | [(False, True)] | [(True, True)] |
| v3 | CuteDSL W4A16 | 4 | 55.072 | 55.368 | 0.99466x | 0.99682x | 0.99249x | [] | [] |
| v3 | CuteDSL W4A4 | 8 | 61.048 | 61.016 | 1.00053x | 1.00079x | 1.00026x | [(True, True)] | [(True, True)] |
| v3 | CuteDSL PER-TOKEN | 8 | 65.416 | 64.833 | 1.00900x | 1.00742x | 1.01058x | [(True, True)] | [(True, True)] |
| v3 | CuteDSL W4A16 | 8 | 69.552 | 71.000 | 0.97961x | 0.98076x | 0.97847x | [] | [] |
| v3 | CuteDSL W4A4 | 16 | 69.304 | 70.472 | 0.98342x | 0.98319x | 0.98366x | [(False, True)] | [(True, True)] |
| v3 | CuteDSL PER-TOKEN | 16 | 74.336 | 75.009 | 0.99104x | 0.98978x | 0.99229x | [(False, True)] | [(True, True)] |
| v3 | CuteDSL W4A16 | 16 | 77.424 | 76.977 | 1.00581x | 1.00289x | 1.00874x | [] | [] |
| v3 | CuteDSL W4A4 | 32 | 101.784 | 101.672 | 1.00110x | 1.00205x | 1.00015x | [(True, True)] | [(True, True)] |
| v3 | CuteDSL PER-TOKEN | 32 | 105.393 | 106.000 | 0.99427x | 0.99486x | 0.99368x | [(False, True)] | [(True, True)] |
| v3 | CuteDSL W4A16 | 32 | 110.001 | 110.560 | 0.99494x | 0.99696x | 0.99293x | [] | [] |
| v3 | CuteDSL W4A4 | 64 | 132.073 | 132.113 | 0.99970x | 1.00327x | 0.99613x | [(False, True)] | [(True, True)] |
| v3 | CuteDSL PER-TOKEN | 64 | 136.017 | 136.193 | 0.99871x | 0.99637x | 1.00106x | [(True, True)] | [(True, True)] |
| v3 | CuteDSL W4A16 | 64 | 145.937 | 146.577 | 0.99564x | 0.99618x | 0.99509x | [] | [] |
| v3 | CuteDSL W4A4 | 128 | 138.225 | 138.265 | 0.99971x | 0.99896x | 1.00047x | [(True, True)] | [(True, True)] |
| v3 | CuteDSL PER-TOKEN | 128 | 142.289 | 143.041 | 0.99474x | 0.99328x | 0.99620x | [(True, True)] | [(True, True)] |
| v3 | CuteDSL W4A16 | 128 | 148.585 | 147.937 | 1.00438x | 1.00552x | 1.00324x | [] | [] |
| v3 | CuteDSL W4A4 | 256 | 147.705 | 148.649 | 0.99365x | 0.99536x | 0.99194x | [(True, True)] | [(True, True)] |
| v3 | CuteDSL PER-TOKEN | 256 | 154.601 | 154.681 | 0.99948x | 1.00166x | 0.99731x | [(True, True)] | [(True, True)] |
| v3 | CuteDSL W4A16 | 256 | 155.353 | 155.666 | 0.99799x | 0.99804x | 0.99794x | [] | [] |
| v3 | CuteDSL W4A4 | 512 | 151.825 | 152.081 | 0.99832x | 0.99801x | 0.99863x | [(False, True)] | [(True, True)] |
| v3 | CuteDSL PER-TOKEN | 512 | 160.617 | 160.073 | 1.00340x | 1.00100x | 1.00580x | [(True, True)] | [(False, False)] |
| v3 | CuteDSL W4A16 | 512 | 160.025 | 160.241 | 0.99865x | 1.00070x | 0.99660x | [] | [] |
| v3 | CuteDSL W4A4 | 4096 | 207.121 | 207.226 | 0.99950x | 0.99930x | 0.99969x | [(False, False)] | [(False, False)] |
| v3 | CuteDSL PER-TOKEN | 4096 | 251.490 | 252.065 | 0.99772x | 0.99937x | 0.99607x | [(True, False)] | [(False, False)] |
| v3 | CuteDSL W4A16 | 4096 | 311.249 | 310.754 | 1.00159x | 1.00052x | 1.00267x | [] | [] |
| v3 | CuteDSL W4A4 | 8192 | 325.618 | 325.682 | 0.99980x | 1.00123x | 0.99838x | [(False, False)] | [(False, False)] |
| v3 | CuteDSL PER-TOKEN | 8192 | 382.235 | 381.907 | 1.00086x | 1.00054x | 1.00117x | [(False, False)] | [(False, False)] |
| v3 | CuteDSL W4A16 | 8192 | 589.324 | 595.059 | 0.99036x | 0.98750x | 0.99324x | [] | [] |
| v3 | CuteDSL W4A4 | 16384 | 525.836 | 525.706 | 1.00025x | 1.00177x | 0.99873x | [(False, False)] | [(False, False)] |
| v3 | CuteDSL PER-TOKEN | 16384 | 675.793 | 673.843 | 1.00289x | 1.00386x | 1.00193x | [(False, False)] | [(False, False)] |
| v3 | CuteDSL W4A16 | 16384 | 1202.627 | 1188.050 | 1.01227x | 1.00093x | 1.02374x | [] | [] |
| v41-flash | CuteDSL MXFP8 | 1 | 10.640 | 10.000 | 1.06399x | 1.05733x | 1.07069x | [(False, True)] | [(False, False)] |
| v41-flash | CuteDSL MXFP4x8 | 1 | 10.632 | 10.095 | 1.05319x | 1.05929x | 1.04712x | [(True, True)] | [(False, False)] |
| v41-flash | CuteDSL MXFP8 | 2 | 23.520 | 23.568 | 0.99796x | 0.99461x | 1.00133x | [(False, False)] | [(True, True)] |
| v41-flash | CuteDSL MXFP4x8 | 2 | 21.456 | 21.800 | 0.98420x | 0.98240x | 0.98599x | [(False, True)] | [(True, True)] |
| v41-flash | CuteDSL MXFP8 | 4 | 51.008 | 50.656 | 1.00694x | 1.00631x | 1.00758x | [(True, True)] | [(True, True)] |
| v41-flash | CuteDSL MXFP4x8 | 4 | 35.329 | 35.936 | 0.98309x | 0.98575x | 0.98044x | [(False, True)] | [(False, False)] |
| v41-flash | CuteDSL MXFP8 | 8 | 73.520 | 73.449 | 1.00097x | 1.00043x | 1.00152x | [(True, True)] | [(True, True)] |
| v41-flash | CuteDSL MXFP4x8 | 8 | 47.544 | 47.609 | 0.99864x | 0.99629x | 1.00100x | [(True, True)] | [(True, True)] |
| v41-flash | CuteDSL MXFP8 | 16 | 103.129 | 103.057 | 1.00070x | 1.00185x | 0.99954x | [(True, True)] | [(True, True)] |
| v41-flash | CuteDSL MXFP4x8 | 16 | 64.337 | 63.777 | 1.00878x | 1.00703x | 1.01053x | [(True, True)] | [(True, True)] |
| v41-flash | CuteDSL MXFP8 | 32 | 213.346 | 213.090 | 1.00120x | 1.00000x | 1.00241x | [(True, True)] | [(True, True)] |
| v41-flash | CuteDSL MXFP4x8 | 32 | 122.248 | 122.641 | 0.99679x | 0.99935x | 0.99425x | [(True, True)] | [(True, True)] |
| v41-flash | CuteDSL MXFP8 | 64 | 352.387 | 351.931 | 1.00130x | 1.00055x | 1.00205x | [(True, True)] | [(True, True)] |
| v41-flash | CuteDSL MXFP4x8 | 64 | 195.752 | 196.649 | 0.99544x | 0.99862x | 0.99227x | [(True, True)] | [(True, True)] |
| v41-flash | CuteDSL MXFP8 | 128 | 462.771 | 463.243 | 0.99898x | 0.99893x | 0.99903x | [(True, True)] | [(True, True)] |
| v41-flash | CuteDSL MXFP4x8 | 128 | 255.794 | 255.097 | 1.00273x | 1.00309x | 1.00238x | [(True, True)] | [(True, True)] |
| v41-flash | CuteDSL MXFP8 | 256 | 530.884 | 530.268 | 1.00116x | 1.00169x | 1.00063x | [(True, True)] | [(True, True)] |
| v41-flash | CuteDSL MXFP4x8 | 256 | 294.354 | 293.970 | 1.00131x | 1.00310x | 0.99951x | [(True, True)] | [(True, True)] |
| v41-flash | CuteDSL MXFP8 | 512 | 536.060 | 536.228 | 0.99969x | 0.99863x | 1.00075x | [(True, True)] | [(True, True)] |
| v41-flash | CuteDSL MXFP4x8 | 512 | 299.962 | 299.506 | 1.00152x | 1.00176x | 1.00129x | [(True, True)] | [(True, True)] |
| v41-flash | CuteDSL MXFP8 | 4096 | 586.933 | 585.932 | 1.00171x | 1.00246x | 1.00096x | [(True, False)] | [(True, True)] |
| v41-flash | CuteDSL MXFP4x8 | 4096 | 355.209 | 357.226 | 0.99435x | 0.99211x | 0.99660x | [(True, False)] | [(False, False)] |
| v41-flash | CuteDSL MXFP8 | 8192 | 670.485 | 672.767 | 0.99661x | 0.99678x | 0.99644x | [(True, False)] | [(True, True)] |
| v41-flash | CuteDSL MXFP4x8 | 8192 | 493.172 | 495.476 | 0.99535x | 0.99384x | 0.99686x | [(True, False)] | [(False, False)] |
| v41-flash | CuteDSL MXFP8 | 16384 | 996.911 | 994.268 | 1.00266x | 1.01045x | 0.99493x | [(True, False)] | [(True, True)] |
| v41-flash | CuteDSL MXFP4x8 | 16384 | 883.574 | 876.687 | 1.00786x | 0.99917x | 1.01662x | [(False, False)] | [(False, False)] |
| v41-flash | CuteDSL W4A4 | 1 | 10.984 | 10.032 | 1.09487x | 1.09420x | 1.09554x | [(False, True)] | [(False, False)] |
| v41-flash | CuteDSL PER-TOKEN | 1 | 13.776 | 13.408 | 1.02745x | 1.02396x | 1.03095x | [(False, True)] | [(False, False)] |
| v41-flash | CuteDSL W4A16 | 1 | 10.400 | 10.688 | 0.97305x | 0.97313x | 0.97297x | [] | [] |
| v41-flash | CuteDSL W4A4 | 2 | 20.616 | 21.232 | 0.97097x | 0.96616x | 0.97580x | [(False, True)] | [(True, True)] |
| v41-flash | CuteDSL PER-TOKEN | 2 | 23.552 | 24.001 | 0.98129x | 0.98132x | 0.98127x | [(False, True)] | [(False, False)] |
| v41-flash | CuteDSL W4A16 | 2 | 24.168 | 24.392 | 0.99082x | 0.98952x | 0.99212x | [] | [] |
| v41-flash | CuteDSL W4A4 | 4 | 35.288 | 35.584 | 0.99169x | 0.99369x | 0.98969x | [(True, True)] | [(True, True)] |
| v41-flash | CuteDSL PER-TOKEN | 4 | 39.376 | 39.424 | 0.99878x | 0.99919x | 0.99838x | [(False, False)] | [(False, False)] |
| v41-flash | CuteDSL W4A16 | 4 | 41.824 | 41.808 | 1.00037x | 0.99808x | 1.00267x | [] | [] |
| v41-flash | CuteDSL W4A4 | 8 | 46.904 | 46.584 | 1.00688x | 1.00965x | 1.00413x | [(True, True)] | [(True, True)] |
| v41-flash | CuteDSL PER-TOKEN | 8 | 52.320 | 52.328 | 0.99984x | 1.00213x | 0.99755x | [(True, True)] | [(True, True)] |
| v41-flash | CuteDSL W4A16 | 8 | 55.008 | 55.769 | 0.98637x | 0.98538x | 0.98736x | [] | [] |
| v41-flash | CuteDSL W4A4 | 16 | 65.328 | 65.400 | 0.99891x | 1.00025x | 0.99756x | [(True, True)] | [(True, True)] |
| v41-flash | CuteDSL PER-TOKEN | 16 | 70.032 | 70.008 | 1.00034x | 0.99931x | 1.00137x | [(True, True)] | [(True, True)] |
| v41-flash | CuteDSL W4A16 | 16 | 71.641 | 71.736 | 0.99867x | 0.99933x | 0.99800x | [] | [] |
| v41-flash | CuteDSL W4A4 | 32 | 127.345 | 126.176 | 1.00926x | 1.01310x | 1.00544x | [(True, True)] | [(True, True)] |
| v41-flash | CuteDSL PER-TOKEN | 32 | 132.568 | 131.696 | 1.00663x | 1.01060x | 1.00266x | [(True, True)] | [(True, True)] |
| v41-flash | CuteDSL W4A16 | 32 | 136.160 | 135.656 | 1.00371x | 1.00721x | 1.00023x | [] | [] |
| v41-flash | CuteDSL W4A4 | 64 | 204.625 | 203.753 | 1.00428x | 1.00614x | 1.00243x | [(True, True)] | [(True, True)] |
| v41-flash | CuteDSL PER-TOKEN | 64 | 210.473 | 209.929 | 1.00259x | 1.00451x | 1.00068x | [(True, True)] | [(True, True)] |
| v41-flash | CuteDSL W4A16 | 64 | 218.521 | 216.537 | 1.00916x | 1.01028x | 1.00804x | [] | [] |
| v41-flash | CuteDSL W4A4 | 128 | 263.337 | 262.793 | 1.00207x | 1.00201x | 1.00213x | [(True, True)] | [(True, True)] |
| v41-flash | CuteDSL PER-TOKEN | 128 | 271.658 | 272.257 | 0.99780x | 0.99665x | 0.99895x | [(True, True)] | [(True, True)] |
| v41-flash | CuteDSL W4A16 | 128 | 281.065 | 279.137 | 1.00691x | 1.00545x | 1.00836x | [] | [] |
| v41-flash | CuteDSL W4A4 | 256 | 303.354 | 303.458 | 0.99966x | 1.00106x | 0.99826x | [(True, True)] | [(True, True)] |
| v41-flash | CuteDSL PER-TOKEN | 256 | 313.034 | 314.201 | 0.99629x | 0.99639x | 0.99618x | [(True, True)] | [(True, True)] |
| v41-flash | CuteDSL W4A16 | 256 | 317.818 | 317.962 | 0.99955x | 1.00055x | 0.99854x | [] | [] |
| v41-flash | CuteDSL W4A4 | 512 | 306.874 | 306.330 | 1.00178x | 1.00136x | 1.00219x | [(True, True)] | [(True, True)] |
| v41-flash | CuteDSL PER-TOKEN | 512 | 324.026 | 322.714 | 1.00407x | 1.00382x | 1.00431x | [(True, False)] | [(True, True)] |
| v41-flash | CuteDSL W4A16 | 512 | 323.002 | 322.873 | 1.00040x | 1.00159x | 0.99921x | [] | [] |
| v41-flash | CuteDSL W4A4 | 4096 | 348.370 | 351.410 | 0.99135x | 0.99081x | 0.99189x | [(True, False)] | [(True, True)] |
| v41-flash | CuteDSL PER-TOKEN | 4096 | 401.594 | 407.586 | 0.98530x | 0.98427x | 0.98632x | [(True, False)] | [(True, True)] |
| v41-flash | CuteDSL W4A16 | 4096 | 567.701 | 568.447 | 0.99869x | 1.00386x | 0.99354x | [] | [] |
| v41-flash | CuteDSL W4A4 | 8192 | 420.570 | 423.002 | 0.99425x | 0.99466x | 0.99383x | [(True, False)] | [(False, False)] |
| v41-flash | CuteDSL PER-TOKEN | 8192 | 514.394 | 517.244 | 0.99449x | 0.99570x | 0.99328x | [(True, False)] | [(True, True)] |
| v41-flash | CuteDSL W4A16 | 8192 | 885.576 | 888.539 | 0.99666x | 0.97458x | 1.01925x | [] | [] |
| v41-flash | CuteDSL W4A4 | 16384 | 651.542 | 661.004 | 0.98569x | 0.98521x | 0.98616x | [(False, False)] | [(False, False)] |
| v41-flash | CuteDSL PER-TOKEN | 16384 | 807.026 | 805.144 | 1.00234x | 1.00834x | 0.99637x | [(False, False)] | [(False, False)] |
| v41-flash | CuteDSL W4A16 | 16384 | 1566.121 | 1642.431 | 0.95354x | 0.95288x | 0.95419x | [] | [] |

Search wall times include compilation, native profiling, IO, and shared CPU contention. Persistent native artifacts are reused. Treat them as observed campaign cost, not an isolated compiler speedup.

| Model | Family | Arm | Process seconds | Pre-warm context seconds | Admission calls | Admitted counts |
|---|---|---|---:|---:|---:|---|
| kimi-k3 | mxfp | A | 928.6 | 906.6 | 44 | {'mxfp8': [640], 'w4a8': [640]} |
| kimi-k3 | mxfp | B | 622.3 | 599.7 | 44 | {'mxfp8': [320], 'w4a8': [320]} |
| kimi-k3 | nvfp4 | A | 693.6 | 664.1 | 44 | {'w4a4': [640], 'w4a4-per-token': [640]} |
| kimi-k3 | nvfp4 | B | 462.4 | 436.4 | 44 | {'w4a4': [320], 'w4a4-per-token': [320]} |
| v3 | mxfp | A | 732.1 | 714.3 | 44 | {'mxfp8': [640], 'w4a8': [640]} |
| v3 | mxfp | B | 432.1 | 414.1 | 44 | {'mxfp8': [320], 'w4a8': [320]} |
| v3 | nvfp4 | A | 594.8 | 571.1 | 44 | {'w4a4': [640], 'w4a4-per-token': [640]} |
| v3 | nvfp4 | B | 453.5 | 436.9 | 44 | {'w4a4': [320], 'w4a4-per-token': [320]} |
| v41-flash | mxfp | A | 756.0 | 737.1 | 44 | {'mxfp8': [640], 'w4a8': [640]} |
| v41-flash | mxfp | B | 546.7 | 527.1 | 44 | {'mxfp8': [320], 'w4a8': [320]} |
| v41-flash | nvfp4 | A | 711.1 | 684.2 | 44 | {'w4a4': [640], 'w4a4-per-token': [640]} |
| v41-flash | nvfp4 | B | 439.7 | 419.2 | 44 | {'w4a4': [320], 'w4a4-per-token': [320]} |
