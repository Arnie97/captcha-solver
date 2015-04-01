import io
import urllib.request
import PIL.Image

def image_filter(source):
    'Produce a binary image from captcha image.'
    return PIL.Image.open(
        source
    ).convert(
        'L'
    ).crop(
        (4, 4, 76, 15)
    ).point(
        lambda x:
            0 if x < 0xC0 else 0xFF
    ).convert(
        '1'
    )


def solve(captcha):
    'Solve the captcha by comparing with a template.'
    template = PIL.Image.open('numbers.bmp')
    last_column, result = -1, ''
    for column in range(72):
        if all(captcha.getpixel((column, row)) for row in range(11)):
            if last_column != column - 1:
                for n in range(9):
                    if all(
                        template.getpixel((2 * n, row)) ==
                        captcha.getpixel((last_column + 1, row * 2))
                        for row in range(4)
                    ) and all(
                        template.getpixel((2 * n + 1, row)) ==
                        captcha.getpixel((column - 1, row * 2))
                        for row in range(4)
                    ):
                        result += str(n + 1)
            last_column = column
    return result


def solve_url(image_url):
    'Get a captcha image from the specified URL and try to solve it.'
    image_bytes = urllib.request.urlopen(image_url).read()
    data_stream = io.BytesIO(image_bytes)
    return solve(image_filter(data_stream))
