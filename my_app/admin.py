from django.contrib import admin

from .models import MpesaDeposits


class MpesaAdmin(admin.ModelAdmin):
    model = MpesaDeposits
    list_display = ['phone_number', 'reference',
                    'transaction_date', 'amount', ]

    def get_name(self, obj):
        return obj.MpesaDeposits.phone_number
    get_name.admin_order_field = 'transaction_date'  # Allows column order sorting
    # get_name.short_description = 'Author Na'  #Renames column head

    # Filtering on side - for some reason, this works
    #list_filter = ['title', 'author__name']


admin.site.register(MpesaDeposits, MpesaAdmin)
