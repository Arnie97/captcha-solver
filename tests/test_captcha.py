import os
import nose
from captcha import image_filter, solve

def test_captcha_solver():
    path = 'tests/samples/'
    for file in os.listdir(path):
        assert solve(image_filter(path + file)) == file[:6]
