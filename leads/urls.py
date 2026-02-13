from django.urls import path
from . import views

urlpatterns = [
    # Duplicate detection API
    path('api/check-duplicates/', views.check_duplicates, name='check_duplicates'),

    # Universal search API
    path('api/universal-search/', views.universal_search, name='universal_search'),

    # Prospect Stage
    path('', views.lead_list, name='lead_list'),
    path('add/', views.add_lead, name='add_lead'),
    
    # Requirement Yes Stage
    path('requirement-yes/', views.requirement_yes_list, name='requirement_yes_list'),
    path('requirement-yes/<int:lead_id>/', views.requirement_yes_detail, name='requirement_yes_detail'),
    
    # Future Requirements
    path('future-requirements/', views.future_requirements_list, name='future_requirements_list'),
    path('future-requirements/<int:lead_id>/', views.future_requirement_detail, name='future_requirement_detail'),
    
    # Regret Offers
    path('regret-offers/', views.regret_offers_list, name='regret_offers_list'),
    path('regret-offers/<int:lead_id>/', views.regret_offer_detail, name='regret_offer_detail'),

    # Lost Orders
    path('lost-orders/', views.lost_orders_list, name='lost_orders_list'),
    path('lost-orders/<int:lead_id>/', views.lost_order_detail, name='lost_order_detail'),
    
    # Customers
    path('customers/', views.customers_list, name='customers_list'),
    path('customers/<int:lead_id>/', views.customer_detail, name='customer_detail'),
    
    # ✅ NEW: Follow-up action (must be before the catch-all pattern)
    path('<int:lead_id>/send-followup/', views.send_followup, name='send_followup'),
    
    # ✅ MOVE THIS TO THE BOTTOM (catch-all pattern)
    path('<int:lead_id>/', views.lead_detail, name='lead_detail'),
]