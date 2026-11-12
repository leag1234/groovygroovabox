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
dist/index.html            The build: same app + 9 sampled kits inlined as
                           base64. ~12 MB. This is what ships.
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
  --kit drumtraks "DrumTraks" electronic kits/drumtraks \
  --kit dr55 "DR-55" electronic kits/dr55 \
  --kit amen "Amen" acoustic kits/amen \
  --kit jazz "Jazz" acoustic kits/jazz \
  --kit tight "Tight" acoustic kits/tight \
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
`feel-intensity`, `humanize`, `chaos`, `midi-mappings`.

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
about 17 s at 110 BPM. Humanize still jitters velocity and micro-timing per hit
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
- **12 kits**: 3 synth, 9 sampled.
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

**Song mode — the next thing.** The design was agreed with Gaël but not built:

```
Setup   starting conditions                     (built)
Take    N recorded bars, frozen, reproducible   (built, fixed at 4 bars)
Song    a timeline of sections, each either a
        take (fixed) or a setup played live     (not built)
```

The primitive it needs already exists and is tested: applying something on a
bar line, used by queued pattern changes, queued setup recalls and take
recording. Open questions he has not answered: whether a section can keep some
tracks live over a frozen take, and whether takes should ever be other than 4
bars.

**Known gaps, in rough priority order:**

1. **The Ghost pad still uses unlocked randomness** — `Math.random() < 0.6` per
   hit, outside the chaos figure system. Its positions (2, 6, 10, 14) are
   idiomatic; only the flicker is noise. Same fix as the chaos figures.
2. **Velocity is random, not shaped.** Humanize jitters velocity; musically what
   matters more is a stable hierarchy — strong on 1 and 3, medium on beats,
   quiet on ghosts. Gaël rated this the next-biggest musical win after the
   locked figures. Not started.
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
6. **`dist/index.html` is a 12 MB tracked binary-ish blob.** Every rebuild is a
   full-file diff. It works, but the repository will grow quickly.

---

## 6. Releases

Releases carry `groovygroovabox.html` as an asset because GitHub serves `.html`
from the repo as `text/plain` — the raw link displays 12 MB of source instead of
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
12 MB file, which circulates detached from the README.

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
