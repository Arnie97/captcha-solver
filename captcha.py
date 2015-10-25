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
        p.get('left', 0),
        p.get('top',  0),
        p.get('left', 0) + p['width'],
        p.get('top',  0) + p['height']
    )).point(
        lambda x:
            0 if x < p.get('threshold', 0x80) else 0xFF
    ).convert(
        '1'
    )


def split_by_whitespace(image):
    'Split a binary image into single characters.'
    characters = []
    whitespace_before = True
    for column in range(image.size[0]):
        whitespace = all(
            image.getpixel((column, row))
            for row in range(image.size[1])
        )
        if whitespace_before and not whitespace:
            characters.append([column])
        elif not whitespace_before and whitespace:
            characters[-1].append(column)
        whitespace_before = whitespace
    if len(characters) and len(characters[-1]) == 1:
        characters[-1].append(image.size[0])
    return characters


def solve(captcha_image, p):
    'Solve the captcha by comparing with a template.'
    template_image = PIL.Image.open(p['template'])
    result = []

    captcha_chars, template_chars = map(
        split_by_whitespace, (
            captcha_image, template_image
        )
    )
    for captcha_index in range(len(captcha_chars)):
        max_similarity = recognized_char = -1
        for template_index in range(len(template_chars)):
            matrix = (
                (captcha_image,  captcha_chars[captcha_index]),
                (template_image, template_chars[template_index])
            )
            current_similarity = sum(
                reduce(
                    lambda x, y: x == y,
                    map(
                        lambda z:
                            z[0].getpixel((
                                col + z[1][0] if col >= 0 else col + z[1][1],
                                row
                            )),
                        matrix
                    )
                )
                for col in p.get(
                    'typical_columns',
                    range(min(map(
                        lambda z:
                            z[1][1] - z[1][0],
                        matrix
                    )))
                )
                for row in p.get(
                    'typical_rows',
                    range(p['height'])
                )
            )
            if current_similarity > max_similarity:
                max_similarity = current_similarity
                recognized_char = template_index
        result.append(recognized_char if recognized_char >= 0 else None)
    return result


def fetch(url):
    'Fetch the specified URL and return the contents as a byte stream.'
    fetched_bytes = urllib.request.urlopen(url).read()
    data_stream = io.BytesIO(fetched_bytes)
    return data_stream
