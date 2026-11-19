from django.db import migrations


def seed_hr_support_and_internship_data(apps, schema_editor):
    # ==========================
    # 1. HR SUPPORT SEED
    # ==========================
    HrSupportSettings = apps.get_model('core', 'HrSupportSettings')
    HrFeatureItem = apps.get_model('core', 'HrFeatureItem')
    HrServiceCard = apps.get_model('core', 'HrServiceCard')
    HrAdditionalServiceItem = apps.get_model('core', 'HrAdditionalServiceItem')
    HrWhyChooseItem = apps.get_model('core', 'HrWhyChooseItem')
    HrProcessStep = apps.get_model('core', 'HrProcessStep')
    HrEmployerBenefit = apps.get_model('core', 'HrEmployerBenefit')
    HrEmployeeBenefit = apps.get_model('core', 'HrEmployeeBenefit')

    hr_settings = HrSupportSettings.objects.first()
    if not hr_settings:
        hr_settings = HrSupportSettings.objects.create(
            hero_visible=True,
            about_visible=True,
            services_visible=True,
            additional_visible=True,
            why_choose_visible=True,
            process_visible=True,
            benefits_visible=True,
            cta_visible=True,
            hero_eyebrow="HR Support Services",
            hero_title="Empowering People. Strengthening Organizations.",
            hero_subtitle="We provide end-to-end HR support to help businesses build a motivated workforce, ensure compliance, and create a positive work environment.",
            hero_primary_btn_text="Get Free Consultation",
            hero_primary_btn_url="/contact/",
            hero_secondary_btn_text="Contact Us",
            hero_secondary_btn_url="/contact/",
            about_tag="About HR Support Services",
            about_title="Complete HR Solutions for Your Business",
            about_description="Our HR experts help you streamline HR operations, develop effective policies, engage employees, manage performance, and maintain accurate documentation.",
            services_tag="What We Offer",
            services_title="Our HR Support Services",
            additional_title="Additional HR Services",
            why_choose_tag="Why Choose Us?",
            process_tag="Our HR Support Process",
            benefits_tag="Benefits",
            employers_badge="For Employers",
            employees_badge="For Employees",
            cta_title="Build a Stronger Workforce with Professional HR Support",
            cta_subtitle="Let us handle your HR processes while you focus on growing your business.",
            cta_primary_btn_text="Schedule HR Consultation",
            cta_primary_btn_url="/contact/",
            cta_secondary_btn_text="Contact Our HR Team",
            cta_secondary_btn_url="/contact/",
            meta_title="HR Support Services — Sky Vision Group Consultancy",
            meta_description="We provide end-to-end HR support to help businesses build a motivated workforce, ensure compliance, and create a positive work environment.",
            meta_keywords="hr support, workplace policies, onboarding systems, hr advisory, employee engagement, performance management",
        )
    else:
        hr_settings.hero_visible = True
        hr_settings.about_visible = True
        hr_settings.services_visible = True
        hr_settings.additional_visible = True
        hr_settings.why_choose_visible = True
        hr_settings.process_visible = True
        hr_settings.benefits_visible = True
        hr_settings.cta_visible = True
        if not hr_settings.hero_eyebrow or "Updated" in hr_settings.hero_eyebrow:
            hr_settings.hero_eyebrow = "HR Support Services"
        if not hr_settings.hero_title:
            hr_settings.hero_title = "Empowering People. Strengthening Organizations."
        if not hr_settings.hero_subtitle or "Test" in hr_settings.hero_subtitle:
            hr_settings.hero_subtitle = "We provide end-to-end HR support to help businesses build a motivated workforce, ensure compliance, and create a positive work environment."
        if not hr_settings.about_title:
            hr_settings.about_title = "Complete HR Solutions for Your Business"
        if not hr_settings.about_description or "Test" in hr_settings.about_description:
            hr_settings.about_description = "Our HR experts help you streamline HR operations, develop effective policies, engage employees, manage performance, and maintain accurate documentation."
        if not hr_settings.services_title:
            hr_settings.services_title = "Our HR Support Services"
        if not hr_settings.cta_title or "TEST" in hr_settings.cta_title:
            hr_settings.cta_title = "Build a Stronger Workforce with Professional HR Support"
        hr_settings.save()

    # Clean dummy test data if present
    HrServiceCard.objects.filter(title__icontains="(TEST)").delete()
    HrServiceCard.objects.filter(title="qqqq").delete()
    HrFeatureItem.objects.filter(title="sss").delete()
    HrAdditionalServiceItem.objects.filter(title__icontains="(TEST)").delete()
    HrAdditionalServiceItem.objects.filter(title="www").delete()
    HrWhyChooseItem.objects.filter(title__icontains="(TEST)").delete()
    HrProcessStep.objects.filter(title__icontains="(TEST)").delete()
    HrProcessStep.objects.filter(title="rrr").delete()
    HrEmployerBenefit.objects.filter(title__icontains="(TEST)").delete()
    HrEmployerBenefit.objects.filter(title="ttttt").delete()
    HrEmployeeBenefit.objects.filter(title__icontains="(TEST)").delete()
    HrEmployeeBenefit.objects.filter(title="TTTT").delete()

    if not HrFeatureItem.objects.exists():
        features = [
            ("100% Statutory Compliance", "fa-solid fa-shield-halved", 1),
            ("Tailored HR Policies", "fa-solid fa-file-contract", 2),
            ("Dedicated HR Advisor", "fa-solid fa-user-tie", 3),
        ]
        for title, icon, order in features:
            HrFeatureItem.objects.create(title=title, icon_class=icon, order=order, is_visible=True)

    if not HrServiceCard.objects.exists():
        services = [
            ("HR Policy Formulation", "Drafting employee handbooks, code of conduct, and workplace policies compliant with labor laws.", "fa-solid fa-file-contract", 1),
            ("Employee Onboarding & Induction", "Structured joining experience with document verification, induction kits, and orientation programs.", "fa-solid fa-user-plus", 2),
            ("Performance Management System", "KPI setting, goal tracking, appraisal frameworks, and performance improvement plans.", "fa-solid fa-chart-line", 3),
            ("Statutory Compliance & Audits", "Ensuring full adherence to labor laws, PF, ESI, Gratuity, Bonus, and shop & establishment acts.", "fa-solid fa-shield-halved", 4),
            ("Employee Relations & Grievance", "Conflict resolution, grievance redressal, disciplinary procedures, and workplace counseling.", "fa-solid fa-handshake", 5),
            ("Exit Management & F&F Settlement", "Exit interviews, clearance workflows, resignation handovers, and timely full & final settlements.", "fa-solid fa-door-open", 6),
        ]
        for title, desc, icon, order in services:
            HrServiceCard.objects.create(title=title, description=desc, icon_class=icon, order=order, is_visible=True)

    if not HrAdditionalServiceItem.objects.exists():
        additionals = [
            ("Training & Development", "fa-solid fa-graduation-cap", 1),
            ("POSH Compliance & Training", "fa-solid fa-shield-halved", 2),
            ("HR Operations & Records", "fa-solid fa-folder-open", 3),
            ("Compensation & Benefits Benchmarking", "fa-solid fa-coins", 4),
            ("Employee Engagement Activities", "fa-solid fa-people-group", 5),
        ]
        for title, icon, order in additionals:
            HrAdditionalServiceItem.objects.create(title=title, icon_class=icon, order=order, is_visible=True)

    if not HrWhyChooseItem.objects.exists():
        why_choose = [
            ("Certified HR Professionals", 1),
            ("100% Legal & Labor Law Compliance", 2),
            ("Customized HR Frameworks for SMEs & Corporates", 3),
            ("Confidential Employee Data Management", 4),
            ("Cost-Effective HR Outsourcing", 5),
            ("PAN India Support & Fast Turnaround", 6),
        ]
        for title, order in why_choose:
            HrWhyChooseItem.objects.create(title=title, order=order, is_visible=True)

    if not HrProcessStep.objects.exists():
        steps = [
            ("Step 1", "HR Audit & Gap Analysis", "fa-solid fa-magnifying-glass", 1),
            ("Step 2", "Strategy & Policy Framework Design", "fa-solid fa-pen-ruler", 2),
            ("Step 3", "System Implementation & Training", "fa-solid fa-gears", 3),
            ("Step 4", "Ongoing Support & Periodic Review", "fa-solid fa-clipboard-check", 4),
        ]
        for step, title, icon, order in steps:
            HrProcessStep.objects.create(step_number=step, title=title, icon_class=icon, order=order, is_visible=True)

    if not HrEmployerBenefit.objects.exists():
        emp_benefits = [
            ("Reduced Legal Liabilities & Risks", 1),
            ("Lower Employee Turnover Rates", 2),
            ("Streamlined & Automated HR Operations", 3),
            ("More Time for Core Business Growth", 4),
            ("High-Performance Workplace Culture", 5),
        ]
        for title, order in emp_benefits:
            HrEmployerBenefit.objects.create(title=title, order=order, is_visible=True)

    if not HrEmployeeBenefit.objects.exists():
        employee_benefits = [
            ("Clear & Transparent Workplace Policies", 1),
            ("Fair & Timely Grievance Redressal", 2),
            ("Objective & Structured Appraisals", 3),
            ("Smooth Onboarding & Documentation", 4),
            ("Safe & Inclusive Work Environment", 5),
        ]
        for title, order in employee_benefits:
            HrEmployeeBenefit.objects.create(title=title, order=order, is_visible=True)

    # ==========================
    # 2. INTERNSHIP SEED
    # ==========================
    InternshipSettings = apps.get_model('core', 'InternshipSettings')
    InternshipStripItem = apps.get_model('core', 'InternshipStripItem')
    InternshipTrackItem = apps.get_model('core', 'InternshipTrackItem')
    InternshipHighlightItem = apps.get_model('core', 'InternshipHighlightItem')
    InternshipWhoCanApplyItem = apps.get_model('core', 'InternshipWhoCanApplyItem')
    InternshipWhatYouLearnItem = apps.get_model('core', 'InternshipWhatYouLearnItem')
    InternshipProcessStep = apps.get_model('core', 'InternshipProcessStep')
    InternshipBenefitItem = apps.get_model('core', 'InternshipBenefitItem')
    InternshipFaqItem = apps.get_model('core', 'InternshipFaqItem')

    intern_settings = InternshipSettings.objects.first()
    if not intern_settings:
        InternshipSettings.objects.create(
            hero_visible=True,
            strip_visible=True,
            domains_visible=True,
            highlights_visible=True,
            who_can_apply_visible=True,
            what_you_learn_visible=True,
            process_visible=True,
            benefits_visible=True,
            faqs_visible=True,
            openings_visible=True,
            cta_visible=True,
            hero_eyebrow="Internship Programme",
            hero_title="Launch your career from day one.",
            hero_tagline="LEARN • GROW • SUCCEED",
            hero_subtitle="Real projects, real mentors, real outcomes. Build the skills employers actually ask for — with a certificate and placement support waiting at the finish line.",
            hero_primary_btn_text="Apply Today",
            hero_primary_btn_url="#openings",
            hero_secondary_btn_text="See how it works",
            hero_secondary_btn_url="#process",
            hero_badge_text="Mission: Hired",
            domains_tag="EXPLORE",
            domains_title="Pick your mission.",
            domains_subtitle="Choose from 7 industry domains.",
            highlights_tag="PROGRAMME HIGHLIGHTS",
            who_can_apply_title="Who Can Apply?",
            what_you_learn_title="What You'll Learn.",
            process_tag="FLIGHT PATH",
            process_title="Our Internship Process.",
            benefits_tag="ADVANTAGES",
            benefits_title="Benefits of Joining Us",
            faqs_tag="QUESTIONS & ANSWERS",
            faqs_title="Frequently Asked Questions",
            openings_tag="NOW HIRING",
            openings_title="Available Internship Positions",
            openings_subtitle="Explore open roles and apply today.",
            cta_title="Build Skills. Gain Experience. Get Hired.",
            cta_subtitle="Step into a role that gives you real work, genuine mentors, and career opportunities.",
            cta_primary_btn_text="Apply for Internship",
            cta_primary_btn_url="/candidate/register/",
            cta_secondary_btn_text="Talk to a Counsellor",
            cta_secondary_btn_url="/contact/",
            meta_title="Internship Programme | Sky Vision Group Consultancy",
            meta_description="Join our top industry-oriented internship programme with live project training, certifications, and placement support.",
            meta_keywords="internship, practical training, live projects, sky vision group, career development",
        )

    if not InternshipStripItem.objects.exists():
        strips = [
            ("Industry Oriented Training", "fa-solid fa-people-group", 1),
            ("Live Projects & Assignments", "fa-solid fa-clipboard-check", 2),
            ("Expert Mentorship", "fa-solid fa-user-tie", 3),
            ("Certificate on Completion", "fa-solid fa-certificate", 4),
            ("Placement Assistance", "fa-solid fa-briefcase", 5),
        ]
        for title, icon, order in strips:
            InternshipStripItem.objects.create(title=title, icon_class=icon, order=order, is_visible=True)

    if not InternshipTrackItem.objects.exists():
        tracks = [
            ("HR Internship", "Recruitment, talent acquisition, employee management and HR operations.", "fa-solid fa-user-group", "01", "d1", 1),
            ("Finance Internship", "Accounting, Tally, GST, financial reporting and Excel for real-world tasks.", "fa-solid fa-chart-line", "02", "d2", 2),
            ("Marketing Internship", "Market research, branding, advertising strategy and campaign management.", "fa-solid fa-bullhorn", "03", "d3", 3),
            ("IT Internship", "Coding, website development, databases and modern IT tools.", "fa-solid fa-code", "04", "d4", 4),
            ("Digital Marketing", "SEO, social media marketing, Google Ads, content and analytics.", "fa-solid fa-desktop", "05", "d5", 5),
            ("Graphic Design", "Branding, social media creatives and visual communication.", "fa-solid fa-pen-nib", "06", "d6", 6),
            ("Business Development Internship", "Communication, lead generation, client handling, sales strategy and business growth skills.", "fa-solid fa-briefcase", "07", "d7 full", 7),
        ]
        for title, desc, icon, badge, style, order in tracks:
            InternshipTrackItem.objects.create(title=title, description=desc, icon_class=icon, badge_number=badge, card_style=style, order=order, is_visible=True)

    if not InternshipHighlightItem.objects.exists():
        highlights = [
            "Duration: 1–6 months", "Flexible timings", "Online & offline training", "Live assignments",
            "Project-based learning", "Weekly performance review", "Career counselling",
            "Resume building assistance", "Interview preparation", "Certificate of completion", "Placement support"
        ]
        for idx, title in enumerate(highlights, 1):
            InternshipHighlightItem.objects.create(title=title, icon_class="fa-solid fa-circle-check", order=idx, is_visible=True)

    if not InternshipWhoCanApplyItem.objects.exists():
        who_can = ["College Students", "Final Year Students", "Fresh Graduates", "Diploma Students", "Job Seekers", "Career Switchers"]
        for idx, title in enumerate(who_can, 1):
            InternshipWhoCanApplyItem.objects.create(title=title, icon_class="fa-solid fa-circle-check", order=idx, is_visible=True)

    if not InternshipWhatYouLearnItem.objects.exists():
        what_learn = [
            "Professional Communication", "Team Collaboration", "Problem Solving", "Time Management",
            "Industry Tools & Software", "Project Execution", "Interview & Resume Skills", "Workplace Ethics"
        ]
        for idx, title in enumerate(what_learn, 1):
            InternshipWhatYouLearnItem.objects.create(title=title, icon_class="fa-solid fa-circle-check", order=idx, is_visible=True)

    if not InternshipProcessStep.objects.exists():
        steps = [
            ("Step 1", "Submit Application", "fa-solid fa-file-signature", False, 1),
            ("Step 2", "Profile Screening", "fa-solid fa-user-check", False, 2),
            ("Step 3", "Technical & HR Interview", "fa-solid fa-comments", False, 3),
            ("Step 4", "Offer & Onboarding", "fa-solid fa-envelope-open-text", False, 4),
            ("Step 5", "Live Training & Projects", "fa-solid fa-diagram-project", False, 5),
            ("Step 6", "Certificate & Placement Support", "fa-solid fa-award", True, 6),
        ]
        for step, title, icon, is_final, order in steps:
            InternshipProcessStep.objects.create(step_number=step, title=title, icon_class=icon, is_final=is_final, order=order, is_visible=True)

    if not InternshipBenefitItem.objects.exists():
        benefits = [
            ("Industry Exposure", "fa-solid fa-chart-line", 1),
            ("Practical Learning", "fa-solid fa-gear", 2),
            ("Professional Certificate", "fa-solid fa-certificate", 3),
            ("Portfolio Development", "fa-solid fa-folder-open", 4),
            ("Resume Enhancement", "fa-solid fa-file-lines", 5),
            ("Interview Preparation", "fa-solid fa-user-tie", 6),
            ("Networking", "fa-solid fa-people-arrows", 7),
            ("Placement Assistance", "fa-solid fa-handshake", 8),
            ("Career Guidance", "fa-solid fa-compass", 9),
        ]
        for title, icon, order in benefits:
            InternshipBenefitItem.objects.create(title=title, icon_class=icon, order=order, is_visible=True)

    if not InternshipFaqItem.objects.exists():
        faqs = [
            ("Is this internship paid?", "Both paid and unpaid internships are available depending on domain and project.", 1),
            ("Will I receive a certificate?", "Yes, a certificate will be awarded after successful completion.", 2),
            ("Is placement assistance available?", "Yes, eligible candidates receive placement support and interview opportunities.", 3),
            ("Can I join while studying?", "Absolutely! Flexible schedules are available for students.", 4),
            ("Is the internship available online?", "Yes, we offer both online and offline internship programmes.", 5),
        ]
        for q, a, order in faqs:
            InternshipFaqItem.objects.create(question=q, answer=a, order=order, is_visible=True)


def unseed_data(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0037_seed_payroll_outsourcing_data'),
    ]

    operations = [
        migrations.RunPython(seed_hr_support_and_internship_data, unseed_data),
    ]

