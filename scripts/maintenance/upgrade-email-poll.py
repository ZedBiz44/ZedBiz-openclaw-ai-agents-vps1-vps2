import pathlib,subprocess,hashlib
p=pathlib.Path('/opt/openclaw/scripts/email-poll.sh');b=pathlib.Path('/opt/openclaw/builds/vps1-email-20261003');s=p.read_text();before=s
old='RESULT=$(docker exec "$AGENT" himalaya -o json envelope list --page-size 10 "flag unseen" 2>/dev/null)'
new='''if docker exec "$AGENT" himalaya --version 2>/dev/null | grep -q '^himalaya v2\\.'; then
  RESULT=$(docker exec "$AGENT" himalaya envelope search --mailbox INBOX --page-size 10 --json "not flag seen" 2>/dev/null)
else
  RESULT=$(docker exec "$AGENT" himalaya -o json envelope list --page-size 10 "not flag seen" 2>/dev/null)
fi'''
assert s.count(old)==1;s=s.replace(old,new)
old="COUNT=$(echo \"$RESULT\" | jq 'if type == \"array\" then length else 0 end' 2>/dev/null)"
new="RESULT=$(printf '%s\\n' \"$RESULT\" | jq -ce 'if type == \"array\" then . elif (.envelopes | type) == \"array\" then .envelopes else error(\"Invalid envelope response\") end') || exit 1\nCOUNT=$(printf '%s\\n' \"$RESULT\" | jq 'length')\n\n# Maintenance proof: never schedule an agent or send a notification.\nif [ \"${EMAIL_POLL_CHECK_ONLY:-0}\" = 1 ]; then\n  printf 'Read-only inbox check passed for %s: %s unread envelopes\\n' \"$AGENT\" \"$COUNT\"\n  exit 0\nfi"
assert s.count(old)==1;s=s.replace(old,new)
model='    --model "google/gemini-2.5-flash" \\\n';assert s.count(model)==2;s=s.replace(model,'')
s=s.replace('+ cheapest model',"+ the agent's configured OAuth model").replace('# Uses "flag unseen" query — only unread messages','# Uses "not flag seen" query — only unread messages')
assert not (b/'email-poll.before.sh').exists();(b/'email-poll.before.sh').write_text(before)
candidate=b/'email-poll.sh';candidate.write_text(s);subprocess.run(['bash','-n',str(candidate)],check=True)
p.write_text(s)
print('Updated existing inbox poller: v1/v2 response compatibility, read-only test mode, inherited agent model')
