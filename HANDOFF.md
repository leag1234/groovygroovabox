# HANDOFF — GroovyGroova Box

Written for whoever picks this up next, human or agent. Read it before touching
the code: several decisions here look arbitrary and are not, and a few of them
cost real work to arrive at.

**Repository:** https://github.com/leag1234/groovygroovabox
**State at handoff:** `d3053e1` on `main`, working tree clean, local == remote.
**Author / owner:** Gaël Duval (GitHub `leag1234`). Concept his, since May 2026.

---

## 1. What this is

A live drum sequencer in **one self-contained HTML file**. 16 steps, 8 tracks,
no build system, no dependencies, no server. You open the file and press Space.

```
src/groovygroovabox.html   The source. ~262 KB, everything in one file.
dist/index.html            The build: same app + 6 sampled kits inlined as
                           base64. ~10 MB. This is what ships.
kits/<kit>/                Samples, plus a CREDITS file per kit.
tools/inject_samples.py    Builds dist from src + kits.
docs/mockups/              UI mockups, not wired to anything.
LICENSE / NOTICE           WTFPL for the code; see §7, the kits are not.
```

### Build

```bash
python3 tools/inject_samples.py src/groovygroovabox.html \
  --kit salamander "Salam." studio kits/salamander \
  --kit tr808 "808" electronic kits/tr808 \
  --kit dmx "DMX" electronic kits/dmx \
  --kit amen "Amen" acoustic kits/amen \
  --kit jazz "Jazz" acoustic kits/jazz \
  --kit rock "Rock" acoustic kits/rock
mv src/groovygroovabox-with-samples.html dist/index.html
```

The kit ids, labels and fallback synths above are **not** arbitrary — they must
match what is already embedded or the kit buttons change. A clean build prints
no `WARNING` and no `Skipped` line. Always rebuild `dist/` before committing a
change to `src/`; they are both tracked and they must agree.

### Run and test

Serve the directory and open it; `file://` will not work for the sample loads.

```bash
python3 -m http.server 8791 --directory .
```

Port **8765 is occupied by Thunderbird** on this machine — using it gives silent
404s that look like a broken build. Pick another.

There is no test suite. Verification is done by driving the page in a browser
and reading the scheduler's own output: stub `window.play` to collect
`{track, time, articulation}` and call `scheduleStep(i, t)` in a loop. That
pattern is used throughout the session history and it is how every claim in the
commit messages was checked. Call `audio()` first or `ctx` is undefined.

---

## 2. Architecture, in one pass

Everything lives in `src/groovygroovabox.html`. Line numbers drift; search for
the symbol names.

**The clock.** `scheduler()` runs on a `setInterval` and schedules ahead into
the Web Audio clock. `scheduleStep(stepIndex, time)` is the heart: it decides
what sounds on one step. `stepDuration()` is derived from BPM. The playhead is
driven by `requestAnimationFrame` reading the audio clock, never by timers, so
it cannot drift under load.

**The funnel.** Every single hit goes through `play(track, time, accent, opts,
articulation)`. Mute checks, chaos pause gates, sample-vs-synth dispatch, MIDI
recording and take capture all hang off it. If you need to observe or intercept
the music, that is the one place.

**Order inside `scheduleStep`.** This matters, because each layer can pre-empt
the ones below it:

```
hold 'drop'        → silence, return
step 0 bookkeeping → take boundary, broken phase, chaos plan, intro/outro
                     handover, queued snapshot / pattern / fill
outro tail         → silence until the scheduled stop lands, return
intro / outro bar  → the gesture replaces everything, return
take playback      → the recording replaces everything, return
wildcard bar       → the drawn gesture replaces everything, return
normal generation  → pattern + alteration pads + chaos figure
```

**Patterns** (`PATTERNS`) are `{name, bpm, pattern: {track: [16 cells]}}`. A cell
is `0` or an articulation string. 23 of them plus `empty`.

**Alteration pads** (`state.alterations`, a Set) transform the pattern live.
Mutually exclusive groups are in `ALTER_EXCLUSIVE_GROUPS`.

**Fills** (`FILLS`) are declarative step maps applied for one bar. Per hit:
`replace` (suppress the pattern's own hit on that track and play this one),
`mute` (suppress without playing), `off` (fractional step offset), `accent`,
`art`, `opts`. Per fill: `minStart`, and `silenceFrom` (from that step, cut the
whole kit so only the fill's hits sound — this is what makes a break a break).

**Wildcards, intros, outros** are one-bar gesture objects:
`events[step] = [{track, art, accent, off, opts}]`, replacing everything for
that bar. `INTROS` hands over to the groove when its bar ends and starts the
transport if fired from a stop; `OUTROS` stops the transport instead.

**Kits.** `KITS` holds the three synth kits; sampled kits are injected as
`window.CUSTOM_SAMPLE_KITS` and fall back to a synth kit per missing
articulation. `GM_MAP` maps (track, articulation) to General MIDI.

**Persistence**, all in `localStorage` under `groovygroova:`:
`bank` (setups), `takes`, `av-offset`, `display-comp`, `feel-mode`,
`feel-intensity`, `humanize`, `chaos`, `midi-mappings`, `songs`. (`humanize` and
`chaos` are purged at load, not restored. `state.humanize` is now the
**Dynamics** slider; the name was kept so saved setups recall it.)

---

## 3. Decisions that must not be casually undone

Each of these was arrived at by listening or measuring, and each is easy to
"fix" back into the problem it solves.

**Chaos never touches the kick.** It used to displace, drop and stutter it.
That reads as rhythmic mush, not variation: the kick is the skeleton the ear
locks onto. The kick is now fully deterministic — pattern, kick pads, and the
Broken half-step shift, which is deliberate and *is* the mode. Verified: the
kick sequence at Chaos 100 is identical to Chaos 0.

**Chaos repeats itself.** It used to be `Math.random()` per hit, per step, per
bar. Nothing ever repeated, so nothing read as intentional. Now `rollChaosFigure`
rolls one bar's deviations once into a 4-bar plan (`rollChaosPlan`), and that
plan is replayed identically twice before a fresh one is drawn —
`CHAOS_PLAN_BARS = 4`, `CHAOS_PLAN_REPEATS = 2`, so a new figure every 8 bars,
about 17 s at 110 BPM. Dynamics still varies level and pitch a hair per hit
on top, which is what stops a repeated figure sounding like a loop.
**Do not reintroduce per-hit randomness.** `chaosP()` was deleted for this
reason; if you see it come back, something regressed.

**Variation follows the phrase.** `PHRASE_WEIGHT = [0.15, 0.45, 0.55, 1.0]`:
the groove states itself, then opens up at the end of the phrase. Measured over
4000 plans at Chaos 100: 0.33 / 1.04 / 1.26 / 2.28 deviations per bar.

**Ghost notes come in cells**, not as coin flips on empty off-steps — see
`GHOST_CELLS`: a pickup into the backbeat, an answer off it, a run back to the
one.

**The kick spacing guard** (`scheduleGroovedKick`) lets pattern kicks always
play and makes only randomly-added ones yield. With Chaos off the kick it has
little left to do, but it still governs Broken's extra ghost kick.

**Hi-hat and ride honour `replaced`.** They did not, for the whole life of the
project, unlike the other six tracks — which meant no fill could ever silence
the time-keeping hand. That is why the relaunch was decoration instead of a
break. Each hat and ride voice checks it individually now.

**Takes are stored in musical time** — position in steps from the top of the
take, not seconds — so a take follows whatever tempo it is replayed at, and
MIDI export converts steps to ticks directly.

**The setup bank deliberately excludes** the A/V calibration offset and the
master volume. They belong to the machine you are listening on, not to the
music. Recalling a setup must never change how loud the box is.

**Swing uses the MPC / LinnDrum scale.** `state.swing` is 50–75: the share of
each pair the first note takes, 66 = triplet. It used to be the odd 16th's delay
in percent of a step (0–60, triplet at 33) while every hint in the app quoted
MPC numbers, so following a hint over-swung the groove ("55 %" was ~77 % MPC).
`state.swingRes` is 16 or 8. 1/16 only moves odd steps, which does nothing at
all to the nine patterns whose hits all sit on even steps — Blues Shuffle could
never shuffle. 1/8 moves the offbeat 8th to `p` of the beat and puts the 16ths
in between halfway inside their swung 8th (`swingOffsetSteps`). Bank entries
carry `swingScale: 'mpc'`; entries without it are converted on recall by
`swingFromLegacy` (50 + old/2).

**A style brings its tempo and swing** (`applyStyleDefaults`, called from
`loadPattern` and at boot). Stopped: tempo, swing and 1/16 · 1/8. Playing: swing
and resolution only — Gaël's call (2026-11-12): a live pattern change must not
make the BPM jump. Bank recalls set `state.pattern` directly and never go
through `loadPattern`, so a saved setup keeps its own values.

**Dynamics replaced Humanize** (2026-11-12, agreed with Gaël). Humanize rolled
an independent random timing and velocity offset per hit: white noise, kick
and hat on the same step flammed by up to 13.6 ms, and the research says that
does not add groove. Dynamics (`dynamicsWeight`, `dynamicsDriftAdvance`):
1. a deterministic level per metric position (`DYN_DB`, scaled in dB by the
   slider), known through `currentStepPos`, which the scheduler sets around
   each `scheduleStep` and takes store per event (`p`) so a swung hit keeps
   its written position; live pads and MIDI in have no position, full weight;
2. that weight picks the sample layer (under 0.85, the softest; the bottom
   layer of a 3-layer set was never played before) and the MIDI velocity;
3. a timing drift shared by every track on a step, sum of three AR(1) at
   poles 0.6 / 0.95 / 0.995, 2.5 ms SD at 100 %. Measured: lag-1
   autocorrelation 0.86, lag-64 0.22, kick-vs-hat flam 0.
At 0 everything is exactly the machine: verified all weights 1, all hits on
the grid. Default is 50 %. Chaos and the setup bank are unchanged.

**The hierarchy never touches accents or written gestures.** Found by Gaël's
ear: the relaunch snares (accented, on the e of 3 and 4) came out ~3 dB under
the backbeat at Dynamics 50. `dynamicsWeight` returns 1 for accented hits, and
`playWritten` plays fills, intros, outros and wildcard hits with no position
(takes record that as `p: null`). Measured after: relaunch and Syncope snares
within 1 dB of the backbeat. Synth kits' ghost is now the kit's own snare
8 dB down; it was a separate noise burst 17–25 dB under the snare.

**Intros and outros reworked** (2026-11-12, Gaël: "some outros are really
miserable, the tom descent especially"). What was wrong, measured:
- on sampled kits, every pitched tom hit played the *middle* tom sped up by
  `pitch/110`: the descent was one rack tom at ×1.82, ×1.59, ×1.41…, and the
  floor tom never played. The shipped kits hold a floor tom and one or two
  rack toms (Salamander ~66 Hz and two takes at ~139 Hz). `tomVoice` maps the
  requested pitch onto the kit's measured range (`kit.toms`, DFT at load),
  picks the nearest real drum and retunes it by ≤ 4 semitones. Applies to
  fills and wildcards too;
- the tom descent and the roll-out landed on beat 4 and then stopped, which
  sounds like a mistake. Every ending now lands on a downbeat and rings;
- the final crash sat 3–6.5 dB under the snare (crash fader 0.3).
  `ENDING_CRASH_VEL` lifts it to 1–4.5 dB under.
Gesture engine: `bars` (1 or 2, events indexed `bar * 16 + step`),
`grooveUntil` (the groove keeps playing under the first steps of bar 0),
per-event `vel`, and `land` on intros (sets `pendingResolve` at handover).
Outros: crash and stop (+ floor tom), triple hit (flammed last hit + floor +
crash), tom descent and roll-out (2 bars, groove for beats 1–2, figure over
3–4, hit on the next one), fade out (2 bars of decreasing level, was "thin
out"). Intros: hat build, tom build and snare roll swell (`vel` ramps) and land.
Not changed: the landing doubles the kick on the groove's one (the groove's
kick plus the resolve's), as fills always did.

**Accented snares and toms in written gestures get +3 dB** (`GESTURE_ACCENT_DB`,
Gaël asked for the relaunch snare to be "at least as loud, even slightly
louder"). At equal level it read as weaker: in a break the kit is cut and the
snare speaks alone, while every groove backbeat lands with the hat. Measured
in the full mix before: relaunch ~5 dB under the groove's backbeat moment on
Salamander. After: relaunch snare 2–3 dB over the groove snare on every kit,
peaks −1.8 dBFS or lower. Takes keep the lift (`w` on recorded events).

**The synth claps were inaudible** (found by Gaël: "Clap 2&4 does nothing").
They sat 18.5 (Acoust.), 19.2 (Electr.) and 27.2 dB (Studio) under their kit's
snare, so the pad added 0.0–0.1 dB on 2 and 4. Recalibrated to ~2.5 dB under
(Studio ~7 dB under: its gated clap is all peak, and Salamander borrows it).
Also: a sampled kit's borrowed synth voices now take `SAMPLE_HEADROOM_DB` like
its samples; without it Salamander's borrowed clap stood 4 dB over its snare
and clipped. Measured after: the clap adds 1–4 dB on every kit, and the Rock
groove with claps peaks under 0 dBFS everywhere (Studio −0.1).

**A style also brings its Feel** (`STYLE_FEEL`), and Intensity back to 100 %.
Intensity is capped at 150 % (it went to 300 %, where Dilla put the backbeat
0.6 of a step late). Saved intensities above 150 are clamped on load.

**Sampled kits are conditioned at decode** (`analyseSampleKit`, 2026-11-12),
after an audit of the 160 shipped files. Nothing in `kits/` is edited, so a new
kit gets the same treatment:
- each buffer starts 2 ms before its first point within 20 dB of peak
  (`kit.starts`, passed as the `start()` offset, 1 ms fade-in). Rock's kick
  transient was 15.6 ms into the file, Salamander's 10.1 ms; now every
  kit's kick, snare and hat sound within 2 ms of the trigger, measured;
- one gain per (kit, track) brings the default sample to the median of the
  shipped kits (`SAMPLE_TARGET_RMS_DB`, RMS over 200 ms from onset), capped
  at ±8 dB, minus `SAMPLE_HEADROOM_DB` = 4. Kick levels now agree within
  0.1 dB across the nine kits. The headroom is not optional: aligned
  transients and raised quiet kits took the Salamander funk groove to
  +3.5 dBFS; with it every kit peaks between −0.9 and −4.8 dBFS;
- ghost notes are set 8 dB under the kit's snare (cap ±20 dB; 12 at first,
  too buried by Gaël's ear): Salamander,
  808 and Jazz ghosts were louder than their snare.
Side effect: sampled kits are about 4 dB quieter than the median kit was.
Not fixed: the synth kit `studio` peaks at +2.3 dBFS on the same groove (it
did before), Jazz has DC offset on snare and toms, and the low tom (layer 0) is never played by any kit.

**The 808 hi-hat was a conga.** Fischer's set names the High Congas `HC`;
`kits/tr808/hh__closed__*` and `hh__foot` were taken from `808hc` (3 % of the
energy above 2 kHz). They are now `808/CH.WAV`, the set's only closed hat (93 %),
same source and terms as the rest of the kit. The snare's soft layer and its
ghost were a snappy-off snare (1 % above 2 kHz, a thud); the soft layer was
dropped and the ghost is the default snare, set 8 dB down at load.

**Takes replay unswung grid time.** Recorded positions already contain the
swing the scheduler applied, so `scheduleStep` hands `takeScheduleStep` the
grid time minus this step's swing. Before that, a take recorded with swing was
swung a second time on replay. Verified: 108 events recorded at Swing 1/8 66 %,
108 identical positions replayed.

**Open and closed hat share a choke group.** Every hi-hat hit calls
`hatChokeAt(time)`; an open, half-open or open-close voice is built on its own
gain (`hatOpenVoice`, via the `voiceBus` override in `masterGain`) so the next
hat can close it with a ~50 ms pedal-like release. Sample and synth kits alike.
Measured with an offline render: the Salamander open hat (3 s) left −36 dB of
ring 0.5–1 s after a closed hat; it now leaves nothing above the closed hat
alone.

**Song view: a take is a recipe, replayed through the engine.** Gaël wants
every live pad usable on recorded material, so frozen hits were not enough.
Since `TAKE_VERSION = 2`, `takeRecordFrame` (called by the scheduler after
each step while recording) stores what moved: grid, swing, feel, Dynamics,
Chaos, pads, held drop, running fill, the bar's chaos figure and break, the
Broken phase (`bp`) and the Ghost pad's notes (`gm`); wildcards drawn go in
`recipe.wcs`. The hits are still stored (`events`) for the take's MIDI and as
the fallback for old takes. Playing a song (`arr`, `arrBeforeStep` at the top
of the scheduler loop) sets the engine from the take's frame, applies the
section's pad automation (`section.auto`: `{type, id, on, rep, k}`), and lets
`scheduleStep` generate as usual; `activeChaosFigure`, `activeChaosPauseType`
and `activeGhostMask` return the recorded values while `arr.playing`.
Verified with a virtual clock: Funk + Chaos 70 + Broken + Syncope + Relaunch,
Rock + Chaos 100 + Ghost, R&B + Broken + Ghost — the song replays the take
hit for hit on every pass. Pad moves live inside one pass of a section
(`arr.over` is cleared at each pass). Song MIDI export runs the song headless
(`midiCollect` in `play()`). **Takes are recorded from the first step after
arming if that step is a bar line** — the take covers the bar that starts
then, which caught a test of mine out.

**The Song view is a timeline** (2026-11-13, Gaël: the card list took too
much room and showed no time). One lane; blocks `left = startG / 16 * px`,
`px` fitted to the width with an 18 px/bar floor (then it scrolls and follows
the cursor). Colours come from a hash of the take id (`takeColor`), so a take
keeps its colour. The cursor is its own rAF loop (`arrCursorLoop`) reading
`arr.vq`, filled by `arrBeforeStep` with each scheduled step's time, with the
same latency/A-V offset as `playheadLoop`. Play starts at `arr.startG`
(ruler click, always a bar line). Edits go through `arrEdit` (stops playback,
except for renaming). The pad keyboard handler now ignores ⌘/Ctrl, or ⌘C/⌘D/⌘V
would also have fired the C, D and V pads.
Second pass after Gaël's review: colours by style (`STYLE_HUES`, one hue per
pattern, shades by recording order; takes now store `style`, older ones are
matched by name), a free drop zone after the last block plus a white
insertion line while dragging, a draggable start marker and a ⏮ button.

**The Ghost pad is locked** (it was known gap 1): `rollChaosPlan` also rolls
`ghostMasks`, one per bar, replayed with the plan, instead of a 60 % coin on
every hit. Without it no song could replay the same way twice.

**MIDI velocity now carries everything the ear gets** (`midiOpts.midiMul` in
`play()`): written `vel` (intro/outro crescendos, the ending crash), the
+3 dB gesture accent and the per-hit variation, on top of the metric weight.
Timing always did: MIDI is recorded at the scheduled time, swing, feel,
drift and flams included.

**The keep-alive tone is at −66 dBFS**, not −42 (`startAudioKeepAlive`). The
27 Hz sine started at the first Play keeps HDMI / soundbar / virtual-driver
outputs from powering down between plays. At −42 dBFS Gaël heard it on
headphones as a constant low rumble that only stopped when the tab closed.
If first beats start getting swallowed again on a display or soundbar
output, this level is the knob — raise it a little, do not remove it.

**Space is play/stop**, with Enter still working. `ownsKeys` skips the global
handler when a focused control owns the key — selects, text inputs, checkboxes,
contenteditable. Range sliders and buttons are deliberately *not* skipped: Space
does nothing to a slider, and a pad clicked with the mouse keeps focus, where
swallowing Space would leave transport dead. A focused button is blurred on
transport keys so it cannot re-fire.

**Keyboard map** (free letters left: none worth taking):

```
Space / Enter  play / stop        Q W E R   hi-hat variants
A S D F G H    kick variants      Z X P     syncope, ghost, clap 2&4
J K            snare echoes       T         Broken
C V B N        fills              U L       relaunch, drag
M (hold)       drop               Y         wildcard
I O            intro / outro
```

---

## 4. What exists, feature by feature

- **23 patterns.** Four were corrected because they did not match the thing they
  are named after: House had the pedal hat on the upbeats instead of the open
  hat; Bo Diddley's last kick was on step 14, neither son nor rumba clave, now
  12; Bossa's rim was on no clave at all, now the bossa clave 0/3/6/10/13;
  Cha-cha had two 16ths stuck together instead of three even notes.
  Eight were added: Blues Shuffle, Motown, Punk / D-Beat, Second Line, UK Garage
  2-Step, Drum & Bass, Dancehall, Afrobeat.
- **7 fills**, including `fill-relaunch` — a real break: the kit cuts for the
  last two beats, leaving kick then a flammed snare, twice, before the groove
  slams back on the one. The flam is a grace note 15 ms ahead of the stroke.
- **7 intros, 5 outros.**
- **9 kits**: 3 synth, 6 sampled. DR-55 (4 real sounds, 10 slots on the synth
  fallback), DrumTraks (a weaker DMX, open hats cut at 0.21 s) and Tight (12
  of its 19 files were Salamander) were removed on 2026-11-12, Gaël's call
  after the kit audit. Gaël kept the synth Acoust. as the boot kit. Setups
  saved on a removed kit recall everything but the kit.
- **Setup bank**: saves the grid plus every groove setting; recall honours the
  Now / Next bar switch.
- **Takes**: record exactly 4 bars starting at the next bar line, frozen, all
  eight tracks. Replay loops them; MIDI export per take. Verified frozen by
  emptying the grid and setting Chaos to 0: 77 events in, 77 identical out.
- **MIDI**: session export and per-take export share `toMidiEvents` so the GM
  mapping cannot diverge. MIDI learn for controllers.
- **A/V calibration** via microphone loopback, with a manual fallback.

---

## 5. Open items

**Song mode — built (2026-11-13), first version.** Gaël's brief: a second
view where takes recorded live are laid end to end into a whole song, with
the live pads usable afterwards (a break, a syncope…) and recorded into the
song, and **no note-by-note editing** there. Next on his list: recording a
reference vocal or guitar as audio, synced, exportable. See "Song view" in §3.

**Known gaps, in rough priority order:**

1. **Song view, first version.** Not done yet: intros/outros pressed in the
   song are played but not recorded; songs and takes cannot be exported or
   imported as files (gap 5 below matters more now); no undo for pad moves
   beyond erasing a section's; a section is always a whole take.
2. **Velocity is now shaped (Dynamics), but the weights in `DYN_DB` are a
   first guess**, not yet confirmed by ear. Hats and ride: beat 0, & −4, e/a
   −9 dB at 100 %; kick 0/−1/−2/−4; snare backbeat 0, elsewhere −3/−5; ghost
   notes untouched. There are no true round-robins — the kits ship 2–3 files
   per sound, used as velocity layers — so the anti-machine-gun is a ±1 dB,
   ±10 cent per-hit variation, a stopgap until kits have alternates.
3. **Trap has no hat rolls**, its defining feature, because the 16-step grid
   cannot express triplets or 32nds. Would need sub-step events, which `off`
   now makes thinkable.
4. **The per-style swing values in `STYLE_SWING` are starting points**, not
   yet confirmed by ear (Shuffle 66/8, Second Line 62/8, Hip-hop 56/8, Funk
   and Breakbeat 54/16, Garage 58/16, everything else straight).
5. **No export/import of the bank or takes.** `localStorage` is per-origin, so
   setups saved on `localhost` do not follow to `indidea.org` or to the
   downloaded file. A JSON export would fix it and is probably a prerequisite
   for song mode being useful.
6. **`dist/index.html` is a 10 MB tracked binary-ish blob.** Every rebuild is a
   full-file diff. It works, but the repository will grow quickly.

---

## 6. Releases

Releases carry `groovygroovabox.html` as an asset because GitHub serves `.html`
from the repo as `text/plain` — the raw link displays 10 MB of source instead of
downloading. The release asset is served with `Content-Disposition: attachment`.

```
v1.2.0 -> f725e95   latest
v1.1.0 -> e1b0770
v1.0.0 -> 1db0941
```

**`v1.2.0` is behind `main`.** It predates the rhythm library rework
(`61fc8ef`) and the relaunch fix (`d3053e1`). A `v1.3.0` is owed.

Publishing needs a fine-grained token (Contents: read and write, that repo
only) that **Gaël creates**; there is no `gh` CLI and no stored credential. The
agreed handoff is a file he writes himself, never pasted into chat:

```bash
install -m 600 /dev/null ~/.ggb-release-token && printf 'Token : ' && read -rs T \
  && printf '%s' "$T" > ~/.ggb-release-token && unset T && echo && echo ok
```

Read it into a `curl -K` config file rather than putting it on the command line,
delete that config when done, and tell him to revoke the token. One failure mode
already bit us: the file held a stale value while the token entry still existed
on GitHub, which looks exactly like a revoked token. Check the file's mtime
against when he created the token before concluding anything.

---

## 7. Licensing — read this before redistributing anything

The code is **WTFPL** (`LICENSE` verbatim, `NOTICE` for copyright and scope).
The sample kits are **not**, and this is genuinely unresolved:

- **Salamander Drumkit** — Alexander Holm, **CC BY-SA 3.0**. Attribution is
  required and ShareAlike applies to adaptations, which the re-encoded samples
  are.
- **TR-808** — Michael Fischer / Technopolis, 1994. The source text says the set
  is free of charge but grants **no redistribution terms**.
- **Amen break** — derived from "Amen, Brother" (The Winstons, 1969), a
  copyrighted recording never licensed for reuse. **Status undetermined, and
  this is the real exposure in a public repository.** Gaël has been told twice
  and has chosen to keep it; that is his call, not a thing to re-litigate, but
  do not make it worse by promoting the kit.
- **Oberheim DMX** — source unverified; there is no `dmx` folder in
  Dirt-Samples, so its origin is undocumented.
- Everything else via Dirt-Samples, which ships no license file and documents
  provenance for only the `808` folder.

Attribution is rendered **into the build** from `kits/<kit>/CREDITS` by
`inject_samples.py` at the `<!-- SAMPLE-CREDITS -->` marker, as static markup so
it survives JavaScript being disabled. A kit without a `CREDITS` file builds but
warns. Do not remove this: for CC BY-SA the notice has to travel inside the
10 MB file, which circulates detached from the README.

Samples were re-encoded through ffmpeg and renamed to a normalised scheme, so
original filenames and metadata are gone and no sample can be traced to a
specific upstream file. Re-establishing that mapping is outstanding work.

---

## 8. Working with Gaël

Things that were learned the hard way and will save you a round trip:

- **He arbitrates musicality by ear.** Measurements are good for "this repeats"
  and "this stays legible"; they say nothing about whether it grooves. Build the
  mechanism, then put it in front of him and ask.
- **Verify, do not assert.** Several claims that seemed obvious were wrong —
  the relaunch was not a break, the hats ignored `replaced`, a fill's lookahead
  consulted the raw pattern and missed the kick pads. Measure before reporting.
- **Do not invent explanations.** He catches it. When you do not know why
  something is behaving a certain way, say so.
- **No lecturing**, particularly about security hygiene on his own account. State
  the risk once, plainly, then do what he asked.
- **Never wipe his `localStorage` while testing.** The bank and takes live under
  the same keys the app uses. Back the key up, restore it, and say that you did.
  Test entries left behind (`Rock 88`) have already annoyed him once.
- He wants the commit pushed and the build regenerated as part of "done", not as
  a follow-up question.
