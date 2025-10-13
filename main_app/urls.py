from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from account import views as account_views
from . import views

app_name = 'main_app'

urlpatterns = [
    path('', account_views.sf_home, name='home'),
    path('dashboard/', account_views.dashboard, name='dashboard'),
    path('pc-list/', views.PCListView.as_view(), name='pc-list'),
    path('bookings/', views.BookingListView.as_view(), name='bookings'),
    path('users/', views.UserListView.as_view(), name='users'),
    path('user-activities/', views.UserActivityListView.as_view(), name='user-activities'),
    path('violation-suspend/<int:pk>/', views.suspend, name='violation-suspend'),
    path('add-pc-from-form/', views.add_pc_from_form, name='add-pc-from-form'),
    path('delete-pc/<int:pk>/', views.delete_pc, name='delete-pc'),
    path('pc-detail/<int:pk>/', views.PCDetailView.as_view(), name='pc-detail'),
    path('pc-update/<int:pk>/', views.PCUpdateView.as_view(), name='pc-update'),
    path('ping-ip/<int:pk>/', views.ping_ip_address, name='ping-ip'),
    path('reservation-approved/<int:pk>/', views.reservation_approved, name='reservation-approved'),
    path('reservation-declined/<int:pk>/', views.reservation_declined, name='reservation-declined'),
    path('pc-reservation/', views.ReservePCListView.as_view(), name='pc-reservation'),
    path('reservation-approval/<int:pk>/', views.ReservationApprovalDetailView.as_view(), 
         name='reservation-approval'),
    path('faculty-booking-confirmation/', views.faculty_booking_confirmation, name='faculty-booking-confirmation'),
    
    # AJAX callback
    path('ajax/get-ping-data/', views.get_ping_data, name='get-ping-data'),
    path('ajax/verify-pc-name/', views.verify_pc_name, name='verify-pc-name'),
    path('ajax/verify-pc-ip-address/', views.verify_pc_ip_address, name='verify-pc-ip-address'),
    path('ajax/get-pc-details/<int:pk>/', views.get_pc_details, name='get-pc-details'),
    path('ajax/reserve-pc/', views.reserve_pc, name='reserve-pc'),
    path('ajax/waiting-approval/<int:pk>/', views.waiting_approval, name='waiting-approval'),
    path('ajax/cancel-reservation/', views.submit_block_booking, name='cancel-reservation'),
    path('ajax/find-user/', views.find_user, name='find-user'),
    path('ajax/send-init-message/', views.send_init_message, name='send-init-message'),
    path('ajax/send-new-message/<int:room_id>/', views.send_new_message, name='send-new-message'),
    path('ajax/load-messages/', views.load_messages, name='load-messages'),
    path('ajax/load-conversation/<int:room_id>/', views.load_conversation, name='load-conversation'),
    path('ajax/change-message-status/', views.change_message_status, name='change-message-status'),
    path('ajax/submit-block-booking/', views.submit_block_booking, name='submit-block-booking'),
    
    # Reporting
    path('booking-data/', views.bookings_by_college, name='booking-data'),
]