from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Wishlist
from catalog.models import Products
from .serializers import WishlistSerializer

class WishlistViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = WishlistSerializer

    def get_queryset(self):
        return Wishlist.objects.filter(user=self.request.user).select_related('product')

    @action(detail=False, methods=['post'])
    def toggle(self, request):
        """
        Toggles a product in the user's wishlist:
        - If already present, removes it.
        - If not present, adds it.
        """
        product_id = request.data.get('product_id')

        if not product_id:
            return Response({"error": "product_id is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            product = Products.objects.get(id=product_id)
        except Products.DoesNotExist:
            return Response({"error": "Product not found."}, status=status.HTTP_404_NOT_FOUND)

        wishlist_item, created = Wishlist.objects.get_or_create(
            user=request.user,
            product=product
        )

        if not created:
            # Item existed, so remove it
            wishlist_item.delete()
            return Response({
                "message": "Product removed from wishlist.",
                "is_in_wishlist": False
            }, status=status.HTTP_200_OK)

        # Item was created
        return Response({
            "message": "Product added to wishlist.",
            "is_in_wishlist": True,
            "data": WishlistSerializer(wishlist_item).data
        }, status=status.HTTP_201_CREATED)
