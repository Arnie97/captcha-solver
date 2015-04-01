import os
import nose
from captcha import image_filter, solve, solve_url


def test_captcha_solver():
    path = 'tests/samples/'
    for file in os.listdir(path):
        assert solve(image_filter(path + file)) == file[:6]


def test_get_image_by_url():
    image_url = 'http://www.afreesms.com/image.php'
    for i in range(10):
        assert len(solve_url(image_url)) == 6
