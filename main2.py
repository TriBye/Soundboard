import time
from machine import Pin, PWM
import asyncio
PINS = [33, 35, 37, 39]
NAMES = ["C", "C#", "D", "D#", "E", "E#", "F", "F#", "G", "G#", "A", "A#", "B"]
from all_star import SONG, BEAT
LEGATO = 0.9
active = []

for pin in PINS:
    active.append(None)
    
def freq(name, octaves):
    pitch = name[:-1]
    octave = int(name[-1]) + octaves
    step = NAMES.index(pitch)
    midi_note = 12 * (octave + 1) + step
    ref_note = 69
    ref_hz = 440
    steps_from_ref = midi_note - ref_note
    hz = ref_hz * 2 ** (steps_from_ref/12)
    return round(hz)

def play_note(pin, hz):
    return PWM(Pin(pin), freq=hz, duty_u16 = int(32768))

def silence(pin):
    Pin(pin, Pin.OUT, value = 0)
    
def stop(i):
    pwm = active[i]
    active[i] = None
    if pwm is not None:
        pwm.deinit()
    silence(PINS[i])
    
def stop_all():
    for i in range(len(PINS)):
        try:
            stop(i)
        except Exception:
            pass
      
async def wait_until(start, beats):
    target = time.ticks_add(start, int(beats*BEAT*1000))
    delay = time.ticks_diff(target, time.ticks_ms())
    if delay > 0:
        await asyncio.sleep_ms(delay)
     
async def play_voice(i, text , pin , octaves, start):
    t = 0.0
    await wait_until(start, 0)
    for token in text.split():
        name, beats = token.split(":")
        length = float(beats)
        if name != "R":
            active[i] = play_note(pin, freq(name, octaves))
            stop_beat = t + length + LEGATO
            await wait_until(start, stop_beat)
            stop(i)
        t += length
        await wait_until(start, t)

async def main():
    for pin in PINS:
        silence(pin)
    while True:
        start = time.ticks_add(time.ticks_ms(), 100)
        voices = []
        for i in range(len(PINS)):
            voices.append(play_voice(i, SONG[i], PINS[i], 0, start))
        await asyncio.gather(*voices)

try:
    asyncio.run(main())
finally:
    stop_all()
    









notes = [
    'E5', 'B4', 'C5', 'D5',
    'C5', 'B4', 'A4', 'A4',
    'C5', 'E5', 'D5', 'C5',
    'B4', 'C5', 'D5', 'E5',
    'C5', 'A4', 'A4',

    'D5', 'F4', 'A4', 'G4',
    'F4', 'E4', 'C5', 'E5',
    'D5', 'C5', 'B4', 'B4',
    'C5', 'D5', 'E5', 'C5',
    'A4', 'A4'
]

beats = [
    0.4, 0.2, 0.2, 0.4,
    0.2, 0.2, 0.4, 0.2,
    0.2, 0.4, 0.2, 0.2,
    0.4, 0.2, 0.4, 0.4,
    0.4, 0.4, 0.8,

    0.4, 0.2, 0.4, 0.2,
    0.2, 0.4, 0.2, 0.4,
    0.2, 0.2, 0.4, 0.2,
    0.2, 0.4, 0.4, 0.4,
    0.4, 0.8
]


for i, note in enumerate(notes):
    pwm = play_note(PINS, freq(note, 2))
    time.sleep(beats[i])
    pwm.deinit()