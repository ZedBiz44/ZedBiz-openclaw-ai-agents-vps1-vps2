"""Reuse source inspection only when Drive proves an unchanged binary copy.

Native documents deliberately need their own comparison; missing hashes are
never interpreted as equality. This does not classify or visually inspect files.
"""
from pathlib import Path


def verify_output(base, row, source, destination, gog):
    checksum = source.get('md5Checksum')
    if not checksum or source.get('size') is None:
        raise ValueError('Native or unhashable file requires native content verification')
    if destination.get('md5Checksum') != checksum or str(destination.get('size')) != str(source['size']):
        raise ValueError('Source and copied bytes differ')
    if source.get('mimeType') != destination.get('mimeType'):
        raise ValueError('Copy MIME metadata changed')
    original_suffix = Path(source['name']).suffix.lower()
    if Path(destination['name']).suffix.lower() != original_suffix:
        raise ValueError('File extension changed')
    if original_suffix in {'.psd', '.psb'} and destination['name'] != source['name']:
        raise ValueError('Photoshop original filename must be retained')
    return ('Saved source inspection reused; live Drive MD5 and size match. '
            'No additional download, format conversion or visual inspection of copy.', None)

