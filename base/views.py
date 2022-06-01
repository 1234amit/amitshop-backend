from importlib.resources import contents
from itertools import product
from django.shortcuts import render
from django.http import JsonResponse, response
from django.contrib.auth.models import User
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
#authentication user
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response

from .models import Product, Order, OrderItem, ShippingAddress, Review
from .products import products

# import serializer 
from .serializers import ProductSerializer, UserSerializer, UserSerializerWithToken, OrderSerializer

#simple jwt token
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
#import hash password
from django.contrib.auth.hashers import make_password
#import status
from rest_framework import status

#import datetime 
from datetime import datetime

# import pagination
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

# from backend.base import serializers


# Create your views here.

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)

        serializer = UserSerializerWithToken(self.user).data
        for k, v in serializer.items():
            data[k] = v

        return data

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


# @api_view(['GET'])
# def getRoutes(request):
#     routes = [
#         '/api/products/',
#         '/api/products/create/',
#         '/api/products/upload/',
#         '/api/products/<id>/reviews/',
#         '/api/products/top/',
#         '/api/products/<id>/',
#         '/api/products/delete/<id>/',
#         '/api/products/<update>/<id>/'

#     ]
#     return Response(routes)

@api_view(['POST'])
def registerUser(request):
    data = request.data

    try:
        user = User.objects.create(
            first_name = data['name'],
            username = data['email'],
            email = data['email'],
            password = make_password(data['password'])
        )

        serializer = UserSerializerWithToken(user, many=False)
        return Response(serializer.data)

    except:
        messages = {'detail': 'User with this email already exist'}
        return Response(messages, status=status.HTTP_404_NOT_FOUND)



@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def updateUserProfile(request):
    user = request.user
    serializer = UserSerializerWithToken(user, many=False)

    data = request.data
    
    user.first_name = data['name']
    user.username = data['email']
    user.email = data['email']

    if data['password'] != '':
        user.password = make_password(data['password'])

    user.save()
    return Response(serializer.data)



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getUserProfile(request):
    user = request.user
    serializer = UserSerializer(user, many=False)
    return Response(serializer.data)


@api_view(['GET'])
def getProducts(request):
    # search the product
    query = request.query_params.get('keyword')
    if query == None:
        query = ''

    products = Product.objects.filter(
        name__icontains=query).order_by('-createdAt')
    # end search the product

    # pagination start here
    page = request.query_params.get('page')
    paginator = Paginator(products, 5)

    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)

    except EmptyPage:
        products = paginator.page(paginator.num_pages)

    if page == None:
        page = 1

    page = int(page)
    # pagination end here
    # products = Product.objects.all()
    serializer = ProductSerializer(products, many=True)
    return Response({'products': serializer.data, 'page': page, 'pages': paginator.num_pages})

@api_view(['GET'])
def getTopProducts(request):
    products = Product.objects.filter(rating__gte=4).order_by('-rating')[0:5]
    serializer = ProductSerializer(products, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def getProduct(request, pk):
    product = Product.objects.get(_id=pk)
    serializer = ProductSerializer(product, many=False)
    return Response(serializer.data)

# order backend code start here
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def addOrderItems(request):
    user = request.user
    data = request.data

    orderItems = data['orderItems']

    if orderItems and len(orderItems) == 0:
        return Response({'detail': 'No Order Items'}, status=status.HTTP_400_BAD_REQUEST)
    else:
        #1. create order items
        order = Order.objects.create(
            user = user,
            paymentMethod = data['paymentMethod'],
            taxPrice = data['taxPrice'],
            shippingPrice=data['shippingPrice'],
            totalPrice = data['totalPrice']
        )
        #2. create shipping address

        shipping = ShippingAddress.objects.create(
            order = order,
            address = data['shippingAddress']['address'],
            city = data['shippingAddress']['city'],
            postalCode = data['shippingAddress']['postalCode'],
            country = data['shippingAddress']['country']
        )
        #3. create orderItems ans set order to orderItems relationship

        for i in orderItems:
            product = Product.objects.get(_id=i['product'])

            item = OrderItem.objects.create(
                product = product,
                order = order,
                name = product.name,
                qty = i['qty'],
                price=i['price'],
                image=product.image.url,

            )

            #4. update stock
            product.countInStock -= item.qty
            product.save()

        serializer = OrderSerializer(order, many=False)
        return Response(serializer.data)



# get my order

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getMyOrders(request):
    user = request.user
    orders = user.order_set.all()
    serializer = OrderSerializer(orders, many=True)
    return Response(serializer.data)


# see all the orders admin and user

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getOrderById(request, pk):
    user = request.user
    try:
        order = Order.objects.get(_id=pk)
        if user.is_staff or order.user == user:
            serializer = OrderSerializer(order, many=False)
            return Response(serializer.data)

        else:
            Response({'detail': 'Not Authorized to viw this order'}, status=status.HTTP_400_BAD_REQUEST)

    except:
            Response({'detail': 'Order does not exist'}, status=status.HTTP_400_BAD_REQUEST)



# update the order is paid
@api_view(['PUT'])
@permission_classes([IsAuthenticated])

def updateOrderIsPaid(request, pk):
    order = Order.objects.get(_id=pk)
    order.isPaid = True
    order.paidAt = datetime.now()

    order.save()

    return Response('Order was Paid')



# see the all user in admin
@api_view(['GET'])
@permission_classes([IsAdminUser])
def getUsers(request):
    users = User.objects.all()
    serializer = UserSerializer(users, many=True)
    return Response(serializer.data)


# get user ny id
@api_view(['GET'])
@permission_classes([IsAdminUser])
def getUserById(request, pk):
    user = User.objects.get(id=pk)
    serializer = UserSerializer(user, many=False)
    return Response(serializer.data)



# update user

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def updateUser(request, pk):
    user = User.objects.get(id=pk)

    data = request.data
    
    user.first_name = data['name']
    user.username = data['email']
    user.email = data['email']
    user.is_staff = data['isAdmin']

    user.save()

    serializer = UserSerializer(user, many=False)
    return Response(serializer.data)



@api_view(['DELETE'])
@permission_classes([IsAdminUser])
def deleteUser(request, pk):
    userFromDeletaion = User.objects.get(id=pk)
    userFromDeletaion.delete()
    return Response('User was Deleted')



# admin products view
# delete product
@api_view(['DELETE'])
@permission_classes([IsAdminUser])
def deleteProduct(request, pk):
    product = Product.objects.get(_id=pk)
    product.delete()
    return Response('Product was Deleted')

# create product
@api_view(['POST'])
@permission_classes([IsAdminUser])
def createProduct(request):
    user = request.user

    product = Product.objects.create(
        user = user,
        name = 'Sample Name',
        price = 0,
        brand = 'Sample Brand',
        countInStock=0,
        category='Sample Category',
        description=''
    )
    serializer = ProductSerializer(product, many=False)
    return Response(serializer.data)


# update product
@api_view(['PUT'])
@permission_classes([IsAdminUser])
def updateProduct(request, pk):
    data = request.data
    product = Product.objects.get(_id=pk)

    product.name = data['name']
    product.price = data['price']
    product.brand = data['brand']
    product.countInStock = data['countInStock']
    product.category = data['category']
    product.description = data['description']

    product.save()

    serializer = ProductSerializer(product, many=False)
    return Response(serializer.data)


# upload image
@api_view(['POST'])

def uploadImage(request):
    data = request.data

    product_id = data['product_id']
    product = Product.objects.get(_id= product_id)

    product.image = request.FILES.get('image')

    product.save()

    return Response('Image was uploaded')


# get orders
@api_view(['GET'])
@permission_classes([IsAdminUser])
def getOrders(request):
    orders = Order.objects.all()
    serializer = OrderSerializer(orders, many=True)
    return Response(serializer.data)



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def createProductReview(request, pk):
    user = request.user
    product = Product.objects.get(_id=pk)
    data = request.data

    #!: Review allready exits
    alreadyExists = product.review_set.filter(user=user).exists()

    if alreadyExists:
        content = {'detail': 'Product already reviewed'}
        return Response(content, status=status.HTTP_400_BAD_REQUEST)

    #2.no reating or 0
    elif data['rating'] == 0:
        content = {'detail': 'Please select a reating'}
        return Response(content, status=status.HTTP_400_BAD_REQUEST)

    #3.create review
    else:
        review = Review.objects.create(
            user=user,
            product=product,
            name=user.first_name,
            rating=data['rating'],
            comment=data['comment'],
        )

        reviews = product.review_set.all()
        product.numReviews = len(reviews)

        total = 0
        for i in reviews:
            total += i.rating

        product.rating = total / len(reviews)
        product.save()

        return Response('Review Added')

