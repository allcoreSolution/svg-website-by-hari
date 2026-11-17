from django.db import migrations


def seed_site_data(apps, schema_editor):
    SiteSettings = apps.get_model('core', 'SiteSettings')
    NavItem = apps.get_model('core', 'NavItem')
    FooterColumn = apps.get_model('core', 'FooterColumn')
    FooterLink = apps.get_model('core', 'FooterLink')
    SocialLink = apps.get_model('core', 'SocialLink')
    FooterService = apps.get_model('core', 'FooterService')

    # 1. SiteSettings
    if not SiteSettings.objects.exists():
        SiteSettings.objects.create(
            site_name="Sky Vision Group of Consultancy",
            tagline="Right Talent, Bright Future.",
            logo_alt_text="Sky Vision Group Consultancy Logo",
            topbar_address="Indira Nagar, Lucknow, UP",
            support_email="info@skyvisiongroup.in",
            topbar_hours="Mon – Sat, 9:30 AM – 6:30 PM",
            helpline_phone="+91 88531 11111",
            secondary_phone="+91 7068115299",
            announcement_text="🚀 Free Career Counselling & Interview Training available this week at Gomti Nagar office!",
            show_announcement=True,
            franchise_url="/contact/",
            show_franchise_btn=True,
            navbar_call_text="+91 7068115299",
            navbar_call_number="+917068115299",
            show_login_btn=True,
            footer_about="Delivering excellence through personalized service and innovative solutions — bespoke recruitment, HR and consultancy that helps businesses and individuals grow with confidence.",
            office_address="12/2 Arvindo Park Road, Sector 12, Indira Nagar, Lucknow, UP",
            office_email="info@skyvisiongroup.in",
            office_phone_1="+91 7068115299",
            office_phone_2="+91 9532625299",
            working_hours="Mon – Sat: 9:30 AM – 6:30 PM",
            copyright_text="© 2026 Sky Vision Group Consultancy. All rights reserved.",
            privacy_policy_url="#",
            terms_url="#",
            footer_credit="Designed with ❤️ by Allcore Solution",
            floating_call_number="+917068115299",
            floating_whatsapp_url="https://whatsapp.com/channel/0029VamiX875K3zaWy6ysU31",
            show_floating_buttons=True,
        )

    # 2. Social Links
    social_defaults = [
        ('facebook', 'https://www.facebook.com/share/197C5xryds/', True, 1),
        ('instagram', 'https://www.instagram.com/skyvisiongroupconsultancy?igsh=NGpkb2NnZ2hhM21k', True, 2),
        ('linkedin', 'https://www.linkedin.com/company/skyvisiongroup/', True, 3),
        ('youtube', 'https://youtube.com/@skyvisiongroupconsultancy?si=-b8dk8MV6SzJfhM1', True, 4),
        ('twitter', 'https://x.com/skyvisiongroup', False, 5),
        ('whatsapp', 'https://whatsapp.com/channel/0029VamiX875K3zaWy6ysU31', True, 6),
    ]
    if not SocialLink.objects.exists():
        for plat, url, enabled, ord_num in social_defaults:
            SocialLink.objects.create(
                platform=plat,
                url=url,
                is_enabled=enabled,
                order=ord_num
            )

    # 3. Primary NavItems
    if not NavItem.objects.exists():
        # Home
        NavItem.objects.create(label="Home", url="/", active_key="home", order=1, is_visible=True)

        # About Us (Parent)
        about_nav = NavItem.objects.create(label="About Us", url="#", active_key="about", order=2, is_visible=True)
        NavItem.objects.create(parent=about_nav, label="About Company", url="/about/", order=1, is_visible=True)
        NavItem.objects.create(parent=about_nav, label="Our Team", url="/about/team/", order=2, is_visible=True)
        NavItem.objects.create(parent=about_nav, label="CEO & Founder", url="/about/ceo/", order=3, is_visible=True)
        NavItem.objects.create(parent=about_nav, label="Journey", url="/about/journey/", order=4, is_visible=True)

        # Services (Parent)
        serv_nav = NavItem.objects.create(label="Services", url="/services/", active_key="services", order=3, is_visible=True)
        NavItem.objects.create(parent=serv_nav, label="Manpower Supply", url="/services/manpower-supply/", order=1, is_visible=True)
        NavItem.objects.create(parent=serv_nav, label="Recruitment & Placement", url="/services/recruitment-placement/", order=2, is_visible=True)
        NavItem.objects.create(parent=serv_nav, label="Contract Staffing", url="/contract-staffing/", order=3, is_visible=True)
        NavItem.objects.create(parent=serv_nav, label="Educational Consultancy", url="/services/educational-consultancy/", order=4, is_visible=True)
        NavItem.objects.create(parent=serv_nav, label="Payroll & Outsourcing", url="/services/payroll-outsourcing/", order=5, is_visible=True)
        NavItem.objects.create(parent=serv_nav, label="HR Support", url="/services/hr-support/", order=6, is_visible=True)
        NavItem.objects.create(parent=serv_nav, label="Internship Programme", url="/services/internship/", order=7, is_visible=True)
        NavItem.objects.create(parent=serv_nav, label="Career Counselling", url="/careers/", order=8, is_visible=True)

        # Standalone items
        NavItem.objects.create(label="Job", url="/job/", active_key="jobs", order=4, is_visible=True)
        NavItem.objects.create(label="Gallery", url="/gallery/", active_key="gallery", order=5, is_visible=True)
        NavItem.objects.create(label="Career", url="/careers/", active_key="careers", order=6, is_visible=True)
        NavItem.objects.create(label="Blog", url="/blog/", active_key="blog", order=7, is_visible=True)
        NavItem.objects.create(label="Contact Us", url="/contact/", active_key="contact", order=8, is_visible=True)

    # 4. Footer Columns & Links
    if not FooterColumn.objects.exists():
        company_col = FooterColumn.objects.create(title="Company", order=1, is_visible=True)
        FooterLink.objects.create(column=company_col, label="Home", url="/", order=1, is_visible=True)
        FooterLink.objects.create(column=company_col, label="About Us", url="/about/", order=2, is_visible=True)
        FooterLink.objects.create(column=company_col, label="Services", url="/services/", order=3, is_visible=True)
        FooterLink.objects.create(column=company_col, label="Internship", url="/services/internship/", order=4, is_visible=True)
        FooterLink.objects.create(column=company_col, label="Jobs", url="/job/", order=5, is_visible=True)
        FooterLink.objects.create(column=company_col, label="Gallery", url="/gallery/", order=6, is_visible=True)

    # 5. Footer Services
    if not FooterService.objects.exists():
        services_defaults = [
            ("Manpower Supply", "/services/manpower-supply/", 1),
            ("Recruitment & Placement", "/services/recruitment-placement/", 2),
            ("Contract Staffing", "/contract-staffing/", 3),
            ("Educational Consultancy", "/services/educational-consultancy/", 4),
            ("Payroll & Outsourcing", "/services/payroll-outsourcing/", 5),
            ("Career Counselling", "/careers/", 6),
        ]
        for name, url, ord_num in services_defaults:
            FooterService.objects.create(name=name, url=url, order=ord_num, is_visible=True)


def unseed_site_data(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(seed_site_data, unseed_site_data),
    ]
