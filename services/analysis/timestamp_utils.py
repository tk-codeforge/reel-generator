def find_timestamp(chunks, phrase, chunk_duration=600):
    """
    Finds approximate timestamp of a phrase inside chunk transcripts
    """

    for i, chunk in enumerate(chunks):
        if phrase.lower() in chunk.lower():
            position = chunk.lower().find(phrase.lower())

            ratio = position / max(len(chunk), 1)

            return (i * chunk_duration) + (ratio * chunk_duration)

    return 0


def get_clip_times(chunks, start_phrase, end_phrase, chunk_duration=600):
    start_sec = find_timestamp(chunks, start_phrase, chunk_duration)
    end_sec = find_timestamp(chunks, end_phrase, chunk_duration)

    duration = max(15, min(120, end_sec - start_sec))

    return start_sec, duration