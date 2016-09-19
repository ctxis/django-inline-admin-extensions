import copy
import types

from django.template import Library
from django.contrib.admin.templatetags.admin_list import (
    paginator_number,
    pagination
)

register = Library()


@register.simple_tag
def parameterized_paginator_number(cl, i):
    '''This ridiculous code makes a copy of paginator_number function
    
    The PAGE_VAR variable is global in paginator number, this function copies
    paginator_number and replaces the global PAGE_VAR with a page_param that
    we can set.
    '''
    # copy the globals of paginator_number
    func_globals_copy = copy.copy(paginator_number.__globals__)
    func_globals_copy['PAGE_VAR'] = cl.page_param

    paginator_number_func_copy = types.FunctionType(
        code=paginator_number.__code__,
        # pass our updated globals
        globals=func_globals_copy,
        name='parameterized_paginator_number',
        argdefs=paginator_number.__defaults__,
        closure=paginator_number.__closure__,
    )
    return paginator_number_func_copy(cl, i)


@register.inclusion_tag('admin/edit_inline/tabular_inline_pagination.html')
def tabular_inline_pagination(cl):
    return pagination(cl)
