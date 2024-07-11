from django.contrib import admin
from Book.models import Category,Book,Borrow,Review,UserAccount
# Register your models here.
admin.site.register(Category)
admin.site.register(Book)
admin.site.register(Borrow)
admin.site.register(Review)
admin.site.register(UserAccount)

class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'description', 'borrowing_price', 'image')
    # Add other fields you want to display in the list view

    # Optionally, you can add search and filter options:
    search_fields = ['title', 'description']
    list_filter = ['borrowing_price']

    # Optionally, you can add readonly fields if needed:
    readonly_fields = ['image']

    # Optionally, you can add fieldsets to organize fields:
    fieldsets = (
        (None, {
            'fields': ('title', 'description', 'borrowing_price')
        }),
        ('Image', {
            'fields': ('image',)
        }),
    )