import random


subtitles = [
    "Click your way to space!",
    "Climb to the heavens and fight god!",
    "Make the Earth tremble before your scientific might!",
    "Click buttons and make number go up!",
    "Making naps productive since May, 2024!",
    "<Minecraft blurb here>",
    "Don't have carpal tunnel? We're here to help!"
]


def random_subtitle() -> str:
    return random.choice(subtitles)
