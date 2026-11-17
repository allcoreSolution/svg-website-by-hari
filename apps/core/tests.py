import json
from django.test import TestCase, Client
from django.contrib.auth.hashers import make_password
from apps.accounts.models import AdminUser, CandidateAccount, EmployerAccount
from apps.jobs.models import Job
from apps.companies.models import Company


class CSRFEnforcementTestCase(TestCase):
    """
    Validates CSRF enforcement across key platform endpoints.
    Uses Client(enforce_csrf_checks=True) to guarantee:
    1. POST without a CSRF token is rejected with HTTP 403.
    2. POST with a valid CSRF token is accepted.
    """

    def setUp(self):
        # Create approved Candidate
        self.candidate_password = "SecretPassword123!"
        self.candidate = CandidateAccount.objects.create(
            full_name="CSRF Candidate",
            email="csrf_cand@example.com",
            phone="9876500001",
            is_approved=True,
            approval_status="approved"
        )
        self.candidate.set_password(self.candidate_password)
        self.candidate.save()

        # Create Company & Employer
        self.company = Company.objects.create(
            name="CSRF Tech Ltd",
            email="hr@csrftech.com",
            phone="9876500002",
            status="Active"
        )
        self.employer_password = "EmployerPass123!"
        self.employer = EmployerAccount.objects.create(
            company=self.company,
            company_name="CSRF Tech Ltd",
            contact_name="CSRF Employer",
            email="csrf_emp@example.com",
            phone="9876500002",
            status="APPROVED"
        )
        self.employer.set_password(self.employer_password)
        self.employer.save()

        # Create active Job
        self.job = Job.objects.create(
            company=self.company,
            employer=self.employer,
            title="Software Engineer",
            category="IT",
            department="Engineering",
            location="Lucknow",
            employment_type="Full Time",
            vacancies="2",
            status="LIVE"
        )

        # Create Admin
        self.admin_password = "AdminPass123!"
        self.admin = AdminUser.objects.create(
            email="csrf_admin@example.com",
            is_active=True
        )
        self.admin.set_password(self.admin_password)
        self.admin.save()

    def test_01_candidate_login_csrf_protection(self):
        """Candidate login POST without CSRF token must be 403; with token must succeed."""
        client = Client(enforce_csrf_checks=True)

        # 1. Without CSRF token -> Rejected (403)
        res_no_csrf = client.post('/candidate/login/', {
            'email': self.candidate.email,
            'password': self.candidate_password
        })
        self.assertEqual(res_no_csrf.status_code, 403)

        # 2. Obtain CSRF cookie
        get_res = client.get('/candidate/login/')
        csrf_token = client.cookies['csrftoken'].value

        # 3. With CSRF token -> Accepted (302 to candidate dashboard)
        res_with_csrf = client.post('/candidate/login/', {
            'csrfmiddlewaretoken': csrf_token,
            'email': self.candidate.email,
            'password': self.candidate_password
        })
        self.assertIn(res_with_csrf.status_code, [200, 302])
        if res_with_csrf.status_code == 302:
            self.assertEqual(res_with_csrf['Location'], '/candidate/dashboard/')

    def test_02_candidate_apply_csrf_protection(self):
        """Candidate job apply POST without CSRF token must be 403; with token must succeed."""
        client = Client(enforce_csrf_checks=True)

        # 1. Without CSRF token -> Rejected (403)
        res_no_csrf = client.post('/api/apply/', {
            'job_id': self.job.id,
            'full_name': self.candidate.full_name,
            'email': self.candidate.email,
            'phone': self.candidate.phone,
        })
        self.assertEqual(res_no_csrf.status_code, 403)

        # Log in candidate
        session = client.session
        session['candidate_id'] = self.candidate.id
        session['candidate_email'] = self.candidate.email
        session.save()

        # 2. Obtain CSRF cookie
        client.get('/jobs/')
        csrf_token = client.cookies['csrftoken'].value

        # 3. With CSRF token -> Accepted (200 success)
        res_with_csrf = client.post('/api/apply/', {
            'csrfmiddlewaretoken': csrf_token,
            'job_id': self.job.id,
            'full_name': self.candidate.full_name,
            'email': self.candidate.email,
            'phone': self.candidate.phone,
        }, HTTP_X_CSRFTOKEN=csrf_token)
        self.assertEqual(res_with_csrf.status_code, 200)
        self.assertEqual(res_with_csrf.json().get('status'), 'success')

    def test_03_employer_job_create_csrf_protection(self):
        """Employer job creation POST without CSRF token must be 403; with token must succeed."""
        client = Client(enforce_csrf_checks=True)

        # Log in employer
        session = client.session
        session['employer_id'] = self.employer.id
        session.save()

        # 1. Without CSRF token -> Rejected (403)
        res_no_csrf = client.post('/employer/jobs/new/', {
            'title': 'New React Developer',
            'department': 'Technology',
            'category': 'IT',
            'employment_type': 'Full Time',
            'location': 'Lucknow',
            'vacancies': '1',
            'experience': '1 Year',
            'salary': '30000',
            'description': 'React developer role',
            'requirements': 'React, JS',
            'deadline': '2026-12-31'
        })
        self.assertEqual(res_no_csrf.status_code, 403)

        # 2. Obtain CSRF cookie
        client.get('/employer/jobs/new/')
        csrf_token = client.cookies['csrftoken'].value

        # 3. With CSRF token -> Accepted (302 redirect to /employer/jobs/)
        res_with_csrf = client.post('/employer/jobs/new/', {
            'csrfmiddlewaretoken': csrf_token,
            'title': 'New React Developer',
            'department': 'Technology',
            'category': 'IT',
            'employment_type': 'Full Time',
            'location': 'Lucknow',
            'vacancies': '1',
            'experience': '1 Year',
            'salary': '30000',
            'description': 'React developer role',
            'requirements': 'React, JS',
            'deadline': '2026-12-31'
        })
        self.assertEqual(res_with_csrf.status_code, 302)
        self.assertEqual(res_with_csrf['Location'], '/employer/jobs/')

    def test_04_admin_login_csrf_protection(self):
        """Admin login POST without CSRF token must be 403; with token must succeed."""
        client = Client(enforce_csrf_checks=True)

        # 1. Without CSRF token -> Rejected (403)
        res_no_csrf = client.post('/api/admin/login/', {
            'email': self.admin.email,
            'password': self.admin_password
        })
        self.assertEqual(res_no_csrf.status_code, 403)

        # 2. Obtain CSRF cookie
        client.get('/admin-panel/login/')
        csrf_token = client.cookies['csrftoken'].value

        # 3. With CSRF token in HTTP_X_CSRFTOKEN header -> Accepted (200 success)
        res_with_csrf = client.post(
            '/api/admin/login/',
            data=json.dumps({
                'email': self.admin.email,
                'password': self.admin_password
            }),
            content_type='application/json',
            HTTP_X_CSRFTOKEN=csrf_token
        )
        self.assertEqual(res_with_csrf.status_code, 200)
        self.assertEqual(res_with_csrf.json().get('status'), 'success')

    def test_05_contact_form_csrf_protection(self):
        """Contact enquiry POST without CSRF token must be 403; with token must succeed."""
        client = Client(enforce_csrf_checks=True)

        payload = {
            'full_name': 'Test Contact User',
            'email': 'contact_user@example.com',
            'phone': '9876543210',
            'service': 'Recruitment',
            'message': 'Hello, I have an enquiry regarding staffing services.'
        }

        # 1. Without CSRF token -> Rejected (403)
        res_no_csrf = client.post(
            '/api/contact/',
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(res_no_csrf.status_code, 403)

        # 2. Obtain CSRF cookie from public contact page
        client.get('/contact/')
        csrf_token = client.cookies['csrftoken'].value

        # 3. With CSRF token in header -> Accepted (200 success)
        res_with_csrf = client.post(
            '/api/contact/',
            data=json.dumps(payload),
            content_type='application/json',
            HTTP_X_CSRFTOKEN=csrf_token
        )
        self.assertEqual(res_with_csrf.status_code, 200)
        self.assertEqual(res_with_csrf.json().get('status'), 'success')


class HeaderFooterDynamicTestCase(TestCase):
    """
    Test suite for dynamic database-driven Header, Navbar & Footer functionality:
    1. Admin saves settings -> immediately visible on public website (cache invalidated).
    2. Non-admin is blocked / redirected from /admin-panel/website/header-footer/.
    3. Invalid inputs (bad email, javascript: scheme) are rejected with validation errors.
    4. Empty optional fields render gracefully without page crashes.
    """

    def setUp(self):
        from apps.core.models import SiteSettings, NavItem, FooterColumn, SocialLink, FooterService
        from apps.accounts.models import AdminUser

        # Create active Admin user
        self.admin = AdminUser.objects.create(
            email="superadmin@skyvisiongoc.com",
            is_active=True
        )
        self.admin.set_password("AdminPass2026!")
        self.admin.save()

        # Seed initial site settings
        self.site = SiteSettings.get_settings()
        self.site.helpline_phone = "+91 88531 11111"
        self.site.support_email = "info@skyvisiongroup.in"
        self.site.announcement_text = "Default Seed Announcement"
        self.site.show_announcement = True
        self.site.save()

        # Create authenticated client
        self.client = Client()
        session = self.client.session
        session['admin_id'] = self.admin.id
        session.save()

    def test_01_admin_saves_header_footer_reflects_on_public_pages(self):
        """When admin saves changes via POST, public pages immediately show updated data."""
        nav_data = [
            {
                'label': 'Dynamic Careers',
                'url': '/careers/',
                'active_key': 'careers',
                'order': 1,
                'is_visible': True,
                'new_tab': False,
                'parent_idx': None
            },
            {
                'label': 'Job Openings',
                'url': '/jobs/',
                'active_key': 'jobs',
                'order': 2,
                'is_visible': True,
                'new_tab': False,
                'parent_idx': 0  # Child of Dynamic Careers
            }
        ]

        footer_cols = [
            {
                'title': 'Explore Links',
                'is_visible': True,
                'links': [
                    {'label': 'Leadership Team', 'url': '/team/', 'is_visible': True, 'new_tab': False}
                ]
            }
        ]

        footer_services = [
            {'name': 'Executive Search 2026', 'url': '/services/executive-search/', 'is_visible': True}
        ]

        post_data = {
            'helpline_phone': '+91 99999 88888',
            'secondary_phone': '+91 88888 77777',
            'support_email': 'care@skyvisiongoc.com',
            'topbar_address': 'Gomti Nagar Head Office, Lucknow',
            'topbar_hours': 'Mon – Sat, 9 AM – 7 PM',
            'announcement_text': '⚡ Massive IT & Banking Placement Drive Active!',
            'show_announcement': 'on',
            'show_franchise_btn': 'on',
            'franchise_url': '/contact/',
            'site_name': 'Sky Vision Elite Consultancy',
            'tagline': 'Connecting Brilliance with Opportunity.',
            'logo_alt_text': 'Sky Vision Elite Logo',
            'navbar_call_text': '+91 99999 88888',
            'navbar_call_number': '+919999988888',
            'show_login_btn': 'on',
            'footer_about': 'Custom tailored executive placement solutions across India.',
            'copyright_text': '© 2026 Sky Vision Elite. All rights reserved.',
            'footer_credit': 'Designed with excellence',
            'privacy_policy_url': '/privacy/',
            'terms_url': '/terms/',
            'social_url_facebook': 'https://facebook.com/skyvisionelite',
            'social_enabled_facebook': 'on',
            'office_address': 'Vibhuti Khand, Gomti Nagar, Lucknow',
            'office_phone_1': '+91 99999 88888',
            'office_phone_2': '+91 88888 77777',
            'office_email': 'care@skyvisiongoc.com',
            'working_hours': 'Mon – Sat: 9:00 AM – 7:00 PM',
            'floating_call_number': '+919999988888',
            'floating_whatsapp_url': 'https://whatsapp.com/channel/skyvision',
            'show_floating_buttons': 'on',
            'nav_items_json': json.dumps(nav_data),
            'footer_cols_json': json.dumps(footer_cols),
            'footer_services_json': json.dumps(footer_services),
        }

        # 1. Admin saves settings
        response = self.client.post('/admin-panel/website/header-footer/', data=post_data)
        self.assertEqual(response.status_code, 302)

        # 2. Verify database records
        from apps.core.models import SiteSettings, NavItem, FooterColumn, SocialLink, FooterService
        site = SiteSettings.get_settings()
        self.assertEqual(site.helpline_phone, '+91 99999 88888')
        self.assertEqual(site.support_email, 'care@skyvisiongoc.com')
        self.assertEqual(site.announcement_text, '⚡ Massive IT & Banking Placement Drive Active!')
        self.assertEqual(NavItem.objects.filter(label='Dynamic Careers').count(), 1)
        self.assertEqual(FooterService.objects.filter(name='Executive Search 2026').count(), 1)

        # 3. Public Home Page should reflect new phone, email, announcement, menu, and footer
        public_client = Client()
        home_res = public_client.get('/')
        self.assertEqual(home_res.status_code, 200)
        self.assertContains(home_res, '+91 99999 88888')
        self.assertContains(home_res, 'care@skyvisiongoc.com')
        self.assertContains(home_res, '⚡ Massive IT &amp; Banking Placement Drive Active!')
        self.assertContains(home_res, 'Dynamic Careers')
        self.assertContains(home_res, 'Executive Search 2026')
        self.assertContains(home_res, 'Explore Links')

    def test_02_non_admin_forbidden_or_redirected(self):
        """Unauthenticated or non-admin user cannot access website management."""
        anon_client = Client()

        # GET request should redirect to admin login
        get_res = anon_client.get('/admin-panel/website/header-footer/')
        self.assertEqual(get_res.status_code, 302)
        self.assertIn('/admin-panel/login/', get_res['Location'])

        # POST request should also redirect
        post_res = anon_client.post('/admin-panel/website/header-footer/', data={'helpline_phone': '123456'})
        self.assertEqual(post_res.status_code, 302)
        self.assertIn('/admin-panel/login/', post_res['Location'])

    def test_03_invalid_inputs_rejected(self):
        """Invalid emails or javascript: URLs are rejected with validation errors."""
        post_data = {
            'helpline_phone': 'NotAPhoneNumber',
            'support_email': 'invalid-email-address',
            'franchise_url': 'javascript:alert(1)',
        }
        res = self.client.post('/admin-panel/website/header-footer/', data=post_data, follow=True)
        # Should stay on page and show error messages
        self.assertEqual(res.status_code, 200)
        messages_text = [m.message for m in res.context['messages']] if 'messages' in res.context else []
        self.assertTrue(any('Email' in m for m in messages_text) or any('telephone' in m for m in messages_text))

    def test_04_empty_fields_render_gracefully_without_crash(self):
        """Optional empty fields do not cause template or 500 crashes on public pages."""
        from apps.core.models import SiteSettings, NavItem, FooterColumn, SocialLink, FooterService
        site = SiteSettings.get_settings()
        site.announcement_text = ""
        site.show_announcement = False
        site.secondary_phone = ""
        site.footer_about = ""
        site.save()

        # Disable social links
        SocialLink.objects.update(is_enabled=False)

        public_client = Client()
        for path in ['/', '/about/', '/services/', '/contact/']:
            res = public_client.get(path)
            self.assertEqual(res.status_code, 200)


class HomePageDynamicTestCase(TestCase):
    """
    Test suite for dynamic database-driven Home Page functionality:
    1. Admin saves changes -> immediately visible on public home page (cache invalidated).
    2. Item delete/hide -> hidden from public home page.
    3. Section toggle off -> entire section is hidden from public home page.
    4. Non-admin is blocked / redirected from /admin-panel/website/home/.
    5. Invalid URLs (javascript: scheme) and invalid images are rejected with validation errors.
    6. Empty database renders gracefully without 500 crashes.
    7. Featured Candidate privacy: only candidates with show_publicly=True are shown;
       no private email, phone, or resume is ever exposed in HTML.
    8. Cache invalidation on save/update works as expected.
    """

    def setUp(self):
        from apps.core.models import (
            HomePageSettings,
            HeroStat,
            GrowthStep,
            HomeServiceCard,
            WhyChooseItem,
            HomeIndustryItem,
            InternshipCard,
            InternshipHighlight,
            FeaturedCandidate,
            GalleryImage,
            GalleryInfoBox,
        )
        from apps.accounts.models import AdminUser

        # Create active Admin user
        self.admin = AdminUser.objects.create(
            email="home_superadmin@skyvisiongoc.com",
            is_active=True
        )
        self.admin.set_password("AdminPass2026!")
        self.admin.save()

        # Seed initial home page settings
        self.home = HomePageSettings.get_settings()
        self.home.hero_title = "Connecting Skilled Talent with Leading Corporate Enterprises"
        self.home.save()

        # Create authenticated client
        self.client = Client()
        session = self.client.session
        session['admin_id'] = self.admin.id
        session.save()

    def test_01_admin_saves_home_page_reflects_on_public_home(self):
        """When admin saves home page settings via POST, changes immediately appear on public home."""
        from apps.core.models import HomePageSettings, HeroStat, HomeServiceCard, WhyChooseItem

        hero_stats = [
            {'icon_class': 'fa-solid fa-trophy', 'value': '15000+', 'label': 'Corporate Placements', 'order': 1, 'is_visible': True}
        ]
        service_cards = [
            {
                'title': 'AI Recruitment Solutions',
                'icon_class': 'fa-solid fa-robot',
                'icon_color': 'cyan',
                'bullets': 'Automated talent matching\n24/7 Screening',
                'link_url': '/services/',
                'link_text': 'Discover More',
                'order': 1,
                'is_visible': True
            }
        ]
        why_choose = [
            {
                'title': '99.5% Placement Guarantee',
                'icon_class': 'fa-solid fa-shield-halved',
                'description': 'Trusted by 500+ top enterprises.',
                'order': 1,
                'is_visible': True
            }
        ]

        post_data = {
            'hero_visible': 'on',
            'hero_title': 'Connecting Elite Talent with Global Enterprises',
            'hero_title_highlight': 'Global Enterprises',
            'hero_subtitle': 'Revolutionizing human capital consultancy with precision staffing.',
            'hero_cta_primary_label': 'Start Career Now',
            'hero_cta_primary_url': '/jobs/',
            'hero_cta_primary_visible': 'on',
            'hero_cta_secondary_label': 'Hire Top Talent',
            'hero_cta_secondary_url': '/employer/hire-talent/',
            'hero_cta_secondary_visible': 'on',
            'services_visible': 'on',
            'services_tag': 'Our Expertise',
            'services_title': 'Pioneering Staffing & Placement Services',
            'services_subtitle': 'Comprehensive workforce solutions for modern enterprises.',
            'about_visible': 'on',
            'about_tag': 'About Sky Vision',
            'about_heading': 'Transforming Careers & Corporate Staffing',
            'about_heading_highlight': 'Corporate Staffing',
            'about_badge_text': 'Decade of Placement Leadership',
            'why_choose_visible': 'on',
            'why_choose_tag': 'Why Choose Us',
            'why_choose_title': 'Delivering Precision Across Every Hire',
            'hero_stats_json': json.dumps(hero_stats),
            'service_cards_json': json.dumps(service_cards),
            'why_choose_json': json.dumps(why_choose),
        }

        # 1. Admin saves settings
        response = self.client.post('/admin-panel/website/home/', data=post_data, follow=True)
        self.assertEqual(response.status_code, 200)

        # 2. Public Home Page should reflect new headline, stat, service, and why-choose
        public_client = Client()
        res = public_client.get('/')
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, 'Connecting Elite Talent with')
        self.assertContains(res, '<span class="highlight">Global Enterprises</span>')
        self.assertContains(res, '15000+')
        self.assertContains(res, 'Corporate Placements')
        self.assertContains(res, 'AI Recruitment Solutions')
        self.assertContains(res, 'Automated talent matching')
        self.assertContains(res, 'Transforming Careers &amp;')
        self.assertContains(res, '<span>Corporate Staffing</span>')
        self.assertContains(res, '99.5% Placement Guarantee')

    def test_02_item_delete_or_hide_disappears_from_frontend(self):
        """Hidden or deleted items must immediately disappear from public home page."""
        from apps.core.models import HeroStat, HomeServiceCard
        from django.core.cache import cache

        # Create visible stat and hidden stat
        HeroStat.objects.all().delete()
        visible_stat = HeroStat.objects.create(
            icon_class='fa-solid fa-star',
            value='850+',
            label='Happy Clients',
            order=1,
            is_visible=True
        )
        hidden_stat = HeroStat.objects.create(
            icon_class='fa-solid fa-ghost',
            value='9999+',
            label='Secret Stat Hidden',
            order=2,
            is_visible=False
        )

        HomeServiceCard.objects.all().delete()
        visible_service = HomeServiceCard.objects.create(
            title='Visible Tech Staffing',
            bullets='Top engineers',
            order=1,
            is_visible=True
        )
        hidden_service = HomeServiceCard.objects.create(
            title='Hidden Secret Service',
            bullets='Invisible',
            order=2,
            is_visible=False
        )

        # Clear cache to simulate instant update
        cache.delete('home_page_context')

        public_client = Client()
        res = public_client.get('/')
        self.assertEqual(res.status_code, 200)

        # Visible items are present
        self.assertContains(res, 'Happy Clients')
        self.assertContains(res, '850+')
        self.assertContains(res, 'Visible Tech Staffing')

        # Hidden items are NOT present
        self.assertNotContains(res, 'Secret Stat Hidden')
        self.assertNotContains(res, 'Hidden Secret Service')

    def test_03_section_toggle_off_hides_entire_section(self):
        """Toggling a section off hides the entire section container gracefully."""
        from apps.core.models import HomePageSettings
        from django.core.cache import cache

        home = HomePageSettings.get_settings()
        home.hero_visible = False
        home.services_visible = False
        home.why_choose_visible = False
        home.save()

        cache.delete('home_page_context')

        public_client = Client()
        res = public_client.get('/')
        self.assertEqual(res.status_code, 200)

        # Hero, Services, and Why Choose sections must not be rendered
        self.assertNotContains(res, '<section class="hero">')
        self.assertNotContains(res, '<section class="services-section">')
        self.assertNotContains(res, '<section class="why-section">')

        # Re-enabling displays them again
        home.hero_visible = True
        home.services_visible = True
        home.why_choose_visible = True
        home.save()
        cache.delete('home_page_context')

        res_after = public_client.get('/')
        self.assertEqual(res_after.status_code, 200)
        self.assertContains(res_after, '<section class="hero">')
        self.assertContains(res_after, '<section class="services-section">')

    def test_04_non_admin_forbidden_or_redirected(self):
        """Unauthenticated or non-admin requests to home page management are redirected to login."""
        anon_client = Client()

        # Both /admin-panel/website/home/ and /admin-panel/website/home-page/
        for url in ['/admin-panel/website/home/', '/admin-panel/website/home-page/']:
            get_res = anon_client.get(url)
            self.assertEqual(get_res.status_code, 302)
            self.assertIn('/admin-panel/login/', get_res['Location'])

            post_res = anon_client.post(url, data={'hero_title': 'Unauthorized Change'})
            self.assertEqual(post_res.status_code, 302)
            self.assertIn('/admin-panel/login/', post_res['Location'])

    def test_05_invalid_url_and_image_rejected(self):
        """Invalid javascript: URLs and malicious image formats are rejected."""
        from django.core.files.uploadedfile import SimpleUploadedFile

        # 1. Test javascript: URL scheme
        post_data = {
            'hero_cta_primary_url': 'javascript:alert("XSS")',
            'hero_title': 'Safe Title',
        }
        res = self.client.post('/admin-panel/website/home/', data=post_data, follow=True)
        self.assertEqual(res.status_code, 200)
        messages_text = [m.message for m in res.context['messages']] if 'messages' in res.context else []
        self.assertTrue(any('javascript:' in m for m in messages_text))

        # 2. Test invalid image (plain text fake image)
        fake_image = SimpleUploadedFile(
            name='exploit.png',
            content=b'NOT_A_VALID_IMAGE_DATA_12345',
            content_type='image/png'
        )
        res_img = self.client.post('/admin-panel/website/home/', data={'hero_image': fake_image}, follow=True)
        self.assertEqual(res_img.status_code, 200)
        img_messages = [m.message for m in res_img.context['messages']] if 'messages' in res_img.context else []
        self.assertTrue(any('valid or readable image' in m for m in img_messages))

    def test_06_empty_database_renders_gracefully_without_crash(self):
        """If all home records are deleted, the public home page must render HTTP 200 without crashing."""
        from apps.core.models import (
            HeroStat,
            GrowthStep,
            HomeServiceCard,
            WhyChooseItem,
            HomeIndustryItem,
            InternshipCard,
            InternshipHighlight,
            FeaturedCandidate,
            GalleryImage,
            GalleryInfoBox,
        )
        from django.core.cache import cache

        HeroStat.objects.all().delete()
        GrowthStep.objects.all().delete()
        HomeServiceCard.objects.all().delete()
        WhyChooseItem.objects.all().delete()
        HomeIndustryItem.objects.all().delete()
        InternshipCard.objects.all().delete()
        InternshipHighlight.objects.all().delete()
        FeaturedCandidate.objects.all().delete()
        GalleryImage.objects.all().delete()
        GalleryInfoBox.objects.all().delete()

        cache.delete('home_page_context')

        public_client = Client()
        res = public_client.get('/')
        self.assertEqual(res.status_code, 200)

    def test_07_featured_candidate_privacy_and_consent(self):
        """
        Guarantees candidate privacy:
        1. Only candidates with show_publicly=True and is_visible=True are displayed.
        2. Candidate's private phone, email, and resume are never leaked in the public HTML.
        """
        from apps.accounts.models import CandidateAccount
        from apps.core.models import FeaturedCandidate
        from django.core.cache import cache

        # Create CandidateAccount with sensitive personal info
        cand_account = CandidateAccount.objects.create(
            full_name="Rajesh Sharma",
            email="confidential_rajesh@secretmail.com",
            phone="9123456789",
            resume="resumes/confidential_resume_1234.pdf",
            is_approved=True
        )

        FeaturedCandidate.objects.all().delete()
        # Candidate 1: explicit consent given
        FeaturedCandidate.objects.create(
            name="Rajesh Sharma",
            role="Senior Python Lead",
            experience="5 Yrs Exp",
            company_placed="TCS Global",
            candidate_ref=cand_account,
            show_publicly=True,
            is_visible=True,
            order=1
        )

        # Candidate 2: NO consent (show_publicly=False)
        FeaturedCandidate.objects.create(
            name="Private Candidate Jane",
            role="Confidential Analyst",
            experience="2 Yrs Exp",
            show_publicly=False,
            is_visible=True,
            order=2
        )

        cache.delete('home_page_context')

        public_client = Client()
        res = public_client.get('/')
        self.assertEqual(res.status_code, 200)

        # Consented candidate is visible
        self.assertContains(res, 'Rajesh Sharma')
        self.assertContains(res, 'Senior Python Lead')
        self.assertContains(res, 'TCS Global')

        # Unconsented candidate is NOT visible
        self.assertNotContains(res, 'Private Candidate Jane')
        self.assertNotContains(res, 'Confidential Analyst')

        # PRIVATE fields must NEVER be leaked
        self.assertNotContains(res, 'confidential_rajesh@secretmail.com')
        self.assertNotContains(res, '9123456789')
        self.assertNotContains(res, 'confidential_resume_1234.pdf')

    def test_08_cache_invalidation_on_save(self):
        """Signals and save handlers must invalidate home_page_context cache immediately."""
        from apps.core.models import HomePageSettings, HeroStat
        from django.core.cache import cache

        cache.set('home_page_context', {'dummy': 'cached_value'})
        self.assertIsNotNone(cache.get('home_page_context'))

        # Saving HomePageSettings triggers post_save signal
        home = HomePageSettings.get_settings()
        home.hero_title = "Brand New Cache Title"
        home.save()

        # Cache must be purged
        self.assertIsNone(cache.get('home_page_context'))

        # Saving a repeatable item (HeroStat) also clears cache
        cache.set('home_page_context', {'dummy': 'cached_value_2'})
        stat = HeroStat.objects.create(value="100+", label="New Stat")
        self.assertIsNone(cache.get('home_page_context'))

    def test_09_home_service_cards_admin_crud_live_sync(self):
        """
        Verify that admin can Create, Edit, Reorder, Toggle, and Delete service cards
        via /admin-panel/website/home/ and they automatically reflect on the live home page ('/').
        """
        import json
        from apps.core.models import HomeServiceCard, HomePageSettings

        # Ensure section is visible
        home = HomePageSettings.get_settings()
        home.services_visible = True
        home.save()

        # Step 1: Create 2 new cards via Admin Panel POST
        cards_payload = [
            {
                "title": "Custom Manpower Solutions",
                "icon_class": "fas fa-users-gear",
                "icon_color": "blue",
                "bullets": "Skilled Engineers\nFactory Technicians",
                "link_url": "/services/manpower/",
                "link_text": "Explore Services",
                "order": 1,
                "is_visible": True,
            },
            {
                "title": "Executive Headhunting",
                "icon_class": "fas fa-user-tie",
                "icon_color": "red",
                "bullets": "C-Level Recruitment\nConfidential Search",
                "link_url": "/services/headhunting/",
                "link_text": "Learn More",
                "order": 2,
                "is_visible": True,
            },
        ]

        post_res = self.client.post('/admin-panel/website/home/', data={
            'service_cards_json': json.dumps(cards_payload),
            'services_visible': 'on',
            'services_title': 'Our Specialized Offerings',
        }, follow=True)
        self.assertEqual(post_res.status_code, 200)

        # Verify DB was populated
        self.assertEqual(HomeServiceCard.objects.count(), 2)
        c1 = HomeServiceCard.objects.get(order=1)
        self.assertEqual(c1.title, "Custom Manpower Solutions")
        self.assertEqual(c1.icon_class, "fas fa-users-gear")
        self.assertEqual(c1.icon_color, "blue")
        self.assertIn("Skilled Engineers", c1.get_bullet_list())

        # Step 2: Verify live homepage automatically displays the new cards
        public_client = Client()
        live_res = public_client.get('/')
        self.assertEqual(live_res.status_code, 200)
        self.assertContains(live_res, "Our Specialized Offerings")
        self.assertContains(live_res, "Custom Manpower Solutions")
        self.assertContains(live_res, "Skilled Engineers")
        self.assertContains(live_res, "Factory Technicians")
        self.assertContains(live_res, "Executive Headhunting")
        self.assertContains(live_res, "C-Level Recruitment")

        # Step 3: Edit one card, delete another, and add a 3rd (CRUD test)
        updated_payload = [
            {
                "title": "Custom Manpower Solutions (Updated)",
                "icon_class": "fas fa-hard-hat",
                "icon_color": "red",
                "bullets": "Offshore Staffing\nOnshore Staffing",
                "link_url": "/services/updated-manpower/",
                "link_text": "View Details",
                "order": 1,
                "is_visible": True,
            },
            {
                "title": "Third Brand New Card",
                "icon_class": "fas fa-briefcase",
                "icon_color": "blue",
                "bullets": "Placement Drive\nCampus Hiring",
                "link_url": "/services/campus/",
                "link_text": "Join Now",
                "order": 2,
                "is_visible": False,
            },
        ]

        post_res2 = self.client.post('/admin-panel/website/home/', data={
            'service_cards_json': json.dumps(updated_payload),
            'services_visible': 'on',
        }, follow=True)
        self.assertEqual(post_res2.status_code, 200)

        # Check DB
        self.assertEqual(HomeServiceCard.objects.count(), 2)
        # Old 'Executive Headhunting' was deleted
        self.assertFalse(HomeServiceCard.objects.filter(title="Executive Headhunting").exists())

        # Step 4: Verify live homepage automatically reflects the edit & delete
        live_res2 = public_client.get('/')
        self.assertEqual(live_res2.status_code, 200)
        # Updated card is visible
        self.assertContains(live_res2, "Custom Manpower Solutions (Updated)")
        self.assertContains(live_res2, "Offshore Staffing")
        # Deleted card is gone
        self.assertNotContains(live_res2, "Executive Headhunting")
        # Hidden card is not in public HTML
        self.assertNotContains(live_res2, "Third Brand New Card")

    def test_10_home_industries_admin_crud_live_sync(self):
        """
        Test Section 5: Industries We Serve CRUD in Admin & live synchronization:
        1. Admin creates multiple industry badges (IT, Healthcare, Manufacturing) via POST.
        2. Database HomeIndustryItem objects are saved and ordered correctly.
        3. Public homepage (/) immediately displays the new badges with custom icons and links.
        4. Admin updates an industry, deletes one, adds a new one, and toggles visibility.
        5. Public homepage immediately reflects the updated list and hides deleted/disabled items.
        """
        from apps.core.models import HomeIndustryItem

        HomeIndustryItem.objects.all().delete()

        # Step 1: Admin adds initial industries
        industries_payload = [
            {
                "name": "Information Technology & AI",
                "icon_class": "fas fa-laptop-code",
                "link_url": "/jobs/?industry=IT",
                "order": 1,
                "is_visible": True,
            },
            {
                "name": "Healthcare & Biotech",
                "icon_class": "fas fa-heartbeat",
                "link_url": "/jobs/?industry=Healthcare",
                "order": 2,
                "is_visible": True,
            },
            {
                "name": "Automobile & Manufacturing",
                "icon_class": "fas fa-industry",
                "link_url": "/jobs/?industry=Manufacturing",
                "order": 3,
                "is_visible": True,
            },
        ]

        post_res = self.client.post('/admin-panel/website/home/', data={
            'industries_items_json': json.dumps(industries_payload),
            'industries_visible': 'on',
            'industries_title': 'Sectors Where SVG Excels',
        }, follow=True)
        self.assertEqual(post_res.status_code, 200)

        # Verify DB records
        self.assertEqual(HomeIndustryItem.objects.count(), 3)
        ind1 = HomeIndustryItem.objects.get(order=1)
        self.assertEqual(ind1.name, "Information Technology & AI")
        self.assertEqual(ind1.icon_class, "fas fa-laptop-code")
        self.assertEqual(ind1.link_url, "/jobs/?industry=IT")
        self.assertTrue(ind1.is_visible)

        # Step 2: Verify live homepage displays the new badges
        public_client = Client()
        live_res = public_client.get('/')
        self.assertEqual(live_res.status_code, 200)
        self.assertContains(live_res, "Sectors Where SVG Excels")
        self.assertContains(live_res, "Information Technology &amp; AI")
        self.assertContains(live_res, "fas fa-laptop-code")
        self.assertContains(live_res, "Healthcare &amp; Biotech")
        self.assertContains(live_res, "fas fa-heartbeat")
        self.assertContains(live_res, "Automobile &amp; Manufacturing")

        # Step 3: Edit one industry, delete Healthcare, and add a hidden industry
        updated_payload = [
            {
                "name": "Information Technology & AI (Updated)",
                "icon_class": "fas fa-microchip",
                "link_url": "/jobs/?industry=IT-AI",
                "order": 1,
                "is_visible": True,
            },
            {
                "name": "Automobile & Manufacturing",
                "icon_class": "fas fa-industry",
                "link_url": "/jobs/?industry=Manufacturing",
                "order": 2,
                "is_visible": True,
            },
            {
                "name": "Secret Drone Technology",
                "icon_class": "fas fa-plane",
                "link_url": "/jobs/?industry=Drones",
                "order": 3,
                "is_visible": False,  # Hidden
            },
        ]

        post_res2 = self.client.post('/admin-panel/website/home/', data={
            'industries_items_json': json.dumps(updated_payload),
            'industries_visible': 'on',
        }, follow=True)
        self.assertEqual(post_res2.status_code, 200)

        # Check DB
        self.assertEqual(HomeIndustryItem.objects.count(), 3)
        self.assertFalse(HomeIndustryItem.objects.filter(name="Healthcare & Biotech").exists())

        # Step 4: Verify live homepage immediately reflects edit, deletion, and hidden status
        live_res2 = public_client.get('/')
        self.assertEqual(live_res2.status_code, 200)
        self.assertContains(live_res2, "Information Technology &amp; AI (Updated)")
        self.assertContains(live_res2, "fas fa-microchip")
        self.assertNotContains(live_res2, "Healthcare &amp; Biotech")
        self.assertNotContains(live_res2, "Secret Drone Technology")

    def test_11_gallery_image_upload_and_live_sync(self):
        """
        Comprehensive test for Gallery Image management:
        1. Non-admin is blocked from /api/admin/website/upload-image/ (403 or redirect).
        2. Admin uploads a real image file -> 200 success with media URL.
        3. Admin saves gallery images list -> GalleryImage objects created with proper URLs.
        4. Public homepage displays the gallery items with their captions, categories, and images.
        5. Editing and deleting items in gallery instantly updates DB and invalidates cache on live site.
        """
        from io import BytesIO
        from django.core.files.uploadedfile import SimpleUploadedFile
        from PIL import Image
        from apps.core.models import GalleryImage

        # 1. Non-admin client is denied
        non_admin_client = Client()
        fake_file = SimpleUploadedFile("test.png", b"fake image content", content_type="image/png")
        denied_res = non_admin_client.post('/api/admin/website/upload-image/', {'image': fake_file})
        self.assertIn(denied_res.status_code, [302, 401, 403])

        # 2. Admin client uploads a valid test image
        img_buffer = BytesIO()
        img = Image.new('RGB', (100, 100), color=(73, 109, 137))
        img.save(img_buffer, format='PNG')
        img_buffer.seek(0)
        uploaded_file = SimpleUploadedFile("placement_test.png", img_buffer.getvalue(), content_type="image/png")

        upload_res = self.client.post('/api/admin/website/upload-image/', {'image': uploaded_file})
        self.assertEqual(upload_res.status_code, 200)
        upload_data = upload_res.json()
        self.assertEqual(upload_data.get('status'), 'success')
        uploaded_url = upload_data.get('image_url')
        self.assertTrue(uploaded_url.startswith('/media/gallery/'))

        # 3. Save gallery images with both uploaded image and static preset
        gallery_payload = [
            {
                "title": "Mega Placement Drive 2026",
                "static_image_path": uploaded_url,
                "category": "Placements",
                "show_on_home": True,
                "is_visible": True,
                "order": 1,
            },
            {
                "title": "AI & Robotics Workshop",
                "static_image_path": "images/general/workshop.png",
                "category": "Workshops",
                "show_on_home": True,
                "is_visible": True,
                "order": 2,
            },
            {
                "title": "Confidential Internal Review",
                "static_image_path": "images/general/interview round.png",
                "category": "Interviews",
                "show_on_home": False,  # Not on home
                "is_visible": True,
                "order": 3,
            }
        ]

        post_res = self.client.post('/admin-panel/website/home/', data={
            'gallery_images_json': json.dumps(gallery_payload),
            'gallery_visible': 'on',
            'gallery_title': 'Life & Moments at SVG',
        }, follow=True)
        self.assertEqual(post_res.status_code, 200)

        # Verify DB records
        self.assertEqual(GalleryImage.objects.count(), 3)
        g1 = GalleryImage.objects.get(order=1)
        self.assertEqual(g1.title, "Mega Placement Drive 2026")
        self.assertEqual(g1.category, "Placements")
        self.assertEqual(g1.get_image_url(), uploaded_url)

        # 4. Check live homepage
        public_client = Client()
        home_res = public_client.get('/')
        self.assertEqual(home_res.status_code, 200)
        self.assertContains(home_res, "Life &amp; Moments at SVG")
        self.assertContains(home_res, "Mega Placement Drive 2026")
        self.assertContains(home_res, uploaded_url)
        self.assertContains(home_res, "AI &amp; Robotics Workshop")
        # Hidden from home should not appear
        self.assertNotContains(home_res, "Confidential Internal Review")


class AboutPagesDynamicTestCase(TestCase):
    """
    Comprehensive test case validating dynamic functionality across all 4 About Us sub-pages:
    1. About Company (/about/ or /about/company/)
    2. CEO & Founder (/about/ceo/)
    3. Our Team (/about/team/)
    4. Journey (/about/journey/)
    
    Validates:
    - Admin sub-page dropdown switcher & quick-tabs on /admin-panel/website/about/
    - Admin POST updates for each of the 4 sub-pages
    - Live public website reflection & dynamic rendering
    - Automatic seeding when database is empty
    - Immediate cache invalidation on save
    """

    def setUp(self):
        from apps.accounts.models import AdminUser
        from django.core.cache import cache
        cache.clear()

        # Create active Admin user
        self.admin = AdminUser.objects.create(
            email="about_superadmin@skyvisiongoc.com",
            is_active=True
        )
        self.admin.set_password("AdminPass2026!")
        self.admin.save()

        # Create authenticated client
        self.client = Client()
        session = self.client.session
        session['admin_id'] = self.admin.id
        session.save()

    def test_01_public_pages_render_and_seed_defaults(self):
        """All 4 public pages should return HTTP 200 and automatically seed initial records."""
        from apps.core.models import (
            AboutCompanySettings,
            CEOMessageSettings,
            CEOLeadershipPrinciple,
            OurTeamSettings,
            TeamMember,
            OurJourneySettings,
            JourneyMilestone,
        )

        pub_client = Client()

        # 1. About Company
        res_comp = pub_client.get('/about/')
        self.assertEqual(res_comp.status_code, 200)
        self.assertContains(res_comp, "About Company of Sky Vision")
        self.assertTrue(AboutCompanySettings.objects.exists())

        # 2. CEO & Founder
        res_ceo = pub_client.get('/about/ceo/')
        self.assertEqual(res_ceo.status_code, 200)
        self.assertContains(res_ceo, "ASHVANI DUBEY")
        self.assertContains(res_ceo, "CEO &amp; FOUNDER")
        self.assertTrue(CEOMessageSettings.objects.exists())
        self.assertTrue(CEOLeadershipPrinciple.objects.count() >= 5)

        # 3. Our Team
        res_team = pub_client.get('/about/team/')
        self.assertEqual(res_team.status_code, 200)
        self.assertContains(res_team, "Meet Our Expert Team")
        self.assertContains(res_team, "Ashvani Dubey")
        self.assertTrue(OurTeamSettings.objects.exists())
        self.assertTrue(TeamMember.objects.count() >= 8)

        # 4. Journey
        res_journey = pub_client.get('/about/journey/')
        self.assertEqual(res_journey.status_code, 200)
        self.assertContains(res_journey, "Our Journey")
        self.assertContains(res_journey, "Growing Together")
        self.assertTrue(OurJourneySettings.objects.exists())
        self.assertTrue(JourneyMilestone.objects.count() >= 5)

    def test_02_admin_panel_renders_all_4_subpages_with_selector(self):
        """Admin website management 'about' module renders selector and all 4 subpage views."""
        # 1. Company View
        res_comp = self.client.get('/admin-panel/website/about/?page=company')
        self.assertEqual(res_comp.status_code, 200)
        self.assertContains(res_comp, 'id="aboutSubPageSelector"')
        self.assertContains(res_comp, 'value="company" selected')
        self.assertContains(res_comp, 'About Company Profile Content')

        # 2. CEO View
        res_ceo = self.client.get('/admin-panel/website/about/?page=ceo')
        self.assertEqual(res_ceo.status_code, 200)
        self.assertContains(res_ceo, 'value="ceo" selected')
        self.assertContains(res_ceo, 'CEO &amp; Founder Message Management')
        self.assertContains(res_ceo, 'principles_json')

        # 3. Team View
        res_team = self.client.get('/admin-panel/website/about/?page=team')
        self.assertEqual(res_team.status_code, 200)
        self.assertContains(res_team, 'value="team" selected')
        self.assertContains(res_team, 'Our Leadership &amp; Team Management')
        self.assertContains(res_team, 'team_members_json')

        # 4. Journey View
        res_journey = self.client.get('/admin-panel/website/about/?page=journey')
        self.assertEqual(res_journey.status_code, 200)
        self.assertContains(res_journey, 'value="journey" selected')
        self.assertContains(res_journey, 'Our Journey &amp; Growth Timeline Management')
        self.assertContains(res_journey, 'milestones_json')

        # 5. Legacy team-ceo route redirects to ?page=ceo
        res_redir = self.client.get('/admin-panel/website/team-ceo/')
        self.assertEqual(res_redir.status_code, 302)
        self.assertIn('/admin-panel/website/about/?page=ceo', res_redir['Location'])

    def test_03_admin_save_company_profile_reflects_on_live_site(self):
        """Saving company profile form updates DB and immediately updates /about/."""
        from apps.core.models import AboutCompanySettings

        post_data = {
            'about_subpage': 'company',
            'page_title': 'Global Corporate Capabilities - Sky Vision Group',
            'page_eyebrow': 'Discover Our Impact',
            'experience_badge': 'Elite Partner Since 2014',
            'visual_heading': 'Over 8 Decades of Collective HR Expertise',
            'visual_subtext': 'Transforming modern workforces across Fortune 500 companies.',
            'welcome_tag': 'Corporate Excellence',
            'welcome_heading': 'Leading The Next Generation of Workforce Solutions',
            'welcome_p1': 'Dynamic recruitment customized to enterprise velocity.',
            'welcome_p2': 'Scalable manpower architecture backed by trusted domain heads.',
            'vision_title': 'Strategic Vision 2030',
            'vision_text': 'To lead India in ethical high-velocity placement solutions.',
            'mission_title': 'Our Core Mandate',
            'mission_text': 'Connecting aspirations with enterprise opportunities seamlessly.',
            'stat_1_count': '15+',
            'stat_1_label': 'Years of Excellence',
            'stat_2_count': '10,000+',
            'stat_2_label': 'Successful Placements',
            'stat_3_count': '450+',
            'stat_3_label': 'Corporate Clients',
            'stat_4_count': '99.9%',
            'stat_4_label': 'Client Retention',
            'why_tag': 'Why Choose Us',
            'why_heading': 'Pioneering Transparent Staffing Solutions',
            'why_subtext': 'Precision vetting, rapid deployment, and verified credentials.',
        }

        save_res = self.client.post('/admin-panel/website/about/?page=company', data=post_data, follow=True)
        self.assertEqual(save_res.status_code, 200)

        # Verify DB
        settings = AboutCompanySettings.get_settings()
        self.assertEqual(settings.page_title, 'Global Corporate Capabilities - Sky Vision Group')
        self.assertEqual(settings.stat_1_count, '15+')
        self.assertEqual(settings.stat_2_count, '10,000+')

        # Verify Live Website
        pub_res = Client().get('/about/')
        self.assertEqual(pub_res.status_code, 200)
        self.assertContains(pub_res, 'Global Corporate Capabilities - Sky Vision Group')
        self.assertContains(pub_res, '15+')
        self.assertContains(pub_res, '10,000+')
        self.assertContains(pub_res, 'Leading The Next Generation of Workforce Solutions')

    def test_04_admin_save_ceo_message_reflects_on_live_site(self):
        """Saving CEO message & principles updates DB and immediately updates /about/ceo/."""
        from apps.core.models import CEOMessageSettings, CEOLeadershipPrinciple

        custom_principles = [
            {
                'title': 'Radical Transparency',
                'description': 'Honest candidate evaluations and clear expectations for clients.',
                'icon_class': 'fa-solid fa-eye',
                'order': 1,
                'is_visible': True
            },
            {
                'title': 'Continuous Innovation',
                'description': 'Leveraging modern AI-assisted screening to reduce time-to-hire.',
                'icon_class': 'fa-solid fa-bolt',
                'order': 2,
                'is_visible': True
            }
        ]

        post_data = {
            'about_subpage': 'ceo',
            'ceo_name': 'DR. ASHVANI DUBEY (HON)',
            'ceo_role': 'FOUNDER & CHIEF EXECUTIVE OFFICER',
            'ceo_org': 'Sky Vision Global Corporate Group',
            'title_eyebrow': 'EXECUTIVE ADDRESS',
            'title_main': 'LEADERSHIP HORIZONS',
            'message_p1': 'Recruitment is fundamentally about catalyzing human potential.',
            'message_p2': 'We partner with enterprises to turn workforce hurdles into competitive advantages.',
            'message_p3': 'Ethics and relentless quality define each milestone in our corporate journey.',
            'message_p4': 'Thank you for placing your trust in Sky Vision.',
            'quote_text': 'Empowering professionals creates generational impact across industries.',
            'vision_text': 'To redefine global consultancy with integrity and technological speed.',
            'mission_text': 'Empowering enterprises and professionals with world-class talent architecture.',
            'signature_name': 'Dr. Ashvani Dubey',
            'linkedin_url': 'https://linkedin.com/in/ashvanidubey',
            'principles_json': json.dumps(custom_principles),
        }

        save_res = self.client.post('/admin-panel/website/about/?page=ceo', data=post_data, follow=True)
        self.assertEqual(save_res.status_code, 200)

        # Verify DB
        ceo_settings = CEOMessageSettings.get_settings()
        self.assertEqual(ceo_settings.ceo_name, 'DR. ASHVANI DUBEY (HON)')
        self.assertEqual(CEOLeadershipPrinciple.objects.count(), 2)

        # Verify Live Website
        pub_res = Client().get('/about/ceo/')
        self.assertEqual(pub_res.status_code, 200)
        self.assertContains(pub_res, 'DR. ASHVANI DUBEY (HON)')
        self.assertContains(pub_res, 'LEADERSHIP HORIZONS')
        self.assertContains(pub_res, 'Radical Transparency')
        self.assertContains(pub_res, 'Continuous Innovation')

    def test_05_admin_save_our_team_reflects_on_live_site(self):
        """Saving Our Team & Team Members updates DB and immediately updates /about/team/."""
        from apps.core.models import OurTeamSettings, TeamMember

        custom_members = [
            {
                'name': 'Er. Ashvani Dubey',
                'role': 'Group CEO',
                'category': 'leadership',
                'static_photo_path': 'images/team/CEO image.png',
                'bio': 'Pioneering human capital solutions across India.',
                'linkedin_url': 'https://linkedin.com/in/ashvani',
                'email_url': 'ashvani@svg.com',
                'order': 1,
                'is_visible': True
            },
            {
                'name': 'Kavita Menon',
                'role': 'Head of Executive Search',
                'category': 'specialist',
                'static_photo_path': 'images/team/female1.jpg',
                'experience_text': 'Experience: 10+ Years',
                'linkedin_url': 'https://linkedin.com/in/kavita',
                'email_url': 'kavita@svg.com',
                'order': 2,
                'is_visible': True
            }
        ]

        post_data = {
            'about_subpage': 'team',
            'hero_eyebrow': 'Meet The Visionaries',
            'hero_title': 'Architects of Exceptional Careers & Teams',
            'hero_description': 'Our multidisciplinary recruitment experts deliver bespoke talent solutions.',
            'hero_btn1_text': 'Explore Leadership',
            'hero_btn1_url': '#leadership',
            'hero_btn2_text': 'Join SVG Team',
            'hero_btn2_url': '/careers/',
            'about_eyebrow': 'Who We Are',
            'about_heading': 'Driven by Passion, United by Excellence',
            'about_description': 'Every placement is handled with personalized care and rigorous vetting.',
            'team_members_json': json.dumps(custom_members),
        }

        save_res = self.client.post('/admin-panel/website/about/?page=team', data=post_data, follow=True)
        self.assertEqual(save_res.status_code, 200)

        # Verify DB
        team_settings = OurTeamSettings.get_settings()
        self.assertEqual(team_settings.hero_title, 'Architects of Exceptional Careers & Teams')
        self.assertEqual(TeamMember.objects.count(), 2)

        # Verify Live Website
        pub_res = Client().get('/about/team/')
        self.assertEqual(pub_res.status_code, 200)
        self.assertContains(pub_res, 'Architects of Exceptional Careers &amp; Teams')
        self.assertContains(pub_res, 'Er. Ashvani Dubey')
        self.assertContains(pub_res, 'Head of Executive Search')
        self.assertContains(pub_res, 'Kavita Menon')

    def test_06_admin_save_our_journey_reflects_on_live_site(self):
        """Saving Journey & Milestones updates DB and immediately updates /about/journey/."""
        from apps.core.models import OurJourneySettings, JourneyMilestone

        custom_milestones = [
            {
                'year': '2022',
                'title': 'SVG Foundation in Lucknow',
                'badge_label': 'Foundational Year',
                'icon_class': 'fa-solid fa-flag',
                'description': 'Commenced specialized recruitment services with 5 founding partners.',
                'order': 1,
                'is_visible': True
            },
            {
                'year': '2026',
                'title': 'Pan-India Corporate Expansion',
                'badge_label': 'National Footprint',
                'icon_class': 'fa-solid fa-globe',
                'description': 'Established branches in Bangalore, Delhi NCR, and Mumbai.',
                'order': 2,
                'is_visible': True
            }
        ]

        post_data = {
            'about_subpage': 'journey',
            'hero_eyebrow': 'Our Evolution',
            'hero_title': 'Decades of Relentless Dedication to Workforce Growth',
            'hero_description': 'From an ambitious regional consultancy to a trusted national partner.',
            'badge_num': '10+',
            'badge_text': 'Years of Trust',
            'stat1_num': '2022',
            'stat1_label': 'Founded',
            'stat2_num': '12,000+',
            'stat2_label': 'Candidates Placed',
            'stat3_num': '600+',
            'stat3_label': 'Corporate Tie-ups',
            'story_tag': 'Our Evolution',
            'story_title': 'A Legacy Built on Commitment and Integrity',
            'story_p1': 'What began in Lucknow has now expanded across India.',
            'story_p2': 'Our focus has never wavered: empowering people and businesses.',
            'story_p3': 'We look forward to forging brighter futures together.',
            'milestones_json': json.dumps(custom_milestones),
        }

        save_res = self.client.post('/admin-panel/website/about/?page=journey', data=post_data, follow=True)
        self.assertEqual(save_res.status_code, 200)

        # Verify DB
        journey_settings = OurJourneySettings.get_settings()
        self.assertEqual(journey_settings.hero_title, 'Decades of Relentless Dedication to Workforce Growth')
        self.assertEqual(journey_settings.stat2_num, '12,000+')
        self.assertEqual(JourneyMilestone.objects.count(), 2)

        # Verify Live Website
        pub_res = Client().get('/about/journey/')
        self.assertEqual(pub_res.status_code, 200)
        self.assertContains(pub_res, 'Decades of Relentless Dedication to Workforce Growth')
        self.assertContains(pub_res, '12,000+')
        self.assertContains(pub_res, 'SVG Foundation in Lucknow')
        self.assertContains(pub_res, 'Pan-India Corporate Expansion')


class AboutCompanyPageDynamicTestSuite(TestCase):
    """
    Exhaustive test suite for the dynamic /about/ (About Company) page.
    Validates:
    1. HTTP 200 on /about/ with all seeded content & typo fix ("5,000+").
    2. Section toggles (why, testimonials, logos, cta) cleanly hide sections.
    3. Item visibility toggles hide individual cards/testimonials.
    4. XSS auto-escaping prevents script injection in titles and quotes.
    5. Empty DB tables do not crash /about/ (graceful empty state).
    6. Admin POST saves repeaters & invalidates public cache immediately.
    7. Unsafe CTA URLs (javascript: schemes) are rejected.
    8. Regression check for all 4 sub-pages (/about/company/, /about/ceo/, /about/team/, /about/journey/).
    """

    def setUp(self):
        from apps.accounts.models import AdminUser
        from django.core.cache import cache
        cache.clear()

        self.admin = AdminUser.objects.create(
            email="about_tester_admin@skyvisiongoc.com",
            is_active=True
        )
        self.admin.set_password("AdminPass2026!")
        self.admin.save()

        self.client = Client()
        session = self.client.session
        session['admin_id'] = self.admin.id
        session.save()

    def test_01_about_page_renders_seeded_content_and_fixed_typo(self):
        """Public /about/ renders HTTP 200 with all seeded sections and the fixed '5,000+' typo."""
        res = Client().get('/about/')
        self.assertEqual(res.status_code, 200)

        # Typo fix verification: "5,000+" instead of old "5,00+"
        self.assertContains(res, '5,000+')
        self.assertNotContains(res, '>5,00+<')

        # Why cards
        self.assertContains(res, 'Professional Team')
        self.assertContains(res, 'Fast Hiring')

        # Testimonials
        self.assertContains(res, 'Rahul Sharma')
        self.assertContains(res, 'Neha Singh')

        # Stats
        self.assertContains(res, 'Successful Placements')

        # Logos
        self.assertContains(res, 'Amazon')
        self.assertContains(res, 'Infosys')

        # Trust points
        self.assertContains(res, 'Expert HR Consultants')

        # Bottom CTA
        self.assertContains(res, 'Start Your Success Story Today!')
        self.assertContains(res, 'Apply Franchise')

    def test_02_section_visibility_toggles(self):
        """Disabling section toggles hides the entire section from /about/."""
        from apps.core.models import AboutCompanySettings
        company = AboutCompanySettings.get_settings()
        company.why_visible = False
        company.testimonials_visible = False
        company.logos_visible = False
        company.cta_visible = False
        company.save()

        res = Client().get('/about/')
        self.assertEqual(res.status_code, 200)
        self.assertNotContains(res, 'Why choose us?')
        self.assertNotContains(res, 'Client Testimonials')
        self.assertNotContains(res, 'Trusted by Leading Companies')
        self.assertNotContains(res, 'Start Your Success Story Today!')

    def test_03_item_visibility_toggle(self):
        """Setting is_visible=False on individual items omits them from /about/."""
        from apps.core.models import AboutWhyCard, AboutTestimonial
        w_card = AboutWhyCard.objects.filter(title='Professional Team').first()
        if w_card:
            w_card.is_visible = False
            w_card.save()

        cand_test = AboutTestimonial.objects.filter(name='Rahul Sharma').first()
        if cand_test:
            cand_test.is_visible = False
            cand_test.save()

        res = Client().get('/about/')
        self.assertEqual(res.status_code, 200)
        self.assertNotContains(res, '<h3>Professional Team</h3>')
        self.assertNotContains(res, '<div class="tt-card-name">Rahul Sharma</div>')

    def test_04_xss_protection(self):
        """HTML and script tags in user fields are auto-escaped and not rendered raw."""
        from apps.core.models import AboutWhyCard, AboutTestimonial
        AboutWhyCard.objects.create(
            title="<script>alert('xss-why')</script>",
            description="<img src=x onerror=alert('xss-desc')>",
            order=99,
            is_visible=True
        )
        AboutTestimonial.objects.create(
            testimonial_type='candidate',
            name="<script>alert('xss-name')</script>",
            role="Engineer",
            quote="Safe review <script>evil()</script>",
            order=99,
            is_visible=True
        )

        res = Client().get('/about/')
        self.assertEqual(res.status_code, 200)
        self.assertNotContains(res, "<script>alert('xss-why')</script>")
        self.assertNotContains(res, "<img src=x onerror=alert('xss-desc')>")
        self.assertNotContains(res, "<script>evil()</script>")
        self.assertContains(res, "&lt;script&gt;alert(&#x27;xss-why&#x27;)&lt;/script&gt;")

    def test_05_empty_db_resilience(self):
        """Clearing all item models does not cause a crash (HTTP 500) on /about/."""
        from apps.core.models import (
            AboutWhyCard, AboutTestimonial, AboutTestimonialStat,
            AboutTrustPoint, AboutPartnerLogo, TeamMember
        )
        from django.core.cache import cache

        AboutWhyCard.objects.all().delete()
        AboutTestimonial.objects.all().delete()
        AboutTestimonialStat.objects.all().delete()
        AboutTrustPoint.objects.all().delete()
        AboutPartnerLogo.objects.all().delete()
        TeamMember.objects.all().delete()
        cache.clear()

        res = Client().get('/about/')
        self.assertEqual(res.status_code, 200)

    def test_06_admin_save_and_cache_invalidation(self):
        """Admin POST updating repeaters and settings immediately invalidates public cache."""
        from apps.core.models import AboutCompanySettings, AboutWhyCard, AboutTestimonial

        new_why_cards = [
            {
                'icon_class': 'fas fa-rocket',
                'title': 'High Velocity Placements',
                'description': 'Speed and precision in every recruitment cycle.',
                'order': 1,
                'is_visible': True
            }
        ]
        new_testimonials = [
            {
                'name': 'Rohan Saxena',
                'role': 'Full Stack Developer',
                'location': 'Noida, UP',
                'quote': 'Sky Vision provided phenomenal interview opportunities.',
                'rating': 5,
                'badge_text': 'Verified Candidate',
                'avatar_style': 2,
                'order': 1,
                'is_visible': True
            }
        ]

        post_data = {
            'about_subpage': 'company',
            'page_title': 'Cutting-Edge Workforce Architecture - SVG',
            'page_eyebrow': 'About Our Vision',
            'experience_badge': '12+ Years Industry Leader',
            'visual_heading': 'Transforming Careers Across 50+ Cities',
            'visual_subtext': 'Dynamic team delivering exceptional hiring results.',
            'welcome_tag': 'Welcome to Sky Vision',
            'welcome_heading': 'Your Trusted Recruitment Engine',
            'welcome_p1': 'Tailored staffing solutions for modern enterprises.',
            'welcome_p2': 'Connecting verified talent with verified organizations.',
            'vision_title': 'Future Forward Vision',
            'vision_text': 'Leading ethical workforce transitions.',
            'mission_title': 'Mission Statement',
            'mission_text': 'Empowering professionals with top career prospects.',
            'stat_1_count': '25+',
            'stat_1_label': 'Years Experience',
            'stat_2_count': '15,000+',
            'stat_2_label': 'Placements',
            'stat_3_count': '800+',
            'stat_3_label': 'Corporate Tie-ups',
            'stat_4_count': '24/7',
            'stat_4_label': 'Support',
            'why_visible': 'on',
            'testimonials_visible': 'on',
            'logos_visible': 'on',
            'industries_visible': 'on',
            'team_visible': 'on',
            'why_tag': 'Our Pillars',
            'why_heading': 'Why Leading Firms Choose Us',
            'why_subtext': 'Unmatched vetting and nationwide delivery network.',
            'why_cards_json': json.dumps(new_why_cards),
            'candidate_testimonials_json': json.dumps(new_testimonials),
            'cta_visible': 'on',
            'cta_heading': 'Join Our Success Network Today!',
            'cta_text': 'Get in touch for bespoke hiring and career guidance.',
            'cta_primary_label': 'Browse All Jobs',
            'cta_primary_url': '/jobs/',
            'cta_franchise_visible': 'on',
            'cta_franchise_label': 'Apply Franchise Now',
            'cta_trophy_visible': 'on',
        }

        save_res = self.client.post('/admin-panel/website/about/?page=company', data=post_data, follow=True)
        self.assertEqual(save_res.status_code, 200)

        # DB verification
        settings = AboutCompanySettings.get_settings()
        self.assertEqual(settings.page_title, 'Cutting-Edge Workforce Architecture - SVG')
        self.assertEqual(settings.stat_1_count, '25+')
        self.assertEqual(AboutWhyCard.objects.count(), 1)
        self.assertEqual(AboutWhyCard.objects.first().title, 'High Velocity Placements')

        # Live site verification without manual cache clearing
        pub_res = Client().get('/about/')
        self.assertEqual(pub_res.status_code, 200)
        self.assertContains(pub_res, 'Cutting-Edge Workforce Architecture - SVG')
        self.assertContains(pub_res, 'High Velocity Placements')
        self.assertContains(pub_res, 'Rohan Saxena')
        self.assertContains(pub_res, 'Join Our Success Network Today!')

    def test_07_invalid_cta_url_rejected(self):
        """Unsafe javascript: schemes in CTA URL are rejected and not saved to DB."""
        from apps.core.models import AboutCompanySettings
        original_url = AboutCompanySettings.get_settings().cta_primary_url

        post_data = {
            'about_subpage': 'company',
            'cta_primary_url': 'javascript:alert("hacked")',
        }
        res = self.client.post('/admin-panel/website/about/?page=company', data=post_data, follow=True)
        # Should stay on page and not update URL
        settings = AboutCompanySettings.get_settings()
        self.assertNotEqual(settings.cta_primary_url, 'javascript:alert("hacked")')
        self.assertEqual(settings.cta_primary_url, original_url)

    def test_08_subpages_regression(self):
        """Verifies that all 4 subpages return HTTP 200 and continue functioning properly."""
        client = Client()
        for url in ['/about/', '/about/company/', '/about/ceo/', '/about/team/', '/about/journey/']:
            res = client.get(url)
            self.assertEqual(res.status_code, 200, f"Failed for url {url}")

    def test_09_admin_about_company_tabs_and_cards_parity(self):
        """
        Verifies that /admin-panel/website/about/?page=company renders:
        1. All 11 section subtabs (including Visibility Controls)
        2. All section cards having home-section-card class
        3. The non-sticky bottom save bar matching Home page
        4. switchAboutCompanyTab script with scrollIntoView
        """
        res = self.client.get('/admin-panel/website/about/?page=company')
        self.assertEqual(res.status_code, 200)
        html = res.content.decode('utf-8')

        # Verify tabs exist
        self.assertIn('id="aboutCompanySectionTabs"', html)
        self.assertIn('data-tab="header_welcome"', html)
        self.assertIn('data-tab="visibility"', html)
        self.assertIn('data-tab="why"', html)
        self.assertIn('data-tab="industries"', html)
        self.assertIn('data-tab="team"', html)
        self.assertIn('data-tab="testimonials_head"', html)
        self.assertIn('data-tab="candidate_testimonials"', html)
        self.assertIn('data-tab="employer_testimonials"', html)
        self.assertIn('data-tab="logos"', html)
        self.assertIn('data-tab="cta"', html)

        # Verify cards have home-section-card class
        self.assertIn('card-about-visibility', html)
        self.assertIn('card-about-header-welcome', html)
        self.assertIn('card-about-why', html)
        self.assertIn('card-about-industries', html)
        self.assertIn('card-about-team', html)
        self.assertIn('card-about-testimonials-head', html)
        self.assertIn('card-about-candidates', html)
        self.assertIn('card-about-employers', html)
        self.assertIn('card-about-logos', html)
        self.assertIn('card-about-cta', html)

        # Verify save bar is non-sticky
        self.assertIn('<!-- BOTTOM SAVE ACTION BAR -->', html)
        self.assertNotIn('position:sticky; bottom:15px; z-index:90;', html)

        # Verify JS function has scrollIntoView
        self.assertIn('function switchAboutCompanyTab', html)
        self.assertIn("c.scrollIntoView({ behavior: 'smooth', block: 'start' });", html)

    def test_10_why_card_visibility_toggle_hides_items_on_public_page(self):
        """
        Verifies that turning OFF individual advantage cards or the whole section
        properly hides them on /about/ without falling back to hardcoded items.
        """
        from apps.core.models import AboutCompanySettings, AboutWhyCard
        from django.core.cache import cache

        # Create two distinct test cards
        AboutWhyCard.objects.all().delete()
        c1 = AboutWhyCard.objects.create(title="Visible Alpha Advantage", description="Alpha test desc", order=1, is_visible=True)
        c2 = AboutWhyCard.objects.create(title="Hidden Beta Advantage", description="Beta test desc", order=2, is_visible=False)

        cache.clear()
        res = Client().get('/about/')
        self.assertEqual(res.status_code, 200)
        html = res.content.decode('utf-8')

        # c1 should be visible, c2 must NOT be visible, and hardcoded items must NOT be visible
        self.assertIn('Visible Alpha Advantage', html)
        self.assertNotIn('Hidden Beta Advantage', html)
        self.assertNotIn('Professional Team', html)

        # Now turn off c1 as well -> section should cleanly hide
        c1.is_visible = False
        c1.save()
        cache.clear()

        res2 = Client().get('/about/')
        html2 = res2.content.decode('utf-8')
        self.assertNotIn('Visible Alpha Advantage', html2)
        self.assertNotIn('class="why-section"', html2)
        self.assertNotIn('Why choose us?', html2)

    def test_11_about_industries_crud_and_live_rendering(self):
        """Admin can Add, Edit, Reorder, Toggle, and Delete AboutIndustryItems with instant live rendering."""
        from apps.core.models import AboutIndustryItem, AboutCompanySettings

        # Ensure clean state
        AboutIndustryItem.objects.all().delete()
        item1 = AboutIndustryItem.objects.create(name="Healthcare & Pharma", icon_class="fas fa-stethoscope", order=1, is_visible=True)
        item2 = AboutIndustryItem.objects.create(name="Automotive Manufacturing", icon_class="fas fa-car", order=2, is_visible=True)

        # POST update: Edit item1, Delete item2, Add item3 (New: Aerospace & Defense), and Add item4 (Hidden: Retail)
        new_industries = [
            {
                'id': item1.id,
                'name': 'Healthcare, Pharma & Biotech',
                'icon_class': 'fas fa-heartbeat',
                'link_url': '/jobs/?industry=health',
                'order': 1,
                'is_visible': True
            },
            {
                'id': None,
                'name': 'Aerospace & Defense Industry',
                'icon_class': 'fas fa-plane-departure',
                'link_url': '/jobs/?industry=defense',
                'order': 2,
                'is_visible': True
            },
            {
                'id': None,
                'name': 'Retail & Consumer Goods',
                'icon_class': 'fas fa-shopping-cart',
                'link_url': '',
                'order': 3,
                'is_visible': False
            }
        ]

        post_data = {
            'about_subpage': 'company',
            'industries_visible': 'on',
            'industries_tag': 'Specialized Domains',
            'industries_heading': 'Key Industries We Power',
            'industries_subtext': 'Custom enterprise recruitment across specialized sectors.',
            'about_industries_json': json.dumps(new_industries),
        }

        save_res = self.client.post('/admin-panel/website/about/?page=company', data=post_data, follow=True)
        self.assertEqual(save_res.status_code, 200)

        # 1. Verify DB
        all_items = list(AboutIndustryItem.objects.all().order_by('order', 'id'))
        self.assertEqual(len(all_items), 3)

        # item2 should be deleted
        self.assertFalse(AboutIndustryItem.objects.filter(name="Automotive Manufacturing").exists())

        # item1 should be updated
        updated_item1 = AboutIndustryItem.objects.get(id=item1.id)
        self.assertEqual(updated_item1.name, 'Healthcare, Pharma & Biotech')
        self.assertEqual(updated_item1.icon_class, 'fas fa-heartbeat')
        self.assertEqual(updated_item1.link_url, '/jobs/?industry=health')
        self.assertTrue(updated_item1.is_visible)

        # Aerospace should be created
        aerospace = AboutIndustryItem.objects.get(name='Aerospace & Defense Industry')
        self.assertEqual(aerospace.icon_class, 'fas fa-plane-departure')
        self.assertTrue(aerospace.is_visible)

        # Retail should be created as hidden
        retail = AboutIndustryItem.objects.get(name='Retail & Consumer Goods')
        self.assertFalse(retail.is_visible)

        # 2. Verify Live Public /about/
        pub_res = Client().get('/about/')
        self.assertEqual(pub_res.status_code, 200)
        content = pub_res.content.decode('utf-8')

        self.assertIn('Specialized Domains', content)
        self.assertIn('Key Industries We Power', content)
        self.assertIn('Healthcare, Pharma &amp; Biotech', content)
        self.assertIn('fas fa-heartbeat', content)
        self.assertIn('Aerospace &amp; Defense Industry', content)
        self.assertIn('fas fa-plane-departure', content)

        # Hidden retail & deleted automotive should NOT be shown
        self.assertNotIn('Retail &amp; Consumer Goods', content)
        self.assertNotIn('Automotive Manufacturing', content)

    def test_12_about_industries_section_visibility_toggle(self):
        """Disabling master industries_visible toggle removes Section 3 from /about/ entirely."""
        from apps.core.models import AboutCompanySettings, AboutIndustryItem
        AboutIndustryItem.objects.all().delete()
        AboutIndustryItem.objects.create(name="FinTech & Banking", icon_class="fas fa-coins", order=1, is_visible=True)

        company = AboutCompanySettings.get_settings()
        company.industries_visible = False
        company.save()

        pub_res = Client().get('/about/')
        self.assertEqual(pub_res.status_code, 200)
        content = pub_res.content.decode('utf-8')

        self.assertNotIn('FinTech &amp; Banking', content)
        self.assertNotIn('class="industries-section"', content)
        self.assertNotIn('Where We Work', content)


class CEOPageDynamicTestSuite(TestCase):
    """
    Comprehensive test suite for the dynamic /about/ceo/ (CEO & Founder) page.
    Validates:
    1. HTTP 200 on /about/ceo/ with all seeded default content.
    2. Admin save updates database and changes reflect on public page immediately.
    3. Section visibility toggles hide corresponding sections on public page.
    4. Inactive principles and stat badges are excluded from public page.
    5. Principles and stat badges CRUD and reorder.
    6. Non-admin cannot save CEO profile (redirected or rejected).
    7. Unsafe URLs (javascript: schemes) and invalid emails are safely sanitized/handled.
    """

    def setUp(self):
        from apps.accounts.models import AdminUser
        from django.core.cache import cache
        cache.clear()

        self.admin = AdminUser.objects.create(
            email="ceo_tester_admin@skyvisiongoc.com",
            is_active=True
        )
        self.admin.set_password("AdminPass2026!")
        self.admin.save()

        self.client = Client()
        session = self.client.session
        session['admin_id'] = self.admin.id
        session.save()

    def test_01_ceo_page_renders_seeded_content(self):
        """Public /about/ceo/ renders HTTP 200 with default seeded content."""
        res = Client().get('/about/ceo/')
        self.assertEqual(res.status_code, 200)

        # Hero
        self.assertContains(res, 'Get To Know Us')
        self.assertContains(res, 'CEO &amp; Founder Message')

        # Profile
        self.assertContains(res, 'ASHVANI DUBEY')
        self.assertContains(res, 'CEO &amp; FOUNDER')
        self.assertContains(res, 'Sky Vision Group of Consultancy')

        # Stat badges
        self.assertContains(res, '10+')
        self.assertContains(res, 'Years Leadership')
        self.assertContains(res, '5,000+')

        # Message & Quote
        self.assertContains(res, 'At Sky Vision Group of Consultancy, our vision is simple')
        self.assertContains(res, 'Great organizations are built by great people')

        # Principles
        self.assertContains(res, 'OUR LEADERSHIP')
        self.assertContains(res, 'PRINCIPLES')
        self.assertContains(res, 'Integrity First')
        self.assertContains(res, 'Excellence in Service')

        # Vision / Mission / Signature
        self.assertContains(res, 'OUR VISION')
        self.assertContains(res, 'OUR MISSION')
        self.assertContains(res, 'Ashvani Dubey')

    def test_02_admin_save_updates_public_ceo_page(self):
        """Admin POST to /admin-panel/website/about/?page=ceo updates DB and public page immediately."""
        from apps.core.models import CEOMessageSettings
        post_data = {
            'about_subpage': 'ceo',
            'hero_visible': 'on',
            'profile_visible': 'on',
            'message_visible': 'on',
            'principles_visible': 'on',
            'vm_visible': 'on',
            'cta_visible': 'on',
            'page_eyebrow': 'Executive Desk',
            'page_title': 'Leadership Vision 2026',
            'hero_subtitle': 'Guiding India toward workforce excellence.',
            'breadcrumb_title': 'Founder Message',
            'ceo_name': 'Dr. Ashvani Dubey',
            'ceo_role': 'Founder & Managing Director',
            'ceo_org': 'Sky Vision Global Group',
            'ceo_tagline': 'Transforming Careers, Building Futures',
            'title_eyebrow': 'A PERSONAL NOTE FROM',
            'title_main': 'OUR FOUNDER',
            'message_p1': 'New dynamic first paragraph about strategic excellence.',
            'message_p2': 'New dynamic second paragraph on client satisfaction.',
            'message_p3': 'New dynamic third paragraph on ethics.',
            'message_p4': 'New dynamic fourth paragraph on future horizons.',
            'quote_text': 'Leadership is the capacity to translate vision into reality.',
            'closing_text': 'With sincere gratitude,',
            'signoff_text': 'Dr. Ashvani Dubey\nFounder & MD',
            'principles_tag': 'CORE PILLARS',
            'principles_title': 'FOUNDATION',
            'principles_subtitle': 'The bedrock of our daily operations.',
            'vision_title': 'FUTURE VISION',
            'vision_icon': 'fa-solid fa-compass',
            'vision_text': 'To be the preeminent workforce architect in Asia.',
            'mission_title': 'CORE MISSION',
            'mission_icon': 'fa-solid fa-flag',
            'mission_text': 'To empower 1,000,000 careers with transparency.',
            'signature_name': 'Dr. Ashvani Dubey',
            'linkedin_url': 'https://www.linkedin.com/in/ashvanidubey/',
            'facebook_url': 'https://www.facebook.com/ashvanidubey/',
            'twitter_url': 'https://x.com/ashvanidubey',
            'instagram_url': 'https://instagram.com/ashvanidubey',
            'email_address': 'ceo@skyvisiongoc.com',
            'cta_heading': 'Ready to Scale Your Team?',
            'cta_text': 'Connect with our executive search consultants today.',
            'cta_btn_label': 'Hire Executive Talent',
            'cta_btn_url': '/contact/',
            'cta_btn2_label': 'Explore Enterprise Solutions',
            'cta_btn2_url': '/services/',
            'meta_title': 'CEO Message | Sky Vision Group',
            'meta_description': 'Official message from the CEO of Sky Vision Group.',
        }

        res = self.client.post('/admin-panel/website/about/?page=ceo', post_data)
        self.assertEqual(res.status_code, 302)

        # Verify DB
        settings = CEOMessageSettings.get_settings()
        self.assertEqual(settings.ceo_name, 'Dr. Ashvani Dubey')
        self.assertEqual(settings.page_title, 'Leadership Vision 2026')
        self.assertEqual(settings.email_address, 'ceo@skyvisiongoc.com')

        # Verify Public page
        pub_res = Client().get('/about/ceo/')
        self.assertEqual(pub_res.status_code, 200)
        self.assertContains(pub_res, 'Leadership Vision 2026')
        self.assertContains(pub_res, 'Dr. Ashvani Dubey')
        self.assertContains(pub_res, 'Founder &amp; Managing Director')
        self.assertContains(pub_res, 'Transforming Careers, Building Futures')
        self.assertContains(pub_res, 'A PERSONAL NOTE FROM')
        self.assertContains(pub_res, 'New dynamic first paragraph about strategic excellence.')
        self.assertContains(pub_res, 'Leadership is the capacity to translate vision into reality.')
        self.assertContains(pub_res, 'FUTURE VISION')
        self.assertContains(pub_res, 'CORE MISSION')
        self.assertContains(pub_res, 'Ready to Scale Your Team?')
        self.assertContains(pub_res, 'Hire Executive Talent')
        self.assertContains(pub_res, 'mailto:ceo@skyvisiongoc.com')
        self.assertContains(pub_res, 'https://x.com/ashvanidubey')
        self.assertContains(pub_res, 'https://instagram.com/ashvanidubey')

    def test_03_section_visibility_toggles(self):
        """Toggling sections off hides them from public /about/ceo/."""
        from apps.core.models import CEOMessageSettings
        settings = CEOMessageSettings.get_settings()
        settings.hero_visible = False
        settings.profile_visible = False
        settings.principles_visible = False
        settings.vm_visible = False
        settings.cta_visible = False
        settings.save()

        pub_res = Client().get('/about/ceo/')
        self.assertEqual(pub_res.status_code, 200)

        # Hero header should be hidden
        self.assertNotContains(pub_res, 'class="page-header"')
        # Profile photo wrap should be hidden
        self.assertNotContains(pub_res, 'class="ceo-photo-wrap"')
        # Principles should be hidden
        self.assertNotContains(pub_res, 'class="principles"')
        # Vision/Mission should be hidden
        self.assertNotContains(pub_res, 'class="vm"')
        # CTA should be hidden
        self.assertNotContains(pub_res, 'class="ceo-cta"')

    def test_04_item_visibility_principles_and_stat_badges(self):
        """Setting is_visible=False on individual principle or stat badge omits it from public page."""
        from apps.core.models import CEOLeadershipPrinciple, CEOStatBadge
        p = CEOLeadershipPrinciple.objects.filter(title='Integrity First').first()
        if p:
            p.is_visible = False
            p.save()

        badge = CEOStatBadge.objects.filter(value='10+').first()
        if badge:
            badge.is_visible = False
            badge.save()

        pub_res = Client().get('/about/ceo/')
        self.assertEqual(pub_res.status_code, 200)

        # Hidden items should not be present
        self.assertNotContains(pub_res, '<h4>Integrity First</h4>')
        self.assertNotContains(pub_res, '<span class="ceo-photo__badge-val">10+</span>')

        # Other items remain visible
        self.assertContains(pub_res, 'Excellence in Service')
        self.assertContains(pub_res, '5,000+')

    def test_05_principles_and_stat_badges_reorder_and_crud(self):
        """Admin can add, reorder, edit, and delete principles and stat badges via JSON payload."""
        import json
        from apps.core.models import CEOLeadershipPrinciple, CEOStatBadge

        principles_payload = [
            {'title': 'Innovation Always', 'description': 'Pushing boundaries in HR technology.', 'icon_class': 'fa-solid fa-lightbulb', 'is_visible': True},
            {'title': 'People First', 'description': 'Human-centric recruitment philosophy.', 'icon_class': 'fa-solid fa-user-heart', 'is_visible': True},
        ]
        stats_payload = [
            {'value': '15+', 'label': 'Industry Awards', 'icon_class': 'fa-solid fa-trophy', 'is_visible': True},
            {'value': '25,000+', 'label': 'Candidates Placed', 'icon_class': 'fa-solid fa-user-check', 'is_visible': True},
        ]

        post_data = {
            'about_subpage': 'ceo',
            'principles_json': json.dumps(principles_payload),
            'ceo_stat_badges_json': json.dumps(stats_payload),
        }
        res = self.client.post('/admin-panel/website/about/?page=ceo', post_data)
        self.assertEqual(res.status_code, 302)

        # Verify DB
        principles = list(CEOLeadershipPrinciple.objects.all().order_by('order'))
        self.assertEqual(len(principles), 2)
        self.assertEqual(principles[0].title, 'Innovation Always')
        self.assertEqual(principles[1].title, 'People First')

        badges = list(CEOStatBadge.objects.all().order_by('order'))
        self.assertEqual(len(badges), 2)
        self.assertEqual(badges[0].value, '15+')
        self.assertEqual(badges[1].value, '25,000+')

        # Verify public page
        pub_res = Client().get('/about/ceo/')
        self.assertEqual(pub_res.status_code, 200)
        self.assertContains(pub_res, 'Innovation Always')
        self.assertContains(pub_res, 'People First')
        self.assertContains(pub_res, '15+')
        self.assertContains(pub_res, 'Industry Awards')
        self.assertContains(pub_res, '25,000+')
        self.assertContains(pub_res, 'Candidates Placed')

    def test_06_unauthenticated_admin_save_rejected(self):
        """Unauthenticated POST to admin save endpoint is redirected and changes rejected."""
        from apps.core.models import CEOMessageSettings
        orig_name = CEOMessageSettings.get_settings().ceo_name

        anon_client = Client()
        res = anon_client.post('/admin-panel/website/about/?page=ceo', {
            'about_subpage': 'ceo',
            'ceo_name': 'Hacker Name',
        })
        self.assertIn(res.status_code, [302, 403])

        # DB must NOT be changed
        current_name = CEOMessageSettings.get_settings().ceo_name
        self.assertEqual(current_name, orig_name)

    def test_07_invalid_urls_and_email_handled_safely(self):
        """Unsafe javascript: schemes and malformed emails are stripped/rejected safely."""
        from apps.core.models import CEOMessageSettings
        post_data = {
            'about_subpage': 'ceo',
            'linkedin_url': 'javascript:alert("hacked")',
            'cta_btn_url': 'javascript:void(0)',
            'email_address': 'not-an-email',
        }
        res = self.client.post('/admin-panel/website/about/?page=ceo', post_data)
        self.assertIn(res.status_code, [200, 302])

        # Security check: DB must reject the unsafe javascript: scheme
        settings = CEOMessageSettings.get_settings()
        self.assertNotIn('javascript:', settings.linkedin_url)
        self.assertNotIn('javascript:', settings.cta_btn_url)

        # Public page must never render malicious javascript:
        pub_res = Client().get('/about/ceo/')
        self.assertEqual(pub_res.status_code, 200)
        self.assertNotContains(pub_res, 'javascript:alert')

    def test_08_service_and_direct_aliases_render_200(self):
        """Ensure /contract-staffing/ and all direct service URLs resolve and render HTTP 200."""
        c = Client()
        urls = [
            '/contract-staffing/',
            '/contract-staffing.html',
            '/services/contract-staffing/',
            '/manpower-supply/',
            '/services/manpower-supply/',
            '/recruitment-placement/',
            '/services/recruitment-placement/',
            '/educational-consultancy/',
            '/services/educational-consultancy/',
            '/payroll-outsourcing/',
            '/services/payroll-outsourcing/',
            '/hr-support/',
            '/services/hr-support/',
            '/internship/',
            '/services/internship/',
        ]
        for url in urls:
            res = c.get(url, follow=True)
            self.assertEqual(res.status_code, 200, f"URL {url} failed to return HTTP 200")


class OurTeamSettingsTestCase(TestCase):
    """
    Comprehensive verification tests for the dynamic 'Our Team' system:
    1. Public page renders 200 with all dynamic content.
    2. Visibility toggles dynamically show/hide sections.
    3. Admin save immediately reflects on DB and public page.
    4. Repeaters (highlights, departments, stats, trust points, core values) CRUD via JSON.
    5. Unauthenticated admin requests are rejected.
    6. Malicious javascript: URLs are stripped/sanitized.
    """

    def setUp(self):
        from apps.accounts.models import AdminUser
        from django.core.cache import cache
        from apps.core.models import (
            OurTeamSettings, TeamMember, TeamFeatureHighlight,
            TeamStat, TeamDepartment, TeamTrustPoint, TeamCoreValue
        )
        cache.clear()

        self.admin = AdminUser.objects.create(
            email="admin_team_test@example.com",
            is_active=True
        )
        self.admin.set_password("AdminPass123!")
        self.admin.save()

        self.client = Client()
        session = self.client.session
        session['admin_id'] = self.admin.id
        session.save()

        # Ensure seed settings exist
        self.settings = OurTeamSettings.get_settings()
        self.settings.hero_title = "Meet Our Expert Team"
        self.settings.about_title = "The People Behind Sky Vision"
        self.settings.hero_visible = True
        self.settings.about_visible = True
        self.settings.leadership_visible = True
        self.settings.specialists_visible = True
        self.settings.departments_visible = True
        self.settings.stats_visible = True
        self.settings.trust_visible = True
        self.settings.values_visible = True
        self.settings.quote_visible = True
        self.settings.cta_visible = True
        self.settings.save()

    def test_01_public_team_page_renders_200_and_dynamic_sections(self):
        """Public /about/team/ renders HTTP 200 and displays dynamic team sections."""
        res = Client().get('/about/team/')
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, 'Meet Our Expert Team')
        self.assertContains(res, 'The People Behind Sky Vision')
        self.assertContains(res, 'Why Clients')
        self.assertContains(res, '<span>Trust</span>')
        self.assertContains(res, 'Our Core')

    def test_02_section_visibility_toggles(self):
        """Toggling section visibility in OurTeamSettings hides/shows public sections."""
        from apps.core.models import OurTeamSettings

        # Turn off hero, quote, and cta
        settings = OurTeamSettings.get_settings()
        settings.hero_visible = False
        settings.quote_visible = False
        settings.cta_visible = False
        settings.save()

        res = Client().get('/about/team/')
        self.assertEqual(res.status_code, 200)
        self.assertNotContains(res, 'class="hero"')
        self.assertNotContains(res, 'lead-msg')
        self.assertNotContains(res, 'cta-band')

        # Turn them back on
        settings.hero_visible = True
        settings.quote_visible = True
        settings.cta_visible = True
        settings.save()

        res2 = Client().get('/about/team/')
        self.assertEqual(res2.status_code, 200)
        self.assertContains(res2, 'class="hero"')
        self.assertContains(res2, 'lead-msg')
        self.assertContains(res2, 'cta-band')

    def test_03_admin_save_updates_content_immediately(self):
        """Admin POST to /admin-panel/website/about/?page=team updates DB and public page."""
        from apps.core.models import OurTeamSettings

        post_data = {
            'about_subpage': 'team',
            'team_has_toggles': '1',
            'hero_visible': 'on',
            'hero_title': 'World-Class Talent Curators',
            'hero_description': 'Connecting exceptional candidates with industry-leading companies.',
            'about_visible': 'on',
            'about_title': 'Pioneers in Strategic Recruitment',
            'quote_visible': 'on',
            'quote_text': 'Recruitment is about matching values and futures, not just CVs.',
            'quote_author_name': 'Super Leader',
            'quote_author_role': 'Managing Director',
            'cta_visible': 'on',
            'cta_heading': 'Ready to Elevate Your Hiring?',
            'cta_btn1_text': 'Connect Now',
            'cta_btn1_url': '/contact/',
        }
        res = self.client.post('/admin-panel/website/about/?page=team', post_data)
        self.assertEqual(res.status_code, 302)

        # Verify DB
        settings = OurTeamSettings.get_settings()
        self.assertEqual(settings.hero_title, 'World-Class Talent Curators')
        self.assertEqual(settings.about_title, 'Pioneers in Strategic Recruitment')
        self.assertEqual(settings.quote_author_name, 'Super Leader')
        self.assertEqual(settings.cta_heading, 'Ready to Elevate Your Hiring?')

        # Verify public page
        pub_res = Client().get('/about/team/')
        self.assertEqual(pub_res.status_code, 200)
        self.assertContains(pub_res, 'World-Class Talent Curators')
        self.assertContains(pub_res, 'Pioneers in Strategic Recruitment')
        self.assertContains(pub_res, 'Super Leader')
        self.assertContains(pub_res, 'Ready to Elevate Your Hiring?')

    def test_04_repeaters_crud_via_json(self):
        """Admin can sync repeatable items (highlights, departments, stats, trust points, values) via JSON."""
        import json
        from apps.core.models import (
            TeamFeatureHighlight, TeamDepartment, TeamStat,
            TeamTrustPoint, TeamCoreValue
        )

        highlights_payload = [
            {'icon': 'fa-solid fa-gem', 'title': 'Elite Advisory', 'description': 'Senior-level counsel for enterprise hiring.', 'is_visible': True},
        ]
        departments_payload = [
            {'name': 'Aerospace & Defense', 'icon': 'fa-solid fa-plane', 'team_size': '8 Recruiters', 'description': 'Specialized defense staffing.', 'is_visible': True},
        ]
        stats_payload = [
            {'icon': 'fa-solid fa-building', 'count': 120, 'suffix': '+', 'label': 'Corporate Clients', 'is_visible': True},
        ]
        trust_payload = [
            {'icon_class': '✓', 'title': 'Rigorous 5-step background vetting', 'is_visible': True},
        ]
        values_payload = [
            {'icon': 'fa-solid fa-lightbulb', 'title': 'Radical Transparency', 'description': 'Honest feedback and clear timelines.', 'is_visible': True},
        ]

        post_data = {
            'about_subpage': 'team',
            'team_has_toggles': '1',
            'hero_visible': 'on',
            'about_visible': 'on',
            'departments_visible': 'on',
            'stats_visible': 'on',
            'trust_visible': 'on',
            'values_visible': 'on',
            'team_highlights_json': json.dumps(highlights_payload),
            'team_departments_json': json.dumps(departments_payload),
            'team_stats_json': json.dumps(stats_payload),
            'team_trust_points_json': json.dumps(trust_payload),
            'team_values_json': json.dumps(values_payload),
        }
        res = self.client.post('/admin-panel/website/about/?page=team', post_data)
        self.assertEqual(res.status_code, 302)

        # Verify DB
        self.assertEqual(TeamFeatureHighlight.objects.count(), 1)
        self.assertEqual(TeamFeatureHighlight.objects.first().title, 'Elite Advisory')

        self.assertEqual(TeamDepartment.objects.count(), 1)
        self.assertEqual(TeamDepartment.objects.first().name, 'Aerospace & Defense')

        self.assertEqual(TeamStat.objects.count(), 1)
        self.assertEqual(TeamStat.objects.first().label, 'Corporate Clients')

        self.assertEqual(TeamTrustPoint.objects.count(), 1)
        self.assertEqual(TeamTrustPoint.objects.first().title, 'Rigorous 5-step background vetting')

        self.assertEqual(TeamCoreValue.objects.count(), 1)
        self.assertEqual(TeamCoreValue.objects.first().title, 'Radical Transparency')

        # Verify public page
        pub_res = Client().get('/about/team/')
        self.assertEqual(pub_res.status_code, 200)
        self.assertContains(pub_res, 'Elite Advisory')
        self.assertContains(pub_res, 'Aerospace &amp; Defense')
        self.assertContains(pub_res, 'Corporate Clients')
        self.assertContains(pub_res, 'Rigorous 5-step background vetting')
        self.assertContains(pub_res, 'Radical Transparency')

    def test_05_unauthenticated_admin_save_rejected(self):
        """Unauthenticated POST to admin save endpoint is redirected and changes rejected."""
        from apps.core.models import OurTeamSettings
        orig_title = OurTeamSettings.get_settings().hero_title

        anon_client = Client()
        res = anon_client.post('/admin-panel/website/about/?page=team', {
            'about_subpage': 'team',
            'hero_title': 'Hacker Team Title',
        })
        self.assertIn(res.status_code, [302, 403])

        current_title = OurTeamSettings.get_settings().hero_title
        self.assertEqual(current_title, orig_title)

    def test_06_malicious_javascript_urls_stripped(self):
        """Unsafe javascript: schemes are stripped/rejected safely."""
        from apps.core.models import OurTeamSettings
        post_data = {
            'about_subpage': 'team',
            'team_has_toggles': '1',
            'hero_btn1_url': 'javascript:alert("hacked")',
            'cta_btn1_url': 'javascript:alert("xss")',
        }
        res = self.client.post('/admin-panel/website/about/?page=team', post_data)
        self.assertIn(res.status_code, [200, 302])

        settings = OurTeamSettings.get_settings()
        self.assertNotIn('javascript:', settings.hero_btn1_url)
        self.assertNotIn('javascript:', settings.cta_btn1_url)

        pub_res = Client().get('/about/team/')
        self.assertEqual(pub_res.status_code, 200)
        self.assertNotContains(pub_res, 'javascript:alert')

    def test_07_departments_heading_tag_and_image_editable(self):
        """Departments section tag, title, and card image update via admin panel and appear on public page."""
        import json
        from apps.core.models import OurTeamSettings, TeamDepartment

        custom_img_url = "https://images.unsplash.com/photo-custom-dept-12345?w=400&q=80"
        depts_payload = [
            {
                'id': None,
                'name': 'Robotics Engineering',
                'icon': 'fa-solid fa-robot',
                'description': 'Advanced robotics automation team.',
                'image_url': custom_img_url,
                'team_size': '20+ Engineers',
                'order': 1,
                'is_visible': True,
            }
        ]

        post_data = {
            'about_subpage': 'team',
            'team_has_toggles': '1',
            'departments_visible': 'on',
            'departments_tag': 'Our Department Units',
            'departments_title': 'Our Specialized <span>Divisions</span>',
            'departments_subtitle': 'World-class departments powering recruitment.',
            'team_departments_json': json.dumps(depts_payload),
        }
        res = self.client.post('/admin-panel/website/about/?page=team', post_data)
        self.assertEqual(res.status_code, 302)

        # Check DB
        settings = OurTeamSettings.get_settings()
        self.assertEqual(settings.departments_tag, 'Our Department Units')
        self.assertEqual(settings.departments_title, 'Our Specialized <span>Divisions</span>')

        dept = TeamDepartment.objects.filter(name='Robotics Engineering').first()
        self.assertIsNotNone(dept)
        self.assertEqual(dept.get_image_url(), custom_img_url)

        # Check public page
        pub_res = Client().get('/about/team/')
        self.assertEqual(pub_res.status_code, 200)
        self.assertContains(pub_res, 'Our Department Units')
        self.assertContains(pub_res, 'Our Specialized <span>Divisions</span>')
        self.assertContains(pub_res, 'Robotics Engineering')
        self.assertContains(pub_res, 'photo-custom-dept-12345')

    def test_08_core_values_json_init_and_clean_title_formatting(self):
        """Verify team_core_values_json_init is present in admin context and clean title formatting works without exposing raw HTML tags."""
        from apps.core.models import TeamCoreValue, OurTeamSettings
        # 1. Create a TeamCoreValue
        TeamCoreValue.objects.all().delete()
        val = TeamCoreValue.objects.create(
            title="Integrity First",
            description="We act with complete honesty and transparency.",
            icon="fa-solid fa-shield-halved",
            order=1,
            is_visible=True
        )

        # 2. Check admin GET response context
        get_res = self.client.get('/admin-panel/website/about/?page=team')
        self.assertEqual(get_res.status_code, 200)
        self.assertIn('team_core_values_json_init', get_res.context)
        self.assertIn('team_values_json_init', get_res.context)

        core_vals_data = json.loads(get_res.context['team_core_values_json_init'])
        self.assertEqual(len(core_vals_data), 1)
        self.assertEqual(core_vals_data[0]['title'], 'Integrity First')
        self.assertEqual(core_vals_data[0]['icon'], 'fa-solid fa-shield-halved')

        # 3. Post with clean title and highlight word
        post_data = {
            'about_subpage': 'team',
            'team_has_toggles': '1',
            'values_visible': 'on',
            'values_clean_title': 'Our Core Values',
            'values_highlight_word': 'Values',
            'values_tag': 'Core Values Tag',
            'team_values_json': json.dumps([
                {
                    'id': val.id,
                    'title': 'Client Obsession',
                    'description': 'Our clients are at the center of everything.',
                    'icon': 'fa-solid fa-award',
                    'order': 1,
                    'is_visible': True,
                },
                {
                    'id': None,
                    'title': 'Excellence in Execution',
                    'description': 'Delivering top tier results with speed.',
                    'icon': 'fa-solid fa-bolt',
                    'order': 2,
                    'is_visible': True,
                }
            ]),
        }
        res = self.client.post('/admin-panel/website/about/?page=team', post_data)
        self.assertEqual(res.status_code, 302)

        # 4. Verify settings & model properties
        settings = OurTeamSettings.get_settings()
        self.assertEqual(settings.values_heading, 'Our Core <span>Values</span>')
        self.assertEqual(settings.values_clean_title, 'Our Core Values')
        self.assertEqual(settings.values_highlight_word, 'Values')

        # 5. Verify DB count
        self.assertEqual(TeamCoreValue.objects.count(), 2)

        # 6. Verify public page renders cards and heading with highlight span
        pub_res = Client().get('/about/team/')
        self.assertEqual(pub_res.status_code, 200)
        self.assertContains(pub_res, 'Our Core <span>Values</span>')
        self.assertContains(pub_res, 'Client Obsession')
        self.assertContains(pub_res, 'Excellence in Execution')
        self.assertContains(pub_res, 'fa-solid fa-award')


class JourneyPageSettingsTestCase(TestCase):
    """
    Comprehensive tests for the fully dynamic Our Journey page:
    1. Public page renders HTTP 200 with seeded content.
    2. Section visibility toggles hide/show each section on the public page.
    3. Admin POST updates settings, headings, highlighted words, and meta immediately.
    4. Repeater models CRUD via JSON (paragraphs, story cards, timeline, milestone cards, impact items, stats, future goals).
    5. Inactive items do not render on the public page.
    6. Non-admin users cannot access or edit Journey admin endpoints.
    7. Image upload and removal works cleanly.
    """

    def setUp(self):
        from apps.accounts.models import AdminUser
        from apps.core.models import (
            OurJourneySettings, JourneyMilestone, JourneyStoryParagraph,
            JourneyStoryCard, JourneyMilestoneCard, JourneyImpactItem,
            JourneyStat, JourneyFutureGoal
        )
        from django.core.cache import cache
        cache.clear()

        # Create admin user and authenticate in test client
        self.admin = AdminUser.objects.create(
            email="journey_admin@skyvision.com",
            is_active=True
        )
        self.admin.set_password("JourneyAdminPass123!")
        self.admin.save()

        self.client = Client()
        session = self.client.session
        session['admin_id'] = self.admin.id
        session.save()

        # Ensure settings exist and all sections visible
        self.settings = OurJourneySettings.get_settings()
        self.settings.hero_visible = True
        self.settings.story_visible = True
        self.settings.timeline_visible = True
        self.settings.milestones_visible = True
        self.settings.impact_visible = True
        self.settings.numbers_visible = True
        self.settings.ahead_visible = True
        self.settings.save()

    def test_01_public_journey_page_renders_200_and_seeded_data(self):
        """Public /about/journey/ renders HTTP 200 with all default seeded sections."""
        res = Client().get('/about/journey/')
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, 'Growing Together, Building Careers, <span>Creating Success</span>')
        self.assertContains(res, 'Our Story')
        self.assertContains(res, 'How Far We&#x27;ve Come')
        self.assertContains(res, 'Our <span>Milestones</span>')
        self.assertContains(res, 'Our Impact')
        self.assertContains(res, 'Our Journey In <span>Numbers</span>')
        self.assertContains(res, 'Looking Ahead')

    def test_02_journey_section_visibility_toggles(self):
        """Toggling section visibility flags hides the respective sections completely."""
        from apps.core.models import OurJourneySettings
        settings = OurJourneySettings.get_settings()
        settings.hero_visible = False
        settings.story_visible = False
        settings.numbers_visible = False
        settings.ahead_visible = False
        settings.save()

        res = Client().get('/about/journey/')
        self.assertEqual(res.status_code, 200)
        self.assertNotContains(res, 'class="oj-hero"')
        self.assertNotContains(res, 'class="oj-story"')
        self.assertNotContains(res, 'class="oj-numbers"')
        self.assertNotContains(res, 'class="oj-looking-ahead"')

        # Timeline and milestones are still visible
        self.assertContains(res, 'class="oj-timeline-section"')
        self.assertContains(res, 'class="oj-milestones"')

    def test_03_admin_save_journey_content_immediately_updates_live_page(self):
        """Admin POST updates clean titles, highlighted words, descriptions, and CTA links immediately."""
        from apps.core.models import OurJourneySettings

        post_data = {
            'about_subpage': 'journey',
            'journey_has_toggles': '1',
            'hero_visible': 'on',
            'hero_eyebrow': 'Exclusive Journey',
            'hero_clean_title': 'Transforming Careers Across The Nation',
            'hero_highlight_word': 'Across The Nation',
            'hero_description': 'Our commitment to recruitment excellence and industry leadership.',
            'stat1_num': '2020',
            'stat1_label': 'Inception Year',
            'badge_num': '10+',
            'badge_text': 'Decade of Trust',
            'hero_btn1_text': 'Read Our History',
            'hero_btn1_url': '#oj-story',
            'story_visible': 'on',
            'story_tag': 'Heritage & Roots',
            'story_clean_title': 'How Our Foundation Was Laid',
            'story_highlight_word': 'Foundation',
            'timeline_visible': 'on',
            'timeline_tag': 'Our Evolution',
            'timeline_clean_title': 'Year by Year Evolution',
            'timeline_highlight_word': 'Evolution',
            'milestones_visible': 'on',
            'milestones_clean_title': 'Proud Achievements Record',
            'milestones_highlight_word': 'Achievements',
            'impact_visible': 'on',
            'impact_clean_title': 'Measurable Impact For Clients',
            'impact_highlight_word': 'Impact',
            'numbers_visible': 'on',
            'numbers_clean_title': 'Stats That Matter Most',
            'numbers_highlight_word': 'Stats',
            'ahead_visible': 'on',
            'ahead_clean_title': 'Vision For The Next Decade',
            'ahead_highlight_word': 'Next Decade',
            'cta_btn1_text': 'Join Us Today',
            'cta_btn1_url': '/contact/',
            'meta_title': 'Custom Journey Title | Sky Vision',
            'meta_description': 'SEO description for our journey page testing.',
        }
        res = self.client.post('/admin-panel/website/about/?page=journey', post_data)
        self.assertEqual(res.status_code, 302)
        self.assertEqual(res['Location'], '/admin-panel/website/about/?page=journey')

        # Check DB
        settings = OurJourneySettings.get_settings()
        self.assertEqual(settings.hero_eyebrow, 'Exclusive Journey')
        self.assertEqual(settings.hero_clean_title, 'Transforming Careers Across The Nation')
        self.assertEqual(settings.hero_highlight_word, 'Across The Nation')
        self.assertEqual(settings.hero_title, 'Transforming Careers <span>Across The Nation</span>')
        self.assertEqual(settings.story_title, 'How Our <span>Foundation</span> Was Laid')
        self.assertEqual(settings.meta_title, 'Custom Journey Title | Sky Vision')

        # Check public page immediately reflects new content
        pub_res = Client().get('/about/journey/')
        self.assertEqual(pub_res.status_code, 200)
        self.assertContains(pub_res, 'Exclusive Journey')
        self.assertContains(pub_res, 'Transforming Careers <span>Across The Nation</span>')
        self.assertContains(pub_res, 'How Our <span>Foundation</span> Was Laid')
        self.assertContains(pub_res, 'Year by Year <span>Evolution</span>')
        self.assertContains(pub_res, 'Proud <span>Achievements</span> Record')
        self.assertContains(pub_res, '<span>Stats</span> That Matter Most')
        self.assertContains(pub_res, 'Join Us Today')
        self.assertContains(pub_res, 'Custom Journey Title | Sky Vision')

    def test_04_repeatables_crud_via_json(self):
        """Admin can add, update, and reorder all 7 repeatable models via hidden JSON inputs."""
        from apps.core.models import (
            JourneyStoryParagraph, JourneyStoryCard, JourneyMilestone,
            JourneyMilestoneCard, JourneyImpactItem, JourneyStat, JourneyFutureGoal
        )

        paragraphs_payload = [
            {'id': None, 'paragraph_text': 'First paragraph describing early days.', 'is_highlight': True, 'order': 1, 'is_visible': True},
            {'id': None, 'paragraph_text': 'Second paragraph describing scaling phase.', 'is_highlight': False, 'order': 2, 'is_visible': True},
        ]
        story_cards_payload = [
            {'id': None, 'title': 'Speed & Quality', 'icon': 'fa-solid fa-bolt', 'color': 'red', 'description': 'Placing candidates faster without cutting corners.', 'order': 1, 'is_visible': True},
        ]
        timeline_payload = [
            {'id': None, 'year': '2023', 'badge_label': '1000 Placed', 'title': 'First Major Milestone', 'description': 'Reached four figures in successful candidate placements.', 'icon_class': 'fa-solid fa-trophy', 'order': 1, 'is_visible': True},
            {'id': None, 'year': '2025', 'badge_label': 'Pan-India', 'title': 'National Expansion', 'description': 'Expanded service branches across major metro cities.', 'icon_class': 'fa-solid fa-earth-asia', 'order': 2, 'is_visible': True},
        ]
        milestone_cards_payload = [
            {'id': None, 'year': '2024', 'title': 'Best Recruitment Award', 'icon_class': 'fa-solid fa-award', 'description': 'Recognized as leading consultant in northern region.', 'order': 1, 'is_visible': True},
        ]
        impact_items_payload = [
            {'id': None, 'title': '99% Compliance Record', 'icon': 'fa-solid fa-shield-check', 'description': 'All background checks and paperwork fully verified.', 'order': 1, 'is_visible': True},
        ]
        stats_payload = [
            {'id': None, 'count': 750, 'suffix': '+', 'label': 'Corporate Tie-ups', 'icon': 'fa-solid fa-handshake', 'order': 1, 'is_visible': True},
            {'id': None, 'count': 99, 'suffix': '%', 'label': 'On-Time Placements', 'icon': 'fa-solid fa-clock', 'order': 2, 'is_visible': True},
        ]
        goals_payload = [
            {'id': None, 'text': 'Expand AI-driven matchmaking capabilities', 'icon': 'fa-solid fa-robot', 'order': 1, 'is_visible': True},
        ]

        post_data = {
            'about_subpage': 'journey',
            'journey_has_toggles': '1',
            'hero_visible': 'on',
            'story_visible': 'on',
            'timeline_visible': 'on',
            'milestones_visible': 'on',
            'impact_visible': 'on',
            'numbers_visible': 'on',
            'ahead_visible': 'on',
            'journey_paragraphs_json': json.dumps(paragraphs_payload),
            'journey_story_cards_json': json.dumps(story_cards_payload),
            'journey_timeline_json': json.dumps(timeline_payload),
            'journey_milestone_cards_json': json.dumps(milestone_cards_payload),
            'journey_impact_items_json': json.dumps(impact_items_payload),
            'journey_stats_json': json.dumps(stats_payload),
            'journey_future_goals_json': json.dumps(goals_payload),
        }
        res = self.client.post('/admin-panel/website/about/?page=journey', post_data)
        self.assertEqual(res.status_code, 302)

        # Check DB counts
        self.assertEqual(JourneyStoryParagraph.objects.count(), 2)
        self.assertEqual(JourneyStoryCard.objects.count(), 1)
        self.assertEqual(JourneyMilestone.objects.count(), 2)
        self.assertEqual(JourneyMilestoneCard.objects.count(), 1)
        self.assertEqual(JourneyImpactItem.objects.count(), 1)
        self.assertEqual(JourneyStat.objects.count(), 2)
        self.assertEqual(JourneyFutureGoal.objects.count(), 1)

        # Check public page displays items
        pub_res = Client().get('/about/journey/')
        self.assertEqual(pub_res.status_code, 200)
        self.assertContains(pub_res, 'First paragraph describing early days.')
        self.assertContains(pub_res, 'oj-story-lead')
        self.assertContains(pub_res, 'Speed &amp; Quality')
        self.assertContains(pub_res, 'First Major Milestone')
        self.assertContains(pub_res, 'Best Recruitment Award')
        self.assertContains(pub_res, '99% Compliance Record')
        self.assertContains(pub_res, 'Corporate Tie-ups')
        self.assertContains(pub_res, 'data-count="750"')
        self.assertContains(pub_res, 'data-suffix="+"')
        self.assertContains(pub_res, 'Expand AI-driven matchmaking capabilities')

    def test_05_inactive_items_do_not_render_on_public_page(self):
        """Items marked with is_visible=False are excluded from the public template."""
        from apps.core.models import JourneyStat, JourneyFutureGoal
        JourneyStat.objects.all().delete()
        JourneyFutureGoal.objects.all().delete()

        JourneyStat.objects.create(count=123, suffix="+", label="Visible Metric", is_visible=True, order=1)
        JourneyStat.objects.create(count=999, suffix="%", label="Secret Hidden Metric", is_visible=False, order=2)

        JourneyFutureGoal.objects.create(text="Public Goal 2026", is_visible=True, order=1)
        JourneyFutureGoal.objects.create(text="Confidential Future Plan", is_visible=False, order=2)

        pub_res = Client().get('/about/journey/')
        self.assertEqual(pub_res.status_code, 200)
        self.assertContains(pub_res, 'Visible Metric')
        self.assertNotContains(pub_res, 'Secret Hidden Metric')
        self.assertContains(pub_res, 'Public Goal 2026')
        self.assertNotContains(pub_res, 'Confidential Future Plan')

    def test_06_non_admin_cannot_access_admin_journey_endpoint(self):
        """Unauthenticated or regular users cannot access the website about management endpoint."""
        anon_client = Client()
        # GET should redirect to admin login
        res_get = anon_client.get('/admin-panel/website/about/?page=journey')
        self.assertEqual(res_get.status_code, 302)
        self.assertIn('/admin-panel/login/', res_get['Location'])

        # POST should redirect to admin login
        res_post = anon_client.post('/admin-panel/website/about/?page=journey', {'about_subpage': 'journey'})
        self.assertEqual(res_post.status_code, 302)
        self.assertIn('/admin-panel/login/', res_post['Location'])

    def test_07_journey_image_upload_and_removal(self):
        """Admin can upload hero, story, and impact images, and later remove them."""
        from django.core.files.uploadedfile import SimpleUploadedFile
        from apps.core.models import OurJourneySettings

        # 1x1 transparent GIF image
        gif_content = b'GIF89a\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00\xff\xff\xff!\xf9\x04\x01\x00\x00\x00\x00,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;'
        uploaded_hero = SimpleUploadedFile("test_journey_hero.png", gif_content, content_type="image/png")

        post_data = {
            'about_subpage': 'journey',
            'hero_visible': 'on',
            'hero_image': uploaded_hero,
        }
        res = self.client.post('/admin-panel/website/about/?page=journey', post_data)
        self.assertEqual(res.status_code, 302)

        settings = OurJourneySettings.get_settings()
        self.assertTrue(bool(settings.hero_image))
        self.assertTrue(settings.hero_image.name.startswith('branding/'))

        # Now remove image
        remove_data = {
            'about_subpage': 'journey',
            'hero_visible': 'on',
            'remove_hero_image': '1',
        }
        res_rem = self.client.post('/admin-panel/website/about/?page=journey', remove_data)
        self.assertEqual(res_rem.status_code, 302)

        settings.refresh_from_db()
        self.assertFalse(bool(settings.hero_image))
        self.assertEqual(settings.get_hero_image(), 'https://images.unsplash.com/photo-1600880292203-757bb62b4baf?w=1000&q=80')


class ManpowerSupplySettingsTestCase(TestCase):
    """
    Comprehensive test suite for the dynamic Manpower Supply service page:
    1. Default public page renders successfully with seeded sections and repeaters.
    2. Master section visibility toggles work seamlessly (hide & show).
    3. Admin saves configuration via POST and changes reflect immediately on public frontend.
    4. Full CRUD and reordering of all 8 repeatable models via JSON inputs.
    5. Non-admin access control & redirection.
    6. Image upload and removal with fallback preservation.
    """

    def setUp(self):
        from apps.accounts.models import AdminUser
        from apps.core.models import ManpowerSupplySettings
        from apps.core.views import seed_initial_manpower_supply_data

        # Create active AdminUser
        self.admin = AdminUser.objects.create(
            email="manpower_superadmin@skyvisiongoc.com",
            is_active=True
        )
        self.admin.set_password("AdminPass2026!")
        self.admin.save()

        # Seed initial manpower supply data
        seed_initial_manpower_supply_data()

        # Authenticated client
        self.client = Client()
        session = self.client.session
        session['admin_id'] = self.admin.id
        session.save()

    def test_01_public_page_default_rendering(self):
        """Public manpower supply page renders all sections and seeded defaults."""
        pub_res = Client().get('/services/manpower-supply/')
        self.assertEqual(pub_res.status_code, 200)

        # Hero
        self.assertContains(pub_res, 'Workforce Solutions')
        self.assertContains(pub_res, 'Manpower Supply')
        self.assertContains(pub_res, 'Services')
        self.assertContains(pub_res, 'Right People')
        self.assertContains(pub_res, 'Right Skills')
        self.assertContains(pub_res, 'Verified &amp;')
        self.assertContains(pub_res, 'Trained Workforce')
        self.assertContains(pub_res, 'On Time')

        # About
        self.assertContains(pub_res, 'About Manpower Supply')
        self.assertContains(pub_res, 'Powering Businesses with the Right Workforce')
        self.assertContains(pub_res, 'Quality Manpower')

        # Services
        self.assertContains(pub_res, 'Our Manpower Supply Services')
        self.assertContains(pub_res, 'We Provide the Best Manpower Solutions')
        self.assertContains(pub_res, 'Skilled Manpower')

        # Industries & Why Choose
        self.assertContains(pub_res, 'Industries We Serve')
        self.assertContains(pub_res, 'Serving a Wide Range of Industries')
        self.assertContains(pub_res, 'Manufacturing')
        self.assertContains(pub_res, 'Why Choose Sky Vision')
        self.assertContains(pub_res, 'Your Trusted Manpower Partner')
        self.assertContains(pub_res, 'Experienced Team')

        # Process
        self.assertContains(pub_res, 'Our Recruitment Process')
        self.assertContains(pub_res, 'Simple Process to Find the Right People')
        self.assertContains(pub_res, 'Requirement Analysis')

        # Stats
        self.assertContains(pub_res, '5000+')
        self.assertContains(pub_res, 'Candidates Placed')

        # FAQs & CTA
        self.assertContains(pub_res, 'Frequently Asked Questions')
        self.assertContains(pub_res, 'Need Manpower For Your Business?')
        self.assertContains(pub_res, 'We are Ready to Help You!')

        # Trust Strip
        self.assertContains(pub_res, 'Trusted by')
        self.assertContains(pub_res, 'Top Companies')

    def test_02_section_visibility_toggles(self):
        """Disabling section switches in admin hides those sections from the public page."""
        from apps.core.models import ManpowerSupplySettings
        from django.core.cache import cache

        settings = ManpowerSupplySettings.get_settings()
        settings.hero_visible = False
        settings.about_visible = False
        settings.services_visible = False
        settings.industries_why_visible = False
        settings.process_visible = False
        settings.stats_visible = False
        settings.faq_cta_visible = False
        settings.trust_visible = False
        settings.save()

        cache.clear()

        pub_res = Client().get('/services/manpower-supply/')
        self.assertEqual(pub_res.status_code, 200)

        # Check all hidden section wrappers are excluded
        self.assertNotContains(pub_res, 'class="ms-hero"')
        self.assertNotContains(pub_res, 'class="ms-about"')
        self.assertNotContains(pub_res, 'class="ms-services"')
        self.assertNotContains(pub_res, 'class="ms-split"')
        self.assertNotContains(pub_res, 'class="sv-process"')
        self.assertNotContains(pub_res, 'class="ms-stats"')
        self.assertNotContains(pub_res, 'class="ms-faq-cta"')
        self.assertNotContains(pub_res, 'class="ms-trust"')

    def test_03_admin_saves_manpower_supply_reflects_live(self):
        """Admin saves text configuration via POST and changes reflect immediately on public frontend."""
        from apps.core.models import ManpowerSupplySettings

        post_data = {
            'srv_subpage': 'manpower_supply',
            'hero_visible': 'on',
            'about_visible': 'on',
            'services_visible': 'on',
            'industries_why_visible': 'on',
            'process_visible': 'on',
            'stats_visible': 'on',
            'faq_cta_visible': 'on',
            'trust_visible': 'on',
            # Hero
            'hero_eyebrow': 'Elite Workforce Staffing',
            'hero_title': 'Enterprise Manpower & Contract Deployment',
            'hero_subtitle': 'Premier enterprise human capital and industrial deployment across India.',
            'hero_feat1_text': 'Zero-Day Onboarding',
            'hero_feat2_text': 'Full Statutory Compliance',
            'hero_feat3_text': 'PAN-India Reach',
            'hero_badge_text': '100% Certified Talent',
            'hero_enquire_btn_text': 'Hire Manpower Now',
            'hero_enquire_btn_url': '/contact/?type=manpower',
            'hero_call_btn_text': 'Direct Helpline',
            'hero_call_phone': '+91 70681 15299',
            # About
            'about_tag': 'About Our Staffing Network',
            'about_title': 'Powering Pan-India Enterprises With Certified Talent',
            'about_description': 'Decade of excellence delivering industrial staffing solutions.',
            # Services
            'services_tag': 'Dedicated Service Verticals',
            'services_title': 'Tailored Manpower Solutions For High Growth Enterprises',
            # Industries & Why Choose
            'industries_tag': 'Key Industry Verticals',
            'industries_title': 'Serving High Impact Sectors Globally',
            'why_choose_tag': 'Our Competitive Edge',
            'why_choose_title': 'Why India Top Companies Partner With Sky Vision',
            # Process
            'process_tag': 'Workforce Deployment Workflow',
            'process_title': 'Fast & Transparent 5-Step Staffing Pipeline',
            'process_subtitle': 'Step-by-step verified candidate onboarding pipeline.',
            # FAQ & CTA
            'faq_tag': 'Frequently Asked Questions on Manpower Solutions',
            'cta_tag': 'Immediate Workforce Requirement?',
            'cta_title': 'Scale Your Workforce Today with Sky Vision',
            'cta_subtitle': 'Customized workforce solutions delivered within days.',
            'cta_call_btn_text': 'Direct Call',
            'cta_call_phone': '+91 70681 15299',
            'cta_enquire_btn_text': 'Request Workforce Quote',
            'cta_enquire_url': '/contact/?type=quote',
            # SEO
            'meta_title': 'Best Manpower Supply Services in India | Sky Vision Group',
            'meta_description': 'Leading manpower supply and staffing consultancy providing verified workforce.',
        }

        res = self.client.post('/admin-panel/website/services/?page=manpower_supply', post_data)
        self.assertEqual(res.status_code, 302)
        self.assertEqual(res['Location'], '/admin-panel/website/services/?page=manpower_supply')

        # Check DB
        settings = ManpowerSupplySettings.get_settings()
        self.assertEqual(settings.hero_eyebrow, 'Elite Workforce Staffing')
        self.assertEqual(settings.hero_title, 'Enterprise Manpower & Contract Deployment')
        self.assertEqual(settings.hero_feat1_text, 'Zero-Day Onboarding')
        self.assertEqual(settings.about_title, 'Powering Pan-India Enterprises With Certified Talent')
        self.assertEqual(settings.services_title, 'Tailored Manpower Solutions For High Growth Enterprises')
        self.assertEqual(settings.meta_title, 'Best Manpower Supply Services in India | Sky Vision Group')

        # Check public page immediately reflects updated content
        pub_res = Client().get('/services/manpower-supply/')
        self.assertEqual(pub_res.status_code, 200)
        self.assertContains(pub_res, 'Elite Workforce Staffing')
        self.assertContains(pub_res, 'Enterprise Manpower & Contract Deployment')
        self.assertContains(pub_res, 'Zero-Day Onboarding')
        self.assertContains(pub_res, 'Full Statutory Compliance')
        self.assertContains(pub_res, 'PAN-India Reach')
        self.assertContains(pub_res, 'Powering Pan-India Enterprises With Certified Talent')
        self.assertContains(pub_res, 'Tailored Manpower Solutions For High Growth Enterprises')
        self.assertContains(pub_res, 'Scale Your Workforce Today with Sky Vision')
        self.assertContains(pub_res, 'Request Workforce Quote')
        self.assertContains(pub_res, 'Best Manpower Supply Services in India | Sky Vision Group')

    def test_04_repeatables_crud_via_json(self):
        """Admin can add, update, reorder, and delete all 8 repeatable models via JSON inputs."""
        from apps.core.models import (
            ManpowerChecklistItem, ManpowerServiceCard, ManpowerIndustryItem,
            ManpowerWhyChooseItem, ManpowerProcessStep, ManpowerStatItem,
            ManpowerFaqItem, ManpowerTrustItem
        )

        checklist_payload = [
            {'id': None, 'text': 'Specialized Engineering Technicians', 'order': 1, 'is_visible': True},
            {'id': None, 'text': '100% Police Verified & Screened', 'order': 2, 'is_visible': True},
        ]
        services_payload = [
            {
                'id': None,
                'title': 'Aviation Technicians',
                'description': 'Certified hangar and line maintenance staff.',
                'icon_class': 'fa-solid fa-plane-up',
                'color_class': 'i-blue',
                'order': 1,
                'is_visible': True
            }
        ]
        industries_payload = [
            {'id': None, 'name': 'Aerospace & Defense', 'icon_class': 'fa-solid fa-jet-fighter', 'order': 1, 'is_visible': True},
            {'id': None, 'name': 'Renewable Solar Energy', 'icon_class': 'fa-solid fa-solar-panel', 'order': 2, 'is_visible': True},
        ]
        why_choose_payload = [
            {
                'id': None,
                'title': 'Zero Compliance Liability',
                'icon_class': 'fa-solid fa-scale-balanced',
                'order': 1,
                'is_visible': True
            }
        ]
        process_payload = [
            {
                'id': None,
                'step_number': '01',
                'title': 'Client Requirement Audit',
                'icon_class': 'fa-solid fa-clipboard-list',
                'order': 1,
                'is_visible': True
            }
        ]
        stats_payload = [
            {'id': None, 'value': '15,000+', 'label': 'Active Contract Staff', 'icon_class': 'fa-solid fa-user-group', 'order': 1, 'is_visible': True},
            {'id': None, 'value': '99.8%', 'label': 'On-Time Attendance', 'icon_class': 'fa-solid fa-clock', 'order': 2, 'is_visible': True},
        ]
        faqs_payload = [
            {
                'id': None,
                'question': 'How quickly can 50+ workers be deployed?',
                'answer': 'Our ready mobilization pool allows deployment within 48 to 72 hours.',
                'order': 1,
                'is_visible': True
            }
        ]
        trust_payload = [
            {
                'id': None,
                'icon_class': 'fa-solid fa-file-shield',
                'line1': 'ISO 9001:2015',
                'line2': 'Certified Quality',
                'order': 1,
                'is_visible': True
            }
        ]

        post_data = {
            'srv_subpage': 'manpower_supply',
            'hero_visible': 'on',
            'about_visible': 'on',
            'services_visible': 'on',
            'industries_why_visible': 'on',
            'process_visible': 'on',
            'stats_visible': 'on',
            'faq_cta_visible': 'on',
            'trust_visible': 'on',
            'manpower_checklist_json': json.dumps(checklist_payload),
            'manpower_services_json': json.dumps(services_payload),
            'manpower_industries_json': json.dumps(industries_payload),
            'manpower_why_choose_json': json.dumps(why_choose_payload),
            'manpower_process_json': json.dumps(process_payload),
            'manpower_stats_json': json.dumps(stats_payload),
            'manpower_faqs_json': json.dumps(faqs_payload),
            'manpower_trust_json': json.dumps(trust_payload),
        }

        res = self.client.post('/admin-panel/website/services/?page=manpower_supply', post_data)
        self.assertEqual(res.status_code, 302)

        # Check DB counts
        self.assertEqual(ManpowerChecklistItem.objects.count(), 2)
        self.assertEqual(ManpowerServiceCard.objects.count(), 1)
        self.assertEqual(ManpowerIndustryItem.objects.count(), 2)
        self.assertEqual(ManpowerWhyChooseItem.objects.count(), 1)
        self.assertEqual(ManpowerProcessStep.objects.count(), 1)
        self.assertEqual(ManpowerStatItem.objects.count(), 2)
        self.assertEqual(ManpowerFaqItem.objects.count(), 1)
        self.assertEqual(ManpowerTrustItem.objects.count(), 1)

        # Check public page reflects new items
        pub_res = Client().get('/services/manpower-supply/')
        self.assertEqual(pub_res.status_code, 200)
        self.assertContains(pub_res, 'Specialized Engineering Technicians')
        self.assertContains(pub_res, '100% Police Verified &amp; Screened')
        self.assertContains(pub_res, 'Aviation Technicians')
        self.assertContains(pub_res, 'Aerospace &amp; Defense')
        self.assertContains(pub_res, 'Renewable Solar Energy')
        self.assertContains(pub_res, 'Zero Compliance Liability')
        self.assertContains(pub_res, 'Client Requirement Audit')
        self.assertContains(pub_res, '15,000+')
        self.assertContains(pub_res, 'Active Contract Staff')
        self.assertContains(pub_res, 'How quickly can 50+ workers be deployed?')
        self.assertContains(pub_res, 'ISO 9001:2015')
        self.assertContains(pub_res, 'Certified Quality')

    def test_05_non_admin_cannot_access_endpoint(self):
        """Unauthenticated or regular user cannot access or modify manpower supply settings."""
        anon_client = Client()
        res_get = anon_client.get('/admin-panel/website/services/?page=manpower_supply')
        self.assertEqual(res_get.status_code, 302)
        self.assertIn('/admin-panel/login/', res_get['Location'])

        res_post = anon_client.post('/admin-panel/website/services/?page=manpower_supply', {'srv_subpage': 'manpower_supply'})
        self.assertEqual(res_post.status_code, 302)
        self.assertIn('/admin-panel/login/', res_post['Location'])

    def test_06_image_upload_and_removal(self):
        """Admin can upload hero, about, and cta images, and later remove them."""
        from django.core.files.uploadedfile import SimpleUploadedFile
        from apps.core.models import ManpowerSupplySettings

        gif_content = b'GIF89a\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00\xff\xff\xff!\xf9\x04\x01\x00\x00\x00\x00,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;'
        uploaded_hero = SimpleUploadedFile("ms_hero.png", gif_content, content_type="image/png")
        uploaded_about = SimpleUploadedFile("ms_about.png", gif_content, content_type="image/png")
        uploaded_cta = SimpleUploadedFile("ms_cta.png", gif_content, content_type="image/png")

        post_data = {
            'srv_subpage': 'manpower_supply',
            'hero_visible': 'on',
            'about_visible': 'on',
            'faq_cta_visible': 'on',
            'hero_image': uploaded_hero,
            'about_image': uploaded_about,
            'cta_image': uploaded_cta,
        }
        res = self.client.post('/admin-panel/website/services/?page=manpower_supply', post_data)
        self.assertEqual(res.status_code, 302)

        settings = ManpowerSupplySettings.get_settings()
        self.assertTrue(bool(settings.hero_image))
        self.assertTrue(bool(settings.about_image))
        self.assertTrue(bool(settings.cta_image))
        self.assertTrue(settings.hero_image.name.startswith('branding/'))

        # Remove images
        remove_data = {
            'srv_subpage': 'manpower_supply',
            'hero_visible': 'on',
            'remove_hero_image': '1',
            'remove_about_image': '1',
            'remove_cta_image': '1',
        }
        res_rem = self.client.post('/admin-panel/website/services/?page=manpower_supply', remove_data)
        self.assertEqual(res_rem.status_code, 302)

        settings.refresh_from_db()
        self.assertFalse(bool(settings.hero_image))
        self.assertFalse(bool(settings.about_image))
        self.assertFalse(bool(settings.cta_image))
        self.assertEqual(settings.get_hero_image(), '/static/images/services/manpower-supply.png')
