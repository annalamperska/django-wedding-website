from django.contrib import admin
from .models import Guest, Party


class GuestInline(admin.TabularInline):
    model = Guest
    fields = ('first_name', 'last_name', 'email', 'is_attending', 'meal', 'is_allergic', 'allergic', 'is_plus_one', 'plus_one_name')
    readonly_fields = ('first_name', 'last_name')


class PartyAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'save_the_date_sent', 'invitation_sent', 'rehearsal_dinner', 'invitation_opened',
                    'is_attending')
    list_filter = ('category', 'is_attending', 'rehearsal_dinner', 'invitation_opened')
    inlines = [GuestInline]


class GuestAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'party', 'email', 'is_attending', 'meal', 'is_allergic', 'allergic', 'is_plus_one', 'plus_one_name')
    list_filter = ('is_attending', 'is_plus_one', 'meal', 'is_allergic', 'party__category', 'party__rehearsal_dinner')


admin.site.register(Party, PartyAdmin)
admin.site.register(Guest, GuestAdmin)
