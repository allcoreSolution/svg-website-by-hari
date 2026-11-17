from django.db import migrations


def seed_about_company_page(apps, schema_editor):
    AboutCompanySettings = apps.get_model('core', 'AboutCompanySettings')
    AboutWhyCard = apps.get_model('core', 'AboutWhyCard')
    AboutTestimonial = apps.get_model('core', 'AboutTestimonial')
    AboutTestimonialStat = apps.get_model('core', 'AboutTestimonialStat')
    AboutTrustPoint = apps.get_model('core', 'AboutTrustPoint')
    AboutPartnerLogo = apps.get_model('core', 'AboutPartnerLogo')
    TeamMember = apps.get_model('core', 'TeamMember')

    # 1. AboutCompanySettings defaults check / ensure 5,000+
    about_settings = AboutCompanySettings.objects.first()
    if not about_settings:
        AboutCompanySettings.objects.create(
            tt_highlight_1="5,000+",
            tt_highlight_2="250+",
        )
    else:
        if not about_settings.tt_highlight_1 or about_settings.tt_highlight_1 == "5,00+":
            about_settings.tt_highlight_1 = "5,000+"
            about_settings.save(update_fields=['tt_highlight_1'])

    # 2. Why Choose Us Cards (6 items)
    if not AboutWhyCard.objects.exists():
        why_items = [
            ("Professional Team", "fas fa-users", "Experienced HR professionals who understand every industry we serve.", 1),
            ("Industry Expertise", "fas fa-building", "Deep experience across manufacturing, IT, healthcare and more.", 2),
            ("Transparent Process", "fas fa-clipboard-check", "100% ethical recruitment with clear communication at every step.", 3),
            ("Fast Hiring", "fas fa-bolt", "Quick turnaround time so roles get filled and candidates get placed sooner.", 4),
            ("Affordable Pricing", "fas fa-hand-holding-dollar", "Cost-effective solutions built for businesses of every size.", 5),
            ("Nationwide Reach", "fas fa-globe-asia", "Serving clients and candidates across India, not just Lucknow.", 6),
        ]
        for title, icon, desc, order in why_items:
            AboutWhyCard.objects.create(
                title=title,
                icon_class=icon,
                description=desc,
                order=order,
                is_visible=True
            )

    # 3. Testimonial Stats (4 stats)
    if not AboutTestimonialStat.objects.exists():
        stats = [
            ("fa-solid fa-user-group", "blue", 500, "+", "Successful Placements", 1),
            ("fa-solid fa-building", "purple", 250, "+", "Hiring Partners", 2),
            ("fa-solid fa-face-smile", "green", 98, "%", "Candidate Satisfaction", 3),
            ("fa-solid fa-trophy", "gold", 8, "+", "Years of Excellence", 4),
        ]
        for icon, col, cnt, suf, lbl, ordr in stats:
            AboutTestimonialStat.objects.create(
                icon_class=icon,
                color=col,
                count=cnt,
                suffix=suf,
                label=lbl,
                order=ordr,
                is_visible=True
            )

    # 4. Candidate Testimonials (6 items)
    if not AboutTestimonial.objects.filter(testimonial_type='candidate').exists():
        cands = [
            (
                "Rahul Sharma", "Sales Executive", "Noida", 5, "Verified Candidate", 1, 1,
                "I'd been job hunting for nearly two months with no luck. Within days of registering with Sky Vision, I had interviews lined up. The team guided me through every round and helped me land a role that actually fit my experience."
            ),
            (
                "Priya Verma", "Customer Success Executive", "Greater Noida", 5, "Verified Candidate", 2, 2,
                "From my first call to my final joining letter, the whole process felt transparent and well managed. The consultants kept me updated at every stage and prepped me properly for each interview."
            ),
            (
                "Amit Kumar", "Warehouse Executive", "Delhi NCR", 5, "Verified Candidate", 3, 3,
                "The entire recruitment process wrapped up within a week. I got my interview schedule on time, regular follow-ups, and support all the way through to my joining date. Genuinely exceeded my expectations."
            ),
            (
                "Rohit Mishra", "Logistics Executive", "Ghaziabad", 5, "Verified Candidate", 4, 4,
                "The consultants were approachable, knowledgeable and genuinely invested in helping me succeed. Every update came promptly, which made the whole hiring experience smooth and professional."
            ),
            (
                "Pooja Gupta", "Accounts Executive", "Noida", 5, "Verified Candidate", 5, 5,
                "What stood out was how transparent and professional the whole process was. The team matched my profile to the right employer and stayed with me right up to onboarding. Highly recommend."
            ),
            (
                "Sanjay Kapoor", "Production Supervisor", "Lucknow", 5, "Verified Candidate", 6, 6,
                "I appreciated how honest they were about the role from day one — no surprises, no over-promising. Joined within two weeks and the transition was completely hassle-free."
            ),
        ]
        for name, role, loc, rating, badge, av_style, ordr, quote in cands:
            AboutTestimonial.objects.create(
                testimonial_type='candidate',
                name=name,
                role=role,
                location=loc,
                rating=rating,
                badge_text=badge,
                avatar_style=av_style,
                order=ordr,
                quote=quote,
                is_visible=True
            )

    # 5. Employer Testimonials (3 items)
    if not AboutTestimonial.objects.filter(testimonial_type='employer').exists():
        emps = [
            (
                "Neha Singh", "Senior HR Manager", "ABC Manufacturing Pvt. Ltd.", 5, "Verified Employer", 3, 1,
                "We've partnered with Sky Vision Group for multiple hiring drives now. They understand our workforce needs, turn candidates around fast, and consistently deliver quality hires. One of our most trusted recruitment partners."
            ),
            (
                "Vikas Khanna", "Talent Acquisition Lead", "Orion Retail Group", 5, "Verified Employer", 1, 2,
                "Reliable shortlists, clear communication, and candidates who actually show up ready for the role. Sky Vision has cut our hiring turnaround time significantly across our store network."
            ),
            (
                "Anjali Rastogi", "HR Business Partner", "Meridian Logistics", 5, "Verified Employer", 4, 3,
                "Ethical, transparent recruitment from start to finish. They take the time to understand our culture before sending profiles, which means far fewer mismatches at the interview stage."
            ),
        ]
        for name, role, comp, rating, badge, av_style, ordr, quote in emps:
            AboutTestimonial.objects.create(
                testimonial_type='employer',
                name=name,
                role=role,
                company=comp,
                rating=rating,
                badge_text=badge,
                avatar_style=av_style,
                order=ordr,
                quote=quote,
                is_visible=True
            )

    # 6. Partner Logos (9 items)
    if not AboutPartnerLogo.objects.exists():
        logos = [
            ("HDFC Bank", "fa-solid fa-building-columns", 1),
            ("ICICI Bank", "fa-solid fa-building-columns", 2),
            ("Genpact", "fa-solid fa-diagram-project", 3),
            ("Cognizant", "fa-solid fa-network-wired", 4),
            ("Amazon", "fa-solid fa-box", 5),
            ("Wipro", "fa-solid fa-microchip", 6),
            ("Infosys", "fa-solid fa-laptop-code", 7),
            ("Paytm", "fa-solid fa-mobile-screen", 8),
            ("Tata Motors", "fa-solid fa-car", 9),
        ]
        for name, icon, ordr in logos:
            AboutPartnerLogo.objects.create(
                name=name,
                icon_class=icon,
                order=ordr,
                is_visible=True
            )

    # 7. Trust Points (4 items)
    if not AboutTrustPoint.objects.exists():
        trust_pts = [
            ("Expert HR Consultants", "fa-solid fa-user-tie", "Experienced professionals guiding every step of your hiring or career journey.", 1),
            ("Right Opportunities", "fa-solid fa-bullseye", "Matching your skills with roles that actually fit — not just any opening.", 2),
            ("Verified Employers", "fa-solid fa-shield-halved", "Every hiring partner is vetted, so candidates step into genuine, trusted roles.", 3),
            ("End-to-End Recruitment", "fa-solid fa-headset", "From first interview to onboarding day, we stay with you the whole way.", 4),
        ]
        for title, icon, text, ordr in trust_pts:
            AboutTrustPoint.objects.create(
                title=title,
                icon_class=icon,
                text=text,
                order=ordr,
                is_visible=True
            )

    # 8. Flag existing team members to show on about page if none flagged yet
    if not TeamMember.objects.filter(show_on_about_page=True).exists():
        members = list(TeamMember.objects.filter(category='leadership').order_by('order', 'id')[:4])
        if not members:
            members = list(TeamMember.objects.all().order_by('order', 'id')[:4])
        for idx, m in enumerate(members, 1):
            m.show_on_about_page = True
            m.about_page_order = idx
            m.save(update_fields=['show_on_about_page', 'about_page_order'])


def reverse_seed_about_company_page(apps, schema_editor):
    AboutWhyCard = apps.get_model('core', 'AboutWhyCard')
    AboutTestimonial = apps.get_model('core', 'AboutTestimonial')
    AboutTestimonialStat = apps.get_model('core', 'AboutTestimonialStat')
    AboutTrustPoint = apps.get_model('core', 'AboutTrustPoint')
    AboutPartnerLogo = apps.get_model('core', 'AboutPartnerLogo')

    AboutWhyCard.objects.all().delete()
    AboutTestimonial.objects.all().delete()
    AboutTestimonialStat.objects.all().delete()
    AboutTrustPoint.objects.all().delete()
    AboutPartnerLogo.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_aboutpartnerlogo_abouttestimonial_and_more'),
    ]

    operations = [
        migrations.RunPython(seed_about_company_page, reverse_seed_about_company_page),
    ]
