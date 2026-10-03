#!/bin/bash
set -euo pipefail
umask 077
B=/root/cody-suzy-maintenance-20261003
test ! -e "$B/activation-before-state"
stop_suzy() {
 systemctl stop --no-block openclaw-suzy
 for i in $(seq 1 60); do
  [[ $(systemctl show -p MainPID --value openclaw-suzy) == 0 ]] && return
  sleep 1
 done
 systemctl kill --kill-whom=all --signal=SIGKILL openclaw-suzy
 sleep 2
 [[ $(systemctl show -p MainPID --value openclaw-suzy) == 0 ]]
}
stop_suzy
trap 'systemctl start openclaw-suzy' ERR
cp -a /root/.openclaw-suzy "$B/activation-before-state"
cp -a /opt/openclaw-suzy "$B/activation-before-program"
python3 - <<'PY'
import pathlib,sqlite3
b=pathlib.Path('/root/cody-suzy-maintenance-20261003/activation-before-state')
for p in [b/'state/openclaw.sqlite',*b.glob('agents/*/agent/openclaw-agent.sqlite')]:
 with sqlite3.connect('file:'+str(p)+'?mode=ro',uri=True) as c:
  assert c.execute('pragma integrity_check').fetchone()[0]=='ok',str(p)
print('FRESH_BACKUP_INTEGRITY_OK')
PY
rollback() {
 trap - ERR
 stop_suzy || true
 mv /root/.openclaw-suzy "$B/activation-failed-state"
 mv /opt/openclaw-suzy "$B/activation-failed-program"
 cp -a "$B/activation-before-state" /root/.openclaw-suzy
 cp -a "$B/activation-before-program" /opt/openclaw-suzy
 systemctl start openclaw-suzy
 echo ACTIVATION_ROLLED_BACK
 exit 1
}
trap rollback ERR
mv /opt/openclaw-suzy/node_modules "$B/activation-old-node_modules"
cp -a "/root/cody-harry-maintenance-20261003/candidate/node_modules" /opt/openclaw-suzy/node_modules
cp "/root/cody-harry-maintenance-20261003/candidate/package.json" "/root/cody-harry-maintenance-20261003/candidate/package-lock.json" /opt/openclaw-suzy/
bash /tmp/cody-suzy-cli-20261003.sh doctor --fix --non-interactive > "$B/activation-doctor.log" 2>&1
bash /tmp/cody-suzy-cli-20261003.sh plugins update @openclaw/codex@2026.9.8 @openclaw/discord@2026.9.8 @openclaw/gradium-speech@2026.9.8 @openclaw/parallel-plugin@2026.9.8 @openclaw/perplexity-plugin@2026.9.8 @openclaw/tavily-plugin@2026.9.8 > "$B/activation-plugins.log" 2>&1
python3 - <<'PY'
import json,pathlib,shutil
p=pathlib.Path('/root/.openclaw-suzy/openclaw.json')
c=json.loads(p.read_text())
before=json.loads(pathlib.Path('/root/cody-suzy-maintenance-20261003/activation-before-state/openclaw.json').read_text())
for original in pathlib.Path('/root/cody-suzy-maintenance-20261003/activation-before-state/workspace').glob('*.md'):
 shutil.copy2(original,pathlib.Path('/root/.openclaw-suzy/workspace')/original.name)
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
bash /tmp/cody-suzy-cli-20261003.sh models auth order set --agent main --provider openai openai:jzedbiz@gmail.com > "$B/activation-auth.log" 2>&1
systemctl start openclaw-suzy
for i in $(seq 1 90); do
 if curl --max-time 2 -sf http://127.0.0.1:4200/health > /dev/null; then
  touch "$B/activation-complete"
  echo ACTIVATION_HEALTH_OK
  exit 0
 fi
 sleep 2
done
false
