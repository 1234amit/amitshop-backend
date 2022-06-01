from django.urls import path
from . import views



urlpatterns = [
    path('users/login/', views.MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    # path('', views.getRoutes, name='routes'),
    path('users/register/', views.registerUser, name="register-user"),
    path('users/profile/', views.getUserProfile, name='users-profile'),
    path('users/profile/update/', views.updateUserProfile, name='user-profile-update'),
    path('users/', views.getUsers, name='users'),
    path('products/', views.getProducts, name='products'),
    path('products/create/', views.createProduct, name='product-create'),
    path('products/<str:pk>', views.getProduct, name='product'),

    # order urls start here
    path('orders/add/', views.addOrderItems, name='orders-add'),
    path('orders/myorders/', views.getMyOrders, name='myorders'),
    path('orders/<str:pk>/', views.getOrderById, name='user-order'),
    path('orders/<str:pk>/pay/', views.updateOrderIsPaid, name='pay'),

    path('users/delete/<str:pk>/', views.deleteUser, name='user-delete'),
    path('users/update/<str:pk>/', views.updateUser, name='update-user'),
    path('users/<str:pk>/', views.getUserById, name='user'),

    path('products/delete/<str:pk>/', views.deleteProduct, name='product-delete'),
    path('products/update/<str:pk>/', views.updateProduct, name='product-update'),
    path('products/upload/', views.uploadImage, name='image-upload'),

    # admin view the order
    path('orders/', views.getOrders, name='orders'),

    path('products/<str:pk>/reviews/', views.createProductReview, name="create-review"),
    path('products/top/', views.getTopProducts, name='top-products' )

    
]
