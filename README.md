### Dhscanner

[![tests](https://github.com/OrenGitHub/dhscanner/actions/workflows/tests.yml/badge.svg)](https://github.com/OrenGitHub/dhscanner/actions/workflows/tests.yml)

### Cli

```bash
$ git clone --recurse-submodules https://github.com/OrenGitHub/dhscanner
$ cd dhscanner

# for fastest (release) build on x64 systems
$ docker compose -f compose.rel.x64.yaml up -d

# for fastest (release) build on ARM64 systems
$ docker compose -f compose.rel.aarch64.yaml up -d

# to experiment and customize dhscanner
$ docker compose -f compose.dev.yaml up -d
```

### GitHub action

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
