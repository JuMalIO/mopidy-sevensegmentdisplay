from __future__ import division
from __future__ import unicode_literals

import os
from mopidy import core
from max7219 import Symbols
from random import randint
import logging
from subprocess import call


class Music:
    P = Symbols.P
    L = Symbols.L
    A = Symbols.A
    Y = Symbols.Y
    S = Symbols.S
    T1 = Symbols.T1
    T2 = Symbols.T2
    O = Symbols.O
    U = Symbols.U
    E = Symbols.E

    ANIMATION_PLAY = {
        "length": 2,
        "repeat": 1,
        "sleep": 0.05,
        "buffer": [
            [0, 0, 0, 0, 0, 0, 0, P],
            [0, 0, 0, 0, 0, 0, P, 0],
            [0, 0, 0, 0, 0, P, 0, 0],
            [0, 0, 0, 0, P, 0, 0, 0],
            [0, 0, 0, P, 0, 0, 0, 0],
            [0, 0, P, 0, 0, 0, 0, L],
            [0, 0, P, 0, 0, 0, L, 0],
            [0, 0, P, 0, 0, L, 0, 0],
            [0, 0, P, 0, L, 0, 0, 0],
            [0, 0, P, L, 0, 0, 0, A],
            [0, 0, P, L, 0, 0, A, 0],
            [0, 0, P, L, 0, A, 0, 0],
            [0, 0, P, L, A, 0, 0, Y],
            [0, 0, P, L, A, 0, Y, 0],
            [0, 0, P, L, A, Y, 0, 0],
            [0, 0, P, L, A, Y, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, P, L, A, Y, 0, 0],
            [0, 0, P, L, A, Y, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, P, L, A, Y, 0, 0],
            [0, 0, P, L, A, Y, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, P, L, A, Y, 0, 0]
        ]
    }

    ANIMATION_STOP = {
        "length": 2,
        "repeat": 1,
        "sleep": 0.05,
        "buffer": [
            [0, 0, 0, 0, 0, 0, 0, S],
            [0, 0, 0, 0, 0, 0, S, 0],
            [0, 0, 0, 0, 0, S, 0, 0],
            [0, 0, 0, 0, S, 0, 0, 0],
            [0, 0, 0, S, 0, 0, 0, 0],
            [0, 0, S, 0, 0, 0, 0, T1],
            [0, 0, S, 0, 0, 0, T1, T2],
            [0, 0, S, 0, 0, T1, T2, 0],
            [0, 0, S, 0, T1, T2, 0, 0],
            [0, 0, S, T1, T2, 0, 0, O],
            [0, 0, S, T1, T2, 0, O, 0],
            [0, 0, S, T1, T2, O, 0, P],
            [0, 0, S, T1, T2, O, P, 0],
            [0, 0, S, T1, T2, O, P, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, S, T1, T2, O, P, 0],
            [0, 0, S, T1, T2, O, P, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, S, T1, T2, O, P, 0],
            [0, 0, S, T1, T2, O, P, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, S, T1, T2, O, P, 0]
        ]
    }

    ANIMATION_PAUSE = {
        "length": 2,
        "repeat": 1,
        "sleep": 0.05,
        "buffer": [
            [0, 0, 0, 0, 0, 0, 0, P],
            [0, 0, 0, 0, 0, 0, P, 0],
            [0, 0, 0, 0, 0, P, 0, 0],
            [0, 0, 0, 0, P, 0, 0, 0],
            [0, 0, 0, P, 0, 0, 0, 0],
            [0, 0, P, 0, 0, 0, 0, A],
            [0, 0, P, 0, 0, 0, A, 0],
            [0, 0, P, 0, 0, A, 0, 0],
            [0, 0, P, 0, A, 0, 0, 0],
            [0, 0, P, A, 0, 0, 0, U],
            [0, 0, P, A, 0, 0, U, 0],
            [0, 0, P, A, 0, U, 0, 0],
            [0, 0, P, A, U, 0, 0, S],
            [0, 0, P, A, U, 0, S, 0],
            [0, 0, P, A, U, S, 0, E],
            [0, 0, P, A, U, S, E, 0],
            [0, 0, P, A, U, S, E, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, P, A, U, S, E, 0],
            [0, 0, P, A, U, S, E, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, P, A, U, S, E, 0],
            [0, 0, P, A, U, S, E, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, P, A, U, S, E, 0]
        ]
    }

    BOTTOM = Symbols.BOTTOM
    TOP = Symbols.TOP
    LEFT_TOP = Symbols.LEFT_TOP
    LEFT_BOTTOM = Symbols.LEFT_BOTTOM
    RIGHT_TOP = Symbols.RIGHT_TOP
    RIGHT_BOTTOM = Symbols.RIGHT_BOTTOM

    ANIMATION_SPINNER = {
        "length": 1,
        "repeat": 3,
        "sleep": 0.05,
        "buffer": [
            [0, 0, 0, 0, 0, 0, 0, BOTTOM],
            [0, 0, 0, 0, 0, 0, BOTTOM, 0],
            [0, 0, 0, 0, 0, BOTTOM, 0, 0],
            [0, 0, 0, 0, BOTTOM, 0, 0, 0],
            [0, 0, 0, BOTTOM, 0, 0, 0, 0],
            [0, 0, BOTTOM, 0, 0, 0, 0, 0],
            [0, BOTTOM, 0, 0, 0, 0, 0, 0],
            [BOTTOM, 0, 0, 0, 0, 0, 0, 0],
            [LEFT_BOTTOM, 0, 0, 0, 0, 0, 0, 0],
            [LEFT_TOP, 0, 0, 0, 0, 0, 0, 0],
            [TOP, 0, 0, 0, 0, 0, 0, 0],
            [0, TOP, 0, 0, 0, 0, 0, 0],
            [0, 0, TOP, 0, 0, 0, 0, 0],
            [0, 0, 0, TOP, 0, 0, 0, 0],
            [0, 0, 0, 0, TOP, 0, 0, 0],
            [0, 0, 0, 0, 0, TOP, 0, 0],
            [0, 0, 0, 0, 0, 0, TOP, 0],
            [0, 0, 0, 0, 0, 0, 0, TOP],
            [0, 0, 0, 0, 0, 0, 0, RIGHT_TOP],
            [0, 0, 0, 0, 0, 0, 0, RIGHT_BOTTOM]
        ]
    }

    MIDDLE = Symbols.MIDDLE

    ANIMATION_START = {
        "length": 5,
        "repeat": 20,
        "sleep": 0.02,
        "buffer": [
            [0, 0, 0, 0, 0, 0, 0, MIDDLE],
            [0, 0, 0, 0, 0, 0, MIDDLE, 0],
            [0, 0, 0, 0, 0, MIDDLE, 0, 0],
            [0, 0, 0, 0, MIDDLE, 0, 0, 0],
            [0, 0, 0, MIDDLE, 0, 0, 0, 0],
            [0, 0, MIDDLE, 0, 0, 0, 0, 0],
            [0, MIDDLE, 0, 0, 0, 0, 0, 0],
            [MIDDLE, 0, 0, 0, 0, 0, 0, 0],
            [0, MIDDLE, 0, 0, 0, 0, 0, 0],
            [0, 0, MIDDLE, 0, 0, 0, 0, 0],
            [0, 0, 0, MIDDLE, 0, 0, 0, 0],
            [0, 0, 0, 0, MIDDLE, 0, 0, 0],
            [0, 0, 0, 0, 0, MIDDLE, 0, 0],
            [0, 0, 0, 0, 0, 0, MIDDLE, 0]
        ]
    }

    M0 = int('00000000', 2)
    M1 = int('00001000', 2)
    M2 = int('00001001', 2)
    M3 = int('01001001', 2)
    MUSIC_EQUALIZER = [M0, M1, M2, M3]

    N = Symbols.N
    B = Symbols.NUMBER[8]
    F = Symbols.F
    C = Symbols.C
    I = Symbols.I
    D = Symbols.D
    H = Symbols.H
    R = Symbols.R
    b = Symbols.B
    G = Symbols.NUMBER[6]

    PRESETS = [
        {"name": "flat", "buffer": [0, F, L, A, T1, T2, 0, 0]},
        {"name": "classical", "buffer": [C, L, A, S, S, I, C, 0]},
        {"name": "club", "buffer": [0, 0, C, L, U, B, 0, 0]},
        {"name": "dance", "buffer": [0, D, A, N, C, E, 0, 0]},
        {"name": "headphones", "buffer": [H, E, A, D, P, H, O, N]},
        {"name": "bass", "buffer": [0, 0, B, A, S, S, 0, 0]},
        {"name": "treble", "buffer": [T1, T2, R, E, b, L, E, 0]},
        {"name": "large_hall", "buffer": [0, 0, H, A, L, L, 0, 0]},
        {"name": "live", "buffer": [0, 0, L, I, U, E, 0, 0]},
        {"name": "party", "buffer": [0, P, A, R, T1, T2, Y, 0]},
        {"name": "pop", "buffer": [0, 0, P, O, P, 0, 0, 0]},
        {"name": "reggae", "buffer": [0, R, E, G, G, A, E, 0]},
        {"name": "rock", "buffer": [0, 0, R, O, C, H, 0, 0]},
        {"name": "ska", "buffer": [0, 0, S, H, A, 0, 0, 0]},
        {"name": "soft_rock", "buffer": [S, O, F, T2, R, O, C, H]},
        {"name": "soft", "buffer": [0, S, O, F, T1, T2, 0, 0]},
        {"name": "techno", "buffer": [T1, T2, E, C, H, N, O, 0]},
        {"name": "nobass", "buffer": [N, O, 0, B, A, S, S, 0]}
    ]

    def __init__(self, core, default_song, preset):
        self.core = core
        self.volume = self.get_volume(),
        self.default_song = default_song,
        self.preset = preset

    def is_playing(self, state=None):
        if (state is None):
            state = self.get_state()
        return state == core.PlaybackState.PLAYING

    def is_paused(self, state=None):
        if (state is None):
            state = self.get_state()
        return state == core.PlaybackState.PAUSED

    def is_stopped(self, state=None):
        if (state is None):
            state = self.get_state()
        return state == core.PlaybackState.STOPPED

    def is_volume_changed(self, volume):
        if (self.volume != volume):
            self.volume = volume
            return True
        else:
            return False

    def is_mute(self):
        return self.core.playback.mute.get()  # self.core.mixer.get_mute()

    def play(self, tracks):
        if (tracks is not None):
            self.core.playback.stop()
            self.core.tracklist.clear()
            self.core.tracklist.add(uris=tracks)
            self.core.tracklist.consume = False
            self.core.tracklist.single = False
            self.core.tracklist.repeat = True
            self.core.tracklist.random = True
        if (not self.is_playing()):
            if (self.core.tracklist.get_length().get() < 1):
                self.core.tracklist.add(uris=[self.default_song])
                self.core.tracklist.repeat = True
                self.core.tracklist.random = True
            self.core.playback.play()

    def pause(self):
        if (not self.is_paused()):
            self.core.playback.pause()

    def stop(self):
        if (self.is_playing()):
            self.core.playback.stop()

    def mute(self):
        self.core.playback.mute = not self.is_mute()  # self.core.mixer.set_mute(not self.is_mute())

    def set_preset(self, value):
        index = 0
        if (value == -1 or value == 1):
            index = (self._get_preset_index(self.preset) + value + len(self.PRESETS)) % len(self.PRESETS)
        else:
            index = self._get_preset_index(value)

        self.preset = self.PRESETS[index]["name"]

        try:
            call(["sh", os.path.join(os.path.dirname(__file__), 'presets.sh'), self.PRESETS[index]["name"]])
        except Exception as inst:
            logging.error(inst)

        return self.PRESETS[index]["buffer"]

    def get_presets(self):
        index = self._get_preset_index(self.preset)
        return self.PRESETS[index:len(self.PRESETS)] + self.PRESETS[0:index]

    def _get_preset_index(self, name):
        for i, d in enumerate(self.PRESETS):
            if (d["name"] == name):
                return i
        return 0

    def get_state(self):
        return self.core.playback.state.get()  # self.core.playback.get_state()

    def get_volume(self):
        return self.core.playback.volume.get()  # self.core.mixer.get_volume()

    def set_volume(self, volume):
        if (volume < 0):
            volume = 0
        elif (volume > 100):
            volume = 100
        self.core.playback.volume = volume  # self.core.mixer.set_volume()

    def increase_volume(self, volume=1):
        self.set_volume(self.get_volume() + volume)

    def decrease_volume(self, volume=1):
        self.set_volume(self.get_volume() - volume)

    def get_default_song(self):
        return self.default_song

    def get_draw_start_animation(self):
        return self.ANIMATION_START

    def get_draw_play_animation(self):
        return self.ANIMATION_PLAY

    def get_draw_stop_animation(self):
        return self.ANIMATION_STOP

    def get_draw_pause_animation(self):
        return self.ANIMATION_PAUSE

    def get_draw_seek_animation(self):
        return self.ANIMATION_SPINNER

    def get_draw_equalizer_animation(self):
        animation = []

        for j in range(120):
            frame = []
            for i in range(8):
                if (j > 0):
                    index = self.MUSIC_EQUALIZER.index(animation[j - 1][i]) + randint(-1, 1)
                    if (index < 0):
                        index = 0
                    elif (index > 3):
                        index = 3
                    frame.append(self.MUSIC_EQUALIZER[index])
                else:
                    frame.append(self.MUSIC_EQUALIZER[randint(0, 3)])
            animation.append(frame)

        return {
            "length": 5,
            "repeat": 1,
            "sleep": 0.05,
            "buffer": animation
        }

    def get_draw_volume(self, volume=None):
        if (volume is None):
            volume = self.get_volume()

        # if (self.is_mute()):
        #     volume = 0

        return [
            Symbols.U,
            Symbols.O,
            Symbols.L,
            Symbols.NONE,
            Symbols.NONE,
            Symbols.NONE if volume < 100 else Symbols.NUMBER[int(volume / 100)],
            Symbols.NONE if volume < 10 else Symbols.NUMBER[int(volume / 10) % 10],
            Symbols.NUMBER[volume % 10]
        ]
