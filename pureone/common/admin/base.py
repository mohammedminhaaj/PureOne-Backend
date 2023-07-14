from django.contrib import admin

admin.site.site_header = 'PureOne Admin'
admin.site.site_title = 'PureOne Admin'
admin.site.index_title = 'PureOne Admin Portal'

class AuditedAdminMixin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
        else:
            obj.modified_by = request.user
            if obj.created_by is None:
                obj.created_by = request.user
        return super().save_model(request, obj, form, change)
    
    def delete_model(self, request, obj) -> None:
        obj.deleted_by = request.user
        return super().delete_model(request, obj)