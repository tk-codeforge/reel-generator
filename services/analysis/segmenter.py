import re

def split_into_segments(transcript_chunks, chunk_duration_sec):
    segments = []

    for i, chunk in enumerate(transcript_chunks):
        if not chunk:
            continue

        sentences = re.split(r'(?<=[.!?]) +', chunk)

        for j, sentence in enumerate(sentences):
            if len(sentence.strip()) < 20:
                continue

            segments.append({
                "text": sentence.strip(),
                "chunk": i + 1,
                "position": j / max(len(sentences), 1),
                "sentence_index": j,
                "total_sentences": len(sentences)
            })

    return segments