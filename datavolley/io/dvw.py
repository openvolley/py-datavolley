# datavolley\io\dvw.py


def read_dvw(filepath: str):
    """
    Read a DataVolley DVW file.

    Args:
        filepath: Path to the DVW file

    Returns:
        Match object with parsed data
    """
    # Read the raw file
    rows = []
    with open(filepath, "r", encoding="utf-8") as f:
        raw_content = f.read()
        for line in f:
            rows.append(line)

    return raw_content
