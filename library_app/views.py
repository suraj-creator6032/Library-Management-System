
from decimal import Decimal
from django.db import connection
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
from django.db import transaction, DatabaseError
from django.http import JsonResponse
from types import SimpleNamespace
from django.contrib.auth import get_user_model

from .forms import (
    BookCreateForm,
    BookUpdateForm,
    BookCopyForm,
    AuthorForm,
    PublisherForm,
    CategoryForm,
    MemberRegistrationForm,
    MemberUpdateForm,
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
    Members,
    Departments,
    
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


# @login_required
# def dashboard(request):
#     try:
#         profile = request.user.profile
#     except UserProfile.DoesNotExist:
#         logout(request)
#         messages.error(
#             request,
#             'Your account is not linked to a library membership.'
#         )
#         return redirect('member_login')

#     member = profile.member

#     # Book catalogue statistics
#     total_books = Books.objects.count()
#     total_copies = BookCopies.objects.count()
#     available_copies = BookCopies.objects.filter(
#         copy_status='AVAILABLE'
#     ).count()

#     # Circulation statistics
#     issued_loans = Loans.objects.filter(
#         loan_status='ISSUED'
#     ).count()

#     # Reservation statistics
#     pending_reservations = Reservations.objects.filter(
#         reservation_status='PENDING'
#     ).count()

#     # Calculate the actual outstanding fine balance.
#     # Multiple payments against one fine are added together.
#     fine_balances = Fines.objects.annotate(
#         paid_amount=Coalesce(
#             Sum('payments__amount'),
#             Value(Decimal('0.00')),
#             output_field=DecimalField(
#                 max_digits=10,
#                 decimal_places=2
#             )
#         )
#     ).values('fine_amount', 'paid_amount')

#     outstanding_fines = sum(
#         (
#             max(
#                 fine['fine_amount'] - fine['paid_amount'],
#                 Decimal('0.00')
#             )
#             for fine in fine_balances
#         ),
#         Decimal('0.00')
#     )

#     context = {
#         'profile': profile,
#         'member': member,
#         'page_title': 'Dashboard',

#         'total_books': total_books,
#         'total_copies': total_copies,
#         'available_copies': available_copies,
#         'issued_loans': issued_loans,
#         'pending_reservations': pending_reservations,
#         'outstanding_fines': outstanding_fines,
#     }

#     return render(
#         request,
#         'library_app/dashboard.html',
#         context
#     )


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

    # 1. Retrieve dashboard statistics using raw SQL.
    statistics_sql = """
        SELECT
            (SELECT COUNT(*)
             FROM books) AS total_books,

            (SELECT COUNT(*)
             FROM book_copies) AS total_copies,

            (SELECT COUNT(*)
             FROM book_copies
             WHERE copy_status = 'AVAILABLE') AS available_copies,

            (SELECT COUNT(*)
             FROM loans
             WHERE loan_status = 'ISSUED') AS issued_loans,

            (SELECT COUNT(*)
             FROM reservations
             WHERE reservation_status = 'PENDING') AS pending_reservations
    """

    with connection.cursor() as cursor:
        cursor.execute(statistics_sql)
        statistics = cursor.fetchone()

    (
        total_books,
        total_copies,
        available_copies,
        issued_loans,
        pending_reservations
    ) = statistics

    # 2. Calculate outstanding fines after subtracting all payments.
    outstanding_fines_sql = """
        SELECT
            COALESCE(
                SUM(
                    GREATEST(
                        f.fine_amount - COALESCE(p.total_paid, 0),
                        0
                    )
                ),
                0.00
            ) AS outstanding_fines

        FROM fines f

        LEFT JOIN (
            SELECT
                fine_id,
                SUM(amount) AS total_paid
            FROM payments
            GROUP BY fine_id
        ) p
            ON f.fine_id = p.fine_id
    """

    with connection.cursor() as cursor:
        cursor.execute(outstanding_fines_sql)
        outstanding_fines = cursor.fetchone()[0]

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


@librarian_required
def members_directory(request):

    # 1. Read search and filter parameters.
    search_query = request.GET.get('q', '').strip()
    selected_type = request.GET.get('type', '').strip()
    selected_department = request.GET.get('department', '').strip()
    selected_status = request.GET.get('status', '').strip()

    # 2. Start with all members and retrieve their departments
    # efficiently using select_related().
    members = Members.objects.select_related(
        'department'
    ).all()

    # 3. Search by name, college ID, email or phone.
    if search_query:
        members = members.filter(
            Q(full_name__icontains=search_query)
            | Q(college_id__icontains=search_query)
            | Q(email__icontains=search_query)
            | Q(phone__icontains=search_query)
        )

    # 4. Apply member-type filter.
    valid_member_types = ['STUDENT', 'FACULTY', 'LIBRARIAN']

    if selected_type in valid_member_types:
        members = members.filter(member_type=selected_type)
    else:
        selected_type = ''

    # 5. Apply department filter.
    if selected_department.isdigit():
        members = members.filter(
            department_id=int(selected_department)
        )
    else:
        selected_department = ''

    # 6. Apply membership-status filter.
    valid_statuses = ['ACTIVE', 'INACTIVE']

    if selected_status in valid_statuses:
        members = members.filter(
            membership_status=selected_status
        )
    else:
        selected_status = ''

    # 7. Order and paginate results.
    members = members.order_by('full_name', 'member_id')

    paginator = Paginator(members, 10)
    page_obj = paginator.get_page(request.GET.get('page'))

    # 8. Directory statistics.
    total_members = Members.objects.count()

    active_members = Members.objects.filter(
        membership_status='ACTIVE'
    ).count()

    student_count = Members.objects.filter(
        member_type='STUDENT'
    ).count()

    faculty_count = Members.objects.filter(
        member_type='FACULTY'
    ).count()

    librarian_count = Members.objects.filter(
        member_type='LIBRARIAN'
    ).count()

    # 9. Department dropdown options.
    departments = Departments.objects.order_by(
        'department_name'
    )

    # 10. Current librarian's membership record.
    member = request.user.profile.member

    context = {
        'page_title': 'Members',

        'members': page_obj,
        'page_obj': page_obj,

        'search_query': search_query,
        'selected_type': selected_type,
        'selected_department': selected_department,
        'selected_status': selected_status,

        'departments': departments,

        'total_members': total_members,
        'active_members': active_members,
        'student_count': student_count,
        'faculty_count': faculty_count,
        'librarian_count': librarian_count,

        'member': member,
    }

    return render(
        request,
        'library_app/members.html',
        context
    )

@login_required
@librarian_required
def add_member(request):
    if request.method == "POST":
        form = MemberRegistrationForm(request.POST)

        if form.is_valid():

            # Only a Django superuser can create another librarian account.
            if (
                form.cleaned_data["member_type"] == "LIBRARIAN"
                and not request.user.is_superuser
            ):
                form.add_error(
                    "member_type",
                    "Only a superuser can create a librarian account."
                )
            else:
                User = get_user_model()

                try:
                    with transaction.atomic():
                        # 1. Create the library member.
                        new_member = form.save()

                        # 2. Create the individual Django login account.
                        new_user = User(
                            username=form.cleaned_data["username"],
                            is_active=(
                                new_member.membership_status == "ACTIVE"
                            ),
                        )
                        new_user.set_password(
                            form.cleaned_data["password1"]
                        )
                        new_user.save()

                        # 3. Link the login account to the member.
                        UserProfile.objects.create(
                            user=new_user,
                            member=new_member,
                        )

                    messages.success(
                        request,
                        f"Member '{new_member.full_name}' was created successfully."
                    )
                    return redirect(
                        "member_detail",
                        member_id=new_member.member_id
                    )

                except IntegrityError:
                    form.add_error(
                        None,
                        "Could not create the member. A username, college ID, "
                        "or email may already exist. Please check the details."
                    )
    else:
        form = MemberRegistrationForm()

    context = {
        "page_title": "Add Member",
        "form": form,
        "member": request.user.profile.member,
    }

    return render(
        request,
        "library_app/add_member.html",
        context
    )


@login_required
@librarian_required
def edit_member(request, member_id):
    target_member = get_object_or_404(
        Members.objects.select_related("department"),
        member_id=member_id,
    )

    current_member = request.user.profile.member

    # Only superusers may modify librarian accounts or roles.
    if (
        target_member.member_type == "LIBRARIAN"
        and not request.user.is_superuser
    ):
        return HttpResponseForbidden(
            "Only a superuser can modify a librarian account."
        )

    if request.method == "POST":
        form = MemberUpdateForm(
            request.POST,
            instance=target_member,
        )

        if form.is_valid():
            new_member_type = form.cleaned_data["member_type"]
            new_status = form.cleaned_data["membership_status"]

            # Only superusers may assign the librarian role.
            if (
                new_member_type == "LIBRARIAN"
                and not request.user.is_superuser
            ):
                form.add_error(
                    "member_type",
                    "Only a superuser can assign the librarian role."
                )

            # Prevent a librarian from deactivating their own account.
            elif (
                target_member.member_id == current_member.member_id
                and new_status == "INACTIVE"
            ):
                form.add_error(
                    "membership_status",
                    "You cannot deactivate your own account."
                )

            else:
                try:
                    with transaction.atomic():
                        updated_member = form.save()

                        # Synchronize the linked Django login account.
                        try:
                            profile = updated_member.user_profile
                        except UserProfile.DoesNotExist:
                            profile = None

                        if profile is not None:
                            user = profile.user
                            user.is_active = (
                                updated_member.membership_status == "ACTIVE"
                            )
                            user.save(update_fields=["is_active"])

                    messages.success(
                        request,
                        f"Member '{updated_member.full_name}' updated successfully."
                    )

                    return redirect(
                        "member_detail",
                        member_id=updated_member.member_id,
                    )

                except IntegrityError:
                    form.add_error(
                        None,
                        "Could not update the member. Check whether the "
                        "college ID or email is already being used."
                    )

    else:
        form = MemberUpdateForm(instance=target_member)

    context = {
        "page_title": "Edit Member",
        "form": form,
        "profile_member": target_member,
        "member": current_member,
    }

    return render(
        request,
        "library_app/edit_member.html",
        context,
    )


@login_required
def member_detail(request, member_id):

    # 1. Retrieve the logged-in user's library profile.
    try:
        current_member = request.user.profile.member
    except UserProfile.DoesNotExist:
        logout(request)
        messages.error(
            request,
            'Your account is not linked to a library membership.'
        )
        return redirect('member_login')

    # 2. Librarians can view any member.
    # Students and faculty can only view their own details.
    if current_member.member_type == 'LIBRARIAN':
        member = get_object_or_404(
            Members.objects.select_related('department'),
            member_id=member_id
        )
    else:
        if current_member.member_id != member_id:
            return HttpResponseForbidden(
                'You are not allowed to view this member profile.'
            )

        member = current_member

    # 3. Retrieve the member's borrowing history.
    loans = Loans.objects.filter(
        member=member
    ).select_related(
        'copy__book'
    ).order_by('-issue_date', '-loan_id')

    # 4. Retrieve the member's reservations.
    reservations = Reservations.objects.filter(
        member=member
    ).select_related(
        'book'
    ).order_by('-reservation_date', '-reservation_id')

    # 5. Calculate membership statistics.
    total_loans = loans.count()

    active_loans = loans.filter(
        loan_status='ISSUED'
    ).count()

    returned_loans = loans.filter(
        loan_status='RETURNED'
    ).count()

    pending_reservations = reservations.filter(
        reservation_status='PENDING'
    ).count()

    # 6. Retrieve recent activity.
    recent_loans = loans[:10]
    recent_reservations = reservations[:10]

    context = {
        'page_title': 'Member Details',
        'member': current_member,
        'profile_member': member,

        'total_loans': total_loans,
        'active_loans': active_loans,
        'returned_loans': returned_loans,
        'pending_reservations': pending_reservations,

        'recent_loans': recent_loans,
        'recent_reservations': recent_reservations,
    }

    return render(
        request,
        'library_app/member_detail.html',
        context
    )


@login_required
def books_catalogue(request):
    search_query = request.GET.get('q', '').strip()
    selected_category = request.GET.get('category', '').strip()

    # Build SQL conditions and parameter values.
    conditions = []
    params = []

    # Search by title, ISBN, or author name.
    if search_query:
        conditions.append("""
            (
                b.title LIKE %s
                OR b.isbn LIKE %s
                OR EXISTS (
                    SELECT 1
                    FROM book_authors ba
                    INNER JOIN authors a
                        ON ba.author_id = a.author_id
                    WHERE ba.book_id = b.book_id
                    AND a.author_name LIKE %s
                )
            )
        """)

        search_pattern = f"%{search_query}%"

        params.extend([
            search_pattern,
            search_pattern,
            search_pattern
        ])

    # Filter by category ID.
    if selected_category:
        if selected_category.isdigit():
            conditions.append("b.category_id = %s")
            params.append(int(selected_category))
        else:
            selected_category = ''

    where_clause = ""

    if conditions:
        where_clause = "WHERE " + " AND ".join(conditions)

    # Count matching books for pagination.
    count_sql = f"""
        SELECT COUNT(*)
        FROM books b
        {where_clause}
    """

    with connection.cursor() as cursor:
        cursor.execute(count_sql, params)
        total_books = cursor.fetchone()[0]

    # Configure pagination: 10 books per page.
    paginator = Paginator(range(total_books), 10)

    page_obj = paginator.get_page(request.GET.get('page'))

    offset = max(page_obj.start_index() - 1, 0)
    limit = paginator.per_page

    # Retrieve book information and physical copy statistics.
    books_sql = f"""
        SELECT
            b.book_id,
            b.title,
            b.isbn,
            b.edition,
            b.publication_year,
            b.language,

            p.publisher_name,
            c.category_name,

            COUNT(DISTINCT bc.copy_id) AS total_copies,

            COUNT(
                DISTINCT CASE
                    WHEN bc.copy_status = 'AVAILABLE'
                    THEN bc.copy_id
                END
            ) AS available_copies

        FROM books b

        INNER JOIN publishers p
            ON b.publisher_id = p.publisher_id

        INNER JOIN categories c
            ON b.category_id = c.category_id

        LEFT JOIN book_copies bc
            ON b.book_id = bc.book_id

        {where_clause}

        GROUP BY
            b.book_id,
            b.title,
            b.isbn,
            b.edition,
            b.publication_year,
            b.language,
            p.publisher_name,
            c.category_name

        ORDER BY b.title

        LIMIT %s OFFSET %s
    """

    with connection.cursor() as cursor:
        cursor.execute(
            books_sql,
            params + [limit, offset]
        )

        columns = [column[0] for column in cursor.description]

        books = [
            dict(zip(columns, row))
            for row in cursor.fetchall()
        ]

    # Preserve the nested structure expected by the existing template:
    # book.publisher.publisher_name
    # book.category.category_name
    for book in books:
        book['publisher'] = {
            'publisher_name': book.pop('publisher_name')
        }

        book['category'] = {
            'category_name': book.pop('category_name')
        }

    # Replace the pagination placeholder with actual book records.
    page_obj.object_list = books

    # Retrieve categories using manually written SQL.
    categories_sql = """
        SELECT
            category_id,
            category_name
        FROM categories
        ORDER BY category_name
    """

    with connection.cursor() as cursor:
        cursor.execute(categories_sql)

        category_columns = [
            column[0] for column in cursor.description
        ]

        categories = [
            dict(zip(category_columns, row))
            for row in cursor.fetchall()
        ]

    context = {
        'page_title': 'Books Catalogue',
        'page_obj': page_obj,
        'categories': categories,
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

    # 1. Retrieve book information with publisher and category.
    book_sql = """
        SELECT
            b.book_id,
            b.isbn,
            b.title,
            b.edition,
            b.publication_year,
            b.language,
            p.publisher_name,
            c.category_name
        FROM books b
        INNER JOIN publishers p
            ON b.publisher_id = p.publisher_id
        INNER JOIN categories c
            ON b.category_id = c.category_id
        WHERE b.book_id = %s
    """

    with connection.cursor() as cursor:
        cursor.execute(book_sql, [book_id])

        columns = [column[0] for column in cursor.description]
        row = cursor.fetchone()

        if row is None:
            raise Http404("Book not found.")

        book_data = dict(zip(columns, row))

    # Preserve nested publisher and category access in the template.
    book = {
        key: value
        for key, value in book_data.items()
        if key not in ('publisher_name', 'category_name')
    }

    book['publisher'] = {
        'publisher_name': book_data['publisher_name']
    }

    book['category'] = {
        'category_name': book_data['category_name']
    }

    # 2. Retrieve all authors associated with this book.
    authors_sql = """
        SELECT
            a.author_id,
            a.author_name,
            a.biography
        FROM book_authors ba
        INNER JOIN authors a
            ON ba.author_id = a.author_id
        WHERE ba.book_id = %s
        ORDER BY a.author_name
    """

    with connection.cursor() as cursor:
        cursor.execute(authors_sql, [book_id])

        author_columns = [
            column[0] for column in cursor.description
        ]

        authors = [
            dict(zip(author_columns, row))
            for row in cursor.fetchall()
        ]

    # 3. Retrieve all physical copies of the book.
    copies_sql = """
        SELECT
            copy_id,
            book_id,
            accession_number,
            acquisition_date,
            copy_status,
            shelf_location
        FROM book_copies
        WHERE book_id = %s
        ORDER BY accession_number
    """

    with connection.cursor() as cursor:
        cursor.execute(copies_sql, [book_id])

        copy_columns = [
            column[0] for column in cursor.description
        ]

        copies = [
            dict(zip(copy_columns, row))
            for row in cursor.fetchall()
        ]

    # 4. Calculate total, available and unavailable copies.
    inventory_sql = """
        SELECT
            COUNT(*) AS total_copies,

            SUM(
                CASE
                    WHEN copy_status = 'AVAILABLE'
                    THEN 1
                    ELSE 0
                END
            ) AS available_copies

        FROM book_copies
        WHERE book_id = %s
    """

    with connection.cursor() as cursor:
        cursor.execute(inventory_sql, [book_id])
        inventory = cursor.fetchone()

    total_copies = inventory[0] or 0
    available_copies = inventory[1] or 0
    unavailable_copies = total_copies - available_copies

    context = {
        'page_title': 'Book Details',
        'book': book,
        'authors': authors,
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



# @librarian_required
# def add_book(request):

#     if request.method == 'POST':
#         form = BookCreateForm(request.POST)

#         if form.is_valid():

#             try:
#                 with transaction.atomic():

#                     # 1. Create the book title.
#                     book = Books.objects.create(
#                         title=form.cleaned_data['title'],
#                         isbn=form.cleaned_data['isbn'],
#                         publisher=form.cleaned_data['publisher'],
#                         category=form.cleaned_data['category'],
#                         edition=form.cleaned_data['edition'] or None,
#                         publication_year=form.cleaned_data['publication_year'],
#                         language=form.cleaned_data['language'] or None,
#                     )

#                     # 2. Associate selected authors.
#                     selected_authors = form.cleaned_data['authors']

#                     for author in selected_authors:
#                         BookAuthors.objects.create(
#                             book=book,
#                             author=author
#                         )

#                     # 3. Register physical copies.
#                     accession_numbers = form.cleaned_data[
#                         'accession_numbers'
#                     ]

#                     shelf_location = (
#                         form.cleaned_data['shelf_location'] or None
#                     )

#                     for accession_number in accession_numbers:
#                         BookCopies.objects.create(
#                             book=book,
#                             accession_number=accession_number,
#                             copy_status='AVAILABLE',
#                             shelf_location=shelf_location,
#                         )

#                 messages.success(
#                     request,
#                     f'"{book.title}" was added successfully with '
#                     f'{len(accession_numbers)} physical copies.'
#                 )

#                 return redirect(
#                     'book_detail',
#                     book_id=book.book_id
#                 )

#             except Exception:
#                 messages.error(
#                     request,
#                     'The book could not be saved. '
#                     'Please check the entered information and try again.'
#                 )

#     else:
#         form = BookCreateForm()

#     return render(
#         request,
#         'library_app/add_book.html',
#         {
#             'form': form,
#             'page_title': 'Add Book',
#         }
#     )


@librarian_required
def add_book(request):

    if request.method == 'POST':
        form = BookCreateForm(request.POST)

        if form.is_valid():

            try:
                with transaction.atomic():

                    # Retrieve validated form data.
                    data = form.cleaned_data

                    publisher_id = data['publisher'].pk
                    category_id = data['category'].pk

                    selected_authors = data['authors']
                    accession_numbers = data['accession_numbers']

                    shelf_location = data['shelf_location'] or None

                    # 1. Insert the book record.
                    insert_book_sql = """
                        INSERT INTO books (
                            title,
                            isbn,
                            publisher_id,
                            category_id,
                            edition,
                            publication_year,
                            language
                        )
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """

                    with connection.cursor() as cursor:
                        cursor.execute(
                            insert_book_sql,
                            [
                                data['title'],
                                data['isbn'] or None,
                                publisher_id,
                                category_id,
                                data['edition'] or None,
                                data['publication_year'],
                                data['language'] or None,
                            ]
                        )

                        # Obtain the automatically generated book ID.
                        book_id = cursor.lastrowid

                    # 2. Insert book-author relationships.
                    insert_authors_sql = """
                        INSERT INTO book_authors (
                            book_id,
                            author_id
                        )
                        VALUES (%s, %s)
                    """

                    author_records = [
                        (book_id, author.pk)
                        for author in selected_authors
                    ]

                    if author_records:
                        with connection.cursor() as cursor:
                            cursor.executemany(
                                insert_authors_sql,
                                author_records
                            )

                    # 3. Insert physical book copies.
                    insert_copies_sql = """
                        INSERT INTO book_copies (
                            book_id,
                            accession_number,
                            copy_status,
                            shelf_location
                        )
                        VALUES (%s, %s, %s, %s)
                    """

                    copy_records = [
                        (
                            book_id,
                            accession_number,
                            'AVAILABLE',
                            shelf_location
                        )
                        for accession_number in accession_numbers
                    ]

                    with connection.cursor() as cursor:
                        cursor.executemany(
                            insert_copies_sql,
                            copy_records
                        )

                # All three operations succeeded and the transaction committed.
                messages.success(
                    request,
                    f'"{data["title"]}" was added successfully with '
                    f'{len(accession_numbers)} physical copies.'
                )

                return redirect(
                    'book_detail',
                    book_id=book_id
                )

            except DatabaseError:
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


# @librarian_required
# def edit_book(request, book_id):
#     book = get_object_or_404(Books, book_id=book_id)

#     if request.method == 'POST':
#         form = BookUpdateForm(request.POST, instance=book)

#         if form.is_valid():
#             try:
#                 with transaction.atomic():
#                     updated_book = form.save()

#                     # Replace the book-author relationships.
#                     BookAuthors.objects.filter(book=updated_book).delete()

#                     selected_authors = form.cleaned_data['authors']

#                     BookAuthors.objects.bulk_create([
#                         BookAuthors(
#                             book=updated_book,
#                             author=author
#                         )
#                         for author in selected_authors
#                     ])

#                 messages.success(
#                     request,
#                     'Book information updated successfully.'
#                 )

#                 return redirect(
#                     'book_detail',
#                     book_id=book.book_id
#                 )

#             except Exception:
#                 messages.error(
#                     request,
#                     'Unable to update the book. Please try again.'
#                 )

#     else:
#         form = BookUpdateForm(instance=book)

#     return render(
#         request,
#         'library_app/edit_book.html',
#         {
#             'form': form,
#             'book': book,
#             'page_title': 'Edit Book',
#         }
#     )


@librarian_required
def edit_book(request, book_id):

    # Retrieve the existing book using raw SQL.
    book_sql = """
        SELECT
            book_id,
            title,
            isbn,
            publisher_id,
            category_id,
            edition,
            publication_year,
            language
        FROM books
        WHERE book_id = %s
    """

    with connection.cursor() as cursor:
        cursor.execute(book_sql, [book_id])
        book_row = cursor.fetchone()

    if book_row is None:
        raise Http404('Book not found.')

    # Build initial data for the existing BookUpdateForm.
    book_data = {
        'title': book_row[1],
        'isbn': book_row[2],
        'publisher': book_row[3],
        'category': book_row[4],
        'edition': book_row[5],
        'publication_year': book_row[6],
        'language': book_row[7],
    }

    if request.method == 'POST':
        form = BookUpdateForm(request.POST)

        if form.is_valid():

            data = form.cleaned_data

            try:
                with transaction.atomic():

                    # 1. Update the book record.
                    update_book_sql = """
                        UPDATE books
                        SET
                            title = %s,
                            isbn = %s,
                            publisher_id = %s,
                            category_id = %s,
                            edition = %s,
                            publication_year = %s,
                            language = %s
                        WHERE book_id = %s
                    """

                    with connection.cursor() as cursor:
                        cursor.execute(
                            update_book_sql,
                            [
                                data['title'],
                                data['isbn'] or None,
                                data['publisher'].pk,
                                data['category'].pk,
                                data['edition'] or None,
                                data['publication_year'],
                                data['language'] or None,
                                book_id,
                            ]
                        )

                    # 2. Remove previous author relationships.
                    with connection.cursor() as cursor:
                        cursor.execute(
                            """
                            DELETE FROM book_authors
                            WHERE book_id = %s
                            """,
                            [book_id]
                        )

                    # 3. Insert the newly selected author relationships.
                    selected_authors = data['authors']

                    author_records = [
                        (book_id, author.pk)
                        for author in selected_authors
                    ]

                    if author_records:
                        with connection.cursor() as cursor:
                            cursor.executemany(
                                """
                                INSERT INTO book_authors (
                                    book_id,
                                    author_id
                                )
                                VALUES (%s, %s)
                                """,
                                author_records
                            )

                messages.success(
                    request,
                    'Book information updated successfully.'
                )

                return redirect(
                    'book_detail',
                    book_id=book_id
                )

            except DatabaseError:
                messages.error(
                    request,
                    'Unable to update the book. Please try again.'
                )

    else:
        form = BookUpdateForm(initial=book_data)

    # Provide a lightweight book object for the existing template.
    book = SimpleNamespace(
        book_id=book_row[0],
        title=book_row[1]
    )

    return render(
        request,
        'library_app/edit_book.html',
        {
            'form': form,
            'book': book,
            'page_title': 'Edit Book',
        }
    )


# @librarian_required
# def add_book_copies(request, book_id):
#     book = get_object_or_404(Books, book_id=book_id)

#     if request.method == 'POST':
#         form = BookCopyForm(request.POST)

#         if form.is_valid():
#             accession_numbers = form.cleaned_data['accession_numbers']
#             shelf_location = form.cleaned_data['shelf_location'] or None

#             try:
#                 with transaction.atomic():
#                     BookCopies.objects.bulk_create([
#                         BookCopies(
#                             book=book,
#                             accession_number=number,
#                             copy_status='AVAILABLE',
#                             shelf_location=shelf_location,
#                         )
#                         for number in accession_numbers
#                     ])

#                 messages.success(
#                     request,
#                     f'{len(accession_numbers)} physical copies '
#                     f'were added successfully.'
#                 )

#                 return redirect(
#                     'book_detail',
#                     book_id=book.book_id
#                 )

#             except IntegrityError:
#                 messages.error(
#                     request,
#                     'One or more accession numbers already exist. '
#                     'Please check and try again.'
#                 )

#             except Exception:
#                 messages.error(
#                     request,
#                     'Unable to register the copies. Please try again.'
#                 )

#     else:
#         form = BookCopyForm()

#     return render(
#         request,
#         'library_app/add_book_copies.html',
#         {
#             'form': form,
#             'book': book,
#             'page_title': 'Add Physical Copies',
#         }
#     )


@librarian_required
def add_book_copies(request, book_id):

    # Retrieve book information using SQL.
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT book_id, title
            FROM books
            WHERE book_id = %s
            """,
            [book_id]
        )
        book_row = cursor.fetchone()

    if book_row is None:
        raise Http404('Book not found.')

    book = SimpleNamespace(
        book_id=book_row[0],
        title=book_row[1]
    )

    if request.method == 'POST':
        form = BookCopyForm(request.POST)

        if form.is_valid():
            accession_numbers = form.cleaned_data['accession_numbers']
            shelf_location = form.cleaned_data['shelf_location'] or None

            try:
                with transaction.atomic():

                    insert_sql = """
                        INSERT INTO book_copies (
                            book_id,
                            accession_number,
                            copy_status,
                            shelf_location
                        )
                        VALUES (%s, %s, %s, %s)
                    """

                    copy_records = [
                        (
                            book_id,
                            number,
                            'AVAILABLE',
                            shelf_location
                        )
                        for number in accession_numbers
                    ]

                    with connection.cursor() as cursor:
                        cursor.executemany(
                            insert_sql,
                            copy_records
                        )

                messages.success(
                    request,
                    f'{len(accession_numbers)} physical copies '
                    f'were added successfully.'
                )

                return redirect(
                    'book_detail',
                    book_id=book_id
                )

            except IntegrityError:
                messages.error(
                    request,
                    'One or more accession numbers already exist. '
                    'Please check and try again.'
                )

            except DatabaseError:
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



# @login_required
# def reference_data(request):
#     member = request.user.profile.member

#     context = {
#         'page_title': 'Library Reference Data',
#         'member': member,
#         'authors': Authors.objects.order_by('author_name'),
#         'publishers': Publishers.objects.order_by('publisher_name'),
#         'categories': Categories.objects.order_by('category_name'),
#     }

#     return render(
#         request,
#         'library_app/reference_data.html',
#         context
#     )


@login_required
def reference_data(request):

    member = request.user.profile.member

    # Retrieve authors.
    authors_sql = """
        SELECT
            author_id,
            author_name,
            biography
        FROM authors
        ORDER BY author_name
    """

    # Retrieve publishers.
    publishers_sql = """
        SELECT
            publisher_id,
            publisher_name,
            address
        FROM publishers
        ORDER BY publisher_name
    """

    # Retrieve categories.
    categories_sql = """
        SELECT
            category_id,
            category_name,
            description
        FROM categories
        ORDER BY category_name
    """

    with connection.cursor() as cursor:

        cursor.execute(authors_sql)
        author_columns = [
            column[0] for column in cursor.description
        ]
        authors = [
            dict(zip(author_columns, row))
            for row in cursor.fetchall()
        ]

        cursor.execute(publishers_sql)
        publisher_columns = [
            column[0] for column in cursor.description
        ]
        publishers = [
            dict(zip(publisher_columns, row))
            for row in cursor.fetchall()
        ]

        cursor.execute(categories_sql)
        category_columns = [
            column[0] for column in cursor.description
        ]
        categories = [
            dict(zip(category_columns, row))
            for row in cursor.fetchall()
        ]

    context = {
        'page_title': 'Library Reference Data',
        'member': member,
        'authors': authors,
        'publishers': publishers,
        'categories': categories,
    }

    return render(
        request,
        'library_app/reference_data.html',
        context
    )


# @librarian_required
# def manage_reference(request, record_type, record_id=None):

#     # Only these three models can be managed through this view.
#     configurations = {
#         'author': {
#             'model': Authors,
#             'form': AuthorForm,
#             'label': 'Author',
#         },
#         'publisher': {
#             'model': Publishers,
#             'form': PublisherForm,
#             'label': 'Publisher',
#         },
#         'category': {
#             'model': Categories,
#             'form': CategoryForm,
#             'label': 'Category',
#         },
#     }

#     config = configurations.get(record_type)

#     if config is None:
#         raise Http404('Invalid reference-data type.')

#     model = config['model']
#     form_class = config['form']
#     label = config['label']

#     instance = None

#     if record_id is not None:
#         instance = get_object_or_404(
#             model,
#             pk=record_id
#         )

#     if request.method == 'POST':
#         form = form_class(
#             request.POST,
#             instance=instance
#         )

#         if form.is_valid():
#             try:
#                 with transaction.atomic():
#                     record = form.save()

#                 action = 'updated' if instance else 'created'

#                 messages.success(
#                     request,
#                     f'{label} "{record}" was {action} successfully.'
#                 )

#                 return redirect('reference_data')

#             except IntegrityError:
#                 messages.error(
#                     request,
#                     f'This {label.lower()} already exists.'
#                 )

#     else:
#         form = form_class(instance=instance)

#     context = {
#         'page_title': f'{"Edit" if instance else "Add"} {label}',
#         'form': form,
#         'record_type': record_type,
#         'label': label,
#         'instance': instance,
#     }

#     return render(
#         request,
#         'library_app/reference_form.html',
#         context
#     )


@librarian_required
def manage_reference(request, record_type, record_id=None):

    # Fixed configuration: never take table or column names from user input.
    configurations = {
        'author': {
            'table': 'authors',
            'pk': 'author_id',
            'name_column': 'author_name',
            'fields': ['author_name', 'biography'],
            'form': AuthorForm,
            'label': 'Author',
        },
        'publisher': {
            'table': 'publishers',
            'pk': 'publisher_id',
            'name_column': 'publisher_name',
            'fields': ['publisher_name', 'address'],
            'form': PublisherForm,
            'label': 'Publisher',
        },
        'category': {
            'table': 'categories',
            'pk': 'category_id',
            'name_column': 'category_name',
            'fields': ['category_name', 'description'],
            'form': CategoryForm,
            'label': 'Category',
        },
    }

    config = configurations.get(record_type)

    if config is None:
        raise Http404('Invalid reference-data type.')

    table = config['table']
    pk_column = config['pk']
    name_column = config['name_column']
    fields = config['fields']
    form_class = config['form']
    label = config['label']

    instance = None
    initial_data = {}

    # Retrieve the existing record for editing.
    if record_id is not None:

        select_sql = f"""
            SELECT {', '.join(fields)}
            FROM {table}
            WHERE {pk_column} = %s
        """

        with connection.cursor() as cursor:
            cursor.execute(select_sql, [record_id])
            row = cursor.fetchone()

        if row is None:
            raise Http404(f'{label} not found.')

        initial_data = dict(zip(fields, row))

        instance = SimpleNamespace(
            **initial_data,
            pk=record_id
        )

    if request.method == 'POST':

        form = form_class(request.POST)

        if form.is_valid():

            cleaned_data = form.cleaned_data

            values = [
                cleaned_data[field]
                for field in fields
            ]

            # Check for duplicate names using SQL.
            duplicate_sql = f"""
                SELECT COUNT(*)
                FROM {table}
                WHERE LOWER({name_column}) = LOWER(%s)
            """

            duplicate_params = [cleaned_data[name_column]]

            if record_id is not None:
                duplicate_sql += f" AND {pk_column} != %s"
                duplicate_params.append(record_id)

            try:
                with transaction.atomic():

                    with connection.cursor() as cursor:
                        cursor.execute(
                            duplicate_sql,
                            duplicate_params
                        )
                        duplicate_exists = cursor.fetchone()[0] > 0

                    if duplicate_exists:
                        form.add_error(
                            name_column,
                            f'This {label.lower()} already exists.'
                        )

                    else:

                        if record_id is None:

                            # Insert a new reference record.
                            placeholders = ', '.join(
                                ['%s'] * len(fields)
                            )

                            insert_sql = f"""
                                INSERT INTO {table} (
                                    {', '.join(fields)}
                                )
                                VALUES ({placeholders})
                            """

                            with connection.cursor() as cursor:
                                cursor.execute(insert_sql, values)

                        else:

                            # Update the existing reference record.
                            assignments = ', '.join(
                                f'{field} = %s'
                                for field in fields
                            )

                            update_sql = f"""
                                UPDATE {table}
                                SET {assignments}
                                WHERE {pk_column} = %s
                            """

                            with connection.cursor() as cursor:
                                cursor.execute(
                                    update_sql,
                                    values + [record_id]
                                )

                        if not duplicate_exists:

                            action = (
                                'updated'
                                if record_id is not None
                                else 'created'
                            )

                            messages.success(
                                request,
                                f'{label} "{cleaned_data[name_column]}" '
                                f'was {action} successfully.'
                            )

                            return redirect('reference_data')

            except IntegrityError:
                form.add_error(
                    name_column,
                    f'This {label.lower()} already exists.'
                )

            except DatabaseError:
                messages.error(
                    request,
                    f'Unable to save this {label.lower()}. Please try again.'
                )

    else:
        form = form_class(initial=initial_data)

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


# @librarian_required
# @require_POST
# def delete_book(request, book_id):

#     book = get_object_or_404(Books, book_id=book_id)

#     # Never delete books that have loan history.
#     has_loan_history = Loans.objects.filter(
#         copy__book=book
#     ).exists()

#     if has_loan_history:
#         messages.error(
#             request,
#             'This book cannot be deleted because it has loan history.'
#         )
#         return redirect('book_detail', book_id=book.book_id)

#     # Never delete books with reservation history.
#     has_reservations = Reservations.objects.filter(
#         book=book
#     ).exists()

#     if has_reservations:
#         messages.error(
#             request,
#             'This book cannot be deleted because it has reservation records.'
#         )
#         return redirect('book_detail', book_id=book.book_id)

#     try:
#         with transaction.atomic():

#             # Delete author associations first.
#             BookAuthors.objects.filter(book=book).delete()

#             # Delete physical copies.
#             BookCopies.objects.filter(book=book).delete()

#             # Delete the book title.
#             book.delete()

#         messages.success(
#             request,
#             'Book and its physical copies were deleted successfully.'
#         )

#         return redirect('books_catalogue')

#     except Exception:
#         messages.error(
#             request,
#             'Unable to delete this book. Database constraints may prevent deletion.'
#         )
#         return redirect('books_catalogue')


@librarian_required
@require_POST
def delete_book(request, book_id):

    try:
        with transaction.atomic():

            # 1. Lock and verify the book record.
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT book_id, title
                    FROM books
                    WHERE book_id = %s
                    FOR UPDATE
                    """,
                    [book_id]
                )

                book_row = cursor.fetchone()

            if book_row is None:
                raise Http404('Book not found.')

            book_title = book_row[1]

            # 2. Check whether any copy has loan history.
            loan_check_sql = """
                SELECT EXISTS (
                    SELECT 1
                    FROM loans l
                    INNER JOIN book_copies bc
                        ON l.copy_id = bc.copy_id
                    WHERE bc.book_id = %s
                )
            """

            with connection.cursor() as cursor:
                cursor.execute(loan_check_sql, [book_id])
                has_loan_history = cursor.fetchone()[0]

            if has_loan_history:
                messages.error(
                    request,
                    'This book cannot be deleted because it has loan history.'
                )
                return redirect('book_detail', book_id=book_id)

            # 3. Check whether reservation records exist.
            reservation_check_sql = """
                SELECT EXISTS (
                    SELECT 1
                    FROM reservations
                    WHERE book_id = %s
                )
            """

            with connection.cursor() as cursor:
                cursor.execute(
                    reservation_check_sql,
                    [book_id]
                )
                has_reservations = cursor.fetchone()[0]

            if has_reservations:
                messages.error(
                    request,
                    'This book cannot be deleted because it has reservation records.'
                )
                return redirect('book_detail', book_id=book_id)

            # 4. Delete book-author relationships.
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    DELETE FROM book_authors
                    WHERE book_id = %s
                    """,
                    [book_id]
                )

            # 5. Delete physical copies.
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    DELETE FROM book_copies
                    WHERE book_id = %s
                    """,
                    [book_id]
                )

            # 6. Delete the book record.
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    DELETE FROM books
                    WHERE book_id = %s
                    """,
                    [book_id]
                )

        messages.success(
            request,
            f'"{book_title}" and its physical copies were deleted successfully.'
        )

        return redirect('books_catalogue')

    except Http404:
        raise

    except DatabaseError:
        messages.error(
            request,
            'Unable to delete this book. Database constraints may prevent deletion.'
        )
        return redirect('books_catalogue')

