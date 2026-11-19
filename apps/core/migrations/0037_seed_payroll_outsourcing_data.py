from django.db import migrations


def seed_payroll_outsourcing_data(apps, schema_editor):
    PayrollOutsourcingSettings = apps.get_model('core', 'PayrollOutsourcingSettings')
    PoServiceCard = apps.get_model('core', 'PoServiceCard')
    PoIndustryItem = apps.get_model('core', 'PoIndustryItem')
    PoWhyChooseItem = apps.get_model('core', 'PoWhyChooseItem')
    PoProcessStep = apps.get_model('core', 'PoProcessStep')
    PoEmployerBenefit = apps.get_model('core', 'PoEmployerBenefit')
    PoEmployeeBenefit = apps.get_model('core', 'PoEmployeeBenefit')
    PoFaqItem = apps.get_model('core', 'PoFaqItem')

    # 1. Settings
    po = PayrollOutsourcingSettings.objects.first()
    if not po:
        po = PayrollOutsourcingSettings.objects.create(
            hero_visible=True,
            about_visible=True,
            services_visible=True,
            panel_visible=True,
            compare_visible=True,
            faq_visible=True,
            cta_visible=True,
            hero_eyebrow="Payroll & Outsourcing",
            hero_title="Payroll & Outsourcing Services",
            hero_subtitle="Streamline your payroll operations, ensure compliance, and manage your workforce efficiently with our expert payroll & outsourcing solutions.",
            hero_primary_btn_text="Get Free Consultation",
            hero_primary_btn_url="#contact",
            hero_secondary_btn_text="Contact Us",
            hero_secondary_btn_url="/contact/",
            about_tag="About Our Services",
            about_title="Complete Payroll & HR Outsourcing Solutions",
            about_description="We provide end-to-end payroll and outsourcing services that help businesses reduce operational burden, ensure accuracy, and stay 100% compliant with statutory regulations.",
            services_title="Our Payroll & Outsourcing Services",
            industries_tag="Industries We Serve",
            why_choose_tag="Why Choose Us?",
            process_tag="Our Payroll Process",
            employers_badge="For Employers",
            employees_badge="For Employees",
            faq_title="Frequently Asked Questions",
            cta_title="Focus On Growing Your Business We'll Handle Your Payroll!",
            cta_subtitle="Partner with us for secure, compliant and hassle-free payroll & outsourcing services.",
            cta_primary_btn_text="Get Free Consultation",
            cta_primary_btn_url="#contact",
            cta_secondary_btn_text="Contact Our Team",
            cta_secondary_btn_url="/contact/",
            meta_title="Payroll & Outsourcing Services — Sky Vision Group Consultancy",
            meta_description="Streamline your payroll operations, ensure compliance, and manage your workforce efficiently with our expert payroll & outsourcing solutions.",
            meta_keywords="payroll outsourcing, payroll processing, statutory compliance, PF ESI management, HR outsourcing",
        )
    else:
        # Ensure all visibility switches are enabled
        po.hero_visible = True
        po.about_visible = True
        po.services_visible = True
        po.panel_visible = True
        po.compare_visible = True
        po.faq_visible = True
        po.cta_visible = True
        if not po.hero_title:
            po.hero_title = "Payroll & Outsourcing Services"
        if not po.hero_eyebrow:
            po.hero_eyebrow = "Payroll & Outsourcing"
        if not po.hero_subtitle:
            po.hero_subtitle = "Streamline your payroll operations, ensure compliance, and manage your workforce efficiently with our expert payroll & outsourcing solutions."
        if not po.about_title:
            po.about_title = "Complete Payroll & HR Outsourcing Solutions"
        if not po.about_description:
            po.about_description = "We provide end-to-end payroll and outsourcing services that help businesses reduce operational burden, ensure accuracy, and stay 100% compliant with statutory regulations."
        if not po.services_title:
            po.services_title = "Our Payroll & Outsourcing Services"
        if not po.industries_tag:
            po.industries_tag = "Industries We Serve"
        if not po.why_choose_tag:
            po.why_choose_tag = "Why Choose Us?"
        if not po.process_tag:
            po.process_tag = "Our Payroll Process"
        if not po.employers_badge:
            po.employers_badge = "For Employers"
        if not po.employees_badge:
            po.employees_badge = "For Employees"
        if not po.faq_title:
            po.faq_title = "Frequently Asked Questions"
        if not po.cta_title:
            po.cta_title = "Focus On Growing Your Business We'll Handle Your Payroll!"
        if not po.cta_subtitle:
            po.cta_subtitle = "Partner with us for secure, compliant and hassle-free payroll & outsourcing services."
        po.save()

    # 2. Services
    if not PoServiceCard.objects.exists():
        services = [
            ("Payroll Processing", "Accurate salary calculation, payslip generation, and timely salary disbursement.", "fa-solid fa-file-invoice", "navy", 1),
            ("Attendance Management", "Track attendance, leaves, shifts, overtime and employee working hours.", "fa-regular fa-calendar-days", "amber", 2),
            ("PF & ESI Management", "Complete PF, ESI registration, contribution, returns and compliance management.", "fa-solid fa-people-group", "navy", 3),
            ("Compliance Management", "Ensure compliance with labour laws and statutory regulations.", "fa-solid fa-shield-halved", "amber", 4),
            ("Employee Records", "Maintain employee data, documents, contracts and HR records securely.", "fa-solid fa-folder-open", "navy", 5),
            ("HR Outsourcing", "End-to-end HR support including recruitment, onboarding & support.", "fa-solid fa-people-group", "amber", 6),
        ]
        for title, desc, icon, theme, order in services:
            PoServiceCard.objects.create(
                title=title,
                description=desc,
                icon_class=icon,
                badge_theme=theme,
                order=order,
                is_visible=True,
            )

    # 3. Industries
    if not PoIndustryItem.objects.exists():
        industries = [
            ("Manufacturing", 1),
            ("Retail", 2),
            ("IT & Software", 3),
            ("Construction", 4),
            ("BPO & Call Centers", 5),
            ("Hospitality", 6),
            ("Logistics & Warehousing", 7),
            ("Education", 8),
            ("Healthcare", 9),
            ("Banking & Finance", 10),
        ]
        for name, order in industries:
            PoIndustryItem.objects.create(name=name, order=order, is_visible=True)

    # 4. Why Choose
    if not PoWhyChooseItem.objects.exists():
        why_choose = [
            ("Accurate Payroll Processing", 1),
            ("100% Statutory Compliance", 2),
            ("Experienced Professionals", 3),
            ("Confidential & Secure Data", 4),
            ("Cost-Effective Solutions", 5),
            ("Timely Salary Processing", 6),
            ("Dedicated HR Support", 7),
            ("PAN India Services", 8),
        ]
        for title, order in why_choose:
            PoWhyChooseItem.objects.create(title=title, order=order, is_visible=True)

    # 5. Process Steps
    if not PoProcessStep.objects.exists():
        process_steps = [
            ("01", "Employee Data Collection", "fa-solid fa-database", 1),
            ("02", "Attendance Verification", "fa-solid fa-user-check", 2),
            ("03", "Salary Calculation", "fa-solid fa-calculator", 3),
            ("04", "PF, ESI & Tax Processing", "fa-solid fa-file-invoice-dollar", 4),
            ("05", "Salary Disbursement", "fa-solid fa-money-bill-transfer", 5),
            ("06", "Payslip Generation", "fa-solid fa-receipt", 6),
            ("07", "Compliance Reporting", "fa-solid fa-clipboard-check", 7),
        ]
        for step, title, icon, order in process_steps:
            PoProcessStep.objects.create(
                step_number=step,
                title=title,
                icon_class=icon,
                order=order,
                is_visible=True,
            )

    # 6. Employer Benefits
    if not PoEmployerBenefit.objects.exists():
        employer_benefits = [
            ("Reduced HR Workload", 1),
            ("Error-Free Payroll", 2),
            ("Legal Compliance", 3),
            ("Lower Administrative Cost", 4),
            ("Secure Employee Records", 5),
        ]
        for title, order in employer_benefits:
            PoEmployerBenefit.objects.create(title=title, order=order, is_visible=True)

    # 7. Employee Benefits
    if not PoEmployeeBenefit.objects.exists():
        employee_benefits = [
            ("Accurate Salary", 1),
            ("Timely Payments", 2),
            ("Digital Payslips", 3),
            ("PF & ESI Benefits", 4),
            ("Better HR Support", 5),
        ]
        for title, order in employee_benefits:
            PoEmployeeBenefit.objects.create(title=title, order=order, is_visible=True)

    # 8. FAQs
    if not PoFaqItem.objects.exists():
        faqs = [
            ("How often is payroll processed?", "Payroll is typically processed monthly, though custom cycles can be arranged.", 1),
            ("Is employee information secure?", "Yes, we follow strict data confidentiality and security protocols.", 2),
            ("Do you manage PF & ESI compliance?", "Yes, we handle complete PF, ESI registration, contribution and compliance filing.", 3),
            ("Can you manage payroll for multiple branches?", "Yes, we manage multi-location and multi-branch payroll seamlessly.", 4),
        ]
        for q, a, order in faqs:
            PoFaqItem.objects.create(question=q, answer=a, order=order, is_visible=True)


def unseed_payroll_outsourcing_data(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0036_alter_recruitmentplacementsettings_hero_hire_btn_url'),
    ]

    operations = [
        migrations.RunPython(seed_payroll_outsourcing_data, unseed_payroll_outsourcing_data),
    ]
