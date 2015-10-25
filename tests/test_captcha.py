import os
import nose
import json
import captcha


def load_json_config(function):
    def test_case():
        path = 'tests/templates/'
        for file in os.listdir(path):
            if file.rsplit('.', 1)[-1] == 'json':
                with open(path + file) as f:
                    params = json.load(f)
                    function(params)
    test_case.__name__ = function.__name__
    return test_case


@load_json_config
def test_captcha_solver(params):
    path = params.get('samples')
    if path is None:
        return
    for file in os.listdir(path):
        image = captcha.image_filter(path + file, params)
        result = captcha.solve(image, params)
        assert ''.join(map(str, result)) == file.rsplit('.', 1)[0]


@load_json_config
def test_get_image_by_url(params):
    for i in range(3):
        image_data = captcha.fetch(params['url'])
        image = captcha.image_filter(image_data, params)
        result = captcha.solve(image, params)
        assert len(result) == params.get('length', 4)
        assert all(x is not None for x in result)
