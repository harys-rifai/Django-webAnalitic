from django.db import models


class Roles(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(unique=True, max_length=255)
    description = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'roles'

    def __str__(self):
        return self.name


class RoleUser(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey('Users', models.DO_NOTHING)
    role = models.ForeignKey(Roles, models.DO_NOTHING)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'role_user'


class AppVersions(models.Model):
    id = models.BigAutoField(primary_key=True)
    version = models.CharField(max_length=255)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    changes = models.TextField(blank=True, null=True)
    link = models.CharField(max_length=255, blank=True, null=True)
    build_by = models.CharField(max_length=255, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'app_versions'

    def __str__(self):
        return self.version


class Companies(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)
    code = models.CharField(unique=True, max_length=255)
    type = models.CharField(max_length=255)
    parent = models.ForeignKey('self', models.DO_NOTHING, blank=True, null=True)
    email = models.CharField(max_length=255, blank=True, null=True)
    phone = models.CharField(max_length=255, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=255, blank=True, null=True)
    province = models.CharField(max_length=255, blank=True, null=True)
    postal_code = models.CharField(max_length=255, blank=True, null=True)
    country = models.CharField(max_length=255)
    tax_id = models.CharField(max_length=255, blank=True, null=True)
    logo = models.CharField(max_length=255, blank=True, null=True)
    is_active = models.BooleanField()
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'companies'

    def __str__(self):
        return self.name


class Departments(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)
    code = models.CharField(unique=True, max_length=255)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField()
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    company = models.ForeignKey(Companies, models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'departments'

    def __str__(self):
        return self.name


class Users(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)
    email = models.CharField(unique=True, max_length=255)
    email_verified_at = models.DateTimeField(blank=True, null=True)
    password = models.CharField(max_length=255)
    remember_token = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    company = models.ForeignKey(Companies, models.DO_NOTHING, blank=True, null=True)
    department = models.ForeignKey(Departments, models.DO_NOTHING, blank=True, null=True)
    active = models.BooleanField()

    class Meta:
        managed = False
        db_table = 'users'

    def __str__(self):
        return self.name


class Distributors(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)
    code = models.CharField(unique=True, max_length=255)
    phone = models.CharField(max_length=255, blank=True, null=True)
    email = models.CharField(max_length=255, blank=True, null=True)
    npwp = models.CharField(max_length=255, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    contact_person = models.CharField(max_length=255, blank=True, null=True)
    contact_phone = models.CharField(max_length=255, blank=True, null=True)
    contact_email = models.CharField(max_length=255, blank=True, null=True)
    termin = models.CharField(max_length=255, blank=True, null=True)
    bank_name = models.CharField(max_length=255, blank=True, null=True)
    bank_account = models.CharField(max_length=255, blank=True, null=True)
    bank_account_name = models.CharField(max_length=255, blank=True, null=True)
    norek = models.CharField(max_length=255, blank=True, null=True)
    is_active = models.BooleanField()
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'distributors'

    def __str__(self):
        return self.name


class PurchaseRequests(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(Users, models.DO_NOTHING)
    item_name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    qty = models.IntegerField()
    estimated_price = models.DecimalField(max_digits=15, decimal_places=2)
    status = models.CharField(max_length=255)
    approved_by_line = models.ForeignKey(Users, models.DO_NOTHING, db_column='approved_by_line', related_name='pr_approved_by_line', blank=True, null=True)
    approved_by_ceo = models.ForeignKey(Users, models.DO_NOTHING, db_column='approved_by_ceo', related_name='pr_approved_by_ceo', blank=True, null=True)
    approved_line_at = models.DateTimeField(blank=True, null=True)
    approved_ceo_at = models.DateTimeField(blank=True, null=True)
    line_manager_notes = models.TextField(blank=True, null=True)
    ceo_notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    deleted_at = models.DateTimeField(blank=True, null=True)
    rejected_info = models.TextField(blank=True, null=True)
    department = models.ForeignKey(Departments, models.DO_NOTHING, blank=True, null=True)
    unit = models.CharField(max_length=255)
    reason = models.TextField(blank=True, null=True)
    group = models.ForeignKey('self', models.DO_NOTHING, blank=True, null=True)
    is_header = models.BooleanField()
    is_grouped = models.BooleanField()

    class Meta:
        managed = False
        db_table = 'purchase_requests'

    def __str__(self):
        return f"{self.po_number} - {self.item_name}" if hasattr(self, 'po_number') else self.item_name


class PurchaseOrders(models.Model):
    id = models.BigAutoField(primary_key=True)
    request = models.ForeignKey(PurchaseRequests, models.DO_NOTHING)
    po_number = models.CharField(unique=True, max_length=255)
    distributor_name = models.CharField(max_length=255)
    distributor_contact = models.CharField(max_length=255, blank=True, null=True)
    total_price = models.DecimalField(max_digits=15, decimal_places=2)
    status = models.CharField(max_length=255)
    created_by = models.ForeignKey(Users, models.DO_NOTHING, db_column='created_by')
    sent_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    distributor = models.ForeignKey(Distributors, models.DO_NOTHING, db_column='distributor_id', blank=True, null=True)
    distributor_phone = models.CharField(max_length=255, blank=True, null=True)
    distributor_email = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'purchase_orders'

    def __str__(self):
        return self.po_number


class MaterialReceipts(models.Model):
    id = models.BigAutoField(primary_key=True)
    po = models.ForeignKey(PurchaseOrders, models.DO_NOTHING)
    mr_number = models.CharField(unique=True, max_length=255)
    received_qty = models.IntegerField()
    transaction_price = models.DecimalField(max_digits=15, decimal_places=2)
    notes = models.TextField(blank=True, null=True)
    received_by = models.ForeignKey(Users, models.DO_NOTHING, db_column='received_by')
    received_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    ppn_percent = models.DecimalField(max_digits=5, decimal_places=2)
    pph_percent = models.DecimalField(max_digits=5, decimal_places=2)
    subtotal = models.DecimalField(max_digits=15, decimal_places=2)
    ppn_amount = models.DecimalField(max_digits=15, decimal_places=2)
    pph_amount = models.DecimalField(max_digits=15, decimal_places=2)
    total_amount = models.DecimalField(max_digits=15, decimal_places=2)

    class Meta:
        managed = False
        db_table = 'material_receipts'

    def __str__(self):
        return self.mr_number


class Assets(models.Model):
    id = models.BigAutoField(primary_key=True)
    asset_code = models.CharField(unique=True, max_length=255)
    name = models.CharField(max_length=255)
    mr = models.ForeignKey(MaterialReceipts, models.DO_NOTHING, blank=True, null=True)
    purchase_request = models.ForeignKey(PurchaseRequests, models.DO_NOTHING, blank=True, null=True)
    quantity = models.IntegerField()
    condition = models.CharField(max_length=255)
    location = models.CharField(max_length=255, blank=True, null=True)
    purchase_date = models.DateField()
    purchase_price = models.DecimalField(max_digits=15, decimal_places=2)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    unit = models.CharField(max_length=255)
    min_stock = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'assets'

    def __str__(self):
        return f"{self.asset_code} - {self.name}"


class Stocks(models.Model):
    id = models.BigAutoField(primary_key=True)
    sku = models.CharField(max_length=255, blank=True, null=True)
    asset = models.ForeignKey(Assets, models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey(Users, models.DO_NOTHING, blank=True, null=True)
    barcode = models.CharField(max_length=255, blank=True, null=True)
    name = models.CharField(max_length=255)
    quantity = models.IntegerField()
    qty_old = models.IntegerField()
    qty_add = models.IntegerField()
    qty_adjustment = models.IntegerField()
    qty_decomist = models.IntegerField()
    unit_price = models.DecimalField(max_digits=15, decimal_places=2)
    unit = models.CharField(max_length=255, blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    min_stock = models.IntegerField()
    low_stock = models.BooleanField()
    flag = models.CharField(max_length=255, blank=True, null=True)
    active = models.BooleanField()
    remark = models.TextField(blank=True, null=True)
    log = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'stocks'

    def __str__(self):
        return self.name
