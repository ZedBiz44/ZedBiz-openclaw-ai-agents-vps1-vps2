"""Patch Edith's isolated GOG build with explicit pre-generated copy IDs."""
from pathlib import Path
import difflib
p=Path('/home/node/.openclaw/workspace/edith-drive-repair/gogcli-324f656a/internal/cmd')
def change(name, old, new):
    f=p/name;s=f.read_text();assert s.count(old)==1,(name,old)
    updated=s.replace(old,new,1)
    patch=''.join(difflib.unified_diff(s.splitlines(True),updated.splitlines(True),fromfile='a/internal/cmd/'+name,tofile='b/internal/cmd/'+name))
    with (p.parent.parent/'edith-copy-identity.patch').open('a') as out:out.write(patch)
    f.write_text(updated)

change('drive.go','\tCopy        DriveCopyCmd', '\tGenerateID  DriveGenerateIDCmd `cmd:"" name:"generate-id" help:"Reserve one Google Drive file ID for an idempotent binary copy"`\n\tCopy        DriveCopyCmd')
change('drive.go','type DriveCopyCmd struct {','type DriveCopyCmd struct {\n\tDestinationID string `name:"destination-id" help:"Previously reserved destination ID (binary copies only)"`')
change('drive.go','ArgName: "fileId",','ArgName: "fileId",\n\t\tDestinationID: c.DestinationID,')
change('drive_copy.go','type copyViaDriveOptions struct {','type copyViaDriveOptions struct {\n\tDestinationID string')
change('drive_copy.go','req := &drive.File{Name: name}','req := &drive.File{Name: name, Id: strings.TrimSpace(opts.DestinationID)}')
(p/'drive_generate_id.go').write_text('''package cmd

import (
    "context"
    "errors"
    "github.com/openclaw/gogcli/internal/outfmt"
)

type DriveGenerateIDCmd struct {}
func (c *DriveGenerateIDCmd) Run(ctx context.Context, flags *RootFlags) error {
    if err := dryRunExit(ctx, flags, "drive.generate-id", map[string]any{"count":1}); err != nil { return err }
    _, svc, err := requireDriveService(ctx, flags)
    if err != nil { return err }
    result, err := svc.Files.GenerateIds().Count(1).Space("drive").Type("files").Context(ctx).Do()
    if err != nil { return err }
    if result == nil || len(result.Ids) != 1 || result.Ids[0] == "" { return errors.New("missing reserved Drive ID") }
    return outfmt.WriteJSON(ctx, stdoutWriter(ctx), map[string]any{"id":result.Ids[0]})
}
''')
print('Patched explicit copy identity and ID reservation command; build not yet activated')

