import concurrent.futures,json,urllib.request
repos={'YTDLP':'yt-dlp/yt-dlp','RCLONE':'rclone/rclone','GH':'cli/cli','YQ':'mikefarah/yq','PANDOC':'jgm/pandoc','UV':'astral-sh/uv','GRON':'tomnomnom/gron','GLOW':'charmbracelet/glow','EZA':'eza-community/eza','DUF':'muesli/duf','FZF':'junegunn/fzf','FREEZE':'charmbracelet/freeze','VHS':'charmbracelet/vhs','GITCLIFF':'orhun/git-cliff','JUST':'casey/just','GREX':'pemistahl/grex','BLOGWATCHER':'Hyaxia/blogwatcher','CAMSNAP':'steipete/camsnap','GOPLACES':'openclaw/goplaces'}
npm={'ASANA_MCP':'@roychri/mcp-server-asana','NOTION_MCP':'@notionhq/notion-mcp-server','CODEX':'@openai/codex','GEMINI_CLI':'@google/gemini-cli','CLAWHUB':'clawhub','XURL':'@xdevplatform/xurl'}
jobs=[(k,'https://api.github.com/repos/'+v+'/releases/latest','tag_name') for k,v in repos.items()]+[(k,'https://registry.npmjs.org/'+v+'/latest','version') for k,v in npm.items()]+[(k,'https://pypi.org/pypi/'+v+'/json','info') for k,v in {'DEBUGPY':'debugpy','NANO_PDF':'nano-pdf'}.items()]
def check(j):
 k,u,f=j
 try:
  d=json.load(urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'ZedBiz-maintenance'}),timeout=30));v=d[f];v=v['version'] if f=='info' else v
  return k+'_VERSION',v.removeprefix('v').removeprefix('rust-')
 except Exception as e:return k+'_VERSION','ERROR '+str(e)
print(json.dumps(dict(concurrent.futures.ThreadPoolExecutor(max_workers=6).map(check,jobs)),indent=2))
