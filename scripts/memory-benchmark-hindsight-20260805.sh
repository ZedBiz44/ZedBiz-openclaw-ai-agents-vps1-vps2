#!/usr/bin/env bash
set -euo pipefail

base_url="${HINDSIGHT_URL:-http://127.0.0.1:8898}"
run_id="2026-08-05"
pointer="https://app.notion.com/p/3b3a3e33d581804aabdbd7d0d4d3fe1a"

agents=(
  "inga|internet-marketing|ZB-HS-AUG05-INGA-1101|crimson|Aurora"
  "suzy|internet-marketing|ZB-HS-AUG05-SUZY-1102|teal|Aspen"
  "gohzed|ghl|ZB-HS-AUG05-GOHZED-1103|navy|Canyon"
  "grogar|ghl|ZB-HS-AUG05-GROGAR-1104|gold|Prairie"
  "marsha|zedbiz-shared|ZB-HS-AUG05-MARSHA-1105|violet|Summit"
  "maggie|zedbiz-shared|ZB-HS-AUG05-MAGGIE-1106|copper|Foothills"
  "frank|zedbiz-shared|ZB-HS-AUG05-FRANK-1107|charcoal|Badlands"
  "ruby|zedbiz-shared|ZB-HS-AUG05-RUBY-1108|silver|Glacier"
)

if [[ "${ROCKY_ONLY:-0}" == "1" ]]; then
  agents=(
    "rocky|rocky-vps4-main::unknown::anonymous|ZB-HS-AUG05-ROCKY-1109|emerald|Mountain"
  )
fi

recall() {
  local agent="$1" bank="$2" query="$3" expected="$4" label="$5"
  local body response elapsed rank count
  body="$(jq -nc \
    --arg q "$query" \
    --arg a "agent:${agent}" \
    '{query:$q,types:["world","experience","observation"],prefer_observations:true,budget:"low",max_tokens:1600,tags:["benchmark:2026-08",$a],tags_match:"all_strict"}')"
  response="$(mktemp)"
  elapsed="$(curl -fsS -o "$response" -w '%{time_total}' \
    -H 'Content-Type: application/json' \
    -d "$body" \
    "$base_url/v1/default/banks/$bank/memories/recall")"
  count="$(jq '.results | length' "$response")"
  rank="$(jq --arg e "$expected" '[.results[].text | ascii_downcase | contains($e|ascii_downcase)] | to_entries | map(select(.value == true) | .key + 1) | first // 0' "$response")"
  jq -nc \
    --arg provider hindsight --arg agent "$agent" --arg bank "$bank" \
    --arg phase recall --arg test "$label" --arg query "$query" \
    --arg expected "$expected" --argjson rank "$rank" \
    --argjson count "$count" --arg elapsed_seconds "$elapsed" \
    '{provider:$provider,agent:$agent,bank:$bank,phase:$phase,test:$test,query:$query,expected:$expected,rank:$rank,result_count:$count,elapsed_seconds:($elapsed_seconds|tonumber)}'
  rm -f "$response"
}

for row in "${agents[@]}"; do
  IFS='|' read -r agent bank marker color project <<<"$row"
  fake_secret="FAKE-SECRET-DO-NOT-STORE-${agent^^}"
  raw_log="ERROR-RAW-LOG-${agent^^}"
  document_id="benchmark-${run_id}-${agent}"
  content="Controlled synthetic benchmark for ${agent}. Exact sentinel ${marker} is owned by ${agent}. The benchmark client prefers ${color} proposal covers. Source pointer: Memory Testing page ${pointer}. Next action: review monthly score. Project ${project} Lantern status was Draft. Correction: Project ${project} Lantern status is Final and Draft is superseded. Noise that must not be retained: greeting hello; calculation 17 plus 28 equals 45; fake secret ${fake_secret}; raw log ${raw_log}; unsupported guess the moon is cheese."
  body="$(jq -nc \
    --arg content "$content" --arg doc "$document_id" \
    --arg agent_tag "agent:${agent}" \
    '{async:false,items:[{content:$content,document_id:$doc,update_mode:"replace",tags:["benchmark:2026-08",$agent_tag,"source_system:codex-benchmark"]}]}')"

  response="$(mktemp)"
  elapsed="$(curl -fsS -o "$response" -w '%{time_total}' \
    -H 'Content-Type: application/json' \
    -d "$body" \
    "$base_url/v1/default/banks/$bank/memories")"
  success="$(jq '.success // false' "$response")"
  items_count="$(jq '.items_count // 0' "$response")"
  jq -nc \
    --arg provider hindsight --arg agent "$agent" --arg bank "$bank" \
    --arg phase retain --argjson success "$success" \
    --argjson items_count "$items_count" --arg elapsed_seconds "$elapsed" \
    '{provider:$provider,agent:$agent,bank:$bank,phase:$phase,success:$success,items_count:$items_count,elapsed_seconds:($elapsed_seconds|tonumber)}'
  rm -f "$response"

  recall "$agent" "$bank" "$marker" "$marker" exact
  recall "$agent" "$bank" "Which proposal cover colour does the benchmark client prefer?" "$color" paraphrase
  recall "$agent" "$bank" "What is the current status of Project ${project} Lantern?" "Final" freshness
  recall "$agent" "$bank" "Where is the Memory Testing source and what is the next action?" "$pointer" pointer
  recall "$agent" "$bank" "$fake_secret" "$fake_secret" unsafe-secret
  recall "$agent" "$bank" "$raw_log" "$raw_log" raw-log
done
