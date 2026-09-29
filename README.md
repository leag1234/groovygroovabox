# GroovyGroova Box

**A live drum sequencer that plays like an instrument, in a single HTML file.**

🎛️ **Try it now: [https://www.indidea.org/groovygroovabox/](https://www.indidea.org/groovygroovabox/)**

GroovyGroova Box is a 16-step, 8-track drum machine built for *live* use: you play with the groove while it runs. Pads and keyboard shortcuts alter the pattern on the fly, a microtiming engine gives each hit a human placement, a controlled-chaos layer carves breaks into the groove, and a "wildcard" lets the machine surprise you with a musical gesture on the next bar. Everything, including 9 sampled drum kits, ships as one self-contained HTML file that works offline.

No install, no build step, no account: open the file in a browser and press Play.

An original concept by **Gaël Duval**, developed since **May 2026**. First public release: **11 September 2026**.

---

## Features

### Sequencer
- 8 tracks (kick, snare, clap, hi-hat, ride, tom, crash, cowbell), 16 steps, per-track volume and mute
- Per-step **articulations**: rim shot, ghost note, cross-stick on the snare; closed, half-open, open, foot and open-close on the hi-hat; bow and bell on the ride
- 17 built-in patterns across rock, pop, funk, disco, house, techno, breakbeat, hip-hop, 2000s R&B, trap, reggae, Afro-Cuban (son, rumba, cha-cha), bossa, samba and Bo Diddley
- Pattern switching **now** or **on the next bar**, tempo 40 to 220 BPM, swing, count-in, metronome

### Live performance
- **Alteration pads** (with keyboard shortcuts): hi-hat variants, kick variants, syncopation, ghost snare, clap on 2 and 4, snare echoes, and **Broken** (2000s R&B chopped-beat mode with a 2-bar A/B cycle)
- **One-shot fills** (rock, short, tom roll, funk) and a hold-to-drop pad
- **Wildcard** (key `Y`): arm it, and on the next bar the machine draws one gesture from a shuffled bag of 12 (half-time, double-time, beat repeat, beat chop, pushed bar, kick-only breakdown, no-kick breakdown, stop-time, full stop, trap roll, snare build, one drop). You choose *when*, it chooses *what*. Exactly one bar, then back to the groove.

### Groove engine
- **Feel**: 13 microtiming presets that shift each instrument a few milliseconds ahead of or behind the grid, expressed as a fraction of a step so they scale with tempo. Straight, Human Loose, Dilla/Drunk, Boom Bap, Bonham Drag, Motown, Reggae One Drop, Purdie Push, Disco Rush, Punk Speed, Afrobeat (Tony Allen), NOLA Second Line, Jazz Shuffle. An Intensity slider (0 to 300 %) scales the preset.
- **Humanize**: per-hit random jitter on timing and velocity, re-rolled on every hit
- **Chaos**: variation on the ornaments — ghost notes, opened hats, a lifted hand, rim swaps. Nothing is decided hit by hit. At the top of each 4-bar plan a **figure** is rolled for every bar, locked, and replayed identically while the plan lives (4 bars, played twice, then a fresh plan — about 17 seconds at 110 BPM). Repetition is what makes randomness read as a musical idea instead of noise; Humanize keeps jittering velocity and micro-timing per hit on top, so a repeated figure never sounds like a loop.
- **Phrase shape**: a drummer states the groove and opens up at the end of the phrase, so the figure's density follows the bar's position in the plan (weights 0.15 / 0.45 / 0.55 / 1.0 — measured at 0.33 / 1.04 / 1.26 / 2.28 deviations per bar at Chaos 100).
- **Ghost notes follow the hand**: they are drawn as idiomatic cells — a pickup into the backbeat, an answer coming off it, a run leading back to the one — never as isolated hits on random off-steps.
- The kick is never randomized: it is the skeleton the ear locks onto, and displacing or dropping it reads as rhythmic mush rather than variation. Above 40 %, it also carves **structured breaks** into the groove: a 4-bar pause plan is drawn, locked and repeated twice before changing, so holes sound arranged rather than accidental. The silenced zone is dimmed on the grid as the break becomes audible.
- Essential hits (downbeat kick, backbeat snare) are never randomized away.
- **Kick spacing guard**: pattern kicks always play; the one extra kick Broken adds yields if it would crowd them. Deliberate rolls — fills and wildcard gestures — never go through this and are untouched.

### Sounds: 12 kits
- **3 synthesized kits**: Acoustic (wood, skins and air), Electronic (808/909 lineage) and Studio (gated, saturated). Cymbals are built from noise resonators rather than oscillators, so they never collapse into a tone.
- **9 sampled kits**:

| Kit | Source | Character |
|---|---|---|
| Salam. | Salamander Drumkit | Full acoustic kit, velocity layers |
| 808 | Roland TR-808 | The classic |
| DMX | Oberheim DMX | 80s hip-hop, "Blue Monday" |
| DrumTraks | Sequential DrumTraks | 8-bit synth-pop |
| DR-55 | Boss DR-55 | 4 voices only, like the original; the rest falls back to synthesis |
| Amen | The Amen break | Extracted from 32 slices, lo-fi jungle |
| Jazz | Jazz kit | Small, dark, brushes |
| Tight | Dry acoustic kit | Punchy and short |
| Rock | Processed acoustic | Heavy mix chain: compression, saturation, low boost |

Any articulation a sampled kit lacks falls back to a matching synth kit, so every pattern plays on every kit.

### Takes
- **Record 4 bars exactly as they play** — the grid, whatever figure Chaos rolled, and the pads you pressed while it ran. Press **● Record 4 bars**: recording arms and starts at the top of the next bar, runs for four, and stops itself. Name it, or keep the suggestion.
- A take is **frozen**: replaying it plays back those four bars note for note. Nothing is regenerated — empty the grid and set Chaos to 0 and the take is unchanged.
- From the list: **▶** loops the take, **♪** downloads it as a MIDI file (GM drum map, same writer as the session export), **✕** deletes it.
- Events are stored in musical time, in steps from the top of the take, so a take follows whatever tempo it is replayed at.

### Setup bank
- **Save** the grid together with every groove setting: tempo, swing, Feel preset and intensity, Humanize, Chaos, the kit, per-track volume and mutes, and which live pads are engaged. Press **+**, and a field opens pre-filled with a suggested name (`Funk 96`, made unique) — type over it or press Enter to keep it.
- **Recall** any entry from the dropdown below. It honours the **Now / Next bar** switch, so an entry can land on a bar line instead of mid-phrase.
- Entries live in the browser's local storage and survive a reload. The A/V calibration offset and the master volume are deliberately *not* stored: they belong to the machine you are listening on, so recalling an entry never changes how loud the box is or how it lines up with the display.
- This is the groundwork for the song mode, which will assemble bank entries into an arrangement.

### Sync and calibration
- The playhead is driven by the audio clock (requestAnimationFrame loop), never by timers, so it cannot drift under main-thread load.
- **A/V calibration**: an automatic mode plays clicks and listens to them through the microphone to measure real end-to-end output latency (multi-path detection handles virtual drivers and second outputs), plus a manual reaction-time fallback. Your fine-tuning is learned and reapplied to future calibrations.
- An inaudible infrasonic keep-alive tone keeps display and soundbar audio paths from sleeping, so the first beat is never swallowed.

### MIDI
- Record the live session and **export it as a MIDI file** (GM drum map, tempo changes included, optional hi-hat pedal CC#4 for EZdrummer and similar)
- Map any MIDI controller to pads, fills, transport and parameters with MIDI learn

---

## Keyboard shortcuts

| Key | Action |
|---|---|
| `Space` or `Enter` | Play / Stop |
| `Q` `W` `E` `R` | Hi-hat: closed, disco, open 16ths, ride |
| `A` `S` `D` `F` `G` `H` | Kick: standard, double, half, four-on-floor, double on 3, syncope 11 |
| `Z` `X` `P` | Syncope, ghost snare, clap 2&4 |
| `J` `K` | Snare echo +1, +3 |
| `T` | Broken |
| `C` `V` `B` `N` | Fills: rock, short, tom roll, funk |
| `M` (hold) | Drop |
| `Y` | Wildcard (arms the next bar) |

---

## Getting started

- **Download the app**: grab
  **[groovygroovabox.html from the latest release](https://github.com/leag1234/groovygroovabox/releases/latest)**
  — one self-contained file, all 12 kits embedded, about 12 MB. Open it in any modern
  browser: no install, no server, works offline. Deploying it to a site? Rename it to
  `index.html`.

  The same file lives in the repository at [`dist/index.html`](dist/index.html), but note
  that GitHub serves `.html` as `text/plain`, so the raw link displays the source instead
  of saving it. The release asset downloads properly; from a terminal, either works:

  ```bash
  curl -L -O https://github.com/leag1234/groovygroovabox/releases/latest/download/groovygroovabox.html
  ```
- **Lightweight**: [`src/groovygroovabox.html`](src/groovygroovabox.html) is the same app without embedded samples (synth kits only, about 200 KB).
- **On iPhone**: tap once anywhere before pressing Play (browser audio policy). If the phone is on silent mode, the app switches the audio session to playback so sound still comes out.

First launch: run **Setup > Auto-calibrate (mic)** once so the moving playhead matches what you hear on your audio setup.

---

## Building your own sample kits

Sample kits are injected into the HTML by `tools/inject_samples.py`. Put your samples in a folder, named as:

```
<track>__<articulation>[__<velocity>].wav|mp3
```

for example `kick__normal__0.wav`, `snare__rim.wav`, `hh__closed__1.wav`, `ride__bell.wav`. Velocity layers are optional (`__0` soft to `__2` hard). Then:

```bash
python3 tools/inject_samples.py src/groovygroovabox.html \
    --kit mykit "My Kit" acoustic path/to/my-kit \
    --kit tr808 "808" electronic kits/tr808
```

The third argument is the synth kit used as fallback for any missing articulation (`acoustic`, `electronic` or `studio`). The output is written next to the source as `groovygroovabox-with-samples.html`.

Tips: keep hats and short hits as WAV (MP3 smears transients under 100 ms), MP3 at 192 kbps is transparent for longer sounds. Run `python3 tools/inject_samples.py` without arguments for the full documentation.

### Kit attribution

Each kit folder carries its own `CREDITS` file, and the injector renders those
into the page at build time, next to the copyright line. That way attribution
travels with the build: `dist/index.html` is a standalone 12 MB file, and
licenses that require a notice (CC BY-SA, for one) need it present in that
file, not only here in the README.

One `key: value` per line; every field is optional:

```
name: Salamander Drumkit
author: Alexander Holm
license: CC BY-SA 3.0
license-url: https://creativecommons.org/licenses/by-sa/3.0/
source-url: https://archive.org/details/SalamanderDrumkit
note: Attribution required. ShareAlike applies to adaptations.
```

A kit with no `CREDITS` file builds fine but prints a warning, since it will
ship without attribution.

---

## Project layout

```
dist/index.html          Ready-to-use build with all sampled kits (deployed at indidea.org)
src/groovygroovabox.html Source, single file, no samples
tools/inject_samples.py  Sample kit injector
kits/                    The sample kits used to build dist/
kits/<kit>/CREDITS       Per-kit attribution, rendered into the build
docs/mockups/            UI mockups (desktop and mobile redesign)
LICENSE                  WTFPL v2, verbatim
NOTICE                   Copyright, authorship and license scope
```

---

## Credits and licenses

**GroovyGroova Box is an original concept by Gaël Duval**, developed since
**May 2026** and first published on **11 September 2026**. Concept, design and
implementation: Gaël Duval.

Code and documentation: **WTFPL** — Do What The Fuck You Want To Public
License, Version 2 (see [`LICENSE`](LICENSE), and [`NOTICE`](NOTICE) for the
copyright statement and the scope of the license). Do what the fuck you want to.

The sample kits are **not** covered by the WTFPL. They are third-party
material, each under its own license, and some carry obligations the WTFPL
cannot lift:

- **Salamander Drumkit** by Alexander Holm, licensed
  **[CC BY-SA 3.0](https://creativecommons.org/licenses/by-sa/3.0/)**
  (Attribution-ShareAlike). Attribution is required, and the ShareAlike term
  applies to adaptations — including the re-encoded and trimmed samples in
  `kits/salamander/`.
- **TR-808, Sequential DrumTraks, Boss DR-55, Amen break, jazz and acoustic
  kits** come from the [Dirt-Samples](https://github.com/tidalcycles/Dirt-Samples)
  collection maintained by the TidalCycles community. Note that Dirt-Samples
  ships no license file and documents provenance for only one of these
  folders: `808` carries
  [`TR808.TXT`](https://github.com/tidalcycles/Dirt-Samples/blob/master/808/TR808.TXT)
  (Michael Fischer / Technopolis, 1994), which states the samples are free of
  charge but grants no explicit redistribution terms. The other folders carry
  no provenance documentation at all, so the status of those samples is
  **undetermined**.
- **Oberheim DMX**: source **unverified**. There is no `dmx` folder in
  Dirt-Samples, so the origin of `kits/dmx/` is currently undocumented.
- The **Rock** and **Tight** kits are processed derivatives of the acoustic
  sources above, and inherit whatever terms those sources carry.

Per-kit attribution lives in `kits/<kit>/CREDITS` and is rendered into
`dist/index.html` at build time, so the notice travels with the standalone
build rather than living only in this file.

Samples were re-encoded and renamed to a normalised scheme, so original
filenames and metadata are no longer present and individual samples cannot be
traced back to a specific upstream file. Re-establishing that mapping is
tracked work.

If you are a rights holder and believe a sample is used inappropriately, open an issue and it will be replaced.

---

Made by Gaël Duval ([@leag1234](https://github.com/leag1234)). Issues and pull requests welcome.
