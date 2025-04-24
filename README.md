# rest_core

![PyPI - Version](https://img.shields.io/pypi/v/rest-core) ![PyPI - Python Version](https://img.shields.io/pypi/pyversions/rest-core)

**A lightweight Django package to enhance your Django REST Framework (DRF) APIs with consistent response formatting, smart exception handling, rate-limit introspection, response time tracking, and pagination utilities.**

## 🔧 Features

- ✅ **Consistent JSON API Responses**
- 🚫 **Custom Exception Handling** with built-in throttle checks
- 🔍 **Rate Limit Inspector** to show per-view throttle info
- ⚙️ **Custom JSON Renderer** for standardized output
- ⏱️ **Response Time Middleware** with `X-Response-Time` header
- 💬 **Developer-friendly Response Class**
- 📄 **Smart Pagination** with detailed pagination metadata

## 📦 Installation

Install from PyPI:

```bash
pip install rest-core
```

## 🚀 Quick Start

### 1. Add to `settings.py`

```python
REST_FRAMEWORK = {
    "DEFAULT_RENDERER_CLASSES": [
        "rest_core.renderers.JSONBaseRenderer",
    ],
    "EXCEPTION_HANDLER": "rest_core.exceptions.base_exception_handler",
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "anon": "10/minute",
        "user": "100/minute",
    },
    "DEFAULT_PAGINATION_CLASS": "rest_core.pagination.PageNumberPagination",
    "PAGE_SIZE": 2,
}
```

### 2. Update Middleware

```python
MIDDLEWARE = [
    ...
    "rest_core.middlewares.ResponseTimeMiddleware",
]
```

## ✅ Usage

### Example View Using Custom Response

```python
from rest_core.response.response import Response
from rest_framework.views import APIView
from rest_core.pagination import get_paginated_data
from rest_framework import serializers

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

class ListAPIView(APIView):
    def get(self, request) -> Response:
        queryset = User.objects.all()
        serializer = UserSerializer(instance=queryset, many=True)
        return Response(
            message="The requested resource was retrieved successfully",
            data=serializer.data,
            status=200
        )
```

## 📄 Example API Response Format

### Standard Response:
```json
{
  "status": "succeeded",
  "status_code": 200,
  "message": "The requested resource was retrieved successfully",
  "data": [
    {
      "id": 1,
      "username": "user1",
      "email": "user1@example.com"
    }
    // ... more items
  ],
  "errors": null,
  "meta": {
    "response_time": "0.001892 seconds",
    "request_id": "uuid",
    "timestamp": "2025-04-23T09:00:00.000Z",
    "documentation_url": "N/A",
    "rate_limits": {
      "throttled_by": null,
      "throttles": {
        "anon": {
          "limit": 10,
          "remaining": 8,
          "reset_time": "2025-04-23T09:01:00Z",
          "retry_after": "60 seconds"
        }
      }
    }
  }
}
```

### Example View Using for Custom Paginated Response

```python
from rest_core.response.response import Response
from rest_framework.views import APIView
from rest_core.pagination import get_paginated_data
from rest_framework import serializers

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

class ListAPIView(APIView):
    def get(self, request) -> Response:
        queryset = User.objects.all()
        paginated_data = get_paginated_data(
            request=request,
            queryset=queryset,
            serializer_class=UserSerializer
        )
        return Response(
            message="The requested resource was retrieved successfully",
            data=paginated_data,
            status=200
        )
```

### Paginated Response:
```json
{
  "status": "succeeded",
  "status_code": 200,
  "message": "The requested resource was retrieved successfully",
  "data": {
    "current_page": 1,
    "total_pages": 5,
    "total_items": 50,
    "items_per_page": 10,
    "has_next": true,
    "has_previous": false,
    "next_page_number": 2,
    "previous_page_number": null,
    "next": "http://api.example.com/users?page=2",
    "previous": null,
    "results": [
      {
        "id": 1,
        "username": "user1",
        "email": "user1@example.com"
      }
      // ... more items
    ]
  },
  "errors": null,
  "meta": {
    "response_time": "0.001892 seconds",
    "request_id": "uuid",
    "timestamp": "2025-04-23T09:00:00.000Z",
    "documentation_url": "N/A",
    "rate_limits": {
      "throttled_by": null,
      "throttles": {
        "anon": {
          "limit": 10,
          "remaining": 8,
          "reset_time": "2025-04-23T09:01:00Z",
          "retry_after": "60 seconds"
        }
      }
    }
  }
}
```

## ⚠️ Exception Throttling

If throttled, the exception handler:

- Detects if the request exceeded limits
- Returns a DRF-standard `429 Too Many Requests` response
- Adds `Retry-After` and reset time in the response metadata

## 🧪 Throttle Inspector

The `ThrottleInspector` class checks throttle classes for the request and includes:

- Rate limits
- Remaining request count
- Time until reset
- Retry suggestions

## ⏱️ Response Time

A custom middleware appends the following header to all responses:

```http
X-Response-Time: 0.001621 seconds
```

## 🙌 Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements or new features.

## 🧾 License

This project is licensed under the MIT License. See the [LICENSE](https://github.com/shaileshpandit141/rest-core/blob/main/LICENSE) file for details.

## 👤 Author

If you have any questions or need assistance with this project, feel free to reach out:

**Shailesh Pandit**
📧 `shaileshpandit141@gmail.com`
