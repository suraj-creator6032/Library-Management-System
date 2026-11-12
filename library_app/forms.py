
from django import forms

from .models import (
    Books,
    Publishers,
    Categories,
    Authors,
    BookCopies,
)


class BookCreateForm(forms.Form):

    title = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter book title',
        })
    )

    isbn = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter ISBN (optional)',
        })
    )

    publisher = forms.ModelChoiceField(
        queryset=Publishers.objects.order_by('publisher_name'),
        empty_label='Select publisher'
    )

    category = forms.ModelChoiceField(
        queryset=Categories.objects.order_by('category_name'),
        empty_label='Select category'
    )

    authors = forms.ModelMultipleChoiceField(
        queryset=Authors.objects.order_by('author_name'),
        required=False,
        widget=forms.CheckboxSelectMultiple
    )

    edition = forms.CharField(
        max_length=50,
        required=False
    )

    publication_year = forms.IntegerField(
        required=False,
        min_value=1000,
        max_value=2100
    )

    language = forms.CharField(
        max_length=50,
        required=False,
        initial='English'
    )

    accession_numbers = forms.CharField(
        widget=forms.Textarea(attrs={
            'rows': 4,
            'placeholder': 'ACC008, ACC009, ACC010',
        }),
        help_text='Enter one or more accession numbers, separated by commas or new lines.'
    )

    shelf_location = forms.CharField(
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Example: A-02',
        })
    )

    def clean_isbn(self):
        isbn = self.cleaned_data.get('isbn', '').strip()

        if isbn and Books.objects.filter(isbn=isbn).exists():
            raise forms.ValidationError(
                'A book with this ISBN already exists.'
            )

        return isbn or None

    def clean_accession_numbers(self):
        raw_value = self.cleaned_data['accession_numbers']

        numbers = [
            number.strip()
            for number in raw_value.replace('\n', ',').split(',')
            if number.strip()
        ]

        if not numbers:
            raise forms.ValidationError(
                'Enter at least one accession number.'
            )

        if len(numbers) != len(set(numbers)):
            raise forms.ValidationError(
                'Duplicate accession numbers were entered.'
            )

        existing_numbers = BookCopies.objects.filter(
            accession_number__in=numbers
        ).values_list('accession_number', flat=True)

        existing_numbers = list(existing_numbers)

        if existing_numbers:
            raise forms.ValidationError(
                'These accession numbers already exist: '
                + ', '.join(existing_numbers)
            )

        return numbers
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for name, field in self.fields.items():
            if name == 'authors':
                continue

            field.widget.attrs.update({
                'class': (
                    'w-full rounded-lg border border-slate-300 '
                    'bg-white px-4 py-2.5 text-sm text-slate-800 '
                    'outline-none transition '
                    'focus:border-indigo-500 focus:ring-2 '
                    'focus:ring-indigo-100'
                )
            })


class BookUpdateForm(forms.ModelForm):

    authors = forms.ModelMultipleChoiceField(
        queryset=Authors.objects.order_by('author_name'),
        required=False,
        widget=forms.CheckboxSelectMultiple
    )

    class Meta:
        model = Books
        fields = [
            'title',
            'isbn',
            'publisher',
            'category',
            'edition',
            'publication_year',
            'language',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for name, field in self.fields.items():
            if name == 'authors':
                continue

            field.widget.attrs.update({
                'class': (
                    'w-full rounded-lg border border-slate-300 '
                    'bg-white px-4 py-2.5 text-sm text-slate-800 '
                    'outline-none transition '
                    'focus:border-indigo-500 focus:ring-2 '
                    'focus:ring-indigo-100'
                )
            })

        if self.instance and self.instance.pk:
            self.fields['authors'].initial = Authors.objects.filter(
            bookauthors__book=self.instance
        )

    def clean_isbn(self):
        isbn = self.cleaned_data.get('isbn')

        if isbn:
            duplicate = Books.objects.filter(
                isbn=isbn
            ).exclude(
                book_id=self.instance.book_id
            ).exists()

            if duplicate:
                raise forms.ValidationError(
                    'Another book already uses this ISBN.'
                )

        return isbn or None


class BookCopyForm(forms.Form):

    accession_numbers = forms.CharField(
        widget=forms.Textarea(attrs={
            'rows': 4,
            'placeholder': 'ACC011, ACC012, ACC013',
        }),
        help_text='Enter unique accession numbers separated by commas or new lines.'
    )

    shelf_location = forms.CharField(
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Example: A-03',
        })
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs.update({
                'class': (
                    'w-full rounded-lg border border-slate-300 '
                    'bg-white px-4 py-2.5 text-sm text-slate-800 '
                    'outline-none transition '
                    'focus:border-indigo-500 focus:ring-2 '
                    'focus:ring-indigo-100'
                )
            })

    def clean_accession_numbers(self):
        raw_value = self.cleaned_data['accession_numbers']

        numbers = [
            number.strip()
            for number in raw_value.replace('\n', ',').split(',')
            if number.strip()
        ]

        if not numbers:
            raise forms.ValidationError(
                'Enter at least one accession number.'
            )

        if len(numbers) != len(set(numbers)):
            raise forms.ValidationError(
                'Duplicate accession numbers were entered.'
            )

        existing = BookCopies.objects.filter(
            accession_number__in=numbers
        ).values_list('accession_number', flat=True)

        if existing:
            raise forms.ValidationError(
                'These accession numbers already exist: '
                + ', '.join(existing)
            )

        return numbers

    

class AuthorForm(forms.ModelForm):

    class Meta:
        model = Authors
        fields = ['author_name', 'biography']
        widgets = {
            'author_name': forms.TextInput(attrs={
                'placeholder': 'Enter author name',
            }),
            'biography': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Enter author biography (optional)',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        apply_form_styles(self.fields)

    def clean_author_name(self):
        name = self.cleaned_data['author_name'].strip()

        duplicate = Authors.objects.filter(
            author_name__iexact=name
        ).exclude(
            author_id=self.instance.author_id
            if self.instance and self.instance.pk else None
        ).exists()

        if duplicate:
            raise forms.ValidationError(
                'An author with this name already exists.'
            )

        return name


class PublisherForm(forms.ModelForm):

    class Meta:
        model = Publishers
        fields = ['publisher_name', 'address']
        widgets = {
            'publisher_name': forms.TextInput(attrs={
                'placeholder': 'Enter publisher name',
            }),
            'address': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Enter publisher address (optional)',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        apply_form_styles(self.fields)


class CategoryForm(forms.ModelForm):

    class Meta:
        model = Categories
        fields = ['category_name', 'description']
        widgets = {
            'category_name': forms.TextInput(attrs={
                'placeholder': 'Enter category name',
            }),
            'description': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Describe this category (optional)',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        apply_form_styles(self.fields)


def apply_form_styles(fields):
    for field in fields.values():
        field.widget.attrs.update({
            'class': (
                'w-full rounded-lg border border-slate-300 '
                'bg-white px-4 py-2.5 text-sm text-slate-800 '
                'outline-none transition '
                'focus:border-indigo-500 focus:ring-2 '
                'focus:ring-indigo-100'
            )
        })


# from django import forms
# from django.db import connection


# ============================================================
# HELPER FUNCTIONS
# ============================================================

# def get_sql_choices(table, id_column, name_column):
#     """
#     Retrieve dropdown/checkbox options using manually written SQL.
#     Table and column names are supplied only by our fixed code.
#     """

#     query = f"""
#         SELECT {id_column}, {name_column}
#         FROM {table}
#         ORDER BY {name_column}
#     """

#     with connection.cursor() as cursor:
#         cursor.execute(query)
#         rows = cursor.fetchall()

#     return [
#         (row[0], row[1])
#         for row in rows
#     ]


# def get_existing_values(table, column, values):
#     """
#     Check which supplied values already exist in a database table.
#     Uses parameterized SQL.
#     """

#     if not values:
#         return []

#     placeholders = ', '.join(['%s'] * len(values))

#     query = f"""
#         SELECT {column}
#         FROM {table}
#         WHERE {column} IN ({placeholders})
#     """

#     with connection.cursor() as cursor:
#         cursor.execute(query, values)
#         rows = cursor.fetchall()

#     return [row[0] for row in rows]


# def apply_form_styles(fields):
#     """
#     Apply common Tailwind CSS classes to form fields.
#     """

#     for field in fields.values():

#         field.widget.attrs.update({
#             'class': (
#                 'w-full rounded-lg border border-slate-300 '
#                 'bg-white px-4 py-2.5 text-sm text-slate-800 '
#                 'outline-none transition '
#                 'focus:border-indigo-500 focus:ring-2 '
#                 'focus:ring-indigo-100'
#             )
#         })


# ============================================================
# BOOK CREATE FORM
# ============================================================

# class BookCreateForm(forms.Form):

#     title = forms.CharField(
#         max_length=255,
#         widget=forms.TextInput(attrs={
#             'placeholder': 'Enter book title',
#         })
#     )

#     isbn = forms.CharField(
#         max_length=20,
#         required=False,
#         widget=forms.TextInput(attrs={
#             'placeholder': 'Enter ISBN (optional)',
#         })
#     )

#     publisher = forms.TypedChoiceField(
#         choices=[],
#         coerce=int,
#         empty_value=None,
#         widget=forms.Select(),
#         label='Publisher'
#     )

#     category = forms.TypedChoiceField(
#         choices=[],
#         coerce=int,
#         empty_value=None,
#         widget=forms.Select(),
#         label='Category'
#     )

#     authors = forms.TypedMultipleChoiceField(
#         choices=[],
#         coerce=int,
#         required=False,
#         widget=forms.CheckboxSelectMultiple
#     )

#     edition = forms.CharField(
#         max_length=50,
#         required=False
#     )

#     publication_year = forms.IntegerField(
#         required=False,
#         min_value=1000,
#         max_value=2100
#     )

#     language = forms.CharField(
#         max_length=50,
#         required=False,
#         initial='English'
#     )

#     accession_numbers = forms.CharField(
#         widget=forms.Textarea(attrs={
#             'rows': 4,
#             'placeholder': 'ACC008, ACC009, ACC010',
#         }),
#         help_text=(
#             'Enter one or more accession numbers, '
#             'separated by commas or new lines.'
#         )
#     )

#     shelf_location = forms.CharField(
#         max_length=50,
#         required=False,
#         widget=forms.TextInput(attrs={
#             'placeholder': 'Example: A-02',
#         })
#     )

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)

#         # Populate publisher choices using SQL.
#         publisher_choices = get_sql_choices(
#             'publishers',
#             'publisher_id',
#             'publisher_name'
#         )

#         self.fields['publisher'].choices = [
#             ('', 'Select publisher')
#         ] + publisher_choices

#         # Populate category choices using SQL.
#         category_choices = get_sql_choices(
#             'categories',
#             'category_id',
#             'category_name'
#         )

#         self.fields['category'].choices = [
#             ('', 'Select category')
#         ] + category_choices

#         # Populate author checkboxes using SQL.
#         self.fields['authors'].choices = get_sql_choices(
#             'authors',
#             'author_id',
#             'author_name'
#         )

#         apply_form_styles(self.fields)

#     def clean_isbn(self):

#         isbn = self.cleaned_data.get('isbn', '').strip()

#         if isbn:

#             with connection.cursor() as cursor:
#                 cursor.execute(
#                     """
#                     SELECT EXISTS (
#                         SELECT 1
#                         FROM books
#                         WHERE isbn = %s
#                     )
#                     """,
#                     [isbn]
#                 )

#                 duplicate = cursor.fetchone()[0]

#             if duplicate:
#                 raise forms.ValidationError(
#                     'A book with this ISBN already exists.'
#                 )

#         return isbn or None

#     def clean_accession_numbers(self):

#         raw_value = self.cleaned_data['accession_numbers']

#         numbers = [
#             number.strip()
#             for number in raw_value.replace('\r', '').replace(
#                 '\n', ','
#             ).split(',')
#             if number.strip()
#         ]

#         if not numbers:
#             raise forms.ValidationError(
#                 'Enter at least one accession number.'
#             )

#         if len(numbers) != len(set(numbers)):
#             raise forms.ValidationError(
#                 'Duplicate accession numbers were entered.'
#             )

#         existing_numbers = get_existing_values(
#             'book_copies',
#             'accession_number',
#             numbers
#         )

#         if existing_numbers:
#             raise forms.ValidationError(
#                 'These accession numbers already exist: '
#                 + ', '.join(existing_numbers)
#             )

#         return numbers


# ============================================================
# BOOK UPDATE FORM
# ============================================================

# class BookUpdateForm(forms.Form):

#     title = forms.CharField(
#         max_length=255
#     )

#     isbn = forms.CharField(
#         max_length=20,
#         required=False
#     )

#     publisher = forms.TypedChoiceField(
#         choices=[],
#         coerce=int,
#         empty_value=None,
#         widget=forms.Select()
#     )

#     category = forms.TypedChoiceField(
#         choices=[],
#         coerce=int,
#         empty_value=None,
#         widget=forms.Select()
#     )

#     authors = forms.TypedMultipleChoiceField(
#         choices=[],
#         coerce=int,
#         required=False,
#         widget=forms.CheckboxSelectMultiple
#     )

#     edition = forms.CharField(
#         max_length=50,
#         required=False
#     )

#     publication_year = forms.IntegerField(
#         required=False,
#         min_value=1000,
#         max_value=2100
#     )

#     language = forms.CharField(
#         max_length=50,
#         required=False
#     )

#     def __init__(self, *args, **kwargs):

#         # The book ID is passed separately for loading existing authors.
#         book_id = kwargs.pop('book_id', None)

#         super().__init__(*args, **kwargs)

#         # Publisher choices.
#         self.fields['publisher'].choices = [
#             ('', 'Select publisher')
#         ] + get_sql_choices(
#             'publishers',
#             'publisher_id',
#             'publisher_name'
#         )

#         # Category choices.
#         self.fields['category'].choices = [
#             ('', 'Select category')
#         ] + get_sql_choices(
#             'categories',
#             'category_id',
#             'category_name'
#         )

#         # Author choices.
#         self.fields['authors'].choices = get_sql_choices(
#             'authors',
#             'author_id',
#             'author_name'
#         )

#         # Load previously associated authors when editing.
#         if book_id is not None and not self.is_bound:

#             with connection.cursor() as cursor:
#                 cursor.execute(
#                     """
#                     SELECT author_id
#                     FROM book_authors
#                     WHERE book_id = %s
#                     """,
#                     [book_id]
#                 )

#                 author_ids = [
#                     row[0] for row in cursor.fetchall()
#                 ]

#             self.fields['authors'].initial = author_ids

#         apply_form_styles(self.fields)

#     def clean_isbn(self):

#         isbn = self.cleaned_data.get('isbn', '').strip()

#         if isbn:

#             book_id = self.initial.get('book_id')

#             with connection.cursor() as cursor:

#                 query = """
#                     SELECT EXISTS (
#                         SELECT 1
#                         FROM books
#                         WHERE isbn = %s
#                         AND book_id != %s
#                     )
#                 """

#                 cursor.execute(
#                     query,
#                     [isbn, book_id]
#                 )

#                 duplicate = cursor.fetchone()[0]

#             if duplicate:
#                 raise forms.ValidationError(
#                     'Another book already uses this ISBN.'
#                 )

#         return isbn or None


# ============================================================
# BOOK COPY FORM
# ============================================================

# class BookCopyForm(forms.Form):

#     accession_numbers = forms.CharField(
#         widget=forms.Textarea(attrs={
#             'rows': 4,
#             'placeholder': 'ACC011, ACC012, ACC013',
#         }),
#         help_text=(
#             'Enter unique accession numbers separated '
#             'by commas or new lines.'
#         )
#     )

#     shelf_location = forms.CharField(
#         max_length=50,
#         required=False,
#         widget=forms.TextInput(attrs={
#             'placeholder': 'Example: A-03',
#         })
#     )

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         apply_form_styles(self.fields)

#     def clean_accession_numbers(self):

#         raw_value = self.cleaned_data['accession_numbers']

#         numbers = [
#             number.strip()
#             for number in raw_value.replace('\r', '').replace(
#                 '\n', ','
#             ).split(',')
#             if number.strip()
#         ]

#         if not numbers:
#             raise forms.ValidationError(
#                 'Enter at least one accession number.'
#             )

#         if len(numbers) != len(set(numbers)):
#             raise forms.ValidationError(
#                 'Duplicate accession numbers were entered.'
#             )

#         existing_numbers = get_existing_values(
#             'book_copies',
#             'accession_number',
#             numbers
#         )

#         if existing_numbers:
#             raise forms.ValidationError(
#                 'These accession numbers already exist: '
#                 + ', '.join(existing_numbers)
#             )

#         return numbers


# ============================================================
# AUTHOR FORM
# ============================================================

# class AuthorForm(forms.Form):

#     author_name = forms.CharField(
#         max_length=150,
#         widget=forms.TextInput(attrs={
#             'placeholder': 'Enter author name',
#         })
#     )

#     biography = forms.CharField(
#         required=False,
#         widget=forms.Textarea(attrs={
#             'rows': 4,
#             'placeholder': 'Enter author biography (optional)',
#         })
#     )

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         apply_form_styles(self.fields)

#     def clean_author_name(self):

#         name = self.cleaned_data['author_name'].strip()

#         if not name:
#             raise forms.ValidationError(
#                 'Author name cannot be empty.'
#             )

#         return name


# ============================================================
# PUBLISHER FORM
# ============================================================

# class PublisherForm(forms.Form):

#     publisher_name = forms.CharField(
#         max_length=150,
#         widget=forms.TextInput(attrs={
#             'placeholder': 'Enter publisher name',
#         })
#     )

#     address = forms.CharField(
#         required=False,
#         widget=forms.Textarea(attrs={
#             'rows': 4,
#             'placeholder': 'Enter publisher address (optional)',
#         })
#     )

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         apply_form_styles(self.fields)

#     def clean_publisher_name(self):

#         name = self.cleaned_data['publisher_name'].strip()

#         if not name:
#             raise forms.ValidationError(
#                 'Publisher name cannot be empty.'
#             )

#         return name


# ============================================================
# CATEGORY FORM
# ============================================================

# class CategoryForm(forms.Form):

#     category_name = forms.CharField(
#         max_length=100,
#         widget=forms.TextInput(attrs={
#             'placeholder': 'Enter category name',
#         })
#     )

#     description = forms.CharField(
#         required=False,
#         widget=forms.Textarea(attrs={
#             'rows': 4,
#             'placeholder': 'Describe this category (optional)',
#         })
#     )

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         apply_form_styles(self.fields)

#     def clean_category_name(self):

#         name = self.cleaned_data['category_name'].strip()

#         if not name:
#             raise forms.ValidationError(
#                 'Category name cannot be empty.'
#             )

#         return name
