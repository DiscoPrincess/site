# Lyric pipeline

Ordinary pushes publish the site from committed `playlists.json`, `tracks.json` and `lyrics/`, without fetching Treblo or installing audio models. `.artist-core/scripts/build_site.py` regenerates pages and asset hashes, then applies the inexpensive timing fallback described below to the published copy of the saved lyrics. No audio analysis runs during publication.

The separate **Analyze DiscoPrincess lyrics** workflow runs daily, manually, or when catalog configuration or analysis code changes. It imports all configured public playlists, then processes up to three new or changed tracks per run in playlist order; cached tracks do not consume the budget. Later daily runs continue through the remaining tracks. Set `LYRIC_MAX_NEW_TRACKS` or `lyric-config.json` to adjust the CPU budget.

1. Preserve source lines and original wording. Retain unusable source lines and full written lyrics for recovery rather than silently deleting them.
2. Align against the original mix with wav2vec2, allowing small padding around Treblo's times. Keep good words even if a neighbouring word is uncertain. The recognition output retains missing timings; publication estimates eligible gaps separately, with explicit provenance.
3. Separate a vocal stem with Demucs htdemucs; cache the stem by audio URL.
4. Decode the original mix with multilingual Whisper base and the vocal stem with multilingual Whisper small, without a lyric prompt. Detect language from the audio.
5. Recover missing timing by matching supplied text to recognized passages. Attempt known-text word alignment on the vocals with wider windows, retaining better first-pass results.
6. Automatically correct a line only when both decoding passes agree on normalized text, every proposed word meets a 0.85 recognition-score threshold, timestamps agree within 0.5 seconds, and the change is close to the source wording. These are conservative heuristics, not proof: both models can share errors, especially in sung, repeated, or invented phrases.
7. Keep the original, replacement, time and provenance for every correction. Uncertain alternatives go into the review report and do not replace displayed words.

`lyrics/report.json` gives coverage, first-pass baseline, corrections, queue status and warnings. `lyrics/review.json` gives suggestions and corrections for review. Coverage measures how much has timing, not the accuracy of that timing. Listening checks are still necessary.

## Estimated playback timing

`.artist-core/scripts/estimate_lyrics.py` runs during the fast build, after recognition. Recognized words remain unchanged. Missing words share the interval between recognized anchors, or between an anchor and the supplied line boundary. For a whole line without recognized words, the supplied line interval is divided using approximate syllable and character weights. This is interpolation, not beat detection or new speech recognition, and depends on the line boundaries being correct.

Estimates carry `estimated: true`, `score: 0`, and `timingSource`. Recognition coverage remains separate from `estimatedWords` and `playbackCoverage` in the published report. Estimates are derived only for the deployed copy, so they never enter the model cache or count as recognition evidence. Invalid bounds, overlapping anchors, mismatched word lists and gaps too short to fit words are left unchanged. Missing line boundaries cannot be recovered by this fallback.

`lyric-overrides.json` supports reviewed fixes:

```json
{"track-uuid": {"Original source line": "Correct words heard in the audio"}}
```

Changes to overrides, source lyrics, configuration or the audio URL invalidate the result cache. Increment `VERSION` in `.artist-core/scripts/build_lyrics.py` when changing model/acceptance behavior. If audio changes at an unchanged URL, increment that version to force reprocessing.

Enhancement errors retain the first-pass result, are reported, and retry on later runs. A successfully processed track with no usable word timings falls back to whole-line display. An initial pass adds overhead on CPU; subsequent analysis reuses cached results and models. Results and refreshed catalogs are committed to the repository; successful analysis triggers the fast publishing workflow. UI changes never advance the analysis queue. The publishing job cancels older deployments so stale builds cannot replace newer UI. All processing stays in CI; visitors download small JSON timing files.

