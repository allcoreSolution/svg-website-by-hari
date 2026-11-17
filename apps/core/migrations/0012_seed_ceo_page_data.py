from django.db import migrations


def seed_ceo_page_data(apps, schema_editor):
    CEOMessageSettings = apps.get_model('core', 'CEOMessageSettings')
    CEOLeadershipPrinciple = apps.get_model('core', 'CEOLeadershipPrinciple')
    CEOStatBadge = apps.get_model('core', 'CEOStatBadge')

    # 1. CEOMessageSettings
    ceo_settings = CEOMessageSettings.objects.first()
    if not ceo_settings:
        CEOMessageSettings.objects.create(
            page_title="CEO & Founder Message",
            page_eyebrow="Get To Know Us",
            hero_subtitle="Driving innovation, excellence, and ethical talent solutions across industries.",
            breadcrumb_title="CEO & Founder",
            ceo_name="ASHVANI DUBEY",
            ceo_role="CEO & FOUNDER",
            ceo_org="Sky Vision Group of Consultancy",
            ceo_tagline="Empowering Businesses. Transforming Careers.",
            ceo_photo_alt="Ashvani Dubey - CEO & Founder",
            static_photo_path="images/team/CEO image.png",
            title_eyebrow="MESSAGE FROM THE",
            title_main="CEO & FOUNDER",
            message_p1="At Sky Vision Group of Consultancy, our vision is simple—connecting the right talent with the right opportunities while helping businesses build stronger teams.",
            message_p2="As the CEO & Founder, I believe that recruitment is more than filling positions—it is about creating opportunities, empowering individuals, and driving organizational success.",
            message_p3="Our commitment to integrity, transparency, and excellence has helped us earn the trust of our clients and candidates across industries. From permanent staffing and executive search to HR outsourcing, internship programs, and workforce solutions, we continuously strive to deliver quality services that create long-term value.",
            message_p4="As the world of work evolves, we remain dedicated to innovation, technology-driven recruitment, and people-first solutions. Together with our team, clients, and partners, we will continue creating opportunities, empowering careers, and building a better future.",
            quote_text="Great organizations are built by great people.\nOur purpose is to connect talent with opportunity and create lasting value for both employers and professionals.",
            closing_text="Warm regards,",
            signoff_text="Ashvani Dubey — CEO & Founder",
            principles_tag="OUR LEADERSHIP",
            principles_title="PRINCIPLES",
            principles_subtitle="The core values that define our culture, decisions, and commitment to excellence.",
            vision_title="OUR VISION",
            vision_icon="fa-solid fa-eye",
            vision_text="To become one of India's most trusted recruitment and HR consulting organizations by delivering innovative workforce solutions that empower businesses and transform careers.",
            mission_title="OUR MISSION",
            mission_icon="fa-solid fa-bullseye",
            mission_text="To connect the right talent with the right opportunities through ethical recruitment, professional excellence, and customer-centric services while creating sustainable value for employers and job seekers.",
            signature_name="Ashvani Dubey",
            linkedin_url="https://www.linkedin.com/company/skyvisiongroup/",
            facebook_url="https://www.facebook.com/share/197C5xryds/",
            email_address="hr@svgconsultancy.com",
            cta_heading="Looking for the Right Talent or Career Opportunity?",
            cta_text="Connect with Sky Vision Group of Consultancy today to discover tailored recruitment and workforce solutions.",
            cta_btn_label="Explore Opportunities",
            cta_btn_url="/jobs/",
            cta_btn2_label="Contact Us",
            cta_btn2_url="/contact/",
            meta_title="CEO & Founder Message — Sky Vision Group Consultancy",
            meta_description="Read the official message from Ashvani Dubey, CEO & Founder of Sky Vision Group of Consultancy. Learn about our vision, mission, and leadership principles.",
        )

    # 2. CEOLeadershipPrinciple (5 items)
    if not CEOLeadershipPrinciple.objects.exists():
        principles = [
            ("Integrity First", "We operate with honesty, transparency, and accountability in everything we do.", "fa-solid fa-shield-halved", 1),
            ("People-Centric Approach", "Every client and candidate is treated with respect and professionalism.", "fa-solid fa-user-group", 2),
            ("Excellence in Service", "We are committed to delivering high-quality recruitment solutions.", "fa-solid fa-medal", 3),
            ("Innovation & Growth", "We continuously improve through technology and modern hiring practices.", "fa-solid fa-lightbulb", 4),
            ("Long-Term Partnerships", "We focus on building relationships based on trust and mutual success.", "fa-solid fa-handshake", 5),
        ]
        for title, desc, icon, order in principles:
            CEOLeadershipPrinciple.objects.create(
                title=title,
                description=desc,
                icon_class=icon,
                order=order,
                is_visible=True
            )

    # 3. CEOStatBadge (3 items)
    if not CEOStatBadge.objects.exists():
        badges = [
            ("10+", "Years Leadership", "fa-solid fa-award", 1),
            ("5,000+", "Candidates Placed", "fa-solid fa-user-check", 2),
            ("250+", "Corporate Partners", "fa-solid fa-building", 3),
        ]
        for val, lbl, icon, order in badges:
            CEOStatBadge.objects.create(
                value=val,
                label=lbl,
                icon_class=icon,
                order=order,
                is_visible=True
            )


def reverse_noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0011_ceostatbadge_ceomessagesettings_breadcrumb_title_and_more'),
    ]

    operations = [
        migrations.RunPython(seed_ceo_page_data, reverse_noop),
    ]
