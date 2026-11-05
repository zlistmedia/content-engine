# Content Engine voice model

Unchanged copies of [Systran/faster-whisper-small](https://huggingface.co/Systran/faster-whisper-small) and [faster-whisper-base](https://huggingface.co/Systran/faster-whisper-base)
(OpenAI Whisper small and base, converted for CTranslate2), MIT licensed. The Content Engine downloads them from
here so it works with Claude's default network settings. `model.bin` is split into parts under
GitHub's file limit; `SHA256SUMS` checks the parts and the rebuilt file.
