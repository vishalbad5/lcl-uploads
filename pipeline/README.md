# LAST CANDLE LEFT — daily Shorts pipeline

Channel: LAST CANDLE LEFT (YouTube @lastcandleleft, channel ID UCWnVL9vYPRuEMpv_88284qQ). Owner: Vishal (calls Claude "Nyx").
Niche: real mysteries, dark history, unexplained phenomena, UFO/UAP, vanishings, strange true people.

## Hard rules (owner's standing rules)
- Every video AND every thumbnail is 9:16, 1080x1920, 30 fps.
- 50-70 s total including the outro. Hook in the first 1.5 s: the strangest fact first, no title card, no date opener.
  The first frame must already show the strange thing (it is the feed thumbnail).
- Visual change every 1.5-2 s; camera always moving; word-by-word captions (Montserrat Black, key words amber, danger words red).
- Open loop around the 60 % mark; end with an either-or question that becomes the pinned comment.
- Candle outro, about 3-5 s: teaser "NEXT: <next episode topic> / EPISODE <n+1>", then
  "REAL STORIES. UNANSWERED QUESTIONS." and "FOLLOW FOR THE NEXT STORY."
- Title: hook first, under 60-70 chars, then "| Ep 0NN #tag #shorts". Never start with "EPISODE".
- Description: first line is a keyword sentence; note "Visuals recreated for this video." (and "Sound recreated" if a sound is synthesized);
  the question; "🕯️ Follow LAST CANDLE LEFT for real stories and unanswered questions."; 5-6 hashtags incl. #shorts. Tags: 10-15 relevant.
- Facts: check every claim against sources found with web search before scripting. Say "claimed", "some believe", "unverified"
  where that is the truth. Never invent quotes, numbers or dates. Never present a recreation as real footage or a real recording.
- Each episode gets its OWN visual style that matches the story (ep011: deep-ocean sonar + spectrogram; ep012: military thermal camera HUD).
  Reuse the engine, not the look.
- Content mix (Vishal, 24 Nov 2026: "a mix, not just one niche"): rotate 6 lanes. The 3 videos of a run come from 3 DIFFERENT lanes,
  and every 2 runs cover all 6. Lanes: (1) Myths & legends (creatures, curses, folklore; told as legend + the real origin),
  (2) Horror / creepy true cases (unsettling real events, haunted places as "claimed"), (3) UFOs / UAP & space signals,
  (4) Conspiracies (the claim vs the evidence; documented real ones like MKUltra/Northwoods say so; never present a false one as true),
  (5) Sci-fi but real (real science that sounds like sci-fi), (6) Unsolved / vanished / dark history.
- Scroll-stop test: pick a topic only if its FIRST SECOND can show one strange, specific image that needs no context
  (a man in a lead mask, animals turned to stone). Prefer lesser-known over over-covered classics (Dyatlov, Mary Celeste, Kola style).
  Write the hook in "you"/present tense where it fits.
- FRESHNESS RULE (Vishal, 24 Nov 2026): EVERY topic, in every lane, must ALSO be either
  (a) trending right now - in the news, viral or newly released in roughly the last 2 weeks (new footage, declassified files,
      a new discovery, an anniversary this week, a story going viral on Reddit/X/TikTok), or
  (b) little-known - a real, verifiable story most viewers have never heard of.
  Aim for at least 1 of the 3 daily videos to be (a). Find them with free WebSearch ("<lane> news this week", "newly declassified",
  "scientists baffled", "rare footage", "this day in history <date>"); vidIQ is optional. Fact-check (a) items extra hard -
  viral claims are often wrong. In the description, say why it is new where true ("New footage released this month").
- No remakes of old episodes. Topics already used are listed in episodes.md — never repeat one.

## Setup in a fresh session
```
git clone --depth 1 https://github.com/vishalbad5/lcl-uploads /home/claude/lcl-uploads   (use add_repo owner=vishalbad5 repo=lcl-uploads access=push first)
pip install --break-system-packages -q kokoro-onnx soundfile
mkdir -p /home/claude/models && cd /home/claude/models
curl -sL -o kokoro.onnx https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx
curl -sL -o voices.bin  https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin
```
Fonts used (present in the workspace): Montserrat[wght].ttf, Anton-Regular.ttf, Inter / InterDisplay.

## Per-episode build (work in /home/claude/epNNN, link ../models as models)
1. Script: ~120-150 words, short lines, one idea per line.
2. Voice, one of:
   - Premium (vidIQ "George - Warm, Captivating Storyteller", voiceId JBFqnCBsd6RMkjVDRZzb, 28 credits per <=1000 chars):
     vidiq_voiceover_generate with scriptLines; download the full audioUrl with curl (assets.vidiq.com is allowed);
     cut it into lines with each line's startSeconds/durationSeconds and re-place them with dramatic gaps (0.1-0.9 s).
   - Free: Kokoro voice bm_george, lang en-gb, built phrase by phrase (see examples/ep011_voice_kokoro.py): per-phrase speed 0.8-1.1,
     pauses, small pitch moves on reveals, soft synthetic breaths/sighs, whispered ending. Check pronunciations with
     k.tokenizer.phonemize (write years as words, e.g. "nineteen ninety-one"; "dived" not "dove").
   Captions: after the voice is made, rewrite spoken numbers in voice_meta.json phrase text as digits ("nineteen hundred" -> "1900") BEFORE align_words.py, so captions show digits and word timings stay aligned.
   Either way write voice_raw.wav and voice_meta.json {"total": sec, "phrases":[{"i","text","start","end","flags"}]}.
3. `python3 ../lcl-uploads/pipeline/align_words.py` -> words.json (caption timing). Also note key word times for cues.
4. Music + sound design in numpy (see examples/*_music.py): drone with a tension curve, pulses, risers into reveals,
   impacts on hits, story-specific effects, candle bells in the outro. Write music.wav (48 kHz stereo).
5. `sh ../lcl-uploads/pipeline/mix.sh` -> mix.wav (-14 LUFS, voice ducks the music).
6. Visuals: render.py = engine_head.py + your scenes file + engine_tail.py (cat them together). The scenes file defines scene
   functions, the SC list [(start, end, fn)], and IMPACTS (times for shake/flash). Helpers: grad, snow (particles), glow_img,
   sharp_img, screen, label (big title), tag (typed small text), draw_caption (automatic from words.json), VIG/GRAIN.
   Look at examples/ep011_scenes.py and examples/ep012_scenes.py.
   - First: `python3 render.py still t1 t2 ...` at the busiest moments, make a contact sheet, LOOK at it, fix problems.
   - Then render scenes in 2 parallel workers: `python3 render.py scenes 0 2 4 ...` and `... 1 3 5 ...` -> scene_XX.mp4.
7. `sh ../lcl-uploads/pipeline/encode.sh LastCandleLeft_Ep0NN_<Slug>.mp4 <number of scenes>` (target < 50 MB), then decode-check
   and grab frames at several times to confirm captions and scenes line up with the voice.
8. Thumbnail 9:16 1080x1920 JPEG: the story's key visual + 2-3 huge words (Anton) + "EP 0NN · <hook>" pill (examples/*_thumb.py).

## Upload path (YouTube via vidIQ)
- vidIQ refuses direct file uploads from this workspace. Host the files on branch `upload-test` of vishalbad5/lcl-uploads:
  orphan commit containing only the mp4s, `git push -f origin <local>:upload-test`, then
  vidiq_video_upload url=https://raw.githubusercontent.com/vishalbad5/lcl-uploads/upload-test/<file>.mp4  -> uploadId.
- Afterwards wipe the branch: force-push an orphan commit containing only README.md to upload-test.
  (Branch deletion is refused through the proxy; force-push works.)
- Thumbnails: vidiq_upload_image with no image -> uploadUrl + transferId; curl -X PUT --data-binary @thumb.jpg to uploadUrl;
  vidiq_upload_image transferId=... -> imageId.
- Draft each video with vidiq_social_post_draft_create: platform YOUTUBE, platformAccountId UCWnVL9vYPRuEMpv_88284qQ,
  privacyStatus public, categoryId 27, title, tags, thumbnailImageId, text = description, publishAt = its slot.
- NEVER call vidiq_social_post_publish until Vishal approves that day's drafts in the conversation.

## Daily slots (IST, Vishal's schedule; audience mostly US + India)
- Each daily run starts at 18:29 IST. Video 1 -> 19:30 IST same day, video 2 -> 22:30 IST same day, video 3 -> 06:30 IST next day.
- Steady state is 3 posts a day at 06:30, 19:30 and 22:30 IST.
- OVERRIDE for the batch started by hand on 2026-11-24 (Ep 014-016): Ep 014 as soon as approved (19:30 slot), Ep 015 at 22:30 IST on 2026-11-24, Ep 016 at 06:30 IST on 2026-11-25. This replaces any other times given for that batch.
