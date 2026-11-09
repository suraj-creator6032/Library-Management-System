# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models
from django.conf import settings


class Authors(models.Model):
    author_id = models.AutoField(primary_key=True)
    author_name = models.CharField(max_length=150)
    biography = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'authors'


class BookAuthors(models.Model):
    pk = models.CompositePrimaryKey('book_id', 'author_id')
    book = models.ForeignKey('Books', models.DO_NOTHING)
    author = models.ForeignKey(Authors, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'book_authors'


class BookCopies(models.Model):
    copy_id = models.AutoField(primary_key=True)
    book = models.ForeignKey('Books', models.DO_NOTHING)
    accession_number = models.CharField(unique=True, max_length=50)
    acquisition_date = models.DateField(blank=True, null=True)
    copy_status = models.CharField(max_length=20, blank=True, null=True)
    shelf_location = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'book_copies'


class Books(models.Model):
    book_id = models.AutoField(primary_key=True)
    isbn = models.CharField(unique=True, max_length=20, blank=True, null=True)
    title = models.CharField(max_length=255)
    publisher = models.ForeignKey('Publishers', models.DO_NOTHING)
    category = models.ForeignKey('Categories', models.DO_NOTHING)
    edition = models.CharField(max_length=50, blank=True, null=True)
    publication_year = models.IntegerField(blank=True, null=True)
    language = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'books'


class Categories(models.Model):
    category_id = models.AutoField(primary_key=True)
    category_name = models.CharField(unique=True, max_length=100)
    description = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'categories'


class Departments(models.Model):
    department_id = models.AutoField(primary_key=True)
    department_name = models.CharField(unique=True, max_length=100)
    department_code = models.CharField(unique=True, max_length=20)

    class Meta:
        managed = False
        db_table = 'departments'


class Fines(models.Model):
    fine_id = models.AutoField(primary_key=True)
    loan = models.OneToOneField('Loans', models.DO_NOTHING)
    fine_amount = models.DecimalField(max_digits=10, decimal_places=2)
    fine_status = models.CharField(max_length=20, blank=True, null=True)
    calculated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'fines'


class LibrarySettings(models.Model):
    setting_id = models.AutoField(primary_key=True)
    setting_key = models.CharField(unique=True, max_length=100)
    setting_value = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'library_settings'


class Loans(models.Model):
    loan_id = models.AutoField(primary_key=True)
    copy = models.ForeignKey(BookCopies, models.DO_NOTHING)
    member = models.ForeignKey('Members', models.DO_NOTHING)
    issued_by = models.ForeignKey('Members', models.DO_NOTHING, db_column='issued_by', related_name='loans_issued_by_set')
    issue_date = models.DateField()
    due_date = models.DateField()
    return_date = models.DateField(blank=True, null=True)
    loan_status = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'loans'


class Members(models.Model):
    member_id = models.AutoField(primary_key=True)
    department = models.ForeignKey(Departments, models.DO_NOTHING, blank=True, null=True)
    college_id = models.CharField(unique=True, max_length=30)
    full_name = models.CharField(max_length=150)
    email = models.CharField(unique=True, max_length=100)
    phone = models.CharField(max_length=15, blank=True, null=True)
    member_type = models.CharField(max_length=20)
    joining_date = models.DateField()
    membership_status = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'members'


class Payments(models.Model):
    payment_id = models.AutoField(primary_key=True)
    fine = models.ForeignKey(Fines, models.DO_NOTHING)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateTimeField(blank=True, null=True)
    payment_method = models.CharField(max_length=30, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'payments'


class Publishers(models.Model):
    publisher_id = models.AutoField(primary_key=True)
    publisher_name = models.CharField(unique=True, max_length=150)
    address = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'publishers'


class Reservations(models.Model):
    reservation_id = models.AutoField(primary_key=True)
    book = models.ForeignKey(Books, models.DO_NOTHING)
    member = models.ForeignKey(Members, models.DO_NOTHING)
    reservation_date = models.DateTimeField(blank=True, null=True)
    reservation_status = models.CharField(max_length=20, blank=True, null=True)
    expiry_date = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'reservations'

class UserProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile'
    )

    member = models.OneToOneField(
        'Members',
        on_delete=models.CASCADE,
        related_name='user_profile'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'user_profiles'

    def __str__(self):
        return f"{self.user.username} - {self.member.full_name}"