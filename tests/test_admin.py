from django.urls import reverse
from django_mock_queries.query import MockSet
from django_mock_queries.query import MockModel
import pytest
import mock
from model_mommy import mommy

from inline_admin_extensions.admin import pagination_formset_factory


class MockFormset(object):
    queryset = MockSet(*[MockModel(name=str(i)) for i in range(0, 100)])
    per_page = 20
    page_param = 'mock'


def test_pagination_formset_factory(rf):
    request = rf.get('/?mock=2')
    formset_cls = pagination_formset_factory(MockFormset, request,
                                             per_page=20, page_param='mock')
    formset = formset_cls()
    assert len(formset._queryset) == 20
    assert formset._queryset[0].name == '40'


def test_pagination_formset_factory__show_all(rf):
    request = rf.get('/?all=a')
    formset_cls = pagination_formset_factory(MockFormset, request,
                                             per_page=20, page_param='mock')
    formset = formset_cls()
    assert formset._queryset.count() == 100
    assert formset._queryset[0].name == '0'


def test_pagination_formset_factory__invalid_parameter(rf):
    request = rf.get('/?mock=hello')
    formset_cls = pagination_formset_factory(MockFormset, request,
                                             per_page=20, page_param='mock')
    formset = formset_cls()
    assert len(formset._queryset) == 20
    assert formset._queryset[0].name == '0'


def test_pagination_formset_factory__invalid_page(rf):
    request = rf.get('/?mock=100')
    formset_cls = pagination_formset_factory(MockFormset, request,
                                             per_page=20, page_param='mock')
    formset = formset_cls()
    assert len(formset._queryset) == 20
    assert formset._queryset[0].name == '80'


@pytest.mark.django_db
def test_pagination_inline(admin_client):
    author = mommy.make('Author')
    mommy.make('Book', wololol='wololol', author=author, _quantity=40)
    response = admin_client.get(reverse('admin:examples_author_change',
                                        args=[author.id]))
    assert 'paginator' in response.content
    assert '<span class="this-page">1</span>' in response.content
    assert '<a href="?book=1" class="end">2</a>' in response.content
    assert 'Show all' in response.content


@pytest.mark.django_db
@mock.patch('examples.admin.BookInline.page_param', 'custom')
def test_pagination_inline__custom_page_param(admin_client):
    author = mommy.make('Author')
    mommy.make('Book', wololol='wololol', author=author, _quantity=40)
    response = admin_client.get(reverse('admin:examples_author_change',
                                        args=[author.id]))

    assert '<a href="?custom=1" class="end">2</a>' in response.content
