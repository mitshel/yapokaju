from django.urls import include, path

from .views import (ProfileEventCreateView, ProfileEventListView,
                    ProfileReviewCreateView, ProfileReviewListView,
                    ProfileSettingsView, ProfileView)

urlpatterns = [
    path('', include('registration.backends.simple.urls')),
    path('profile/', include([
        path('', ProfileView.as_view(), name='profile'),
        path('settings/', ProfileSettingsView.as_view(), name='profile_settings'),
        path('events/', ProfileEventListView.as_view(), name='profile_event_list'),
        path('events/create/', ProfileEventCreateView.as_view(), name='profile_event_create'),
        path('events/<int:id>/', ProfileEventListView.as_view(), name='profile_event_detail'),
        path('reviews/', ProfileReviewListView.as_view(), name='profile_review_list'),
        path('reviews/create/', ProfileReviewCreateView.as_view(), name='profile_reviews_create'),
    ]))
]
