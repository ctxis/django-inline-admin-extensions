from collections import namedtuple
import copy
import types

import django
from django.template import Library
from django.contrib.admin.templatetags.admin_list import (
    paginator_number,
    pagination
)
from django.contrib.admin.utils import flatten_fieldsets

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


def get_updated_url(formset, old_param, new_param):
    query_dict = formset.cl.params.copy()
    ordering = query_dict.getlist(formset.order_param, [])

    try:
        index = ordering.index(old_param)
        if new_param:
            ordering[index] = new_param
        else:
            del ordering[index]
    except ValueError:
        ordering.append(new_param)

    query_dict.setlist(formset.order_param, ordering)
    return query_dict.urlencode()


SortingUrl = namedtuple('SortingUrl', ['sort', 'toggle', 'remove'])


def get_toggle_remove_urls(formset, ordering):
    toggle_remove_urls = {}
    for param in reversed(ordering):
        none, pfx, field_name = param.rpartition('-')
        if pfx == '-':
            toggle_remove_urls[field_name] = SortingUrl(
                'ascending',
                get_updated_url(formset, param, field_name),
                get_updated_url(formset, param, ''),
            )
        elif pfx == '':
            toggle_remove_urls[field_name] = SortingUrl(
                'descending',
                get_updated_url(formset, param, ''.join(['-', param])),
                get_updated_url(formset, param, '')
            )
    return toggle_remove_urls


SortableField = namedtuple('SortableField', ['name', 'field', 'urls'])


@register.inclusion_tag('admin/edit_inline/tabular_header_row.html')
def table_header_row(inline_admin_formset):
    '''Similar to InlineAdminFormSet.fields but also returns field name

    Update the dict returned by InlineAdminFormSet.fields and update it with
    additional attributes that we need for adding sorting urls.
    '''
    formset = inline_admin_formset.formset
    query_dict = formset.cl.params.copy()
    ordering = query_dict.getlist(formset.order_param, [])
    toggle_remove_urls = get_toggle_remove_urls(formset, ordering)

    try:
        fk_name = formset.fk.name
    except AttributeError:
        fk_name = None
    field_names = [i for i in flatten_fieldsets(inline_admin_formset.fieldsets)
                   if i != fk_name]

    fields = []
    for field_name, field in zip(field_names, inline_admin_formset.fields()):
        try:
            urls = toggle_remove_urls[field_name]
        except KeyError:
            toggle = get_updated_url(formset, None, field_name)
            urls = SortingUrl('', toggle, '')
        fields.append(SortableField(field_name, field, urls))

    return {
        'fields': fields,
        'formset': formset,
    }


@register.simple_tag
def django_version():
    return django.VERSION
