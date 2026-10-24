from pathlib import Path
import urllib.request,json,hashlib,tarfile,subprocess,shutil,os
B=Path('/root/cody-vps2-followup-20261023');os.umask(0o077)
def fetch(repo,tag,name,checksum):
 base='https://github.com/'+repo+'/releases/download/'+tag+'/'
 p=B/name;p.write_bytes(urllib.request.urlopen(base+name,timeout=90).read())
 lines=urllib.request.urlopen(base+checksum,timeout=30).read().decode().splitlines()
 expected=next(l.split()[0] for l in lines if l.split()[-1].lstrip('*')==name)
 assert hashlib.sha256(p.read_bytes()).hexdigest()==expected
 return p
g=fetch('openclaw/gogcli','v0.47.0','gogcli_0.47.0_linux_amd64.tar.gz','checksums.txt')
with tarfile.open(g) as t:
 m=next(m for m in t.getmembers() if m.name.split('/')[-1]=='gog' and m.isfile());p=B/'gog-0.47.0';p.write_bytes(t.extractfile(m).read());p.chmod(0o755)
subprocess.run([str(p),'--version'],check=True)
fetch('cli/cli','v2.102.0','gh_2.102.0_linux_amd64.deb','gh_2.102.0_checksums.txt')
gh=fetch('cli/cli','v2.103.2','gh_2.103.2_linux_amd64.deb','gh_2.103.2_checksums.txt')
wrapper=Path('/usr/local/bin/gog');old=wrapper.read_text();assert 'REAL=/usr/local/libexec/gog-0.45.0' in old
shutil.copy2(wrapper,B/'gog-wrapper-before');shutil.copy2('/usr/local/libexec/gog-0.45.0',B/'gog-binary-before')
dest=Path('/usr/local/libexec/gog-0.47.0');shutil.copy2(p,dest);dest.chmod(0o755)
new=old.replace('REAL=/usr/local/libexec/gog-0.45.0','REAL=/usr/local/libexec/gog-0.47.0')
tmp=wrapper.with_name('gog.followup-new');tmp.write_text(new);tmp.chmod(0o755);tmp.replace(wrapper)
assert wrapper.read_text().replace('0.47.0','0.45.0')==old
subprocess.run(['dpkg','-i',str(gh)],check=True)
for c in [['gog','--version'],['gh','--version']]:subprocess.run(c,check=True)
(B/'native-tools-installed.json').write_text(json.dumps({'gog':'0.47.0','gh':'2.103.2','wrapperPreserved':True}))
