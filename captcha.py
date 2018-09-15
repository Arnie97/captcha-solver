import io
import urllib.request
from functools import reduce
import operator
import PIL.Image
import PIL.ImageOps


def image_filter(source, left=0, top=0, width=0, height=0, threshold=128, **_):
    'Produce a binary image from captcha image.'
    image = PIL.Image.open(source)
    if not width:
        width = image.size[0] - left
    if not height:
        height = image.size[1] - top

    return image.crop((
        left, top, left + width, top + height
    )).convert(
        'L'
    ).point(
        lambda x: 0 if x < threshold else 0xFF
    ).convert(
        '1'
    )


def remove_noise(image, radius=1, threshold=0.5):
    '''Remove salt-and-pepper noise from the image.

    If the ratio of white points in neighborhood of a point is more than the
    specified threshold, then paint the point as white.
    '''
    new_image = image.copy()
    for column in range(image.size[0]):
        for row in range(image.size[1]):
            if image.getpixel((column, row)):  # ignore white points
                continue
            neighbors = [
                (x, y)
                for x in range(column - radius, column + radius + 1)
                for y in range(row - radius, row + radius + 1)
                if 0 <= x < image.size[0] and 0 <= y < image.size[1]
            ]
            white_neighbors = sum(
                bool(image.getpixel(pair))
                for pair in neighbors
            )
            if white_neighbors > len(neighbors) * threshold:
                new_image.putpixel((column, row), 0xFF)
    return new_image


def split_by_whitespace(image):
    '''Split a binary image into single characters.

    This function returns a list. Each element in the list is itself a list of
    two integrals, which represent the range of columns consisting a recognized
    character. The recognized characters are sorted in increasing order by
    their first column.
    '''
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


def trim_borders(image, invert=True):
    'Remove white or black borders from the image.'
    reference = PIL.ImageOps.invert(image.convert('L')) if invert else image
    return image.crop(reference.getbbox())


def vertical_align(image, characters=None, border=2):
    'Align all characters to the bottom.'
    if characters is None:
        characters = split_by_whitespace(image)
    x = border
    new_image = PIL.Image.new('1', image.size, 0xFF)
    for left, right in characters:
        char_image = trim_borders(image.crop((left, 0, right, image.size[1])))
        new_image.paste(char_image, (x, image.size[1] - char_image.size[1]))
        x += char_image.size[0] + border
    return new_image


def solve(captcha_image, template, typical_columns=[], typical_rows=[], **_):
    'Solve the captcha by comparing with a template.'
    template_image = PIL.Image.open(template)
    result = []

    captcha_chars, template_chars = map(
        split_by_whitespace, (
            captcha_image, template_image
        )
    )
    for captcha_char in captcha_chars:
        max_similarity = recognized_char = -1
        for digit, template_char in enumerate(template_chars):
            matrix = (
                (captcha_image,  captcha_char),
                (template_image, template_char),
            )
            current_similarity = sum(
                reduce(
                    operator.eq,
                    map(
                        # Typical columns are specified in a format similar to
                        # Python indexing, i.e. if it is below zero, it is
                        # treated as chars[-1] + typical_column; otherwise,
                        # it is parsed into chars[0] + col.
                        lambda z: z[0].getpixel((col + z[1][col < 0], row)),
                        matrix
                    )
                )
                for col in typical_columns or range(min(map(
                    lambda z: z[1][1] - z[1][0],
                    matrix
                )))
                for row in typical_rows or range(template_image.size[1])
            )
            if current_similarity > max_similarity:
                max_similarity = current_similarity
                recognized_char = digit
        result.append(recognized_char if recognized_char >= 0 else None)
    return result


def fetch(url):
    'Fetch the specified URL and return the contents as a byte stream.'
    fetched_bytes = urllib.request.urlopen(url).read()
    data_stream = io.BytesIO(fetched_bytes)
    return data_stream
