
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
