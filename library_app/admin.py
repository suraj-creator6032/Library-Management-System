from django.contrib import admin
from .models import (
    Departments,
    Members,
    Authors,
    Publishers,
    Categories,
    Books,
    BookAuthors,
    BookCopies,
    Loans,
    Reservations,
    Fines,
    Payments,
    LibrarySettings,
    UserProfile,
)


@admin.register(Books)
class BooksAdmin(admin.ModelAdmin):
    list_display = ('book_id', 'title', 'isbn', 'edition')
    search_fields = ('title', 'isbn')


@admin.register(Members)
class MembersAdmin(admin.ModelAdmin):
    list_display = (
        'member_id',
        'college_id',
        'full_name',
        'email',
        'member_type',
        'membership_status',
    )
    search_fields = ('college_id', 'full_name', 'email')
    list_filter = ('member_type', 'membership_status')


@admin.register(BookCopies)
class BookCopiesAdmin(admin.ModelAdmin):
    list_display = (
        'copy_id',
        'accession_number',
        'book_id',
        'copy_status',
        'shelf_location',
    )
    search_fields = ('accession_number',)
    list_filter = ('copy_status',)


admin.site.register(Departments)
admin.site.register(Authors)
admin.site.register(Publishers)
admin.site.register(Categories)
admin.site.register(Loans)
admin.site.register(Reservations)
admin.site.register(Fines)
admin.site.register(Payments)
admin.site.register(LibrarySettings)
admin.site.register(UserProfile)
