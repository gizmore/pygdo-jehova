"""Load a random, local lyric track for a round of Musical Chairs."""

from pathlib import Path
from random import choice

# Deliberately original: a chat game needs rhythm cues, not song lyrics.
LYRICS = (
    'The circle turns, the music goes,',
    'Feet keep time on friendly toes.',
    'Round the chairs, but do not rush,',
    'Listen close for the sudden hush.',
    'One more step and one more spin,',
    'When the music stops, sit in!',
)

LYRICS_DIR = Path(__file__).with_name('lyrics')
LYRIC_SUFFIXES = frozenset(('.nfo', '.nf0', '.txt'))


def random_lyrics(exclude: str = '') -> tuple[str, tuple[str, ...]]:
    """Return the identifier and non-empty lines from one random local track.

    The original built-in lines keep the game playable when no track has
    been installed yet.  Files make it possible to curate a playlist without
    a code change.
    """
    if not LYRICS_DIR.is_dir():
        return '__builtins__', LYRICS
    files = [path for path in LYRICS_DIR.iterdir()
             if path.is_file() and path.suffix.lower() in LYRIC_SUFFIXES]
    if not files:
        return '__builtins__', LYRICS
    alternatives = [path for path in files if str(path) != exclude]
    track = choice(alternatives or files)
    try:
        lines = tuple(line.strip() for line in track.read_text(encoding='utf-8').splitlines()
                      if line.strip())
    except OSError:
        return '__builtins__', LYRICS
    return str(track), lines or LYRICS


def next_lyrics(channel, track: str, lines: tuple[str, ...], count: int) -> tuple[tuple[str, ...], bool]:
    """Take one block and persist its cursor; report whether the track ended."""
    from gdo.core.GDO_Method import GDO_Method
    from gdo.core.GDO_MethodValChannel import GDO_MethodValChannel

    key = Path(track).name
    method = GDO_Method.get_by_name('jehova.jehova')
    entry = GDO_MethodValChannel.table().get_by_id(method.get_id(), channel.get_id(), key)
    start = int(entry.get_val()) if entry else 0
    start %= len(lines)
    end = min(start + count, len(lines))
    selected = lines[start:end]
    ended = end == len(lines)
    position = '0' if ended else str(end)
    if entry:
        entry.save_val('mv_val', position)
    else:
        GDO_MethodValChannel.blank({
            'mv_method': method.get_id(),
            'mv_channel': channel.get_id(),
            'mv_key': key,
            'mv_val': position,
        }).insert()
    return selected, ended
