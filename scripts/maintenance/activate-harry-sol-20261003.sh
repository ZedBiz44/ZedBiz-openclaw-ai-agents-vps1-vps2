#!/bin/bash
set -euo pipefail
umask 077
B=/root/cody-harry-maintenance-20261003
test ! -e "$B/activation-before-state"
stop_harry() {
 systemctl stop --no-block openclaw-harry
 for i in $(seq 1 60); do
  [[ $(systemctl show -p MainPID --value openclaw-harry) == 0 ]] && return
  sleep 1
 done
 systemctl kill --kill-whom=all --signal=SIGKILL openclaw-harry
 sleep 2
 [[ $(systemctl show -p MainPID --value openclaw-harry) == 0 ]]
}
stop_harry
trap 'systemctl start openclaw-harry' ERR
cp -a /root/.openclaw-harry "$B/activation-before-state"
cp -a /opt/openclaw-harry "$B/activation-before-program"
python3 - <<'PY'
import pathlib,sqlite3
b=pathlib.Path('/root/cody-harry-maintenance-20261003/activation-before-state')
for p in [b/'state/openclaw.sqlite',*b.glob('agents/*/agent/openclaw-agent.sqlite')]:
 with sqlite3.connect('file:'+str(p)+'?mode=ro',uri=True) as c:
  assert c.execute('pragma integrity_check').fetchone()[0]=='ok',str(p)
print('FRESH_BACKUP_INTEGRITY_OK')
PY
rollback() {
 trap - ERR
 stop_harry || true
 mv /root/.openclaw-harry "$B/activation-failed-state"
 mv /opt/openclaw-harry "$B/activation-failed-program"
 cp -a "$B/activation-before-state" /root/.openclaw-harry
 cp -a "$B/activation-before-program" /opt/openclaw-harry
 systemctl start openclaw-harry
 echo ACTIVATION_ROLLED_BACK
 exit 1
}
trap rollback ERR
mv /opt/openclaw-harry/node_modules "$B/activation-old-node_modules"
cp -a "$B/candidate/node_modules" /opt/openclaw-harry/node_modules
cp "$B/candidate/package.json" "$B/candidate/package-lock.json" /opt/openclaw-harry/
bash /tmp/cody-harry-cli-20261003.sh doctor --fix --non-interactive > "$B/activation-doctor.log" 2>&1
bash /tmp/cody-harry-cli-20261003.sh plugins update @openclaw/codex@2026.9.8 @openclaw/discord@2026.9.8 @openclaw/gradium-speech@2026.9.8 @openclaw/parallel-plugin@2026.9.8 @openclaw/perplexity-plugin@2026.9.8 @openclaw/tavily-plugin@2026.9.8 > "$B/activation-plugins.log" 2>&1
python3 - <<'PY'
import json,pathlib,shutil
p=pathlib.Path('/root/.openclaw-harry/openclaw.json')
c=json.loads(p.read_text())
before=json.loads(pathlib.Path('/root/cody-harry-maintenance-20261003/activation-before-state/openclaw.json').read_text())
for original in pathlib.Path('/root/cody-harry-maintenance-20261003/activation-before-state/workspace').glob('*.md'):
 shutil.copy2(original,pathlib.Path('/root/.openclaw-harry/workspace')/original.name)
if 'skills' in before:c['skills']=before['skills']
c['plugins']['entries']['codex'].setdefault('config',{}).setdefault('appServer',{})['command']='/usr/bin/codex'
c['plugins']['entries']['codex']['config']['appServer']['clearEnv']=['OPENAI_API_KEY','CODEX_API_KEY']
d=c['agents']['defaults']; d['model']['primary']='openai/gpt-6.1-sol'; d['model']['fallbacks']=[]
d.setdefault('models',{})['openai/gpt-6.1-sol']={'agentRuntime':{'id':'codex'}}
a=d.setdefault('modelPolicy',{}).setdefault('allow',[])
if 'openai/gpt-6.1-sol' not in a:a.append('openai/gpt-6.1-sol')
c.setdefault('auth',{}).setdefault('order',{})['openai']=['openai:jzedbiz@gmail.com']
p.write_text(json.dumps(c,indent=2)+'\n')
PY
bash /tmp/cody-harry-cli-20261003.sh models auth order set --agent main --provider openai openai:jzedbiz@gmail.com > "$B/activation-auth.log" 2>&1
systemctl start openclaw-harry
for i in $(seq 1 90); do
 if curl --max-time 2 -sf http://127.0.0.1:4100/health > /dev/null; then
  touch "$B/activation-complete"
  echo ACTIVATION_HEALTH_OK
  exit 0
 fi
 sleep 2
done
false
