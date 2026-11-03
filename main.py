import time
from machine import Pin, PWM

SPEAKER_PINS = (33,35,37,39)
BPM = 224
SONG = "hava_nagila"  # "hava_nagila" oder "erika"
HAVA_FAST_BPM = 248
SECTION_PAUSE_BEATS = 2
NOTE_NAMES = {"H": "B", "Cis": "C#", "Fis": "F#", "Gis": "G#", "Bb": "A#"}

ERIKA_LINES = [
    "G. A | H H | H D | D G | G H | H. A | G R R R",
    "D G | A R R R | H. A | G R R R",
    "G. A | H H | H D | D G | G H | H. A | G R R R",
    "D G | A R R R | H. A | G R R R",
    "D. G | A A | A A | D. H | G R R R",
    "D G | A A | A A | D. C | H R R R",
    "G. A | H H | H D | D G | G H | H. A | G R R R",
    "D G | A R R R | H. A | G",
]

HAVA_SECTIONS = [
    (BPM, [
        "E. E | Gis F E | Gis. Gis | H A Gis | A. A | C H A | Gis F F | Gis",
        "E. E | Gis F E | Gis. Gis | H A Gis | A. A | C H A | Gis F F | E",
    ]),
    (HAVA_FAST_BPM, [
        "Gis Gis | F E E E | F F | E D D D | D F | E D D A | Gis F F | Gis",
        "Gis Gis | F E E E | F F | E D D D | D F | E D D A | Gis F F | E",
    ]),
    (HAVA_FAST_BPM, [
        "A A | A A | A A",
        "A A A | C. H | A C | H A",
        "A A A | C. H | A C | H A",
        "H H H | D. C | H D | C H",
        "H H H | E | E E | C H A Gis | A",
    ]),
]


def parse_melody(lines, four_four=False):
    # Hava: angenommene 4/4-Dauern wie in der vorherigen Version.
    rhythms = {1: (4,), 2: (2, 2), 3: (2, 1, 1), 4: (1, 1, 1, 1)}
    melody = []
    for line in lines:
        for group in line.split("|"):
            tokens = group.split()
            if not tokens:
                continue
            durations = None
            if four_four:
                durations = rhythms[len(tokens)]
                if any(token.endswith(".") for token in tokens):
                    if len(tokens) != 2 or not tokens[0].endswith("."):
                        raise ValueError("Expected a dotted pair")
                    durations = (3, 1)
            short_note = False
            for index, token in enumerate(tokens):
                if token == "R":
                    melody.append((None, durations[index] if four_four else 1))
                    short_note = False
                    continue
                dotted = token.endswith(".")
                beats = 1.5 if dotted else (0.5 if short_note else 1)
                if four_four:
                    beats = durations[index]
                note = token.rstrip(".")
                name = NOTE_NAMES.get(note, note) + "4"
                melody.append((name, beats))
                short_note = dotted
    return melody

MELODY = parse_melody(ERIKA_LINES)

SONGS = {
    "erika": [(BPM, MELODY)],
    "hava_nagila": [(bpm, parse_melody(lines, four_four=True))
                    for bpm, lines in HAVA_SECTIONS],
}

NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
def freq(name, octaves=0):
    pitch = name[:-1]
    octave = int(name[-1]) + octaves
    step = NAMES.index(pitch)
    midi_note = 12 * (octave + 1) + step
    ref_note = 69
    ref_hz = 440
    steps_from_ref = midi_note - ref_note
    hz = ref_hz * 2 ** (steps_from_ref / 12)
    return round(hz)

def play_note(name, duration=0.5, octaves=0):
    if name is None:
        time.sleep(duration)
        return
    hz = freq(name, octaves)
    buzzers = []
    try:
        for pin_number in SPEAKER_PINS:
            buzzers.append(PWM(Pin(pin_number), freq=hz, duty=512))
        time.sleep(duration)
    finally:
        for buzzer in buzzers:
            buzzer.deinit()

def play_melody(melody=MELODY, bpm=BPM):
    if bpm <= 0:
        raise ValueError("bpm must be positive")
    seconds_per_beat = 60 / bpm
    for name, beats in melody:
        duration = beats * seconds_per_beat
        if name is None:
            play_note(None, duration)
        else:
            play_note(name, duration * 0.85)
            time.sleep(duration * 0.15)

def play_song():
    if SONG not in SONGS:
        raise ValueError("SONG must be 'hava_nagila' or 'erika'")
    for index, (bpm, melody) in enumerate(SONGS[SONG]):
        if index:
            play_note(None, SECTION_PAUSE_BEATS * 60 / bpm)
        play_melody(melody, bpm)

if __name__ == "__main__":
    play_song()
