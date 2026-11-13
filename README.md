# GroovyGroova Box

**A live drum sequencer that plays like an instrument, in a single HTML file.**

🎛️ **Try it now: [https://www.indidea.org/groovygroovabox/](https://www.indidea.org/groovygroovabox/)**

GroovyGroova Box is a 16-step, 8-track drum machine built for *live* use: you play with the groove while it runs. Pads and keyboard shortcuts alter the pattern on the fly, a microtiming engine gives each hit a human placement, a controlled-chaos layer carves breaks into the groove, and a "wildcard" lets the machine surprise you with a musical gesture on the next bar. Everything, including 6 sampled drum kits, ships as one self-contained HTML file that works offline.

No install, no build step, no account: open the file in a browser and press Play.

An original concept by **Gaël Duval**, developed since **May 2026**. First public release: **11 September 2026**.

---

## Features

### Sequencer
- 8 tracks (kick, snare, clap, hi-hat, ride, tom, crash, cowbell), 16 steps, per-track volume and mute
- Per-step **articulations**: rim shot, ghost note, cross-stick on the snare; closed, half-open, open, foot and open-close on the hi-hat; bow and bell on the ride
- 23 built-in patterns: rock, funk, breakbeat, blues shuffle, Motown, punk / D-beat, New Orleans second line, disco, house, UK garage 2-step, drum & bass, hip-hop, 2000s R&B, trap, reggae, dancehall, Afro-Cuban (son, rumba, cha-cha), bossa, samba, Bo Diddley and Afrobeat
- Pattern switching **now** or **on the next bar**, tempo 40 to 220 BPM, swing, count-in, metronome
- **Swing** in the MPC / LinnDrum convention: 50 % is straight, 54 % loosens, 58–62 % swings, 66 % is a triplet, 75 % is dotted. The **1/16 · 1/8** button picks what gets swung: 1/16 swings the odd 16ths (funk, garage, house), 1/8 swings the offbeat 8ths and carries the 16ths with them (shuffle, jazz, boom bap on 8th hats). Blues Shuffle wants 1/8 at 66 %.
- **Each style brings its tempo and swing.** Choosing a pattern while stopped sets its tempo, swing and 1/16 · 1/8 (Blues Shuffle 95 BPM, 1/8 at 66 %; Funk 100, 1/16 at 54 %; Drum & Bass 174, straight…). Changing pattern while playing brings the swing but keeps your tempo, so a live switch never makes the BPM jump. A saved setup always recalls its own values.
- **Sampled kits are conditioned when they load**: every sample starts on its attack (some files had 10–20 ms of dead time before the hit, a soft flam against the hats), each instrument is brought to the same level in every kit (they differed by 9–13 dB), and ghost notes sit 8 dB under the kit's snare (in three kits the ghost file was louder than the snare). The synth kits follow the same rule: their ghost is the kit's own snare, 8 dB down. Nothing in the files is changed.
- The hi-hat is one instrument: an open or half-open hat rings until the next hat closes it (choke group, as on every drum machine since the 808)

### Live performance
- **Alteration pads** (with keyboard shortcuts): hi-hat variants, kick variants, syncopation, ghost snare, clap on 2 and 4, snare echoes, and **Broken** (2000s R&B chopped-beat mode with a 2-bar A/B cycle)
- **One-shot fills**: rock, short, tom roll, funk, **relaunch** (a real break: the whole kit cuts for the last two beats, leaving kick then a flammed snare, twice, before the groove slams back on the one), **drag** and **linear**. Plus a hold-to-drop pad.
- **Intros and outros**: seven intros (stick count, crash drop-in, hi-hat build, tom build, snare roll, kick pulse, clave) and five outros (crash and stop, triple hit, tom descent, snare roll out, fade out). An intro plays one bar then hands over to the groove — pressing it from a stop starts the transport; the builds (hi-hat, toms, snare roll) swell and land on the groove's one with crash and kick. An outro starts at the next bar and stops the transport when it ends; every ending lands its last hit on a downbeat and lets it ring. The tom descent and the roll-out keep the groove for two beats, play the figure over beats 3 and 4, and hit on the one of the following bar. Pitched tom figures pick the right drum of a sampled kit (floor or rack) and retune it by at most 4 semitones, instead of speeding up one tom. Keys `I` and `O`.
- **Wildcard** (key `Y`): arm it, and on the next bar the machine draws one gesture from a shuffled bag of 12 (half-time, double-time, beat repeat, beat chop, pushed bar, kick-only breakdown, no-kick breakdown, stop-time, full stop, trap roll, snare build, one drop). You choose *when*, it chooses *what*. Exactly one bar, then back to the groove.

### Groove engine
- **Feel**: 13 microtiming presets that shift each instrument a few milliseconds ahead of or behind the grid, expressed as a fraction of a step so they scale with tempo. Straight, Human Loose, Dilla/Drunk, Boom Bap, Bonham Drag, Motown, Reggae One Drop, Purdie Push, Disco Rush, Punk Speed, Afrobeat (Tony Allen), NOLA Second Line, Jazz Shuffle. An Intensity slider (0 to 150 %) scales the preset. Each style selects its own Feel when you choose it (Funk → Purdie Push, Hip-hop → Boom Bap, Blues Shuffle → Jazz Shuffle…); pick another to override.
- **Dynamics** (default 50 %): the touch of a drummer. The beat is played strong, the "&" lighter, the 16ths between lighter still (about −2 and −4.5 dB at 50 %); light hits use the soft sample layers; each hit varies a hair in level and pitch so a repeated sample never sounds like a machine gun; and the timing wanders slowly like one drummer's clock, the same for every limb — never one limb against the other. Accented hits and written gestures (fills, intros, outros, wildcards) are never turned down: an accent is strong wherever it falls. At 0 % every hit is identical and on the grid: the machine. MIDI export carries the same velocities.
- **Chaos**: variation on the ornaments — ghost notes, opened hats, a lifted hand, rim swaps. Nothing is decided hit by hit. At the top of each 4-bar plan a **figure** is rolled for every bar, locked, and replayed identically while the plan lives (4 bars, played twice, then a fresh plan — about 17 seconds at 110 BPM). Repetition is what makes randomness read as a musical idea instead of noise; Dynamics keeps every hit slightly different on top, so a repeated figure never sounds like a loop.
- **Phrase shape**: a drummer states the groove and opens up at the end of the phrase, so the figure's density follows the bar's position in the plan (weights 0.15 / 0.45 / 0.55 / 1.0 — measured at 0.33 / 1.04 / 1.26 / 2.28 deviations per bar at Chaos 100).
- **Ghost notes follow the hand**: they are drawn as idiomatic cells — a pickup into the backbeat, an answer coming off it, a run leading back to the one — never as isolated hits on random off-steps.
- The kick is never randomized: it is the skeleton the ear locks onto, and displacing or dropping it reads as rhythmic mush rather than variation. Above 40 %, it also carves **structured breaks** into the groove: a 4-bar pause plan is drawn, locked and repeated twice before changing, so holes sound arranged rather than accidental. The silenced zone is dimmed on the grid as the break becomes audible.
- Essential hits (downbeat kick, backbeat snare) are never randomized away.
- **Kick spacing guard**: pattern kicks always play; the one extra kick Broken adds yields if it would crowd them. Deliberate rolls — fills and wildcard gestures — never go through this and are untouched.

### Sounds: 9 kits
- **3 synthesized kits**: Acoustic (wood, skins and air), Electronic (808/909 lineage) and Studio (gated, saturated). Cymbals are built from noise resonators rather than oscillators, so they never collapse into a tone.
- **6 sampled kits**:

| Kit | Source | Character |
|---|---|---|
| Salam. | Salamander Drumkit | Full acoustic kit, velocity layers |
| 808 | Roland TR-808 | The classic |
| DMX | Oberheim DMX | 80s hip-hop, "Blue Monday" |
| Amen | The Amen break | Extracted from 32 slices, lo-fi jungle |
| Jazz | Jazz kit | Small, dark, brushes |
| Rock | Processed acoustic | Heavy mix chain: compression, saturation, low boost |

Any articulation a sampled kit lacks falls back to a matching synth kit, so every pattern plays on every kit.

### Takes
- **Record 4 bars exactly as they play** — the grid, whatever figure Chaos rolled, and the pads you pressed while it ran. Press **● Record 4 bars**: recording arms and starts at the top of the next bar, runs for four, and stops itself. Name it, or keep the suggestion.
- A take is **frozen**: replaying it plays back those four bars note for note. Nothing is regenerated — empty the grid and set Chaos to 0 and the take is unchanged.
- From the list: **▶** loops the take, **♪** downloads it as a MIDI file (GM drum map, same writer as the session export), **✕** deletes it.
- Events are stored in musical time, in steps from the top of the take, so a take follows whatever tempo it is replayed at.
- A take also keeps its **recipe**, step by step: the grid, the groove settings, the pads engaged, the drop held, the fill running, Chaos's locked figure and break for each bar, the Broken phase, the Ghost pad's notes, any wildcard drawn. That is what lets the Song view replay it through the engine and still apply pads to it. Takes recorded before this version have no recipe: they play as recorded, without pads.

### Song view
- **Live | Song** at the top switches views. The Song view lays takes end to end on a **timeline**, like an arrange window: a ruler with bars and beats, one block per section, named by its role (Intro, Verse, Chorus…) and coloured by style: every Funk take in shades of yellow, every Breakbeat take in shades of blue, one shade per take, a thin line between passes, a tick for each recorded pad move. A section plays one take, repeated as many times as you set (a 4-bar take ×4 is a 16-bar verse). The whole song fits the width when it can; a long one scrolls and follows the cursor.
- **Building it**: click a take in the colour palette to add it after the selected block (or at the end), or drag it where you want — a white line shows where it will land, and there is always free room after the last block to drop onto. Drag blocks to reorder them. Click a block to edit it in the bar underneath: swap its take, change its passes, name it, duplicate, copy / paste, move, erase its pad moves, delete. Keyboard: ⌘C ⌘V ⌘D, Delete, ← → to select, Alt+← → to move.
- **Playing it**: a cursor follows the audio (same latency and A/V offset as the live playhead), with bar, beat, time and the section playing. Click the ruler, or drag the orange marker, to choose where Play starts; **⏮** goes back to the top; double-click a block to play from it. Space plays from the start marker; the song stops by itself at the end and lets the last hit ring.
- **The pads work on the song.** Broken, Syncope, the kick and hi-hat variants, Ghost, fills, Drop, the wildcard: everything the Live view does, applied to the take as it plays. **● Rec pads** is armed by default (pressing nothing changes nothing): what you press is written into the section at the step it lands on and replays every time; **⌫** on a section erases its pad moves. A pad move lasts until you press it again or the pass of the section ends.
- There is no note-by-note editing in the Song view, on purpose: a song is arranged with the pads.
- The take replays **identically**: the same hits as when it was recorded, Chaos, Ghost pad and Broken included (verified hit for hit). Tempo and kit apply to the whole song.
- **♪ MIDI** downloads the whole song as one MIDI file, pad moves included. Songs are saved in the browser, like setups and takes.

### Audio tracks
- **Four mono tracks** under the drums in the Song view, for reference vocals or guitars. Each has a small channel strip: name, **R** (arm), **M** (mute), **S** (solo — soloing an audio track also mutes the drums; the click keeps going), volume, pan (double-click to centre), input channel (In 1 / In 2) and a level meter.
- **Recording**: arm one or more tracks, choose the input, press **● Rec audio**. The song plays from the start marker after a **count-in** (**Count-in: Off · 1 bar · 2 bars**, next to the Rec button, 2 bars by default, also used by Play; counted 1-2-3-4 with the one accented, shown as a large translucent number over the interface) and the armed tracks record until you stop or the song ends. A new take covers what was on the track only where it overlaps, so you can redo just a chorus. While recording, each armed lane draws the take as it comes in, in red, up to the cursor. Click a take to select it, then **✕ Delete take** in the bar underneath, the ✕ on the take, or the Delete key.
- **Alignment**: the recording is shifted back by the round-trip latency of your setup. The **A/V auto-calibration** (Setup tab) measures it and fills the **Lat** field; adjust it by hand if takes sound early or late. There is no software monitoring: listen to yourself through your interface or your instrument.
- The audio is stored in the browser's IndexedDB, with the song. It needs a microphone permission, which browsers only give on `https://` or `localhost`.
- **⤓ Export audio** downloads a ZIP for a DAW, everything starting at bar 1: `drums.wav` (the drums rendered exactly as played), one WAV per recorded track (raw, before fader and pan), `mix.wav` (drums plus tracks through the console) and `drums.mid`.

### Setup bank
- **Save** the grid together with every groove setting: tempo, swing, Feel preset and intensity, Dynamics, Chaos, the kit, per-track volume and mutes, and which live pads are engaged. Press **+**, and a field opens pre-filled with a suggested name (`Funk 96`, made unique) — type over it or press Enter to keep it.
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
| `U` `L` | Fills: relaunch, drag |
| `I` `O` | Intro / Outro |
| `M` (hold) | Drop |
| `Y` | Wildcard (arms the next bar) |

---

## Getting started

- **Download the app**: grab
  **[groovygroovabox.html from the latest release](https://github.com/leag1234/groovygroovabox/releases/latest)**
  — one self-contained file, all 9 kits embedded, about 10 MB. Open it in any modern
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
travels with the build: `dist/index.html` is a standalone 10 MB file, and
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

## Picking this up

[`HANDOFF.md`](HANDOFF.md) is the orientation document: architecture, the decisions that
look arbitrary and are not, open items, the release process and the unresolved sample
licensing. Read it before changing the engine.

## Project layout

```
dist/index.html          Ready-to-use build with all sampled kits (deployed at indidea.org)
src/groovygroovabox.html Source, single file, no samples
tools/inject_samples.py  Sample kit injector
kits/                    The sample kits used to build dist/
kits/<kit>/CREDITS       Per-kit attribution, rendered into the build
docs/mockups/            UI mockups (desktop and mobile redesign)
HANDOFF.md               Orientation for whoever picks this up next
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
- **TR-808, Amen break, jazz and rock
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
- The **Rock** kit is a processed derivative of the acoustic sources above
  and inherits whatever terms those carry. An audit found it very likely
  contains processed Salamander samples, and that six of the **Jazz** kit's
  samples (crash, rides, bell, cross-stick, ghost) are Salamander files: the
  CC BY-SA attribution and ShareAlike apply to those, and their `CREDITS`
  say so.

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
