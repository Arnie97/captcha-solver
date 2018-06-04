import os
import json
import captcha


def load_json_config(function):
    def test_case(templates='tests/templates', samples='tests/samples'):
        for file in os.listdir(templates):
            name, ext = os.path.splitext(file)
            if ext != '.json':
                continue
            with open(os.path.join(templates, file)) as f:
                params = json.load(f)
            if 'template' not in params:
                default_template = os.path.join(templates, name + '.bmp')
                if os.path.isfile(default_template):
                    params['template'] = default_template
            if 'samples' not in params:
                default_samples = os.path.join(samples, name)
                if os.path.isdir(default_samples):
                    params['samples'] = default_samples
            function(**params)
    test_case.__name__ = function.__name__
    return test_case


@load_json_config
def test_captcha_solver(samples=None, **params):
    if not samples:
        return
    for file in os.listdir(samples):
        image = captcha.image_filter(os.path.join(samples, file), **params)
        result = captcha.solve(image, **params)
        assert ''.join(map(str, result)) == os.path.splitext(file)[0], samples


@load_json_config
def test_get_image_by_url(url=None, length=4, **params):
    if not url:
        return
    for i in range(3):
        image_data = captcha.fetch(url)
        image = captcha.image_filter(image_data, **params)
        result = captcha.solve(image, **params)
        assert len(result) == length, url
        assert all(x is not None for x in result), url
