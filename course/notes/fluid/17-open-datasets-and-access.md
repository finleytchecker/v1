# 17 - Open datasets with known answers (for the downloader)

## Plain English
To grade a Fluid model you need data where someone already knows the answer: wells that tested gas, oil or water, or synthetic models where you placed the gas yourself. This note summarises what is free, how big it is, and how to get it. Nothing has been downloaded yet. These are the specs a downloader script needs.

| id | What | Size | Licence | Access |
|---|---|---|---|---|
| force-2020-zenodo | 118 Norwegian wells, LAS, lithology labels | 170 MB | CC BY 4.0 | direct HTTPS from Zenodo record 4351156 |
| seg-2016-ml-contest | 9+2 Kansas wells, facies labels (csv) | ~1 MB | not open (contest use) | git clone seg/2016-ml-contest |
| volve | Full North Sea oil field: seismic (pre-stack, 4D), logs, models, production | ~40,000 files, ~5 TB | Equinor Open Data Licence | Databricks Marketplace + Equinor user guide (registration) |
| volve-ml-repo | Small Volve log CSVs | small | MIT code / Equinor data | git clone |
| f3-zenodo-interpretation | F3 post-stack images, horizons, masks | 1.7 GB | CC BY 4.0 | Zenodo record 1471548 |
| f3-facies-benchmark | F3 numpy volumes + labels + logs | 2.1 GB | MIT | wget zenodo.org/record/3755060/files/data.zip (md5 bc593227...) |
| poseidon-tgs | NW Australia 3D, near/mid/far/full angle stacks, velocities | ~2,900 km2 (total GB not stated) | CC BY 4.0 (SEG-Y CC BY 3.0 AU) | `aws s3 ls --no-sign-request s3://tgs-opendata-poseidon/` (us-west-2), MDIO format |
| nopims | Australian offshore logs and reports (Poseidon wells) | per well | see GA copyright | portal, no registration for public listings |
| nlog | Dutch well logs (LAS/LIS) and seismic | per well/survey | see disclaimer | NLOG data centre |
| kgs-las-archives | ~28,900 Kansas LAS files | ~9 GB in 18 ZIPs | not stated | direct HTTPS ZIPs |
| parihaka-hf | NZ 3D cube + facies labels | 582 MB | CC BY 4.0 | Hugging Face datasets |
| agl-elastic-marmousi | Elastic Marmousi2 Vp/Vs/rho + data | not stated | licence must travel with data | S3 tarball listed on SEG Wiki |
| seam-phase1-netl | SEAM Phase I elastic earth models | not stated | see record | NETL EDX |

## Which ones carry fluid answers?
- **Strong**: Volve (petrophysical Sw, production), Poseidon + NOPIMS wells (gas discovery, tested wells), NLOG (production per well).
- **Lithology only**: FORCE 2020, SEG 2016, F3 benchmark, Parihaka. They are still useful for building the lithology half of {fluid x lithology}.
- **Synthetic truth**: Marmousi2 and SEAM, plus your own Gassmann + Devito models.

## Checkable facts
- The FORCE 2020 Zenodo record's LAS zip is 169.8 MB. [source: force-2020-zenodo]
- The Poseidon survey covers about 2,900 km2 and is stored in MDIO v1 format. [source: poseidon-tgs]
- The Poseidon bucket name is tgs-opendata-poseidon, in AWS region us-west-2. [source: poseidon-tgs]
- Volve contains about 40,000 files from a field produced 2008-2016. [source: volve]
- The Equinor Open Data Licence replaced CC BY-NC-SA 4.0 for Volve from September 2020. [source: volve]
- The F3 facies benchmark data.zip is 1.1 GB with md5 bc5932279831a95c0b244fd765376d85. [source: f3-facies-benchmark]
- The Parihaka mirror cube is 782 inlines x 590 crosslines x 1006 samples at 4 ms. [source: parihaka-hf]
- NLOG well logs become public after a 5-year confidentiality period. [source: nlog]

## Sources
force-2020-zenodo, force-2020-github, seg-2016-ml-contest, volve, volve-ml-repo, agile-volve-licence-blog, f3-zenodo-interpretation, f3-facies-benchmark, poseidon-tgs, nopims, nlog, nlog-epos-petrel, kgs-las-archives, kgs-las-search, parihaka-hf, parihaka-f3-mendeley, agl-elastic-marmousi, seam-phase1-netl, seg-wiki-open-data
