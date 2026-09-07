"""Take str and splits it into chunks of chunk_size with chunk_overlap."""


def chunk_text(text: str, chunk_size: int, chunk_overlap: int) -> list[str]:
    """Split text into chunks of up to chunk_size with a specified overlap.

    The function attempts to break on '##' markers or on spaces to avoid
    splitting words when possible. If neither is found in the current window,
    it advances by chunk_size - chunk_overlap to create the next chunk.

    Args:
        text: The input string to be chunked.
        chunk_size: Maximum size of each chunk (number of characters).
        chunk_overlap: Number of characters to overlap between consecutive
            chunks. Must be less than chunk_size.

    Returns:
        A list of string chunks.

    Raises:
        ValueError: If chunk_overlap is greater than or equal to chunk_size.

    """
    index = 0
    chunks = []

    if chunk_overlap >= chunk_size:
        raise ValueError("chunk_overlap must be less than chunk_size")

    while index < len(text):
        chunk = text[index : index + chunk_size]
        if index + chunk_size >= len(text):
            chunks.append(chunk)
            break
        hash_index = chunk.rfind("##")
        space_index = chunk.rfind(" ")
        if hash_index != -1:
            chunk = chunk[:hash_index]
            index += hash_index + 2
        elif space_index != -1:
            chunk = chunk[:space_index]
            index += space_index + 1
        else:
            index += chunk_size - chunk_overlap
        chunks.append(chunk)
    return chunks


text = "aaaa bbbb cccc dddd"
chunks = chunk_text(text, chunk_size=12, chunk_overlap=2)
for c in chunks:
    print(c)
