#!/usr/bin/env bash
set -euo pipefail

base_url="${HINDSIGHT_URL:-http://127.0.0.1:8898}"
pointer="https://app.notion.com/p/3b3a3e33d581804aabdbd7d0d4d3fe1a"
run_tag="green-pilot:2026-08-05"

agents=(
  "inga|internet-marketing|ZB-HS-GREEN-INGA-9101"
  "suzy|internet-marketing|ZB-HS-GREEN-SUZY-9102"
  "gohzed|ghl|ZB-HS-GREEN-GOHZED-9103"
  "grogar|ghl|ZB-HS-GREEN-GROGAR-9104"
  "marsha|zedbiz-shared|ZB-HS-GREEN-MARSHA-9105"
  "maggie|zedbiz-shared|ZB-HS-GREEN-MAGGIE-9106"
  "frank|zedbiz-shared|ZB-HS-GREEN-FRANK-9107"
  "ruby|zedbiz-shared|ZB-HS-GREEN-RUBY-9108"
)

if [[ "${ROCKY_ONLY:-0}" == "1" ]]; then
  agents=("rocky|rocky-vps4-main::unknown::anonymous|ZB-HS-GREEN-ROCKY-9109")
fi

recall_check() {
  local agent="$1" bank="$2" query="$3" expected="$4" label="$5"
  local body response elapsed rank
  body="$(jq -nc --arg q "$query" --arg tag "$run_tag" --arg agent_tag "agent:$agent" \
    '{query:$q,types:["world","experience","observation"],prefer_observations:false,budget:"low",max_tokens:1200,tags:[$tag,$agent_tag],tags_match:"all_strict"}')"
  response="$(mktemp)"
  elapsed="$(curl -fsS -o "$response" -w '%{time_total}' -H 'Content-Type: application/json' -d "$body" \
    "$base_url/v1/default/banks/$bank/memories/recall")"
  rank="$(jq --arg expected "$expected" '[.results[] | ((.text // "") + " " + ((.metadata // {}) | tojson)) | contains($expected)] | to_entries | map(select(.value == true) | .key + 1) | first // 0' "$response")"
  jq -nc --arg agent "$agent" --arg bank "$bank" --arg test "$label" --arg expected "$expected" \
    --argjson rank "$rank" --arg elapsed "$elapsed" \
    '{provider:"hindsight",agent:$agent,bank:$bank,test:$test,expected:$expected,rank:$rank,elapsed_seconds:($elapsed|tonumber),pass:($rank>0)}'
  rm -f "$response"
}

for row in "${agents[@]}"; do
  IFS='|' read -r agent bank marker <<<"$row"
  exact_doc="green-exact-2026-08-05-$agent"
  source_doc="green-source-2026-08-05-$agent"
  body="$(jq -nc --arg marker "$marker" --arg pointer "$pointer" --arg exact_doc "$exact_doc" --arg source_doc "$source_doc" \
    --arg tag "$run_tag" --arg agent_tag "agent:$agent" \
    '{async:false,items:[
      {content:("Exact identifier for the Hindsight Green test is "+$marker+". Return this value verbatim when asked."),document_id:$exact_doc,update_mode:"replace",tags:[$tag,$agent_tag,"fact-type:exact"],metadata:{record_type:"exact_identifier",exact_value:$marker,source_url:$pointer}},
      {content:("The complete authoritative source URL for the Hindsight Green test is "+$pointer+". Return this complete URL verbatim when asked."),document_id:$source_doc,update_mode:"replace",tags:[$tag,$agent_tag,"fact-type:source"],metadata:{record_type:"authoritative_source",source_url:$pointer,next_action:"review monthly score"}}
    ]}')"
  curl -fsS -H 'Content-Type: application/json' -d "$body" "$base_url/v1/default/banks/$bank/memories" >/dev/null
  recall_check "$agent" "$bank" "What is the exact identifier for the Hindsight Green test?" "$marker" exact
  recall_check "$agent" "$bank" "What is the complete authoritative source URL for the Hindsight Green test?" "$pointer" source-pointer
  curl -fsS -X DELETE "$base_url/v1/default/banks/$bank/documents/$exact_doc" >/dev/null
  curl -fsS -X DELETE "$base_url/v1/default/banks/$bank/documents/$source_doc" >/dev/null
done
