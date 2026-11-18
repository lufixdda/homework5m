from django.db.models import Avg, Count
from rest_framework import serializers
from .models import Category, Product, Review


class CategorySerializer(serializers.ModelSerializer):
    products_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Category
        fields = ['id', 'name', 'products_count']

    def validate_name(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError('Name cannot be empty.')
        return value.strip()


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'title', 'description', 'price', 'category']

    def validate_title(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError('Title cannot be empty.')
        return value.strip()

    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError('Price must be greater than 0.')
        return value


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['id', 'text', 'stars', 'product']

    def validate_text(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError('Text cannot be empty.')
        return value.strip()

    def validate_stars(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError('Stars must be between 1 and 5.')
        return value


class ReviewNestedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['id', 'text', 'stars']


class ProductReviewSerializer(serializers.ModelSerializer):
    reviews = ReviewNestedSerializer(many=True, read_only=True)
    rating = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['id', 'title', 'description', 'price', 'category', 'reviews', 'rating']

    def get_rating(self, obj):
        reviews = obj.reviews.all()
        if reviews.exists():
            avg = reviews.aggregate(avg=Avg('stars'))['avg']
            return round(avg, 2) if avg is not None else None
        return None