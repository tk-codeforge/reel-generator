import re

def build_dataset_from_shorts(transcript: str, views: int, likes: int):
    rows = []

    if not transcript:
        return rows

    # Better sentence splitting
    sentences = re.split(r'[.!?]\s+', transcript)

    total_sentences = max(len(sentences), 1)

    for i, sentence in enumerate(sentences):
        sentence = sentence.strip()
        if not sentence:
            continue

        position = i / total_sentences
        engagement = likes / max(views, 1)

        # Label logic (simple baseline)
        label = 1 if views > 500000 else 0

        rows.append({
            "text": sentence,
            "position": position,
            "views": views,
            "likes": likes,
            "engagement": engagement,
            "label": label
        })

    return rows