import io
import urllib.request
from functools import reduce
import PIL.Image


def image_filter(source, p):
    'Produce a binary image from captcha image.'
    return PIL.Image.open(
        source
    ).convert(
        'L'
    ).crop((
        p['left'],
        p['top'],
        p['left'] + p['width'] * p['chars_per_captcha'],
        p['top'] + p['height']
    )).point(
        lambda x:
            0 if x < p['threshold'] else 0xFF
    ).convert(
        '1'
    )


def solve(captcha_image, p):
    'Solve the captcha by comparing with a template.'
    template_image = PIL.Image.open(p['template'])
    result = []
    for captcha_index in range(p['chars_per_captcha']):
        max_similarity = recognized_char = -1
        for template_index in range(p['chars_per_template']):
            current_similarity = sum(
                reduce(
                    lambda x, y: x == y,
                    map(
                        lambda z:
                            z[0].getpixel((column + z[1] * p['width'], row)),
                        (
                            (captcha_image,  captcha_index),
                            (template_image, template_index)
                        )
                    )
                )
                for column in range(p['width'])
                for row in range(p['height'])
            )
            if current_similarity > max_similarity:
                max_similarity = current_similarity
                recognized_char = template_index
        result.append(recognized_char if recognized_char > 0 else None)
    return result


def fetch(url):
    'Fetch the specified URL and return the contents as a byte stream.'
    fetched_bytes = urllib.request.urlopen(url).read()
    data_stream = io.BytesIO(fetched_bytes)
    return data_stream
