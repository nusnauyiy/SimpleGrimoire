def split_overlapping_chunk_size(chunk_size: int):
    if chunk_size <= 0:
        raise Exception(f"Chunk size cannot be <= 0: {chunk_size}")

    def _split_overlapping_chunk_size(input_bytes: bytes, start: int):
        if start + chunk_size > len(input_bytes):
            return len(input_bytes)
        return start + chunk_size

    return _split_overlapping_chunk_size


chunk_sizes = [256, 128, 64, 32, 2, 1]
split_overlapping_chunk_size_rules = [split_overlapping_chunk_size(chunk_size) for chunk_size in chunk_sizes]
