from rest_framework import generics, permissions
from .models import TutorProfile, Subject
from .serializers import TutorProfileSerializer, SubjectSerializer


class SubjectListView(generics.ListCreateAPIView):
    queryset = Subject.objects.all().order_by("name")
    serializer_class = SubjectSerializer


class TutorListView(generics.ListAPIView):
    serializer_class = TutorProfileSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        queryset = TutorProfile.objects.filter(
            verification_status="verified"
        ).order_by("-average_rating")

        subject = self.request.query_params.get("subject")
        mode = self.request.query_params.get("mode")
        city = self.request.query_params.get("city")
        min_rating = self.request.query_params.get("min_rating")

        if subject:
            queryset = queryset.filter(subjects__name__icontains=subject)

        if mode:
            queryset = queryset.filter(tutoring_mode__in=[mode, "both"])

        if city:
            queryset = queryset.filter(city__icontains=city)

        if min_rating:
            queryset = queryset.filter(average_rating__gte=min_rating)

        return queryset.distinct()


class TutorCreateView(generics.CreateAPIView):
    serializer_class = TutorProfileSerializer
    permission_classes = [permissions.IsAuthenticated]


class TutorDetailView(generics.RetrieveAPIView):
    queryset = TutorProfile.objects.all()
    serializer_class = TutorProfileSerializer
    permission_classes = [permissions.AllowAny]