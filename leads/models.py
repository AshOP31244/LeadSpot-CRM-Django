from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


# --------------------
# USER ROLE PROFILE
# --------------------
class Profile(models.Model):
    ROLE_CHOICES = (
        ('marketing', 'Marketing'),
        ('sales', 'Sales'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

    def __str__(self):
        return f"{self.user.username} - {self.role}"


# --------------------
# LEAD MODEL
# --------------------
class Lead(models.Model):
    STAGE_CHOICES = (
        ('prospect', 'Prospect'),
        ('requirement_yes', 'Requirement Yes'),
        ('future', 'Future Requirement'),
        ('reconnect', 'Reconnect'),
        ('regret', 'Regret Offer'),
    )

    # Basic Info
    lead_code = models.CharField(max_length=20, unique=True)
    company_name = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    sector = models.CharField(max_length=100, null=True, blank=True)
    source = models.CharField(max_length=100, null=True, blank=True)

    # Contact Info
    contact_name = models.CharField(max_length=150, null=True, blank=True)
    contact_email = models.EmailField(null=True, blank=True)
    contact_phone = models.CharField(max_length=15, null=True, blank=True)
    department = models.CharField(max_length=100, null=True, blank=True)

    # Stage Management
    stage = models.CharField(max_length=30, choices=STAGE_CHOICES, default='prospect')
    
    # Client Type (filled when moving from prospect)
    client_type_main = models.CharField(max_length=50, null=True, blank=True)
    client_type_detail = models.CharField(max_length=100, null=True, blank=True)

    # Metadata
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='leads_created')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    #recconect
    last_call_date = models.DateField(null=True, blank=True)  # Last time someone called
    last_remark = models.TextField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.lead_code} - {self.company_name}"


# --------------------
# CALL HISTORY
# --------------------
class CallHistory(models.Model):
    OUTCOME_CHOICES = (
        ('yes', 'Requirement Yes'),
        ('future', 'Future Requirement'),
        ('reconnect', 'Reconnect'),
        ('regret', 'Regret Offer'),
    )

    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name='call_history')
    
    # Call Dates
    expected_call_date = models.DateField(null=True, blank=True)
    actual_call_date = models.DateField()
    
    # Outcome
    outcome = models.CharField(max_length=20, choices=OUTCOME_CHOICES)
    remark = models.TextField()

    # Metadata
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-actual_call_date']
        verbose_name_plural = "Call Histories"

    def __str__(self):
        return f"{self.lead.company_name} - {self.outcome} on {self.actual_call_date}"


# --------------------
# REQUIREMENT YES DATA
# --------------------
class RequirementYes(models.Model):
    SALES_STAGE_CHOICES = (
        ('costing_created', 'Costing Created'),
        ('quotation_created', 'Quotation Created'),
        ('quotation_sent', 'Quotation Sent'),
        ('quotation_revision', 'Quotation Revision'),
        ('quotation_accepted', 'Quotation Accepted'),
        ('po_received', 'PO Received'),
        ('oa_created', 'OA Created'),
        ('oa_sent', 'OA Sent'),
        ('oa_revision', 'OA Revision'),
        ('oa_accepted', 'OA Accepted'),
        ('order_completed', 'Order Completed'),
        ('order_lost', 'Order Lost'),
    )

    lead = models.OneToOneField(Lead, on_delete=models.CASCADE)

    client_type_main = models.CharField(max_length=50)
    client_type_detail = models.CharField(max_length=100, blank=True, null=True)

    tank_application = models.CharField(max_length=255, blank=True, null=True)
    tank_location = models.CharField(max_length=255, blank=True, null=True)

    tanks_json = models.JSONField(default=list)

    assigned_sales_person = models.CharField(max_length=100, blank=True, null=True)

    expected_delivery_date = models.DateField(blank=True, null=True)
    followup_date = models.DateField(blank=True, null=True)

    sales_stage = models.CharField(max_length=50, choices=SALES_STAGE_CHOICES, default='costing_created')
    current_remark = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

# --------------------
# QUOTATION TRACKING
# --------------------
class Quotation(models.Model):
    requirement = models.ForeignKey(RequirementYes, on_delete=models.CASCADE, related_name='quotations')
    
    expected_date = models.DateField()
    actual_date = models.DateField(null=True, blank=True)
    
    quotation_number = models.CharField(max_length=50, null=True, blank=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    
    notes = models.TextField(null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Quotation for {self.requirement.lead.company_name}"


# --------------------
# MEETING SCHEDULE
# --------------------
class Meeting(models.Model):
    requirement = models.ForeignKey(RequirementYes, on_delete=models.CASCADE, related_name='meetings')
    
    meeting_date = models.DateField()
    meeting_type = models.CharField(
        max_length=20,
        choices=(
            ('online', 'Online'),
            ('onsite', 'On-site'),
            ('phone', 'Phone Call'),
        ),
        default='online'
    )
    
    attendees = models.CharField(max_length=255, null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    outcome = models.TextField(null=True, blank=True)
    
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-meeting_date']

    def __str__(self):
        return f"Meeting - {self.requirement.lead.company_name} on {self.meeting_date}"


# --------------------
# STAGE HISTORY (AUDIT TRAIL)
# --------------------
class StageHistory(models.Model):
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name='stage_history')
    
    from_stage = models.CharField(max_length=30)
    to_stage = models.CharField(max_length=30)
    
    changed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    changed_at = models.DateTimeField(auto_now_add=True)
    
    notes = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ['-changed_at']
        verbose_name_plural = "Stage Histories"

    def __str__(self):
        return f"{self.lead.company_name}: {self.from_stage} → {self.to_stage}"


# --------------------
# REGRET OFFER DATA
# --------------------
class RegretOffer(models.Model):
    """Stores data when lead is marked as Regret Offer"""
    
    lead = models.OneToOneField(Lead, on_delete=models.CASCADE, related_name='regret_data')
    
    # Client Type Details
    client_type_main = models.CharField(max_length=50)
    client_type_detail = models.CharField(max_length=100, null=True, blank=True)
    
    # Tank Details (Competitor)
    tank_type = models.CharField(max_length=100)
    tank_type_other = models.CharField(max_length=100, null=True, blank=True)
    
    # Follow-up
    followup_date = models.DateField()
    remark = models.TextField()
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.lead.company_name} - Regret Offer"


# --------------------
# FUTURE REQUIREMENT DATA
# --------------------
class FutureRequirement(models.Model):
    """Stores data when lead is marked as Future Requirement"""
    
    lead = models.OneToOneField(Lead, on_delete=models.CASCADE, related_name='future_data')
    
    # Client Type Details
    client_type_main = models.CharField(max_length=50)
    client_type_detail = models.CharField(max_length=100, null=True, blank=True)
    
    # Timeline
    followup_date = models.DateField()
    expected_timeline = models.CharField(max_length=100, null=True, blank=True)
    
    remark = models.TextField()
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.lead.company_name} - Future Requirement"


# --------------------
# ADDITIONAL CONTACTS
# --------------------
class AdditionalContact(models.Model):
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name='additional_contacts')
    
    CONTACT_TYPE_CHOICES = (
        ('phone', 'Phone'),
        ('email', 'Email'),
    )
    
    contact_type = models.CharField(max_length=10, choices=CONTACT_TYPE_CHOICES)
    contact_value = models.CharField(max_length=255)
    is_primary = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.lead.company_name} - {self.contact_type}: {self.contact_value}"