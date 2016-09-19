import mock
from django.contrib.admin.templatetags.admin_list import paginator_number
from inline_admin_extensions.templatetags.inline_admin_paginator import (
    parameterized_paginator_number
)
from inline_admin_extensions import admin


def test_parameterized_paginator_number__same_as_paginator_number(rf):
    '''Test that our copy implementation matches the django paginator_number'''
    request = rf.get('/')
    mock_paginator = mock.Mock(num_pages=50)
    cl = admin.InlineChangeList(request, 0, 'p', mock_paginator)
    assert parameterized_paginator_number(cl, '.') == paginator_number(cl, '.')
    assert parameterized_paginator_number(cl, 0) == paginator_number(cl, 0)
    assert parameterized_paginator_number(cl, 1) == paginator_number(cl, 1)
    assert parameterized_paginator_number(cl, 1) != paginator_number(cl, 0)


def test_parameterized_paginator_number__different_parameter(rf):
    request = rf.get('/')
    mock_paginator = mock.Mock(num_pages=50)
    cl = admin.InlineChangeList(request, 0, 'different_param', mock_paginator)
    assert parameterized_paginator_number(cl, '.') == paginator_number(cl, '.')
    assert parameterized_paginator_number(cl, 0) == paginator_number(cl, 0)
    assert parameterized_paginator_number(cl, 1) != paginator_number(cl, 1)
    assert parameterized_paginator_number(cl, 1) != paginator_number(cl, 0)
    assert 'different_param=1' in parameterized_paginator_number(cl, 1)
