# Example: Backend + ML/AI Project — `[backend, ml-ai]`

A walkthrough of the Gemstack 5-step workflow for a **backend project with ML/AI components** — e.g., a transcription pipeline, a RAG service, an inference server, or any project that uses ML models or LLM APIs.

**Topology:** `[backend, ml-ai]`
**Active Guardrails:** `backend.md` + `ml-ai.md` — data integrity, anti-mocking, Evaluation-Driven Development (EDD), circuit breaker cost controls, prompt versioning
**Example Project:** A Python ML pipeline for subtitle transcription using faster-whisper

---

## The Feature

> "Add speaker diarization — identify who is speaking at each point in the audio, so transcripts show `Speaker 1: ...`, `Speaker 2: ...` instead of a flat wall of text."

---

## Step 1: `/step1-spec` (The Contract)

**Roles:** Product Visionary + UI/UX Designer + Architect + **ML Engineer**
**Phases:** Ideate, Design

### What happens

The **Product Visionary** defines the opportunity:
- **Pain:** Transcripts of conversations/interviews are unusable because you can't tell who said what.
- **Vision:** Each segment is tagged with a speaker label, making multi-speaker audio readable.

The **Architect** locks in the pipeline contract:

```python
# Added to ARCHITECTURE.md

# Input: audio file path + existing transcript segments
# Output: transcript segments with speaker labels added

@dataclass
class DiarizedSegment:
    start: float
    end: float
    text: str
    speaker: str  # "Speaker 1", "Speaker 2", etc.

def diarize(audio_path: str, segments: list[Segment]) -> list[DiarizedSegment]:
    """Assign speaker labels to existing transcript segments."""
```

The **ML Engineer** joins this step for model selection:

```
Model evaluation:
- pyannote/speaker-diarization-3.1: Best accuracy, requires GPU, HuggingFace gated model
- speechbrain/spkrec-ecapa-voxceleb: Lighter, CPU-viable, less accurate
- simple-diarizer: Minimal dependencies, basic accuracy

Recommendation: pyannote 3.1 with fallback to speechbrain on CPU-only machines.
Hardware detection already exists in the pipeline.
```

### Topology influence
- **ML/AI topology:** The ML Engineer must add the diarization model to the **Model Ledger** in `ARCHITECTURE.md` with resource requirements, and define evaluation metrics before any code is written.
- **Backend topology:** The Architect defines the exact function signature and data flow.

### Key output
```
docs/designs/2026-04-15-speaker-diarization.md    # Design spec
.agent/ARCHITECTURE.md                             # Updated with DiarizedSegment type,
                                                   # Model Ledger updated with diarization model
```

---

## Step 2: `/step2-trap` (Setting the Trap)

**Roles:** Principal Engineer + SDET + **ML Engineer**
**Phases:** Contract & Plan

### What happens

The **Principal Backend Engineer** writes the task plan:
```
1. Add DiarizedSegment dataclass (trivial)
2. Implement pyannote diarization wrapper (complex)
3. Implement speechbrain fallback (moderate)
4. Add hardware-aware model routing for diarization (moderate)
5. Integrate diarization into the main pipeline (moderate)
6. Update CLI with --diarize flag (trivial)
```

The **SDET** writes tests:
```python
def test_diarize_two_speakers():
    """Test that a known two-speaker audio file produces two distinct speaker labels."""
    segments = transcribe("fixtures/two_speakers.wav")
    result = diarize("fixtures/two_speakers.wav", segments)
    speakers = set(seg.speaker for seg in result)
    assert len(speakers) == 2

def test_diarize_single_speaker():
    """Single-speaker audio should produce exactly one speaker label."""
    segments = transcribe("fixtures/single_speaker.wav")
    result = diarize("fixtures/single_speaker.wav", segments)
    speakers = set(seg.speaker for seg in result)
    assert len(speakers) == 1

def test_diarize_preserves_text():
    """Speaker assignment must not alter the original transcript text."""
    segments = transcribe("fixtures/two_speakers.wav")
    original_texts = [s.text for s in segments]
    result = diarize("fixtures/two_speakers.wav", segments)
    result_texts = [s.text for s in result]
    assert original_texts == result_texts
```

The **ML Engineer** defines evaluation thresholds:

```markdown
# Added to TESTING.md — ML/AI Evaluation Thresholds

| Metric | Target | Current | Method |
|--------|--------|---------|--------|
| Diarization Error Rate (DER) | < 15% | — | pyannote.metrics on eval set |
| Speaker count accuracy | > 90% | — | Correct speaker count on 20-file eval set |
| Pipeline throughput (with diarization) | > 0.5x realtime | — | Wall clock on 10-min file |
```

### Topology influence
- **ML/AI topology:** Evaluation thresholds are defined BEFORE code is written. The Builder must meet these thresholds, not just pass unit tests.
- **ML/AI topology:** The Eval/Holdout Boundary is documented — eval set is fixtures, holdout set is reserved for human-only validation.

---

## Step 3: `/step3-build` (The Autonomous Factory)

**Roles:** Principal Backend Engineer + **ML Engineer**
**Phases:** Build

### What happens

The Builder implements the diarization pipeline. The ML Engineer is active for model integration and eval verification.

```bash
$ python -m pytest tests/test_diarization.py -v
# ✘ 3 failing → implement diarize()
$ python -m pytest tests/test_diarization.py -v
# ✘ 1 failing → fix speaker count detection
$ python -m pytest tests/test_diarization.py -v
# ✔ 3 passed — Exit Code 0

# ML Engineer also runs eval:
$ python eval/run_diarization_eval.py
# DER: 12.3% (target: < 15%) ✔
# Speaker count accuracy: 95% (target: > 90%) ✔
# Throughput: 0.7x realtime (target: > 0.5x) ✔
```

### Topology influence
- **Backend topology:** Real audio files in tests, no mocked model outputs. The anti-mocking rule means the tests actually run inference.
- **ML/AI topology:** The **circuit breaker** is relevant — if the diarization model's resource usage exceeds the documented cap in the Model Ledger, it must be flagged.

---

## Step 4: `/step4-audit` (The Jury)

**Roles:** Security Engineer + SDET + **ML Engineer**
**Phases:** Test, Review, Audit

### What happens

**SDET attack patterns:**
- Empty audio file (0 bytes)
- Extremely long audio (3+ hours)
- Audio with background music and no speech
- Corrupted audio file
- Already-diarized segments passed in again

**ML Engineer verification:**
- Do eval scores meet the thresholds from Step 2?
- Does the GPU fallback to CPU work correctly?
- Is the model version pinned? (Reproducibility)
- Memory profiling: does it OOM on long files?

**Security Engineer:**
- Can malicious audio input cause arbitrary code execution?
- Is the HuggingFace token properly secured (not in code)?
- Are temporary audio files cleaned up after processing?

### Output
```
.agent/AUDIT_FINDINGS.md

## Findings

### [HIGH] OOM on files > 2 hours
The diarization model loads the entire audio into VRAM. Files > 2 hours
exceed the 8GB VRAM limit on consumer GPUs.

**Fix:** Implement chunked diarization with sliding windows and speaker
re-identification across chunk boundaries.

### [MEDIUM] Model version not pinned
pyannote/speaker-diarization uses @latest. A model update could silently
change behavior and degrade eval scores.

**Fix:** Pin to pyannote/speaker-diarization-3.1 explicitly.
```

---

## Step 5: `/step5-ship` (The Gatekeeper)

**Roles:** DevOps Engineer + Principal Engineer
**Phases:** Integrate, Ship

### What happens

1. **Integrate:** Verify no placeholder model configs remain, all hardware detection paths work
2. Run the full test suite + eval suite
3. Update the **Prompt Versioning Changelog** in `STATUS.md` with a v1.0 baseline for the diarization model config
4. Update the Model Ledger with final resource measurements
5. Tag release, deploy
6. Archive docs, reset `STATUS.md`

### Topology influence
- **ML/AI topology:** The Prompt Versioning Changelog gets a baseline entry tracking the diarization model version, so future config changes can be diffed and rolled back if evals degrade.

---

## Standalone Phase: `/fix`

**Users report** that the `--diarize` flag silently does nothing when run on a CPU-only machine without the speechbrain fallback installed.

```
/fix

Bug: Running `aisrt --diarize input.mp4` on a CPU-only machine produces
a transcript with no speaker labels and no error message. Expected: either
use the CPU fallback model, or print a clear error explaining what's missing.
```

The agent:
1. **Diagnoses:** Hardware detection correctly identifies CPU-only, but the fallback import fails silently with a bare `except: pass`
2. **Patches:** Replaces bare except with explicit `ImportError` handling and a user-facing error message
3. **Verifies:** Tests on CPU-only path with speechbrain not installed
4. **Done.**
