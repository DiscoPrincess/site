# Lyric pipeline

Each deployment imports all configured public playlists. The pipeline processes up to three new or changed tracks per run in playlist order; cached tracks do not consume the budget. Later daily runs continue through the remaining tracks. Set `LYRIC_MAX_NEW_TRACKS` or `lyric-config.json` to adjust the CPU budget.

1. Preserve source lines and original wording. Retain unusable source lines and full written lyrics for recovery rather than silently deleting them.
2. Align against the original mix with wav2vec2, allowing small padding around Treblo's times. Keep good words even if a neighbouring word is uncertain. Untimed words remain visible and do not get fabricated timestamps.
3. Separate a vocal stem with Demucs htdemucs; cache the stem by audio URL.
4. Decode the original mix with multilingual Whisper base and the vocal stem with multilingual Whisper small, without a lyric prompt. Detect language from the audio.
5. Recover missing timing by matching supplied text to recognized passages. Attempt known-text word alignment on the vocals with wider windows, retaining better first-pass results.
6. Automatically correct a line only when both decoding passes agree on normalized text, every proposed word meets a 0.85 recognition-score threshold, timestamps agree within 0.5 seconds, and the change is close to the source wording. These are conservative heuristics, not proof: both models can share errors, especially in sung, repeated, or invented phrases.
7. Keep the original, replacement, time and provenance for every correction. Uncertain alternatives go into the review report and do not replace displayed words.

`lyrics/report.json` gives coverage, first-pass baseline, corrections, queue status and warnings. `lyrics/review.json` gives suggestions and corrections for review. Coverage measures how much has timing, not the accuracy of that timing. Listening checks are still necessary.

`lyric-overrides.json` supports reviewed fixes:

```json
{"track-uuid": {"Original source line": "Correct words heard in the audio"}}
```

Changes to overrides, source lyrics, configuration or the audio URL invalidate the result cache. Increment `VERSION` in `scripts/build_lyrics.py` when changing model/acceptance behavior. If audio changes at an unchanged URL, increment that version to force reprocessing.

Enhancement errors retain the first-pass result, are reported, and retry on later runs. A successfully processed track with no usable word timings falls back to whole-line display. An initial pass adds overhead on CPU; subsequent publication reuses saved results and models. All processing stays in CI; visitors download small JSON timing files.
