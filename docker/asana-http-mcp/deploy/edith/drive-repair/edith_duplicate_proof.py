"""Record an exact duplicate's own preservation proof without copying it again."""
def make_proof(row, original, source, active, canonical, source_access, active_access, now):
    fid=row['source_id'];cid=row.get('active_copy_source_id',fid)
    assert cid!=fid and row.get('action')=='copy'
    assert source['id']==fid and original['id']==fid
    assert canonical['source_id']==cid and canonical.get('content_read') and canonical.get('permissions_matched') is True
    assert active['id']==canonical['active_id'] and not source.get('trashed') and not active.get('trashed')
    assert row['planned_path']==canonical['path'] and active['name']==canonical['name']
    assert source.get('name')==original.get('name')
    for key in ('md5Checksum','size'):
        assert source.get(key) and source[key]==original.get(key)==active.get(key)==canonical.get(key)
    assert source_access==active_access
    result=dict(canonical,source_id=fid,canonical_source_id=cid,verified_at=now,
                content_read='Own source checksum and size match verified canonical content; reused unchanged inspection',
                match_method='exact_duplicate_checksum_size')
    return result

