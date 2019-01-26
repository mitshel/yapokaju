from django.urls import include, path

from .views import (ProfileEventChangeView, ProfileEventCreateView,
                    ProfileEventDetailView, ProfileEventListView,
                    ProfileSettingsView, ProfileView)

urlpatterns = [
    path('', include('registration.backends.default.urls')),

    path('profile/', include([
        path('', ProfileView.as_view(), name='profile'),
        path('settings/', ProfileSettingsView.as_view(), name='profile_settings'),
        path('events/', ProfileEventListView.as_view(), name='profile_event_list'),
        path('events/create/', ProfileEventCreateView.as_view(), name='profile_event_create'),
        path('events/<int:pk>/', ProfileEventDetailView.as_view(), name='profile_event_detail'),
        path('events/<int:pk>/change/', ProfileEventChangeView.as_view(), name='profile_event_change'),
    ]))
]
