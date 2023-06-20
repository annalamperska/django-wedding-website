from django.contrib import admin
from .models import Guest, Party


class GuestInline(admin.TabularInline):
    model = Guest
    fields = ('first_name', 'last_name', 'is_attending', 'meal', 'is_allergic', 'allergic', 'is_plus_one', 'plus_one_name')
    readonly_fields = ('first_name', 'last_name')


class PartyAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'invitation_opened', 'is_attending', 'phoneNumber', 'emailAddress', 'comments')
    list_filter = ('category', 'is_attending', 'invitation_opened')
    inlines = [GuestInline]


class GuestAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'party', 'is_attending', 'meal', 'is_allergic', 'allergic', 'is_plus_one', 'plus_one_name')
    list_filter = ('is_attending', 'is_plus_one', 'meal', 'is_allergic', 'party__category')


admin.site.register(Party, PartyAdmin)
admin.site.register(Guest, GuestAdmin)
