from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Banner, PromoSection
from .serializers import BannerSerializer, PromoSectionSerializer

class BannerViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Banner.objects.filter(is_active=True)
    serializer_class = BannerSerializer
    http_method_names = ['get']


class PromoSectionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = PromoSection.objects.all()
    serializer_class = PromoSectionSerializer
    http_method_names = ['get']
    
    @action(detail=False, methods=['get'], url_path='exclusive-offer')
    def exclusive_offer(self, request):
        promo = PromoSection.objects.filter(type='exclusive_offer').first()
        serializer = self.get_serializer(promo)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'], url_path='deal-of-day')
    def deal_of_day(self, request):
        promo = PromoSection.objects.filter(type='deal_of_day').first()
        serializer = self.get_serializer(promo)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'], url_path='member-benefits')
    def member_benefits(self, request):
        promo = PromoSection.objects.filter(type='member_benefits').first()
        serializer = self.get_serializer(promo)
        return Response(serializer.data, status=status.HTTP_200_OK)
