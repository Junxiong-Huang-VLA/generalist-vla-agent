# CALVIN Download Notes

## Official Source

- Repo: `https://github.com/mees/calvin`
- Dataset script reference: `dataset/download_data.sh`

## Split Sizes (from HTTP headers)

- `debug`: ~1.24 GB zip
- `D`: ~165.20 GB zip
- `ABC`: ~517.17 GB zip
- `ABCD`: ~655.67 GB zip

## Resume Download

```bash
python scripts/download_calvin.py --split D --output-dir data/external/calvin
```

Re-run the same command to resume from interruption.

## Check Progress

```bash
python scripts/check_calvin_download.py ^
  --zip-path data/external/calvin/task_D_D.zip ^
  --total-bytes 177382499170
```

## Extract After Download

```bash
python scripts/download_calvin.py --split debug --output-dir data/external/calvin --extract
```
