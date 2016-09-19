from django.contrib import admin

from inline_admin_extensions.admin import PaginationInline
from examples.models import Author, Book


class BookInline(PaginationInline):
    model = Book


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    inlines = [BookInline]
