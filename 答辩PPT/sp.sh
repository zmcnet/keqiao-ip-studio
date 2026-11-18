#!/usr/bin/env bash
V="/c/Users/kybll/.workbuddy/binaries/node/versions/22.22.2-6"
export TENCENT_DOCS_LOCAL_MCP="http://localhost:39099"
PROJ="/c/Users/kybll/Desktop/AIGC/keqiao-ip-studio/答辩PPT"
PPTX="$PROJ/柯桥水乡IP造物台_答辩PPT.pptx"
cd "$PROJ"
case "$1" in
  lint)
    "$V/node.exe" "$V/lib/node_modules/@tencent/slidep/dist/index.js" lint "$PPTX" --dsl-file "slides/$2.slide" 2>/dev/null | tail -1
    ;;
  put)
    "$V/node.exe" "$V/lib/node_modules/@tencent/slidep/dist/index.js" upsert-dsl "$PPTX" --dsl-file "slides/$2.slide" 2>/dev/null | tail -1
    ;;
esac
