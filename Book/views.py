from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from .forms import UserRegisterForm, DepositForm, ReviewForm
from .models import Book, Category, Borrow, UserAccount
from django.utils import timezone

# Registration view
def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            UserAccount.objects.create(user=user, balance=0)
            login(request, user)
            return redirect('home')
    else:
        form = UserRegisterForm()
    return render(request, 'register.html', {'form': form})

# Home view
def home(request):
    categories = Category.objects.all()
    category_id = request.GET.get('category')
    if category_id:
        books = Book.objects.filter(category_id=category_id)
    else:
        books = Book.objects.all()
    return render(request, 'home.html', {'categories': categories, 'books': books})

# Deposit view
@login_required
def deposit(request):
    if request.method == 'POST':
        form = DepositForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data['amount']
            user_account = get_object_or_404(UserAccount, user=request.user)
            user_account.balance += amount
            user_account.save()
            send_mail(
                'Deposit Successful',
                f'You have successfully deposited {amount} taka.',
                'noreply@example.com',
                [request.user.email],
                fail_silently=False,
            )
            return redirect('profile')
    else:
        form = DepositForm()
    return render(request, 'deposit.html', {'form': form})

# Profile view
@login_required
def profile(request):
    user_account = get_object_or_404(UserAccount, user=request.user)
    borrows = Borrow.objects.filter(user=request.user)
    return render(request, 'profile.html', {'user_account': user_account, 'borrows': borrows})

# Borrow book view
@login_required
def borrow_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    user_account = get_object_or_404(UserAccount, user=request.user)
    if user_account.balance < book.borrowing_price:
        return render(request, 'borrow_book.html', {'book': book, 'error': 'Insufficient balance'})
    
    if request.method == 'POST':
        Borrow.objects.create(user=request.user, book=book)
        user_account.balance -= book.borrowing_price
        user_account.save()
        send_mail(
            'Book Borrowed',
            f'You have successfully borrowed "{book.title}".',
            'noreply@example.com',
            [request.user.email],
            fail_silently=False,
        )
        return redirect('profile')
    return render(request, 'borrow_book.html', {'book': book})

# Return book view
@login_required
def return_book(request, borrow_id):
    borrow = get_object_or_404(Borrow, id=borrow_id, user=request.user)
    if request.method == 'POST':
        user_account = get_object_or_404(UserAccount, user=request.user)
        user_account.balance += borrow.book.borrowing_price
        user_account.save()
        borrow.return_date = timezone.now()
        borrow.save()
        send_mail(
            'Book Returned',
            f'You have successfully returned "{borrow.book.title}".',
            'noreply@example.com',
            [request.user.email],
            fail_silently=False,
        )
        return redirect('profile')
    return render(request, 'return_book.html', {'borrow': borrow})

# Book detail view
def book_detail(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    reviews = book.review_set.all()
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.book = book
            review.user = request.user
            review.save()
            return redirect('book_detail', book_id=book.id)
    else:
        form = ReviewForm()
    return render(request, 'book_detail.html', {'book': book, 'reviews': reviews, 'form': form})

# Filter books by category
def book_list(request):
    category_id = request.GET.get('category')
    books = Book.objects.all()

    if category_id:
        category = get_object_or_404(Category, id=category_id)
        books = books.filter(category=category)

    categories = Category.objects.all()
    context = {
        'books': books,
        'categories': categories,
    }
    return render(request, 'book_list.html', context)

# Login view
def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            return render(request, 'login.html', {'error': 'Invalid username or password'})
    return render(request, 'login.html')

# Logout view
@login_required
def user_logout(request):
    logout(request)
    return redirect('home')
