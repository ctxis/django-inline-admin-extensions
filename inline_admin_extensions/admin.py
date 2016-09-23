from django.contrib import admin
from django.contrib.admin.views.main import ChangeList, ORDER_VAR
from django.core import exceptions
from django.core.paginator import EmptyPage, InvalidPage, Paginator


class InlineChangeList(object):
    can_show_all = True
    multi_page = True
    get_query_string = ChangeList.__dict__['get_query_string']

    def __init__(self, request, page_num, page_param, paginator):
        self.show_all = 'all' in request.GET
        self.page_num = page_num
        self.page_param = page_param
        self.paginator = paginator
        self.result_count = paginator.count
        self.params = request.GET


def pagination_formset_factory(formset_class, request, **cls_attrs):
    class PaginationFormSet(formset_class):
        def __init__(self, *args, **kwargs):
            super(PaginationFormSet, self).__init__(*args, **kwargs)

            qs = self.queryset
            paginator = Paginator(qs, self.per_page)
            try:
                page_num = int(request.GET.get(self.page_param, '0'))
            except ValueError:
                page_num = 0
            self.page_num = page_num

            try:
                page = paginator.page(page_num + 1)
            except (EmptyPage, InvalidPage):
                page = paginator.page(paginator.num_pages)

            self.cl = InlineChangeList(request, page_num, self.page_param,
                                       paginator)
            self.paginator = paginator

            if self.cl.show_all:
                self._queryset = qs
            else:
                self._queryset = page.object_list

    for k, v in cls_attrs.items():
        setattr(PaginationFormSet, k, v)

    return PaginationFormSet


class PaginationInline(admin.TabularInline):
    template = 'admin/edit_inline/tabular_paginated.html'
    per_page = 20

    @property
    def page_param(self):
        return self.model.__name__.lower()

    @property
    def order_param(self, prefix=ORDER_VAR):
        return '_'.join([prefix, self.model.__name__.lower()])

    def get_formset(self, request, obj=None, **kwargs):
        formset_class = super(PaginationInline, self).get_formset(
            request, obj, **kwargs)

        return pagination_formset_factory(
            formset_class,
            request,
            per_page=self.per_page,
            page_param=self.page_param,
            order_param=self.order_param,
        )

    def get_queryset(self, request):
        queryset = super(PaginationInline, self).get_queryset(request)
        return queryset

    def get_ordering(self, request):
        ordering = super(PaginationInline, self).get_ordering(request)
        if self.order_param not in request.GET:
            return ordering

        ordering = []
        order_params = request.GET.getlist(self.order_param)
        for p in order_params:
            none, pfx, idx = p.rpartition('-')
            try:
                self.model._meta.get_field(idx)
                ordering.append(p)
            except exceptions.FieldDoesNotExist:
                pass
        return ordering
