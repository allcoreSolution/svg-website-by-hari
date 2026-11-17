from django.db import migrations


def seed_home_page_data(apps, schema_editor):
    HomePageSettings = apps.get_model('core', 'HomePageSettings')
    HeroStat = apps.get_model('core', 'HeroStat')
    GrowthStep = apps.get_model('core', 'GrowthStep')
    HomeServiceCard = apps.get_model('core', 'HomeServiceCard')
    WhyChooseItem = apps.get_model('core', 'WhyChooseItem')
    InternshipCard = apps.get_model('core', 'InternshipCard')
    InternshipHighlight = apps.get_model('core', 'InternshipHighlight')
    FeaturedCandidate = apps.get_model('core', 'FeaturedCandidate')
    GalleryImage = apps.get_model('core', 'GalleryImage')
    GalleryInfoBox = apps.get_model('core', 'GalleryInfoBox')

    # 1. HomePageSettings
    if not HomePageSettings.objects.exists():
        HomePageSettings.objects.create(
            hero_visible=True,
            hero_unit_tag="A Unit of Radha Enterprises",
            hero_eyebrow="Staffing · Recruitment · Consultancy",
            hero_title="Find Your Dream Job For Your Future",
            hero_title_highlight="Future",
            hero_subtitle="Manpower supply, recruitment, HR outsourcing, educational consultancy and career development — one team, across India.",
            hero_cta_primary_label="Apply Now",
            hero_cta_primary_url="#",
            hero_cta_primary_visible=True,
            hero_cta_secondary_label="Hire Talent",
            hero_cta_secondary_url="/employer/hire-talent/",
            hero_cta_secondary_visible=True,
            hero_cta_internship_label="Apply Internship",
            hero_cta_internship_url="#",
            hero_cta_internship_visible=True,
            hero_image_alt="Recruitment team illustration",
            hero_search_visible=True,
            hero_growth_steps_visible=True,
            job_pills_visible=True,

            services_tag="What We Do",
            services_title="Our professional services",
            services_subtitle="End-to-end workforce and business solutions tailored to your needs.",
            services_visible=True,

            about_tag="About Us",
            about_heading="Welcome to Sky Vision Group Consultancy",
            about_heading_highlight="Sky Vision Group Consultancy",
            about_content="At Sky Vision Group Consultancy, we are committed to delivering reliable and innovative workforce solutions that help businesses grow and professionals build successful careers. With expertise in Recruitment & Placement, Manpower Supply, Contract Staffing, Payroll & Outsourcing, HR Support, Educational Consultancy, Internship Programs, and Career Counseling, we provide end-to-end services tailored to the evolving needs of organizations across diverse industries.",
            about_badge_text="Trusted since 2014",
            about_image_alt="Sky Vision Office & Team",
            about_sub_title="6+ years placing India's workforce",
            about_sub_snippet="5,000+ candidates placed across manufacturing, IT, healthcare, retail and BPO sectors.",
            about_vision_title="Our Vision",
            about_vision_desc="To become India's most trusted consultancy brand.",
            about_mission_title="Our Mission",
            about_mission_desc="Empowering businesses and professionals through smart workforce solutions.",
            about_btn_label="Read More",
            about_btn_url="/about/",
            about_btn_visible=False,
            about_visible=True,

            why_choose_tag="Our Advantage",
            why_choose_title="Why choose us?",
            why_choose_subtitle="We provide reliable recruitment solutions with speed, quality and transparency.",
            why_choose_visible=True,

            industries_tag="Where We Work",
            industries_title="Industries we serve",
            industries_subtitle="From factory floors to corporate offices, we staff the sectors that keep India running.",
            industries_visible=True,

            internship_heading="Internship Programme",
            internship_subtitle="Build your career with professional internship opportunities.",
            internship_box_title="90-Day Professional Internship Programme",
            internship_cta_label="Apply Now",
            internship_cta_url="#",
            internship_visible=True,

            job_categories_visible=True,
            latest_jobs_visible=True,

            candidates_tag="Meet The Talent",
            candidates_title="Featured candidates",
            candidates_subtitle="Verified, job-ready professionals available for immediate placement.",
            candidates_visible=True,

            gallery_tag="A Glimpse Inside",
            gallery_title="Our gallery",
            gallery_subtitle="Moments from our placement drives, training sessions and team events.",
            gallery_btn_label="View Full Gallery",
            gallery_btn_url="/gallery/",
            gallery_btn_visible=False,
            gallery_visible=True,

            contact_title="Contact Information",
            contact_form_title="Send Us a Message",
            contact_map_url="https://www.google.com/maps?q=12/2+Arvindo+Park+Road+Sector+12+Indira+Nagar+Lucknow+Uttar+Pradesh+226016&output=embed",
            contact_visible=True,

            meta_title="Sky Vision Group of Consultancy | Recruitment & Staffing Lucknow",
            meta_description="Premier manpower staffing, recruitment, educational consultancy, and payroll outsourcing in Lucknow and nationwide."
        )

    # 2. Hero Stats
    if not HeroStat.objects.exists():
        stats = [
            ("fa-solid fa-briefcase", "10K+", "Experience", 1),
            ("fa-solid fa-building", "500+", "Placed Candidates", 2),
            ("fa-solid fa-user-group", "25K+", "Happy Candidates", 3),
        ]
        for icon, val, lbl, ord_n in stats:
            HeroStat.objects.create(icon_class=icon, value=val, label=lbl, order=ord_n, is_visible=True)

    # 3. Growth Steps
    if not GrowthStep.objects.exists():
        steps = [
            (1, "Connect", "We understand your needs", 1),
            (2, "Consult", "We find the right opportunities", 2),
            (3, "Execute", "We deliver best results", 3),
            (4, "Grow", "We help you achieve more", 4),
        ]
        for num, tit, subt, ord_n in steps:
            GrowthStep.objects.create(step_number=num, title=tit, subtitle=subt, order=ord_n, is_visible=True)

    # 4. Home Service Cards
    if not HomeServiceCard.objects.exists():
        services = [
            (
                "Manpower Supply Services",
                "fas fa-users",
                "blue",
                "Skilled Manpower\nUnskilled Manpower\nIndustrial Workforce\nFactory Staff\nOffice Staff",
                "/services/manpower-supply/",
                1
            ),
            (
                "Recruitment & Placement Services",
                "fas fa-search",
                "red",
                "Permanent Hiring\nExecutive Hiring\nBulk Hiring\nCampus Recruitment\nOverseas Recruitment",
                "/services/recruitment-placement/",
                2
            ),
            (
                "Contract Staffing Services",
                "fas fa-user-friends",
                "blue",
                "Temporary Staffing\nProject Staffing\nSeasonal Workforce\nThird Party Payroll",
                "/contract-staffing/",
                3
            ),
            (
                "Educational Consultancy Services",
                "fas fa-graduation-cap",
                "red",
                "Admission Guidance\nCollege Selection\nCareer Planning\nSkill Development",
                "/services/educational-consultancy/",
                4
            ),
            (
                "Payroll & Outsourcing Services",
                "fas fa-file-invoice",
                "blue",
                "Salary Processing\nAttendance Management\nPF & ESI Management\nCompliance Management",
                "/services/payroll-outsourcing/",
                5
            ),
            (
                "HR Support Services",
                "fas fa-headset",
                "red",
                "HR Policies\nEmployee Engagement\nPerformance Management\nHR Documentation",
                "/services/hr-support/",
                6
            ),
            (
                "Internship Programme",
                "fas fa-briefcase",
                "blue",
                "HR Internship\nFinance Internship\nMarketing Internship\nIT Internship\nDigital Marketing Internship",
                "/services/internship/",
                7
            ),
            (
                "Career Counselling Services",
                "fas fa-people-arrows",
                "red",
                "Career Assessment\nResume Building\nInterview Preparation\nJob Guidance",
                "/careers/",
                8
            ),
        ]
        for tit, icon, color, bullets, url, ord_n in services:
            HomeServiceCard.objects.create(
                title=tit,
                icon_class=icon,
                icon_color=color,
                bullets=bullets,
                link_url=url,
                order=ord_n,
                is_visible=True
            )

    # 5. Why Choose Us Items
    if not WhyChooseItem.objects.exists():
        items = [
            ("Professional Team", "fas fa-users", "Experienced HR professionals who understand every industry we serve.", 1),
            ("Industry Expertise", "fas fa-building", "Deep experience across manufacturing, IT, healthcare and more.", 2),
            ("Transparent Process", "fas fa-clipboard-check", "100% ethical recruitment with clear communication at every step.", 3),
            ("Fast Hiring", "fas fa-bolt", "Quick turnaround time so roles get filled and candidates get placed sooner.", 4),
            ("Affordable Pricing", "fas fa-hand-holding-dollar", "Cost-effective solutions built for businesses of every size.", 5),
            ("Nationwide Reach", "fas fa-globe-asia", "Serving clients and candidates across India, not just Lucknow.", 6),
        ]
        for tit, icon, desc, ord_n in items:
            WhyChooseItem.objects.create(title=tit, icon_class=icon, description=desc, order=ord_n, is_visible=True)

    # 6. Internship Highlights
    if not InternshipHighlight.objects.exists():
        benefits = [
            "Live Projects",
            "Practical Exposure",
            "Internship Certificate",
            "Recommendation Letter",
            "Placement Assistance",
            "Internship Completion Certificate",
            "Flexible Learning Schedule",
            "Expert Mentor Guidance",
            "Resume & LinkedIn Profile Building",
            "Letter of Recommendation",
        ]
        for idx, txt in enumerate(benefits, 1):
            InternshipHighlight.objects.create(
                item_type='benefit',
                text=txt,
                icon_class="fa-solid fa-check",
                order=idx,
                is_visible=True
            )

        bottom_badges = [
            ("Live Projects", "fa-solid fa-laptop-code", 1),
            ("Practical Training", "fa-solid fa-file-signature", 2),
            ("Expert Guidance", "fa-regular fa-star", 3),
            ("Certificate", "fa-solid fa-certificate", 4),
            ("Recommendation Letter", "fa-solid fa-user-check", 5),
            ("Placement Assistance", "fa-solid fa-briefcase", 6),
        ]
        for txt, icon, ord_n in bottom_badges:
            InternshipHighlight.objects.create(
                item_type='bottom_badge',
                text=txt,
                icon_class=icon,
                order=ord_n,
                is_visible=True
            )

    # 7. Internship Cards
    if not InternshipCard.objects.exists():
        domains = [
            ("HR Internship", "fa-solid fa-users", "#2563EB", "Recruitment Process\nPayroll Management\nHR Documentation", 1),
            ("Finance Internship", "fas fa-chart-line", "#0D9488", "GST\nTDS\nAccounting\nFinancial Analysis", 2),
            ("Marketing Internship", "fas fa-bullhorn", "#EA580C", "Sales\nBranding\nMarket Research", 3),
            ("Digital Marketing Internship", "fas fa-globe", "#2563EB", "SEO\nSocial Media Marketing\nGoogle Ads", 4),
            ("IT Internship", "fas fa-desktop", "#7C3AED", "Web Development\nProgramming\nDatabase Management", 5),
            ("Graphic Design Internship", "fa-solid fa-pen-nib", "#D97706", "Graphics Design\nBranding and Identity\nVideo Editing", 6),
        ]
        for dom, icon, color, bullets, ord_n in domains:
            InternshipCard.objects.create(
                domain_name=dom,
                icon_class=icon,
                icon_color=color,
                bullets=bullets,
                order=ord_n,
                is_visible=True
            )

    # 8. Featured Candidates
    if not FeaturedCandidate.objects.exists():
        candidates = [
            ("Sheridan Bastin", "Java Programmer", "1 Yr Exp", "linear-gradient(135deg,#5B7CFF,#2F3FA6)", 1),
            ("Tanner Fullerton", "PHP Developer", "6 Yrs Exp", "linear-gradient(135deg,#FF7A29,#C94E00)", 2),
            ("Jessica Lee", "UI/UX Designer", "4 Yrs Exp", "linear-gradient(135deg,#22B8A0,#0E6E5F)", 3),
            ("Michael Smith", "React Developer", "5 Yrs Exp", "linear-gradient(135deg,#5B7CFF,#2F3FA6)", 4),
            ("David Wilson", "Python Developer", "8 Yrs Exp", "linear-gradient(135deg,#FF7A29,#C94E00)", 5),
            ("Emma Watson", "Frontend Developer", "3 Yrs Exp", "linear-gradient(135deg,#22B8A0,#0E6E5F)", 6),
        ]
        for name, role, exp, col, ord_n in candidates:
            FeaturedCandidate.objects.create(
                name=name,
                role=role,
                experience=exp,
                avatar_color=col,
                show_publicly=True,
                order=ord_n,
                is_visible=True
            )

    # 9. Gallery Images
    if not GalleryImage.objects.exists():
        gallery = [
            ("Corporate Events", "images/general/placement drives.png", "Events", 1),
            ("Interview Rounds", "images/general/interview round.png", "Interviews", 2),
            ("Placement Drives", "images/general/placement drives.png", "Placements", 3),
            ("Training Sessions", "images/general/training session.png", "Training", 4),
            ("Workshops", "images/general/workshop.png", "Workshops", 5),
            ("Team Activities", "images/general/team activities.png", "Team", 6),
        ]
        for tit, static_p, cat, ord_n in gallery:
            GalleryImage.objects.create(
                title=tit,
                static_image_path=static_p,
                category=cat,
                show_on_home=True,
                order=ord_n,
                is_visible=True
            )

    # 10. Gallery Info Boxes
    if not GalleryInfoBox.objects.exists():
        boxes = [
            (
                "Looking For The Right Talent",
                "We help you build real skills and grow faster.",
                "fa-solid fa-bullseye",
                "View Programs",
                "/services/",
                False,
                1
            ),
            (
                "Looking For A Great Opportunity",
                "Explore our specialized programs for you.",
                "fa-solid fa-globe",
                "Explore Now",
                "/jobs/",
                False,
                2
            ),
            (
                "Participate In Our Internship Program",
                "Gain hands-on experience and kickstart your career.",
                "fa-solid fa-graduation-cap",
                "Apply Internship",
                "#",
                True,
                3
            ),
        ]
        for tit, txt, icon, lbl, url, popup, ord_n in boxes:
            GalleryInfoBox.objects.create(
                title=tit,
                text=txt,
                icon_class=icon,
                btn_label=lbl,
                btn_url=url,
                is_popup=popup,
                order=ord_n,
                is_visible=True
            )


def reverse_seed_data(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_homepagesettings_about_btn_label_and_more'),
    ]

    operations = [
        migrations.RunPython(seed_home_page_data, reverse_seed_data),
    ]
