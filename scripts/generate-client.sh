#! /usr/bin/env bash

set -e
set -x

cd backend

# OpenAPI JSON을 깔끔하게 생성하고 포맷팅
uv run python -c "
import sys
import json
import os

os.environ['LOG_LEVEL'] = 'ERROR'

import io
from contextlib import redirect_stdout, redirect_stderr

with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
    import app.main
    openapi_spec = app.main.app.openapi()

print(json.dumps(openapi_spec, indent=2, ensure_ascii=False))
" > ../frontend/src/openapi.json

cd ../frontend

# 클라이언트 생성
npm run generate-client

# 생성된 클라이언트 코드 포맷팅
npx biome format --write ./src/client
