from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden, JsonResponse
from django.contrib import messages
from django.db import transaction
import json
from datetime import datetime, timedelta
from django.urls import reverse
from django.utils import timezone
from django.db.models import Q
from difflib import SequenceMatcher 

from .models import (
    Lead, Profile, CallHistory, RequirementYes, 
    StageHistory, Quotation, Meeting, RegretOffer, 
    FutureRequirement, AdditionalContact
)
from .forms import LeadCreateForm


# ===========================================
# HELPER FUNCTION: Clear Lead States
# ===========================================
def clear_lead_states(lead):
    """Clear all state-specific objects when moving between major stages"""
    RegretOffer.objects.filter(lead=lead).delete()
    FutureRequirement.objects.filter(lead=lead).delete()
    RequirementYes.objects.filter(lead=lead).delete()


# ===========================================
# LEAD LIST (ALL PROSPECTS)
# ===========================================
@login_required
def lead_list(request):
    """Show all leads in Prospect stage"""
    profile, _ = Profile.objects.get_or_create(
        user=request.user,
        defaults={'role': 'marketing'}
    )
    
    # Marketing sees all prospects
    if profile.role == 'marketing':
        leads = Lead.objects.filter(stage='prospect')
    else:
        # Sales sees requirement_yes leads
        leads = Lead.objects.filter(stage='requirement_yes')
    
    return render(request, 'leads/lead_list.html', {
        'leads': leads,
        'role': profile.role
    })


# ===========================================
# LEAD DETAIL (PROSPECT STAGE)
# ===========================================
@login_required
def lead_detail(request, lead_id):
    lead = get_object_or_404(Lead, id=lead_id)

    if request.user.profile.role != 'marketing':
        return HttpResponseForbidden("Only marketing can update prospect leads.")

    if request.method == 'POST':
        with transaction.atomic():
            actual_call_date = request.POST.get('actual_call_date')
            expected_call_date = request.POST.get('expected_call_date')
            outcome = request.POST.get('outcome')

            if not actual_call_date or not outcome:
                messages.error(request, 'Please fill all required fields')
                return render(request, 'leads/lead_detail.html', {'lead': lead})

            # 🔹 Get outcome-specific remark
            outcome_remark = ''
            if outcome == 'yes':
                outcome_remark = request.POST.get('remark', '')
            elif outcome == 'reconnect':
                outcome_remark = request.POST.get('remark_reconnect', '')
            elif outcome == 'future':
                outcome_remark = request.POST.get('remark_future', '')
            elif outcome == 'regret':
                outcome_remark = request.POST.get('remark_regret', '')

            # 🔹 Always save call history FIRST (important)
            CallHistory.objects.create(
                lead=lead,
                expected_call_date=expected_call_date or None,
                actual_call_date=actual_call_date,
                outcome=outcome,
                remark=outcome_remark,
                created_by=request.user
            )

            if outcome == 'yes':
                return handle_requirement_yes(request, lead)

            elif outcome == 'regret':
                return handle_regret_offer(request, lead, actual_call_date, expected_call_date)

            elif outcome == 'future':
                return handle_future_requirement(request, lead, actual_call_date, expected_call_date)

            elif outcome == 'reconnect':
                return handle_reconnect(request, lead, actual_call_date, expected_call_date)

    # ✅ NEW: Get call history for this lead
    call_history = CallHistory.objects.filter(
        lead=lead
    ).select_related('created_by').order_by('-actual_call_date')
    
    # ✅ NEW: Get only reconnect history (optional - you can show all)
    reconnect_history = CallHistory.objects.filter(
        lead=lead,
        outcome='reconnect'
    ).select_related('created_by').order_by('-actual_call_date')

    return render(request, 'leads/lead_detail.html', {
        'lead': lead,
        'call_history': call_history,  # All call history
        'reconnect_history': reconnect_history  # Only reconnects
    })

# ===========================================
# HANDLE REQUIREMENT YES
# ===========================================
def handle_requirement_yes(request, lead):
    client_type_main = request.POST.get('client_type_main')
    tank_application = request.POST.get('tank_application')
    assigned_sales = request.POST.get('assigned_sales_person')
    remark = request.POST.get('remark', '')

    if not client_type_main or not tank_application or not assigned_sales:
        messages.error(request, "Missing required Requirement details")
        return redirect('lead_detail', lead_id=lead.id)

    # ----------------------------------
    # ✅ COLLECT TANK DETAILS
    # ----------------------------------
    tank_types = request.POST.getlist('tank_type[]')
    tank_capacities = request.POST.getlist('tank_capacity[]')
    tank_quantities = request.POST.getlist('tank_quantity[]')

    # 🔍 DEBUG: Print to console
    print(f"DEBUG - Tank Types: {tank_types}")
    print(f"DEBUG - Tank Capacities: {tank_capacities}")
    print(f"DEBUG - Tank Quantities: {tank_quantities}")

    tanks = []
    for t, c, q in zip(tank_types, tank_capacities, tank_quantities):
        if t and c and q:
            tanks.append({
                "tank_type": t,
                "capacity": c,
                "quantity": int(q)
            })

    print(f"DEBUG - Final tanks array: {tanks}")  # 🔍 DEBUG

    if not tanks:
        messages.error(request, "Please add at least one tank detail")
        return redirect('lead_detail', lead_id=lead.id)

    old_stage = lead.stage

    # ----------------------------------
    # ✅ UPDATE LEAD
    # ----------------------------------
    lead.stage = 'requirement_yes'
    lead.client_type_main = client_type_main
    lead.client_type_detail = (
        request.POST.get('consultant_type')
        or request.POST.get('contractor_type')
        or request.POST.get('endclient_category')
        or ''
    )
    lead.save()

    # ----------------------------------
    # ✅ CREATE OR UPDATE REQUIREMENT YES
    # ----------------------------------
    requirement, created = RequirementYes.objects.get_or_create(
        lead=lead,
        defaults={
            'client_type_main': client_type_main,
            'client_type_detail': lead.client_type_detail,
            'tank_application': tank_application,
            'tank_location': request.POST.get('tank_location', ''),
            'assigned_sales_person': assigned_sales,
            'expected_delivery_date': request.POST.get('expected_delivery_date') or None,
            'tanks_json': tanks,
            'current_remark': remark,
            'sales_stage': 'costing_created'  # ✅ Changed from 'quotation_sent'
        }
    )

    if not created:
        requirement.client_type_main = client_type_main
        requirement.client_type_detail = lead.client_type_detail
        requirement.tank_application = tank_application
        requirement.tank_location = request.POST.get('tank_location', '')
        requirement.assigned_sales_person = assigned_sales
        requirement.expected_delivery_date = request.POST.get('expected_delivery_date') or None
        requirement.tanks_json = tanks
        requirement.current_remark = remark
        requirement.save()

    print(f"DEBUG - Saved requirement tanks_json: {requirement.tanks_json}")  # 🔍 DEBUG

    # ----------------------------------
    # ✅ STAGE HISTORY
    # ----------------------------------
    if old_stage != 'requirement_yes':
        StageHistory.objects.create(
            lead=lead,
            from_stage=old_stage,
            to_stage='requirement_yes',
            changed_by=request.user,
            notes='Converted to Requirement Yes'
        )

    messages.success(request, 'Lead moved to Requirement Yes')
    return redirect('requirement_yes_detail', lead_id=lead.id)


# ===========================================
# HANDLE REGRET OFFER
# ===========================================
def handle_regret_offer(request, lead, actual_call_date, expected_call_date):
    """Process Regret Offer outcome"""
    
    client_type_main = request.POST.get('client_type_regret')
    followup_date = request.POST.get('followup_date_regret')
    tank_type = request.POST.get('tank_type_regret')
    remark = request.POST.get('remark_regret')
    
    if not all([client_type_main, followup_date, tank_type, remark]):
        messages.error(request, 'Please fill all required fields')
        return render(request, 'leads/lead_detail.html', {'lead': lead})
    
    # Get client type detail
    client_type_detail = None
    if client_type_main == 'CONSULTANT':
        consultant_type = request.POST.get('consultant_type_regret')
        client_type_detail = request.POST.get('consultant_other_text_regret') if consultant_type == 'Other' else consultant_type
    elif client_type_main == 'CONTRACTOR':
        contractor_type = request.POST.get('contractor_type_regret')
        client_type_detail = request.POST.get('contractor_other_text_regret') if contractor_type == 'Other' else contractor_type
    elif client_type_main == 'END_CLIENT':
        endclient_category = request.POST.get('endclient_category_regret')
        client_type_detail = request.POST.get('endclient_other_text_regret') if endclient_category == 'Other' else endclient_category
    
    tank_type_other = request.POST.get('tank_type_other_text_regret') if tank_type == 'Other' else None
    
    # Update lead
    old_stage = lead.stage
    lead.stage = 'regret'
    lead.save()
    
    # Create call history
    CallHistory.objects.create(
        lead=lead,
        expected_call_date=expected_call_date or None,
        actual_call_date=actual_call_date,
        outcome='regret',
        remark=remark,
        created_by=request.user
    )
    
    # ✅ FIX 1: Use get_or_create for RegretOffer (idempotent)
    regret_offer, created = RegretOffer.objects.get_or_create(
        lead=lead,
        defaults={
            'client_type_main': client_type_main,
            'client_type_detail': client_type_detail,
            'tank_type': tank_type,
            'tank_type_other': tank_type_other,
            'followup_date': followup_date,
            'remark': remark,
        }
    )
    
    if not created:
        # Update existing regret offer
        regret_offer.client_type_main = client_type_main
        regret_offer.client_type_detail = client_type_detail
        regret_offer.tank_type = tank_type
        regret_offer.tank_type_other = tank_type_other
        regret_offer.followup_date = followup_date
        regret_offer.remark = remark
        regret_offer.save()
    
    # Create stage history
    StageHistory.objects.create(
        lead=lead,
        from_stage=old_stage,
        to_stage='regret',
        changed_by=request.user,
        notes=f"Moved to Regret Offer. Competitor: {tank_type}"
    )
    
    messages.success(request, f'{lead.company_name} moved to Regret Offer')
    return redirect('regret_offers_list')


# ===========================================
# HANDLE FUTURE REQUIREMENT
# ===========================================
def handle_future_requirement(request, lead, actual_call_date, expected_call_date):
    """Process Future Requirement outcome"""
    
    client_type_main = request.POST.get('client_type_future')
    followup_date = request.POST.get('followup_date_future')
    remark = request.POST.get('remark_future')
    
    if not all([client_type_main, followup_date, remark]):
        messages.error(request, 'Please fill all required fields')
        return render(request, 'leads/lead_detail.html', {'lead': lead})
    
    # Get client type detail
    client_type_detail = None
    if client_type_main == 'CONSULTANT':
        consultant_type = request.POST.get('consultant_type_future')
        client_type_detail = request.POST.get('consultant_other_text_future') if consultant_type == 'Other' else consultant_type
    elif client_type_main == 'CONTRACTOR':
        contractor_type = request.POST.get('contractor_type_future')
        client_type_detail = request.POST.get('contractor_other_text_future') if contractor_type == 'Other' else contractor_type
    elif client_type_main == 'END_CLIENT':
        endclient_category = request.POST.get('endclient_category_future')
        client_type_detail = request.POST.get('endclient_other_text_future') if endclient_category == 'Other' else endclient_category
    
    # Update lead
    old_stage = lead.stage
    lead.stage = 'future'
    lead.save()
    
    # Create call history
    CallHistory.objects.create(
        lead=lead,
        expected_call_date=expected_call_date or None,
        actual_call_date=actual_call_date,
        outcome='future',
        remark=remark,
        created_by=request.user
    )
    
    # ✅ Apply same pattern for FutureRequirement
    future_req, created = FutureRequirement.objects.get_or_create(
        lead=lead,
        defaults={
            'client_type_main': client_type_main,
            'client_type_detail': client_type_detail,
            'followup_date': followup_date,
            'remark': remark
        }
    )
    
    if not created:
        future_req.client_type_main = client_type_main
        future_req.client_type_detail = client_type_detail
        future_req.followup_date = followup_date
        future_req.remark = remark
        future_req.save()
    
    # Create stage history
    StageHistory.objects.create(
        lead=lead,
        from_stage=old_stage,
        to_stage='future',
        changed_by=request.user,
        notes="Moved to Future Requirement"
    )
    
    messages.success(request, f'{lead.company_name} moved to Future Requirement')
    return redirect('future_requirements_list')


# ===========================================
# HANDLE RECONNECT
# ===========================================
def handle_reconnect(request, lead, actual_call_date, expected_call_date):
    """Process Reconnect outcome - stays in prospect"""
    
    followup_date = request.POST.get('followup_date_reconnect')
    remark = request.POST.get('remark_reconnect')
    
    if not all([followup_date, remark]):
        messages.error(request, 'Please fill all required fields')
        return render(request, 'leads/lead_detail.html', {'lead': lead})
    
    # ✅ Lead STAYS in prospect stage (not a separate stage)
    lead.stage = 'prospect'  # Keep in prospect
    lead.last_call_date = actual_call_date  # Store last call
    lead.last_remark = remark  # Store last remark
    lead.save()
    
    # Create call history
    CallHistory.objects.create(
        lead=lead,
        expected_call_date=followup_date or None,  # ✅ Use followup_date
        actual_call_date=actual_call_date,
        outcome='reconnect',
        remark=remark,
        created_by=request.user
    )
    
    messages.success(request, f'{lead.company_name} marked for reconnect')
    return redirect('lead_list')


# ===========================================
# REQUIREMENT YES LIST
# ===========================================
@login_required
def requirement_yes_list(request):
    requirements = (
        RequirementYes.objects
        .select_related('lead')
        .filter(lead__stage='requirement_yes')  
        .exclude(sales_stage__in=['not_converted', 'order_lost', 'order_completed'])
    )

    return render(request, 'leads/requirement_yes_list.html', {
        'requirements': requirements
    })



# ===========================================
# REQUIREMENT YES DETAIL
# ===========================================
@login_required
def requirement_yes_detail(request, lead_id):
    lead = get_object_or_404(Lead, id=lead_id)

    if lead.stage != 'requirement_yes':
        return redirect(get_lead_detail_url(lead))
    requirement = get_object_or_404(RequirementYes, lead=lead)

    if request.method == 'POST':
        action = request.POST.get('action')

        # ✅ FIXED: Schedule Meeting
        if action == 'schedule_meeting':
            meeting_date = request.POST.get('meeting_date')
            
            if not meeting_date:
                messages.error(request, 'Please provide a meeting date')
                return redirect('requirement_yes_detail', lead_id=lead.id)
            
            try:
                Meeting.objects.create(
                    requirement=requirement,
                    meeting_date=meeting_date,  # Already in YYYY-MM-DD format
                    notes=request.POST.get('notes', ''),
                    created_by=request.user
                )
                messages.success(request, 'Meeting scheduled successfully!')
            except Exception as e:
                messages.error(request, f'Error scheduling meeting: {str(e)}')
            
            return redirect('requirement_yes_detail', lead_id=lead.id)

        elif action == 'update_stage':
            old = requirement.sales_stage
            requirement.sales_stage = request.POST.get('sales_stage')
            remark = request.POST.get('remark', '')
            requirement.current_remark = remark
            requirement.save()

            StageHistory.objects.create(
                lead=lead,
                from_stage=old,
                to_stage=requirement.sales_stage,
                changed_by=request.user,
                notes=remark
            )
            messages.success(request, 'Order progress updated successfully!')

        # ✅ NEW: Mark as Regret
        elif action == 'mark_regret':
            final_remark = request.POST.get('final_remark', '')
            if not final_remark:
                messages.error(request, 'Please provide a remark')
                return redirect('requirement_yes_detail', lead_id=lead.id)

            # Move lead back to regret stage
            lead.stage = 'regret'
            lead.save()

            # Create/update regret offer
            RegretOffer.objects.update_or_create(
                lead=lead,
                defaults={
                    'client_type_main': requirement.client_type_main,
                    'client_type_detail': requirement.client_type_detail,
                    'tank_type': 'Not specified',
                    'followup_date': timezone.now().date() + timedelta(days=30),
                    'remark': final_remark,
                }
            )

            # Create stage history
            StageHistory.objects.create(
                lead=lead,
                from_stage='requirement_yes',
                to_stage='regret',
                changed_by=request.user,
                notes=final_remark
            )

            messages.success(request, f'{lead.company_name} moved to Regret section')
            return redirect('regret_offers_list')

        # ✅ NEW: Mark as Lost Order
        elif action == 'mark_lost':
            final_remark = request.POST.get('final_remark', '')
            if not final_remark:
                messages.error(request, 'Please provide a remark')
                return redirect('requirement_yes_detail', lead_id=lead.id)

            # Update requirement to lost
            requirement.sales_stage = 'order_lost'
            requirement.current_remark = final_remark
            requirement.save()

            # Create stage history
            StageHistory.objects.create(
                lead=lead,
                from_stage=requirement.sales_stage,
                to_stage='order_lost',
                changed_by=request.user,
                notes=final_remark
            )

            messages.warning(request, f'{lead.company_name} marked as Lost Order')
            return redirect('lost_orders_list')

        # ✅ NEW: Mark as Customer (Order Completed)
        elif action == 'mark_customer':
            final_remark = request.POST.get('final_remark', '')
            if not final_remark:
                messages.error(request, 'Please provide a remark')
                return redirect('requirement_yes_detail', lead_id=lead.id)

            # Update requirement to completed
            requirement.sales_stage = 'order_completed'
            requirement.current_remark = final_remark
            requirement.save()

            # Create stage history
            StageHistory.objects.create(
                lead=lead,
                from_stage=requirement.sales_stage,
                to_stage='order_completed',
                changed_by=request.user,
                notes=final_remark
            )

            messages.success(request, f' {lead.company_name} converted to Customer!')
            return redirect('customers_list')

        return redirect('requirement_yes_detail', lead_id=lead.id)

    # Get call history
    call_history = CallHistory.objects.filter(
        lead=lead
    ).select_related('created_by').order_by('-actual_call_date')

    return render(request, 'leads/requirement_yes_detail.html', {
        'lead': lead,
        'requirement': requirement,
        'history': StageHistory.objects.filter(lead=lead).order_by('-changed_at'),
        'meetings': Meeting.objects.filter(requirement=requirement),
        'quotations': Quotation.objects.filter(requirement=requirement),
        'call_history': call_history,
    })



def get_lead_detail_url(lead):
    return {
        'prospect': reverse('lead_detail', args=[lead.id]),
        'requirement_yes': reverse('requirement_yes_detail', args=[lead.id]),
        'regret': reverse('regret_offer_detail', args=[lead.id]),
        'future': reverse('future_requirement_detail', args=[lead.id]),
    }.get(lead.stage, reverse('lead_list'))


# ===========================================
# UPDATE SALES STAGE
# ===========================================
def update_sales_stage(request, requirement):
    """Update the sales stage of a requirement with remark"""
    
    new_stage = request.POST.get('sales_stage')
    remark = request.POST.get('remark', '').strip()
    followup_date = request.POST.get('followup_date')
    
    if not new_stage:
        messages.error(request, 'Please select a sales stage')
        return redirect('requirement_yes_detail', lead_id=requirement.lead.id)
    
    if not remark:
        messages.error(request, 'Please provide a remark for this update')
        return redirect('requirement_yes_detail', lead_id=requirement.lead.id)
    
    old_stage = requirement.sales_stage
    old_stage_display = dict(RequirementYes.SALES_STAGE_CHOICES).get(old_stage, old_stage)
    new_stage_display = dict(RequirementYes.SALES_STAGE_CHOICES).get(new_stage, new_stage)
    
    # Update requirement
    requirement.sales_stage = new_stage
    requirement.current_remark = remark
    if followup_date:
        requirement.followup_date = followup_date
    requirement.save()
    
    # Create stage history
    StageHistory.objects.create(
        lead=requirement.lead,
        from_stage=old_stage,
        to_stage=new_stage,
        changed_by=request.user,
        notes=remark
    )
    
    # Check if order completed or lost - update main lead stage
    if new_stage == 'order_completed':
        requirement.lead.stage = 'requirement_yes'  # Keep in requirement_yes but mark as completed
        requirement.lead.save()
    elif new_stage == 'order_lost':
        requirement.lead.stage = 'requirement_yes'  # Keep in requirement_yes but mark as lost
        requirement.lead.save()
    
    messages.success(request, f'Status updated: {old_stage_display} → {new_stage_display}')
    return redirect('requirement_yes_detail', lead_id=requirement.lead.id)


# ===========================================
# SCHEDULE MEETING
# ===========================================
def schedule_meeting(request, requirement):
    """Schedule a meeting for a requirement"""
    
    meeting_date = request.POST.get('meeting_date')
    meeting_type = request.POST.get('meeting_type')
    attendees = request.POST.get('attendees', '')
    notes = request.POST.get('notes', '')
    
    if not meeting_date or not meeting_type:
        messages.error(request, 'Please fill in required meeting details')
        return redirect('requirement_yes_detail', lead_id=requirement.lead.id)
    
    # Create meeting
    Meeting.objects.create(
        requirement=requirement,
        meeting_date=meeting_date,
        meeting_type=meeting_type,
        attendees=attendees,
        notes=notes,
        created_by=request.user
    )
    
    # Update stage if not already in meeting_scheduled or beyond
    stage_order = ['quotation_sent', 'pre_sales', 'meeting_scheduled', 'waiting_po', 'po_received']
    current_stage_index = stage_order.index(requirement.sales_stage) if requirement.sales_stage in stage_order else -1
    meeting_stage_index = stage_order.index('meeting_scheduled')
    
    if current_stage_index < meeting_stage_index:
        requirement.sales_stage = 'meeting_scheduled'
        requirement.save()
        
        StageHistory.objects.create(
            lead=requirement.lead,
            from_stage=f"sales_{stage_order[current_stage_index]}",
            to_stage="sales_meeting_scheduled",
            changed_by=request.user,
            notes="Meeting scheduled - auto-updated sales stage"
        )
    
    messages.success(request, 'Meeting scheduled successfully!')
    return redirect('requirement_yes_detail', lead_id=requirement.lead.id)


# ===========================================
# UPDATE QUOTATION
# ===========================================
def update_quotation(request, requirement):
    """Update or create quotation details"""
    
    expected_date = request.POST.get('expected_date')
    actual_date = request.POST.get('actual_date')
    quotation_number = request.POST.get('quotation_number', '')
    amount = request.POST.get('amount', '')
    
    if not expected_date:
        messages.error(request, 'Please provide expected quotation date')
        return redirect('requirement_yes_detail', lead_id=requirement.lead.id)
    
    # Get or create quotation
    quotation, created = Quotation.objects.get_or_create(
        requirement=requirement,
        defaults={
            'expected_date': expected_date,
            'created_by': request.user
        }
    )
    
    # Update fields
    quotation.expected_date = expected_date
    quotation.actual_date = actual_date or None
    quotation.quotation_number = quotation_number
    
    if amount:
        try:
            quotation.amount = float(amount)
        except ValueError:
            pass
    
    quotation.save()
    
    action_text = 'created' if created else 'updated'
    messages.success(request, f'Quotation {action_text} successfully!')
    return redirect('requirement_yes_detail', lead_id=requirement.lead.id)


# ===========================================
# ADD LEAD
# ===========================================
@login_required
def add_lead(request):
    if request.method == 'POST':
        form = LeadCreateForm(request.POST)
        if form.is_valid():
            lead = form.save(commit=False)
            lead.created_by = request.user
            
            # Generate unique lead code
            last_lead = Lead.objects.order_by('-id').first()
            next_id = (last_lead.id + 1) if last_lead else 1
            lead.lead_code = f"EP{next_id:05d}"
            
            lead.save()
            messages.success(request, f'Lead {lead.lead_code} created successfully!')
            return redirect('lead_detail', lead_id=lead.id)
    else:
        form = LeadCreateForm()
    
    return render(request, 'leads/add_lead.html', {'form': form})


# ===========================================
# LOST ORDERS LIST
# ===========================================
@login_required
def lost_orders_list(request):
    
    
    lost_orders = RequirementYes.objects.filter(
        sales_stage__in=['not_converted', 'order_lost']
    ).select_related('lead')
    
    return render(request, 'leads/lost_orders_list.html', {
        'lost_orders': lost_orders,
        'lost_orders_count': lost_orders.count(),
    })

# ===========================================
# LOST ORDERS Detail
# ===========================================
@login_required
def lost_order_detail(request, lead_id):
    """
    View for Lost Order details - Read-only view showing why order was lost
    """
    lead = get_object_or_404(Lead, id=lead_id)
    requirement = get_object_or_404(RequirementYes, lead=lead)
    
    # ✅ Verify this is actually a lost order
    if requirement.sales_stage not in ['not_converted', 'order_lost']:
        messages.warning(request, 'This lead is not marked as a lost order.')
        return redirect('requirement_yes_detail', lead_id=lead.id)
    
    # Get call history from prospect stage
    call_history = CallHistory.objects.filter(
        lead=lead
    ).select_related('created_by').order_by('-actual_call_date')
    
    # Get stage history (sales progression)
    stage_history = StageHistory.objects.filter(
        lead=lead
    ).select_related('changed_by').order_by('-changed_at')
    
    # Get meetings if any
    meetings = Meeting.objects.filter(
        requirement=requirement
    ).select_related('created_by').order_by('-meeting_date')
    
    # Get quotations if any
    quotations = Quotation.objects.filter(
        requirement=requirement
    ).select_related('created_by').order_by('-created_at')
    
    # ✅ Find the "Lost Order" conversion record
    lost_order_record = stage_history.filter(
        to_stage='order_lost'
    ).first()
    
    return render(request, 'leads/lost_order_detail.html', {
        'lead': lead,
        'requirement': requirement,
        'call_history': call_history,
        'stage_history': stage_history,
        'meetings': meetings,
        'quotations': quotations,
        'lost_order_record': lost_order_record,  
    })
# ===========================================
# CUSTOMERS LIST
# ===========================================
@login_required
def customers_list(request):
    """Show all leads marked as Order Completed (Customers)"""
    
    # ✅ Filter by order_completed status and ensure lead exists
    customers = RequirementYes.objects.filter(
        sales_stage='order_completed',
        lead__isnull=False
    ).select_related('lead')
    
    return render(request, 'leads/customers_list.html', {
        'customers': customers,
        'customers_count': customers.count(),
    })

# ===========================================
# CUSTOMERS DETAILS
# ===========================================
# In views.py - customer_detail function
@login_required
def customer_detail(request, lead_id):
    """
    View for Customer details - Read-only view showing completed order journey
    """
    lead = get_object_or_404(Lead, id=lead_id)
    requirement = get_object_or_404(RequirementYes, lead=lead)
    
    # ✅ Verify this is actually a customer
    if requirement.sales_stage != 'order_completed':
        messages.warning(request, 'This lead is not marked as a customer.')
        return redirect('requirement_yes_detail', lead_id=lead.id)
    
    # Get call history from prospect stage
    call_history = CallHistory.objects.filter(
        lead=lead
    ).select_related('created_by').order_by('-actual_call_date')
    
    # Get stage history (sales progression)
    stage_history = StageHistory.objects.filter(
        lead=lead
    ).select_related('changed_by').order_by('-changed_at')
    
    # ✅ FORMAT STAGE NAMES HERE
    for item in stage_history:
        item.to_stage_display = item.to_stage.replace('_', ' ').title()
    
    # Get meetings if any
    meetings = Meeting.objects.filter(
        requirement=requirement
    ).select_related('created_by').order_by('-meeting_date')
    
    # Get quotations if any
    quotations = Quotation.objects.filter(
        requirement=requirement
    ).select_related('created_by').order_by('-created_at')
    
    # ✅ Find the "Customer Conversion" record
    customer_conversion_record = stage_history.filter(
        to_stage='order_completed'
    ).first()
    
    return render(request, 'leads/customer_detail.html', {
        'lead': lead,
        'requirement': requirement,
        'call_history': call_history,
        'stage_history': stage_history,
        'meetings': meetings,
        'quotations': quotations,
        'customer_conversion_record': customer_conversion_record,
    })

# ===========================================
# FUTURE REQUIREMENTS LIST
# ===========================================
@login_required
def future_requirements_list(request):
    """Show all leads marked as Future Requirement"""
    
    future_reqs = FutureRequirement.objects.select_related('lead').order_by('-followup_date')
    
    return render(request, 'leads/future_requirement_list.html', {
        'future_requirements': future_reqs
    })


# ===========================================
# FUTURE REQUIREMENT DETAIL
# ===========================================
@login_required
def future_requirement_detail(request, lead_id):
    """View and update future requirement details"""
    
    lead = get_object_or_404(Lead, id=lead_id)
    future_req = get_object_or_404(FutureRequirement, lead=lead)

    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'convert_to_requirement':
            # ✅ VALIDATE AND CONVERT TO REQUIREMENT YES
            client_type_main = request.POST.get('client_type_main')
            tank_application = request.POST.get('tank_application')
            assigned_sales = request.POST.get('assigned_sales_person')
            remark = request.POST.get('remark', '')

            if not client_type_main or not tank_application or not assigned_sales:
                messages.error(request, "Missing required Requirement details")
                return redirect('future_requirement_detail', lead_id=lead.id)

            # Collect tank details
            tank_types = request.POST.getlist('tank_type[]')
            tank_capacities = request.POST.getlist('tank_capacity[]')
            tank_quantities = request.POST.getlist('tank_quantity[]')

            tanks = []
            for t, c, q in zip(tank_types, tank_capacities, tank_quantities):
                if t and c and q:
                    tanks.append({
                        "tank_type": t,
                        "capacity": c,
                        "quantity": int(q)
                    })

            if not tanks:
                messages.error(request, "Please add at least one tank detail")
                return redirect('future_requirement_detail', lead_id=lead.id)

            # Get client type detail
            client_type_detail = (
                request.POST.get('consultant_type')
                or request.POST.get('contractor_type')
                or request.POST.get('endclient_category')
                or ''
            )

            # Handle "Other" options
            if request.POST.get('consultant_type') == 'Other':
                client_type_detail = request.POST.get('consultant_other_text', '')
            elif request.POST.get('contractor_type') == 'Other':
                client_type_detail = request.POST.get('contractor_other_text', '')
            elif request.POST.get('endclient_category') == 'Other':
                client_type_detail = request.POST.get('endclient_other_text', '')

            # ✅ CLEAR FUTURE REQUIREMENT STATE
            old_stage = lead.stage
            FutureRequirement.objects.filter(lead=lead).delete()

            # ✅ UPDATE LEAD
            lead.stage = 'requirement_yes'
            lead.client_type_main = client_type_main
            lead.client_type_detail = client_type_detail
            lead.save()

            # ✅ CREATE REQUIREMENT YES
            requirement = RequirementYes.objects.create(
                lead=lead,
                client_type_main=client_type_main,
                client_type_detail=client_type_detail,
                tank_application=tank_application,
                tank_location=request.POST.get('tank_location', ''),
                assigned_sales_person=assigned_sales,
                expected_delivery_date=request.POST.get('expected_delivery_date') or None,
                tanks_json=tanks,
                current_remark=remark,
                sales_stage='costing_created'
            )

            # ✅ STAGE HISTORY
            StageHistory.objects.create(
                lead=lead,
                from_stage=old_stage,
                to_stage='requirement_yes',
                changed_by=request.user,
                notes=f'Converted from Future Requirement to Requirement Yes'
            )

            messages.success(request, f'✅ {lead.company_name} converted to Requirement Yes')
            return redirect('requirement_yes_detail', lead_id=lead.id)
        
        elif action == 'update_followup':
            # Update follow-up date and remarks
            new_followup_date = request.POST.get('followup_date')
            new_remark = request.POST.get('remark')
            
            if new_followup_date:
                future_req.followup_date = new_followup_date
            if new_remark:
                future_req.remark = new_remark
            future_req.save()
            
            # Create call history entry
            CallHistory.objects.create(
                lead=lead,
                actual_call_date=request.POST.get('actual_call_date'),
                outcome='future',
                remark=new_remark,
                created_by=request.user
            )
            
            messages.success(request, 'Future requirement updated successfully')
            return redirect('future_requirement_detail', lead_id=lead.id)
        
        elif action == 'mark_regret':
            # Convert to regret offer
            return redirect('lead_detail', lead_id=lead.id)
    
    # Get call history for this lead
    call_history = CallHistory.objects.filter(lead=lead).order_by('-actual_call_date')
    
    return render(request, 'leads/future_requirement_detail.html', {
        'lead': lead,
        'future_req': future_req,
        'call_history': call_history
    })


# ===========================================
# REGRET OFFERS LIST
# ===========================================
@login_required
def regret_offers_list(request):
    """Show all leads marked as Regret Offer"""
    
    regret_offers = RegretOffer.objects.select_related('lead').order_by('-followup_date')
    
    return render(request, 'leads/regret_offers_list.html', {
        'regret_offers': regret_offers
    })


# ===========================================
# REGRET OFFER DETAIL
# ===========================================
@login_required
def regret_offer_detail(request, lead_id):
    lead = get_object_or_404(Lead, id=lead_id)
    regret_offer = get_object_or_404(RegretOffer, lead=lead)

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'reconvert':
            old_stage = lead.stage
            
            # ✅ FIX 2: Delete regret state object when reconverting
            RegretOffer.objects.filter(lead=lead).delete()
            
            lead.stage = 'prospect'
            lead.save()

            StageHistory.objects.create(
                lead=lead,
                from_stage=old_stage,
                to_stage='prospect',
                changed_by=request.user,
                notes='Re-engaged from Regret Offer'
            )

            messages.success(
                request,
                f'{lead.company_name} moved back to prospects'
            )
            return redirect('lead_detail', lead_id=lead.id)

        elif action == 'update_followup':
            new_followup_date = request.POST.get('followup_date')
            new_remark = request.POST.get('remark')

            if new_followup_date:
                regret_offer.followup_date = new_followup_date
            if new_remark:
                regret_offer.remark = new_remark
            regret_offer.save()

            messages.success(request, 'Regret offer updated successfully')

    call_history = CallHistory.objects.filter(
        lead=lead
    ).order_by('-actual_call_date')

    return render(request, 'leads/regret_offer_detail.html', {
        'lead': lead,
        'regret_offer': regret_offer,
        'call_history': call_history
    })



def convert_lead(lead, to_stage, *, regret_data=None, requirement_data=None, user=None, notes=""):
    with transaction.atomic():
        old_stage = lead.stage

        # 🔥 Clear ALL other states first
        RequirementYes.objects.filter(lead=lead).delete()
        RegretOffer.objects.filter(lead=lead).delete()
        FutureRequirement.objects.filter(lead=lead).delete()

        # 🔁 Apply new state
        if to_stage == 'requirement_yes':
            RequirementYes.objects.create(**requirement_data, lead=lead)

        elif to_stage == 'regret':
            RegretOffer.objects.create(**regret_data, lead=lead)

        elif to_stage == 'future':
            FutureRequirement.objects.create(**future_data, lead=lead)

        # ✅ Update lead LAST
        lead.stage = to_stage
        lead.save()

        StageHistory.objects.create(
            lead=lead,
            from_stage=old_stage,
            to_stage=to_stage,
            changed_by=user,
            notes=notes
        )


# ===========================================
# Check Duplicates API
# ===========================================

@login_required
def check_duplicates(request):
    """
    API endpoint to check for duplicate leads in real-time
    Returns matching leads based on company name, email, or phone
    """
    if request.method != 'GET':
        return JsonResponse({'error': 'Invalid request method'}, status=405)
    
    company_name = request.GET.get('company_name', '').strip()
    email = request.GET.get('email', '').strip()
    phone = request.GET.get('phone', '').strip()
    
    matches = []
    
    # Exact match for email
    if email:
        email_matches = Lead.objects.filter(contact_email__iexact=email)
        for lead in email_matches:
            matches.append({
                'id': lead.id,
                'company_name': lead.company_name,
                'contact_email': lead.contact_email,
                'contact_phone': lead.contact_phone,
                'stage': lead.get_stage_display(),
                'stage_code': lead.stage,
                'lead_code': lead.lead_code,
                'match_type': 'email',
                'match_score': 100
            })
    
    # Exact match for phone
    if phone:
        phone_matches = Lead.objects.filter(contact_phone=phone)
        for lead in phone_matches:
            # Avoid duplicates if already matched by email
            if not any(m['id'] == lead.id for m in matches):
                matches.append({
                    'id': lead.id,
                    'company_name': lead.company_name,
                    'contact_email': lead.contact_email,
                    'contact_phone': lead.contact_phone,
                    'stage': lead.get_stage_display(),
                    'stage_code': lead.stage,
                    'lead_code': lead.lead_code,
                    'match_type': 'phone',
                    'match_score': 100
                })
    
    # Fuzzy match for company name (similarity > 70%)
    if company_name and len(company_name) >= 3:
        all_leads = Lead.objects.all()
        
        for lead in all_leads:
            # Skip if already matched
            if any(m['id'] == lead.id for m in matches):
                continue
            
            # Calculate similarity ratio
            similarity = SequenceMatcher(None, 
                                        company_name.lower(), 
                                        lead.company_name.lower()).ratio()
            
            # Match if similarity > 70%
            if similarity > 0.7:
                matches.append({
                    'id': lead.id,
                    'company_name': lead.company_name,
                    'contact_email': lead.contact_email,
                    'contact_phone': lead.contact_phone,
                    'stage': lead.get_stage_display(),
                    'stage_code': lead.stage,
                    'lead_code': lead.lead_code,
                    'match_type': 'company_name',
                    'match_score': int(similarity * 100)
                })
    
    # Sort by match score (highest first)
    matches.sort(key=lambda x: x['match_score'], reverse=True)
    
    # Limit to top 5 matches
    matches = matches[:5]
    
    return JsonResponse({
        'matches': matches,
        'count': len(matches)
    })


# ===========================================
# UNIVERSAL SEARCH API
# ===========================================
@login_required
def universal_search(request):
    """
    Universal search API endpoint
    Searches across company name, contact name, email, and phone
    """
    if request.method != 'GET':
        return JsonResponse({'error': 'Invalid request method'}, status=405)
    
    query = request.GET.get('q', '').strip()
    
    if len(query) < 2:
        return JsonResponse({'results': [], 'count': 0})
    
    # Search across multiple fields
    leads = Lead.objects.filter(
        Q(company_name__icontains=query) |
        Q(contact_name__icontains=query) |
        Q(contact_email__icontains=query) |
        Q(contact_phone__icontains=query) |
        Q(lead_code__icontains=query)
    ).select_related()[:20]  # Limit to 20 results
    
    results = []
    for lead in leads:
        results.append({
            'id': lead.id,
            'company_name': lead.company_name,
            'contact_name': lead.contact_name,
            'contact_email': lead.contact_email,
            'contact_phone': lead.contact_phone,
            'lead_code': lead.lead_code,
            'stage_code': lead.stage,
            'stage_display': lead.get_stage_display(),
            'city': lead.city,
            'state': lead.state,
        })
    
    return JsonResponse({
        'results': results,
        'count': len(results)
    })