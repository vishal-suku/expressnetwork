import typing
from django.core.paginator import Paginator
from django.db.models import QuerySet
from rest_framework import serializers

class Pagination:
    def get_paginated_response(
        self,
        queryset: QuerySet,
        page_number: int,
        data_per_page: int,
        serializer_class: serializers.Serializer,
    ) -> typing.Tuple[dict, int]:
        # Input validation
        try:
            page_number = int(page_number)
            data_per_page = int(data_per_page)
        except ValueError:
            raise serializers.ValidationError(
                {"result": False, "msg": "Page number or Data per page should be numbers"},
                code="validation_error",
            )
    
        # Pagination
        paginator = Paginator(queryset, data_per_page)
        
        # Validate page number
        if page_number < 1 or page_number > paginator.num_pages:
            raise serializers.ValidationError(
                {"result": False, "msg": "Invalid page number"},
                code="validation_error",
            )

        # Get paginated objects for the specified page
        paginated_objs = paginator.get_page(page_number)

        # Serialize data
        serializer_instance = serializer_class(paginated_objs, many=True)
        serialized_data = serializer_instance.data
        return serialized_data, paginator.num_pages

    def get_paginated_objs(
        self,
        queryset: QuerySet,
        page_number: int,
        data_per_page: int,
    ) -> typing.Tuple[QuerySet, int]:
        # Input validation
        try:
            page_number = int(page_number)
            data_per_page = int(data_per_page)
        except ValueError:
            raise serializers.ValidationError(
                {"result": False, "msg": "Page number or Data per page should be numbers"},
                code="validation_error",
            )
    
        # Pagination
        paginator = Paginator(queryset, data_per_page)
        
        # Validate page number
        if page_number < 1 or page_number > paginator.num_pages:
            raise serializers.ValidationError(
                {"result": False, "msg": "Invalid page number"},
                code="validation_error",
            )

        # Get paginated objects for the specified page
        paginated_objs = paginator.get_page(page_number)

        return paginated_objs, paginator.num_pages