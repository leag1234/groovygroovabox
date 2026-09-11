#!/usr/bin/env python3
"""
inject_samples.py — Embed drum samples into the GroovyGroova Box HTML.

USAGE
-----
1. Prepare a directory with your drum samples. Filenames must follow this
   convention (case-insensitive, .wav or .mp3 or .ogg):

       <track>__<articulation>[__<velocity>].<ext>

   Velocity is optional and is an integer 0-9 (low to high) used to layer
   multiple samples for the same articulation (Round Robin / velocity layers).

   Recognized tracks:        kick, snare, clap, hh, ride, tom, crash
   Recognized articulations:
       kick:  normal
       snare: normal, rim, ghost, crossstick
       clap:  normal
       hh:    closed, open, foot, openclose
       ride:  normal, bell
       tom:   normal
       crash: normal

   Examples:
       kick__normal.wav
       snare__normal__0.wav   (lowest velocity)
       snare__normal__3.wav   (highest velocity)
       snare__rim.wav
       snare__ghost.wav
       hh__closed.wav
       hh__open.wav
       hh__foot.wav
       tom__normal__0.wav    (low tom)
       tom__normal__1.wav    (mid tom)
       tom__normal__2.wav    (high tom)
       ride__bell.wav

2. Run (single kit, legacy):

       python3 inject_samples.py path/to/samples/ groovygroova-box.html

   Or several kits at once (each becomes a kit button):

       python3 inject_samples.py groovygroova-box.html \
           --kit salamander "Salam." studio /path/salamander \
           --kit tr808 "808" electronic /path/808 \
           --kit jazz "Jazz" acoustic /path/jazz

   --kit <id> <label> <fallback-synth-kit> <dir>
   fallback-synth-kit is one of: acoustic, electronic, studio — used for any
   (track, articulation) the kit does not provide.

3. Attribution. A kit directory may carry a CREDITS file, one "key: value"
   per line, recognized keys being name, author, license, license-url,
   source-url and note. Those are rendered as static markup into the page at
   the <!-- SAMPLE-CREDITS --> marker, so the notice ships inside the built
   HTML instead of living only alongside it. A kit without a CREDITS file
   builds fine but warns, since it will ship without attribution.

   This produces "<html>-with-samples.html" next to the source HTML.

NOTES
-----
- Samples should be short (typically 0.3 - 3 seconds for drums; cymbals can
  be longer). Total file size limit is practical, not technical: keep the
  final HTML under ~15 MB for a reasonable load time.
- Recommended sample rate: 44.1 kHz, 16-bit. Higher is fine but inflates the
  base64 payload.
- Missing articulations are silently skipped; the Samples kit will fall
  back to the Studio synth for any unmapped articulation.
"""

import base64
import html
import json
import mimetypes
import os
import re
import sys
from collections import defaultdict
from pathlib import Path


VALID_TRACKS = {
    'kick':    ['normal'],
    'snare':   ['normal', 'rim', 'ghost', 'crossstick'],
    'clap':    ['normal'],
    'hh':      ['closed', 'halfopen', 'open', 'foot', 'openclose'],
    'ride':    ['normal', 'bell'],
    'tom':     ['normal'],
    'crash':   ['normal'],
    'cowbell': ['normal'],
}

CREDITS_FILENAMES = ('CREDITS', 'CREDITS.txt')

CREDITS_MARKER = '<!-- SAMPLE-CREDITS -->'


FILENAME_RE = re.compile(
    r'^(?P<track>[a-z]+)__(?P<art>[a-z]+)(?:__(?P<vel>\d+))?\.(wav|mp3|ogg)$',
    re.IGNORECASE,
)


def scan_samples(directory: Path):
    """Scan a directory and return {track: {art: [(velocity, path), ...]}}."""
    samples = defaultdict(lambda: defaultdict(list))
    skipped = []

    for f in sorted(directory.iterdir()):
        if not f.is_file():
            continue
        if f.name in CREDITS_FILENAMES:
            continue                      # attribution metadata, not a sample
        m = FILENAME_RE.match(f.name)
        if not m:
            skipped.append(f.name)
            continue
        track = m.group('track').lower()
        art   = m.group('art').lower()
        vel   = int(m.group('vel')) if m.group('vel') else 0
        if track not in VALID_TRACKS:
            skipped.append(f.name + ' (unknown track)')
            continue
        if art not in VALID_TRACKS[track]:
            skipped.append(f.name + f' (unknown articulation for {track})')
            continue
        samples[track][art].append((vel, f))

    return samples, skipped


def encode_file(path: Path) -> str:
    """Return a base64 data URI for the given file."""
    mime, _ = mimetypes.guess_type(str(path))
    if mime is None:
        # Best-effort fallback
        ext = path.suffix.lower()
        mime = {'.wav': 'audio/wav', '.mp3': 'audio/mpeg', '.ogg': 'audio/ogg'}.get(ext, 'application/octet-stream')
    data = path.read_bytes()
    b64 = base64.b64encode(data).decode('ascii')
    return f'data:{mime};base64,{b64}'


def build_samples_dict(scanned):
    """Convert scanned dict into the {track: {art: [url, url, ...]}} structure."""
    out = {}
    for track, arts in scanned.items():
        out[track] = {}
        for art, entries in arts.items():
            entries.sort(key=lambda e: e[0])   # sort by velocity ascending
            out[track][art] = [encode_file(p) for (_, p) in entries]
    return out


def read_credits(directory: Path):
    """Read a kit's CREDITS file into a dict.

    Format is one "key: value" per line; blank lines and lines starting with
    '#' are ignored. Recognized keys: name, author, license, license-url,
    source-url, note. Returns {} when the kit ships no CREDITS file.
    """
    for fname in CREDITS_FILENAMES:
        path = directory / fname
        if path.is_file():
            break
    else:
        return {}

    meta = {}
    for line in path.read_text(encoding='utf-8').splitlines():
        line = line.strip()
        if not line or line.startswith('#') or ':' not in line:
            continue
        key, _, value = line.partition(':')
        value = value.strip()
        if value:
            meta[key.strip().lower()] = value
    return meta


def render_credits_html(kits):
    """Build the static attribution block for the kits being embedded.

    Emitted as plain markup rather than script-rendered, so the notice is
    present in the file even with JavaScript disabled.
    """
    entries = []
    for kid, kit in kits.items():
        meta = kit.get('credits') or {}
        if not meta:
            continue

        e = html.escape
        head = '<strong>' + e(kit['label']) + '</strong> \u2014 ' + e(meta.get('name', kid))
        if meta.get('author'):
            head += ' by ' + e(meta['author'])
        parts = [head]
        if meta.get('license'):
            lic = e(meta['license'])
            if meta.get('license-url'):
                lic = ('<a href="' + e(meta['license-url']) + '" target="_blank" '
                       'rel="noopener noreferrer">' + lic + '</a>')
            parts.append(lic)
        line = ', '.join(parts)

        if meta.get('source-url'):
            line += (' (<a href="' + e(meta['source-url']) + '" target="_blank" '
                     'rel="noopener noreferrer">source</a>)')
        if meta.get('note'):
            line += '<span class="credit-note">' + e(meta['note']) + '</span>'
        entries.append('      <li>' + line + '</li>')

    if not entries:
        return ''

    return (
        '<details class="credit-samples">\n'
        '    <summary>Sample kits: ' + str(len(entries)) + ' third-party kits, '
        'not covered by the WTFPL \u2014 licenses and attribution</summary>\n'
        '    <ul>\n' + '\n'.join(entries) + '\n    </ul>\n'
        '  </details>'
    )


def inject(html_path: Path, samples_dict, output_path: Path, kits=None):
    """Inject samples into the HTML as a <script> at the top of the body.
    Single kit: window.CUSTOM_SAMPLES (legacy). Multi-kit: window.CUSTOM_SAMPLE_KITS."""
    source = html_path.read_text(encoding='utf-8')

    if kits is not None:
        # Attribution is rendered into the markup, not shipped to the runtime.
        runtime_kits = {
            kid: {k: v for k, v in kit.items() if k != 'credits'}
            for kid, kit in kits.items()
        }
        payload = json.dumps(runtime_kits, separators=(',', ':'))
        assign = f'window.CUSTOM_SAMPLE_KITS = {payload};'
    else:
        payload = json.dumps(samples_dict, separators=(',', ':'))
        assign = f'window.CUSTOM_SAMPLES = {payload};'
    injection = (
        '<script id="custom-samples-injected">\n'
        '// Auto-injected by inject_samples.py — DO NOT EDIT MANUALLY\n'
        f'{assign}\n'
        '</script>\n'
    )

    # Sample attribution, substituted into the page credit
    credits_html = render_credits_html(kits) if kits else ''
    if CREDITS_MARKER in source:
        source = source.replace(CREDITS_MARKER, credits_html, 1)
    elif credits_html:
        print(f'WARNING: {CREDITS_MARKER} not found in {html_path.name}; '
              'sample attribution could not be placed in the page.',
              file=sys.stderr)

    # Insert right after <body ...> tag
    body_re = re.compile(r'(<body[^>]*>)', re.IGNORECASE)
    m = body_re.search(source)
    if not m:
        raise RuntimeError('Could not find <body> tag in HTML.')
    insert_at = m.end()
    new_html = source[:insert_at] + '\n' + injection + source[insert_at:]

    output_path.write_text(new_html, encoding='utf-8')


def human_size(n_bytes):
    for unit in ['B', 'KB', 'MB', 'GB']:
        if n_bytes < 1024:
            return f'{n_bytes:.1f} {unit}'
        n_bytes /= 1024
    return f'{n_bytes:.1f} TB'


def scan_and_report(samples_dir: Path, title: str):
    print(f'Scanning {samples_dir} ({title}) ...')
    scanned, skipped = scan_samples(samples_dir)
    if not scanned:
        print('  No valid samples found. Filenames must follow:')
        print('  <track>__<articulation>[__<velocity>].<wav|mp3|ogg>')
        sys.exit(1)
    total_size = 0
    for track in scanned:
        for art, entries in scanned[track].items():
            for vel, pth in entries:
                total_size += pth.stat().st_size
    print(f'  {sum(len(e) for a in scanned.values() for e in a.values())} files, {human_size(total_size)}')
    if skipped:
        print('  Skipped: ' + ', '.join(skipped))
    return scanned


def main_multi(argv):
    """python3 inject_samples.py <html> --kit id label fallback dir [--kit ...]"""
    html_path = Path(argv[1]).resolve()
    if not html_path.is_file():
        print(f'ERROR: {html_path} not found', file=sys.stderr)
        sys.exit(1)
    kits = {}
    i = 2
    while i < len(argv):
        if argv[i] != '--kit' or i + 4 >= len(argv) + 0 and i + 4 > len(argv) - 1 + 1:
            pass
        if argv[i] != '--kit':
            print(f'ERROR: unexpected argument {argv[i]}', file=sys.stderr)
            sys.exit(1)
        kid, label, fallback, d = argv[i+1], argv[i+2], argv[i+3], Path(argv[i+4]).resolve()
        if fallback not in ('acoustic', 'electronic', 'studio'):
            print(f'ERROR: fallback must be acoustic|electronic|studio, got {fallback}', file=sys.stderr)
            sys.exit(1)
        if not d.is_dir():
            print(f'ERROR: {d} is not a directory', file=sys.stderr)
            sys.exit(1)
        scanned = scan_and_report(d, f'kit {kid} / {label}')
        credits = read_credits(d)
        if credits:
            print(f'  credits: {credits.get("name", kid)}'
                  f' \u2014 {credits.get("license", "license unstated")}')
        else:
            print(f'  WARNING: no CREDITS file in {d}; this kit will ship '
                  'without attribution', file=sys.stderr)
        kits[kid] = {
            'label': label,
            'fallback': fallback,
            'samples': build_samples_dict(scanned),
            'credits': credits,
        }
        i += 5
    if not kits:
        print(__doc__); sys.exit(1)
    output_path = html_path.with_name(html_path.stem.replace('-with-samples', '') + '-with-samples.html')
    print(f'\nWriting {output_path} ...')
    inject(html_path, None, output_path, kits=kits)
    print(f'Done. {len(kits)} kit(s). Final HTML size:  {human_size(output_path.stat().st_size)}')


def main():
    if len(sys.argv) >= 3 and sys.argv[2] == '--kit':
        main_multi(sys.argv)
        return
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(1)

    samples_dir = Path(sys.argv[1]).resolve()
    html_path = Path(sys.argv[2]).resolve()

    if not samples_dir.is_dir():
        print(f'ERROR: {samples_dir} is not a directory', file=sys.stderr)
        sys.exit(1)
    if not html_path.is_file():
        print(f'ERROR: {html_path} not found', file=sys.stderr)
        sys.exit(1)

    print(f'Scanning {samples_dir} ...')
    scanned, skipped = scan_samples(samples_dir)

    if not scanned:
        print('No valid samples found. Filenames must follow:')
        print('  <track>__<articulation>[__<velocity>].<wav|mp3|ogg>')
        sys.exit(1)

    print('\nFound samples:')
    total_size = 0
    for track in scanned:
        for art, entries in scanned[track].items():
            for vel, p in entries:
                size = p.stat().st_size
                total_size += size
                label = f'  {track}/{art}'
                if len(entries) > 1:
                    label += f' [vel {vel}]'
                print(f'{label.ljust(30)} {p.name.ljust(35)} {human_size(size).rjust(10)}')

    if skipped:
        print('\nSkipped files (filename did not match convention):')
        for s in skipped:
            print(f'  {s}')

    print(f'\nTotal samples size: {human_size(total_size)}')
    print(f'(Base64 encoding will add ~33% overhead)')

    print('\nEncoding samples to base64...')
    samples_dict = build_samples_dict(scanned)

    output_path = html_path.parent / (html_path.stem + '-with-samples.html')
    print(f'Writing {output_path} ...')
    inject(html_path, samples_dict, output_path)

    final_size = output_path.stat().st_size
    print(f'\nDone. Output file: {output_path}')
    print(f'Final HTML size:  {human_size(final_size)}')
    print('\nOpen the HTML in your browser and pick the "Samples" kit.')


if __name__ == '__main__':
    main()
