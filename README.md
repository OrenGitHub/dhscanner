### Dhscanner

[![tests](https://github.com/OrenGitHub/dhscanner/actions/workflows/tests.yml/badge.svg)](https://github.com/OrenGitHub/dhscanner/actions/workflows/tests.yml)

### GitHub action  ( 👈 preferred and easiest way )

<details>
<summary>click here to copy the yaml file</summary>

```yaml
name: dhscanner-sast

on:
  push:
    branches:
      - main

jobs:
  run-dhscanner:
    runs-on: ubuntu-latest

    steps:
      - name: clone dhscanner (with submodules)
        run: |
          git clone --recurse-submodules https://github.com/OrenGitHub/dhscanner
          cd dhscanner
          docker compose -f compose.rel.x64.yaml up -d

      - name: checkout specific tag
        uses: actions/checkout@v4

      - name: send the whole repo to dhscanner
        run: |
          tar -cz . | curl -v -X POST \
            -H "X-Code-Sent-To-External-Server: false" \
            -H "Content-Type: application/octet-stream" \
            --data-binary @- http://127.0.0.1:443/ > output.sarif

      - name: Upload SARIF results
        uses: github/codeql-action/upload-sarif@v3
        with:
          sarif_file: output.sarif

      - name: fail workflow if sarif contains findings
        run: |
          if jq '.runs[].results | length > 0' output.sarif | grep -q 'true'; then
            echo "Sarif findings detected, failing the workflow"
            exit 1
          fi
```
</details>

### Cli [^1]

You only need docker 🐳 to install and run dhscanner !

<details>
<summary>clone the repo</summary><br>

```bash
$ git clone --recurse-submodules https://github.com/OrenGitHub/dhscanner
$ cd dhscanner
```
</details>

<details>
<summary>for fastest relase build on x64 systems</summary><br>

```bash
$ docker compose -f compose.rel.x64.yaml up -d
```  
</details>

<details>
<summary>for fastest relase build on ARM / aarch64 systems</summary><br>

```bash
$ docker compose -f compose.rel.aarch64.yaml up -d
```  
</details>

<details>
<summary>for dev builds ( all systems )</summary><br>

```bash
$ docker compose -f compose.dev.yaml up -d
```  
</details>

<details>
<summary>start scanning !</summary><br>

```bash
$ python ./cli.py --scan_dirname ../the/src/dir/to/scan --ignore_testing_code true
```  
</details>

[^1]: takes around 3 minutes on modern laptops
