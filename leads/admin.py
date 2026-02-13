from django.contrib import admin
from .models import (
    Lead, Profile, CallHistory, RequirementYes,
    StageHistory, Quotation, Meeting, RegretOffer,
    FutureRequirement, AdditionalContact
)

@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ['lead_code', 'company_name', 'city', 'stage', 'created_at']
    list_filter = ['stage', 'created_at']
    search_fields = ['company_name', 'lead_code', 'contact_name']

@admin.register(RequirementYes)
class RequirementYesAdmin(admin.ModelAdmin):
    list_display = ['lead', 'client_type_main', 'assigned_sales_person', 'sales_stage', 'created_at']
    list_filter = ['sales_stage', 'client_type_main', 'assigned_sales_person', 'created_at']
    search_fields = ['lead__company_name', 'lead__lead_code', 'tank_application']
    
    fieldsets = (
        ('Lead Information', {
            'fields': ('lead',)
        }),
        ('Client Details', {
            'fields': ('client_type_main', 'client_type_detail')
        }),
        ('Tank Details', {
            'fields': ('tank_application', 'tank_location', 'tanks_json')
        }),
        ('Assignment', {
            'fields': ('assigned_sales_person', 'expected_delivery_date')
        }),
        ('Sales Tracking', {
            'fields': ('sales_stage', 'current_remark', 'followup_date')
        }),
    )
    
    # Make optional fields not required in admin
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        # These fields are optional
        optional_fields = ['client_type_detail', 'tank_location', 'expected_delivery_date', 
                          'current_remark', 'followup_date']
        for field_name in optional_fields:
            if field_name in form.base_fields:
                form.base_fields[field_name].required = False
        return form
    
    # Show tanks in a more readable format
    readonly_fields = ['formatted_tanks']
    
    def formatted_tanks(self, obj):
        if not obj.tanks_json:
            return "No tanks"
        tanks_str = ""
        for i, tank in enumerate(obj.tanks_json, 1):
            tanks_str += f"{i}. {tank.get('type', 'N/A')} - {tank.get('capacity', 'N/A')} - Qty: {tank.get('quantity', 'N/A')}\n"
        return tanks_str
    formatted_tanks.short_description = "Tank Details"

@admin.register(CallHistory)
class CallHistoryAdmin(admin.ModelAdmin):
    list_display = ['lead', 'outcome', 'actual_call_date', 'created_by', 'created_at']
    list_filter = ['outcome', 'actual_call_date']
    search_fields = ['lead__company_name', 'remark']

@admin.register(StageHistory)
class StageHistoryAdmin(admin.ModelAdmin):
    list_display = ['lead', 'from_stage', 'to_stage', 'changed_by', 'changed_at']
    list_filter = ['from_stage', 'to_stage', 'changed_at']
    search_fields = ['lead__company_name', 'notes']

@admin.register(Meeting)
class MeetingAdmin(admin.ModelAdmin):
    list_display = ['requirement', 'meeting_date', 'meeting_type', 'created_by']
    list_filter = ['meeting_type', 'meeting_date']
    search_fields = ['requirement__lead__company_name', 'attendees', 'notes']

@admin.register(Quotation)
class QuotationAdmin(admin.ModelAdmin):
    list_display = ['requirement', 'expected_date', 'actual_date', 'quotation_number', 'amount']
    list_filter = ['expected_date', 'actual_date']
    search_fields = ['requirement__lead__company_name', 'quotation_number']

admin.site.register(Profile)
admin.site.register(RegretOffer)
admin.site.register(FutureRequirement)
admin.site.register(AdditionalContact)