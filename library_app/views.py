
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Value, DecimalField
from django.db.models.functions import Coalesce
from django.shortcuts import render, redirect
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .decorators import librarian_required
from django.db import IntegrityError
from django.http import HttpResponseForbidden
from django.http import Http404
from django.views.decorators.http import require_POST
from django.db import transaction

from .forms import (
    BookCreateForm,
    BookUpdateForm,
    BookCopyForm,
    AuthorForm,
    PublisherForm,
    CategoryForm,
)

from .models import (
    UserProfile,
    Books,
    BookCopies,
    Loans,
    Reservations,
    Fines,
    Categories,
    BookAuthors,
    Authors,
    Publishers,
)


def member_login(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:
            login(request, user)
            return redirect('dashboard')

        messages.error(request, 'Invalid username or password.')

    return render(request, 'library_app/login.html')


@login_required
def dashboard(request):
    try:
        profile = request.user.profile
    except UserProfile.DoesNotExist:
        logout(request)
        messages.error(
            request,
            'Your account is not linked to a library membership.'
        )
        return redirect('member_login')

    member = profile.member

    # Book catalogue statistics
    total_books = Books.objects.count()
    total_copies = BookCopies.objects.count()
    available_copies = BookCopies.objects.filter(
        copy_status='AVAILABLE'
    ).count()

    # Circulation statistics
    issued_loans = Loans.objects.filter(
        loan_status='ISSUED'
    ).count()

    # Reservation statistics
    pending_reservations = Reservations.objects.filter(
        reservation_status='PENDING'
    ).count()

    # Calculate the actual outstanding fine balance.
    # Multiple payments against one fine are added together.
    fine_balances = Fines.objects.annotate(
        paid_amount=Coalesce(
            Sum('payments__amount'),
            Value(Decimal('0.00')),
            output_field=DecimalField(
                max_digits=10,
                decimal_places=2
            )
        )
    ).values('fine_amount', 'paid_amount')

    outstanding_fines = sum(
        (
            max(
                fine['fine_amount'] - fine['paid_amount'],
                Decimal('0.00')
            )
            for fine in fine_balances
        ),
        Decimal('0.00')
    )

    context = {
        'profile': profile,
        'member': member,
        'page_title': 'Dashboard',

        'total_books': total_books,
        'total_copies': total_copies,
        'available_copies': available_copies,
        'issued_loans': issued_loans,
        'pending_reservations': pending_reservations,
        'outstanding_fines': outstanding_fines,
    }

    return render(
        request,
        'library_app/dashboard.html',
        context
    )


@login_required
def member_logout(request):
    logout(request)
    return redirect('member_login')



@login_required
def books_catalogue(request):
    search_query = request.GET.get('q', '').strip()
    selected_category = request.GET.get('category', '').strip()

    books = Books.objects.select_related(
        'publisher',
        'category'
    ).annotate(
        total_copies=Count('bookcopies', distinct=True),
        available_copies=Count(
            'bookcopies',
            filter=Q(bookcopies__copy_status='AVAILABLE'),
            distinct=True
        )
    )

    # Search by title, ISBN, or author name.
    if search_query:
        books = books.filter(
            Q(title__icontains=search_query) |
            Q(isbn__icontains=search_query) |
            Q(bookauthors__author__author_name__icontains=search_query)
        ).distinct()

    # Filter by category.
    if selected_category:
        if selected_category.isdigit():
            books = books.filter(
                category_id=int(selected_category)
            )
        else:
            selected_category = ''

    books = books.order_by('title')

    # Display 10 books per page.
    paginator = Paginator(books, 10)
    page_obj = paginator.get_page(request.GET.get('page'))

    context = {
        'page_title': 'Books Catalogue',
        'page_obj': page_obj,
        'categories': Categories.objects.order_by('category_name'),
        'search_query': search_query,
        'selected_category': selected_category,
        'member': request.user.profile.member,
    }

    return render(
        request,
        'library_app/books_catalogue.html',
        context
    )



@login_required
def book_detail(request, book_id):
    book = get_object_or_404(
        Books.objects.select_related(
            'publisher',
            'category'
        ).prefetch_related(
            'bookauthors_set__author',
            'bookcopies_set'
        ),
        book_id=book_id
    )

    copies = book.bookcopies_set.all().order_by(
        'accession_number'
    )

    total_copies = copies.count()

    available_copies = copies.filter(
        copy_status='AVAILABLE'
    ).count()

    unavailable_copies = total_copies - available_copies

    context = {
        'page_title': 'Book Details',
        'book': book,
        'copies': copies,
        'total_copies': total_copies,
        'available_copies': available_copies,
        'unavailable_copies': unavailable_copies,
        'member': request.user.profile.member,
    }

    return render(
        request,
        'library_app/book_detail.html',
        context
    )



@librarian_required
def add_book(request):

    if request.method == 'POST':
        form = BookCreateForm(request.POST)

        if form.is_valid():

            try:
                with transaction.atomic():

                    # 1. Create the book title.
                    book = Books.objects.create(
                        title=form.cleaned_data['title'],
                        isbn=form.cleaned_data['isbn'],
                        publisher=form.cleaned_data['publisher'],
                        category=form.cleaned_data['category'],
                        edition=form.cleaned_data['edition'] or None,
                        publication_year=form.cleaned_data['publication_year'],
                        language=form.cleaned_data['language'] or None,
                    )

                    # 2. Associate selected authors.
                    selected_authors = form.cleaned_data['authors']

                    for author in selected_authors:
                        BookAuthors.objects.create(
                            book=book,
                            author=author
                        )

                    # 3. Register physical copies.
                    accession_numbers = form.cleaned_data[
                        'accession_numbers'
                    ]

                    shelf_location = (
                        form.cleaned_data['shelf_location'] or None
                    )

                    for accession_number in accession_numbers:
                        BookCopies.objects.create(
                            book=book,
                            accession_number=accession_number,
                            copy_status='AVAILABLE',
                            shelf_location=shelf_location,
                        )

                messages.success(
                    request,
                    f'"{book.title}" was added successfully with '
                    f'{len(accession_numbers)} physical copies.'
                )

                return redirect(
                    'book_detail',
                    book_id=book.book_id
                )

            except Exception:
                messages.error(
                    request,
                    'The book could not be saved. '
                    'Please check the entered information and try again.'
                )

    else:
        form = BookCreateForm()

    return render(
        request,
        'library_app/add_book.html',
        {
            'form': form,
            'page_title': 'Add Book',
        }
    )



@librarian_required
def edit_book(request, book_id):
    book = get_object_or_404(Books, book_id=book_id)

    if request.method == 'POST':
        form = BookUpdateForm(request.POST, instance=book)

        if form.is_valid():
            try:
                with transaction.atomic():
                    updated_book = form.save()

                    # Replace the book-author relationships.
                    BookAuthors.objects.filter(book=updated_book).delete()

                    selected_authors = form.cleaned_data['authors']

                    BookAuthors.objects.bulk_create([
                        BookAuthors(
                            book=updated_book,
                            author=author
                        )
                        for author in selected_authors
                    ])

                messages.success(
                    request,
                    'Book information updated successfully.'
                )

                return redirect(
                    'book_detail',
                    book_id=book.book_id
                )

            except Exception:
                messages.error(
                    request,
                    'Unable to update the book. Please try again.'
                )

    else:
        form = BookUpdateForm(instance=book)

    return render(
        request,
        'library_app/edit_book.html',
        {
            'form': form,
            'book': book,
            'page_title': 'Edit Book',
        }
    )


@librarian_required
def add_book_copies(request, book_id):
    book = get_object_or_404(Books, book_id=book_id)

    if request.method == 'POST':
        form = BookCopyForm(request.POST)

        if form.is_valid():
            accession_numbers = form.cleaned_data['accession_numbers']
            shelf_location = form.cleaned_data['shelf_location'] or None

            try:
                with transaction.atomic():
                    BookCopies.objects.bulk_create([
                        BookCopies(
                            book=book,
                            accession_number=number,
                            copy_status='AVAILABLE',
                            shelf_location=shelf_location,
                        )
                        for number in accession_numbers
                    ])

                messages.success(
                    request,
                    f'{len(accession_numbers)} physical copies '
                    f'were added successfully.'
                )

                return redirect(
                    'book_detail',
                    book_id=book.book_id
                )

            except IntegrityError:
                messages.error(
                    request,
                    'One or more accession numbers already exist. '
                    'Please check and try again.'
                )

            except Exception:
                messages.error(
                    request,
                    'Unable to register the copies. Please try again.'
                )

    else:
        form = BookCopyForm()

    return render(
        request,
        'library_app/add_book_copies.html',
        {
            'form': form,
            'book': book,
            'page_title': 'Add Physical Copies',
        }
    )



@login_required
def reference_data(request):
    member = request.user.profile.member

    context = {
        'page_title': 'Library Reference Data',
        'member': member,
        'authors': Authors.objects.order_by('author_name'),
        'publishers': Publishers.objects.order_by('publisher_name'),
        'categories': Categories.objects.order_by('category_name'),
    }

    return render(
        request,
        'library_app/reference_data.html',
        context
    )


@librarian_required
def manage_reference(request, record_type, record_id=None):

    # Only these three models can be managed through this view.
    configurations = {
        'author': {
            'model': Authors,
            'form': AuthorForm,
            'label': 'Author',
        },
        'publisher': {
            'model': Publishers,
            'form': PublisherForm,
            'label': 'Publisher',
        },
        'category': {
            'model': Categories,
            'form': CategoryForm,
            'label': 'Category',
        },
    }

    config = configurations.get(record_type)

    if config is None:
        raise Http404('Invalid reference-data type.')

    model = config['model']
    form_class = config['form']
    label = config['label']

    instance = None

    if record_id is not None:
        instance = get_object_or_404(
            model,
            pk=record_id
        )

    if request.method == 'POST':
        form = form_class(
            request.POST,
            instance=instance
        )

        if form.is_valid():
            try:
                with transaction.atomic():
                    record = form.save()

                action = 'updated' if instance else 'created'

                messages.success(
                    request,
                    f'{label} "{record}" was {action} successfully.'
                )

                return redirect('reference_data')

            except IntegrityError:
                messages.error(
                    request,
                    f'This {label.lower()} already exists.'
                )

    else:
        form = form_class(instance=instance)

    context = {
        'page_title': f'{"Edit" if instance else "Add"} {label}',
        'form': form,
        'record_type': record_type,
        'label': label,
        'instance': instance,
    }

    return render(
        request,
        'library_app/reference_form.html',
        context
    )


@librarian_required
@require_POST
def delete_book(request, book_id):

    book = get_object_or_404(Books, book_id=book_id)

    # Never delete books that have loan history.
    has_loan_history = Loans.objects.filter(
        copy__book=book
    ).exists()

    if has_loan_history:
        messages.error(
            request,
            'This book cannot be deleted because it has loan history.'
        )
        return redirect('book_detail', book_id=book.book_id)

    # Never delete books with reservation history.
    has_reservations = Reservations.objects.filter(
        book=book
    ).exists()

    if has_reservations:
        messages.error(
            request,
            'This book cannot be deleted because it has reservation records.'
        )
        return redirect('book_detail', book_id=book.book_id)

    try:
        with transaction.atomic():

            # Delete author associations first.
            BookAuthors.objects.filter(book=book).delete()

            # Delete physical copies.
            BookCopies.objects.filter(book=book).delete()

            # Delete the book title.
            book.delete()

        messages.success(
            request,
            'Book and its physical copies were deleted successfully.'
        )

        return redirect('books_catalogue')

    except Exception:
        messages.error(
            request,
            'Unable to delete this book. Database constraints may prevent deletion.'
        )
        return redirect('books_catalogue')
