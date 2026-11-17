from decimal import Decimal
from django.test import TestCase, Client
from django.conf import settings
from django.utils import timezone
from django.core.management import call_command

from apps.accounts.models import AdminUser, CandidateAccount, EmployerAccount, Role
from apps.candidates.models import Applicant
from apps.candidates.status_helpers import set_applicant_status
from apps.placements.models import Placement, JobOffer
from apps.ledger.models import PlacementCommission, LedgerEntry
from apps.ledger.services import (
    parse_salary_to_monthly, parse_date_flexible,
    ensure_commission_for_joined, record_payment,
    update_salary, waive_commission, cancel_commission
)


class LedgerServicesTestCase(TestCase):
    def test_parse_salary_to_monthly_formats(self):
        # 6 LPA -> 50,000 / month
        m1, _ = parse_salary_to_monthly("6 LPA")
        self.assertEqual(m1, Decimal('50000.00'))

        # 6.5 lpa -> 54,166.67 / month
        m2, _ = parse_salary_to_monthly("6.5 lpa")
        self.assertEqual(m2, Decimal('54166.67'))

        # ₹6,00,000 -> 50,000 / month
        m3, _ = parse_salary_to_monthly("₹6,00,000")
        self.assertEqual(m3, Decimal('50000.00'))

        # 600000 -> 50,000 / month
        m4, _ = parse_salary_to_monthly("600000")
        self.assertEqual(m4, Decimal('50000.00'))

        # 3.6 lakh -> 30,000 / month
        m5, _ = parse_salary_to_monthly("3.6 lakh")
        self.assertEqual(m5, Decimal('30000.00'))

        # 25000/month -> 25,000 / month
        m6, _ = parse_salary_to_monthly("25000/month")
        self.assertEqual(m6, Decimal('25000.00'))

        # 25k pm -> 25,000 / month
        m7, _ = parse_salary_to_monthly("25k pm")
        self.assertEqual(m7, Decimal('25000.00'))

        # 25,000 per month -> 25,000 / month
        m8, _ = parse_salary_to_monthly("25,000 per month")
        self.assertEqual(m8, Decimal('25000.00'))

        # 4 LPA - 5 LPA -> lower bound 4 LPA = 33,333.33
        m9, note9 = parse_salary_to_monthly("4 LPA - 5 LPA")
        self.assertEqual(m9, Decimal('33333.33'))
        self.assertIn("lower bound", note9)

        # Garbage input -> returns None without crashing
        m_bad, _ = parse_salary_to_monthly("Not Applicable / Negotiable")
        self.assertIsNone(m_bad)

    def test_commission_calculation_50_percent(self):
        applicant = Applicant.objects.create(
            full_name="Rahul Verma",
            email="rahul@example.com",
            phone="9876543210",
            expected_salary="6 LPA"
        )
        comm = ensure_commission_for_joined(applicant=applicant)
        # Salary = 50,000.00 -> 50% commission = 25,000.00
        self.assertEqual(comm.first_month_salary, Decimal('50000.00'))
        self.assertEqual(comm.commission_amount, Decimal('25000.00'))
        self.assertEqual(comm.balance, Decimal('25000.00'))
        self.assertEqual(comm.status, 'PENDING')
        self.assertEqual(comm.entries.count(), 1)
        self.assertEqual(comm.entries.first().entry_type, 'DEBIT')

    def test_idempotent_commission_creation(self):
        applicant = Applicant.objects.create(
            full_name="Anita Sharma",
            email="anita@example.com",
            phone="9876543211",
            expected_salary="30000/month"
        )
        c1 = ensure_commission_for_joined(applicant=applicant)
        c2 = ensure_commission_for_joined(applicant=applicant)
        self.assertEqual(c1.id, c2.id)
        self.assertEqual(PlacementCommission.objects.filter(applicant=applicant).count(), 1)

    def test_missing_salary_and_update(self):
        applicant = Applicant.objects.create(
            full_name="Vikram Singh",
            email="vikram@example.com",
            phone="9876543212"
        )
        comm = ensure_commission_for_joined(applicant=applicant)
        self.assertEqual(comm.status, 'SALARY_MISSING')
        self.assertEqual(comm.commission_amount, Decimal('0.00'))

        # Fix salary
        update_salary(comm, Decimal('40000.00'), reason="Salary verified")
        comm.refresh_from_db()
        self.assertEqual(comm.first_month_salary, Decimal('40000.00'))
        self.assertEqual(comm.commission_amount, Decimal('20000.00'))
        self.assertEqual(comm.balance, Decimal('20000.00'))
        self.assertEqual(comm.status, 'PENDING')

    def test_payment_recording_and_receipts(self):
        applicant = Applicant.objects.create(
            full_name="Pooja Patel",
            email="pooja@example.com",
            phone="9876543213",
            expected_salary="50000/month"
        )
        comm = ensure_commission_for_joined(applicant=applicant) # 25,000 due

        # Overpayment rejection
        with self.assertRaises(ValueError):
            record_payment(comm, Decimal('30000.00'))

        # Zero/negative payment rejection
        with self.assertRaises(ValueError):
            record_payment(comm, Decimal('0.00'))

        # Partial payment: 10,000
        e1 = record_payment(comm, Decimal('10000.00'), payment_mode='UPI', reference_no='UPI123')
        comm.refresh_from_db()
        self.assertEqual(comm.status, 'PARTIAL')
        self.assertEqual(comm.balance, Decimal('15000.00'))
        self.assertTrue(e1.receipt_no.startswith('RCPT-'))

        # Final payment: 15,000
        e2 = record_payment(comm, Decimal('15000.00'), payment_mode='Bank Transfer', reference_no='TXN456')
        comm.refresh_from_db()
        self.assertEqual(comm.status, 'PAID')
        self.assertEqual(comm.balance, Decimal('0.00'))
        self.assertNotEqual(e1.receipt_no, e2.receipt_no)

    def test_waiver_and_reversal(self):
        applicant = Applicant.objects.create(
            full_name="Sanjay Gupta",
            email="sanjay@example.com",
            phone="9876543214",
            expected_salary="40000/month"
        )
        comm = ensure_commission_for_joined(applicant=applicant) # 20,000 due

        waive_commission(comm, reason="Management discount approved")
        comm.refresh_from_db()
        self.assertEqual(comm.status, 'WAIVED')
        self.assertEqual(comm.balance, Decimal('0.00'))


class StatusHelpersHookTestCase(TestCase):
    def test_set_applicant_status_joined_triggers_ledger(self):
        applicant = Applicant.objects.create(
            full_name="Amit Kumar",
            email="amit@example.com",
            phone="9876543215",
            expected_salary="6 LPA"
        )
        set_applicant_status(applicant, 'Joined', changed_by='admin')
        comm = PlacementCommission.objects.filter(applicant=applicant).first()
        self.assertIsNotNone(comm)
        self.assertEqual(comm.commission_amount, Decimal('25000.00'))

    def test_sync_ledger_management_command(self):
        Applicant.objects.create(
            full_name="Karan Johar",
            email="karan@example.com",
            phone="9876543216",
            status="Joined",
            expected_salary="5 LPA"
        )
        call_command('sync_ledger')
        self.assertTrue(PlacementCommission.objects.filter(candidate_name="Karan Johar").exists())


class AccessControlTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        role, _ = Role.objects.get_or_create(name='Super Admin', defaults={'is_super': True})
        self.admin = AdminUser.objects.create(
            email='admin@example.com',
            password_hash='pbkdf2_sha256$hashed',
            is_active=True,
            role=role
        )

        self.candidate = CandidateAccount.objects.create(
            full_name='Test Candidate',
            email='candidate@example.com',
            password_hash='pbkdf2_sha256$hashed',
            phone='9876543299'
        )

    def test_unauthenticated_and_candidate_access_blocked(self):
        urls = [
            '/admin-panel/ledger/',
            '/admin-panel/ledger/payments/',
            '/api/admin/ledger/',
            '/api/admin/ledger/payments/',
        ]

        # 1. Unauthenticated -> 302 redirect / 401 / 403
        for u in urls:
            res = self.client.get(u)
            self.assertIn(res.status_code, [302, 401, 403])

        # 2. Candidate session -> 302 redirect / 401 / 403
        s = self.client.session
        s['candidate_id'] = self.candidate.id
        s.save()

        for u in urls:
            res = self.client.get(u)
            self.assertIn(res.status_code, [302, 401, 403])

    def test_admin_access_allowed(self):
        s = self.client.session
        s['admin_id'] = self.admin.id
        s['admin_username'] = 'Super Admin'
        s.save()

        res = self.client.get('/admin-panel/ledger/')
        self.assertEqual(res.status_code, 200)
        self.assertIn('Ledger', res.content.decode('utf-8'))

        res_p = self.client.get('/admin-panel/ledger/payments/')
        self.assertEqual(res_p.status_code, 200)
        self.assertIn('Payments', res_p.content.decode('utf-8'))


class CSRFProtectionTestCase(TestCase):
    def setUp(self):
        self.client = Client(enforce_csrf_checks=True)
        self.admin = AdminUser.objects.create(
            email='admin_csrf@example.com',
            password_hash='pbkdf2_sha256$hashed',
            is_active=True
        )
        s = self.client.session
        s['admin_id'] = self.admin.id
        s.save()

        self.comm = PlacementCommission.objects.create(
            candidate_name="CSRF Test",
            company_name="Company CSRF",
            first_month_salary=Decimal('50000.00'),
            commission_percent=Decimal('50.00'),
            commission_amount=Decimal('25000.00'),
            status='PENDING'
        )
        LedgerEntry.objects.create(
            commission=self.comm,
            entry_type='DEBIT',
            amount=Decimal('25000.00'),
            running_balance=Decimal('25000.00')
        )

    def test_post_without_csrf_token_rejected_403(self):
        res = self.client.post(
            f'/api/admin/ledger/{self.comm.id}/payment/',
            {'amount': '10000.00'}
        )
        self.assertEqual(res.status_code, 403)


class NavigationAndReportsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        role, _ = Role.objects.get_or_create(name='Super Admin', defaults={'is_super': True})
        self.admin = AdminUser.objects.create(
            email='admin_nav@example.com',
            password_hash='pbkdf2_sha256$hashed',
            is_active=True,
            role=role
        )
        s = self.client.session
        s['admin_id'] = self.admin.id
        s.save()

    def test_sidebar_renders_ledger_and_reports_company_loads(self):
        res = self.client.get('/admin-panel/ledger/')
        self.assertEqual(res.status_code, 200)
        html = res.content.decode('utf-8')
        self.assertIn('Ledger', html)
        self.assertNotIn('Subscriptions', html)

        # /admin-panel/reports/company/ must still load cleanly
        res_rep = self.client.get('/admin-panel/reports/company/')
        self.assertEqual(res_rep.status_code, 200)
