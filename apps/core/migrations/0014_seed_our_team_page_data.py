from django.db import migrations


def seed_our_team_page_data(apps, schema_editor):
    OurTeamSettings = apps.get_model('core', 'OurTeamSettings')
    TeamFeatureHighlight = apps.get_model('core', 'TeamFeatureHighlight')
    TeamStat = apps.get_model('core', 'TeamStat')
    TeamDepartment = apps.get_model('core', 'TeamDepartment')
    TeamTrustPoint = apps.get_model('core', 'TeamTrustPoint')
    TeamCoreValue = apps.get_model('core', 'TeamCoreValue')
    TeamMember = apps.get_model('core', 'TeamMember')

    # 1. OurTeamSettings
    team_settings = OurTeamSettings.objects.first()
    if not team_settings:
        OurTeamSettings.objects.create(
            hero_visible=True,
            about_visible=True,
            leadership_visible=True,
            specialists_visible=True,
            departments_visible=True,
            stats_visible=True,
            trust_visible=True,
            values_visible=True,
            quote_visible=True,
            cta_visible=True,
            breadcrumb_title="Our Team",
            hero_eyebrow="Our Team",
            hero_title="Meet Our Expert Team",
            hero_description="Behind every successful placement is a dedicated team of recruitment professionals committed to connecting exceptional talent with outstanding opportunities across every industry we serve.",
            hero_btn1_text="Meet Our Leaders",
            hero_btn1_url="#leadership",
            hero_btn2_text="Join Our Team →",
            hero_btn2_url="#join",
            hero_image_alt="Sky Vision recruitment team collaborating in the office",
            about_eyebrow="About Our Team",
            about_heading="The People Behind Sky Vision",
            about_description="At Sky Vision Group Consultancy, our team is the driving force behind every successful recruitment journey. With expertise across recruitment, HR consulting, career guidance, and client management, we work together to deliver exceptional hiring solutions for businesses and rewarding career opportunities for candidates.",
            leadership_title="Our <span>Leadership</span> Team",
            leadership_subtitle="Visionary leaders guiding Sky Vision's strategy, culture, and client success.",
            leadership_max_items=12,
            specialists_title="Our <span>Recruitment</span> Specialists",
            specialists_subtitle="Skilled consultants dedicated to matching the right talent with the right opportunity.",
            specialists_max_items=24,
            departments_title="Our <span>Departments</span>",
            departments_subtitle="Specialized teams working together to deliver end-to-end recruitment and consulting solutions.",
            trust_heading="Why Clients <span>Trust</span> Our Team",
            static_trust_image="images/services/manpower-supply 2.png",
            values_heading="Our Core <span>Values</span>",
            quote_text="Every great placement starts with listening — to the client's needs and the candidate's aspirations. Our team's commitment to that balance is what has made Sky Vision a trusted recruitment partner across industries.",
            quote_author_name="Ashvani Dubey",
            quote_author_role="CEO & Founder, Sky Vision Group Consultancy",
            static_quote_image="images/team/CEO image.png",
            cta_icon="👥",
            cta_heading="Want to Work With Us?",
            cta_description="We're always looking for passionate professionals who want to make a difference in recruitment and HR consulting.",
            cta_btn1_text="Join Our Team",
            cta_btn1_url="/careers/",
            cta_btn2_text="Current Openings",
            cta_btn2_url="/careers/",
            meta_title="Our Leadership & Team — Sky Vision Group Consultancy",
            meta_description="Meet the visionary leadership and expert recruitment team behind Sky Vision Group Consultancy in Lucknow.",
        )
    else:
        # Update empty fields if needed
        dirty = False
        if not team_settings.leadership_title:
            team_settings.leadership_title = "Our <span>Leadership</span> Team"
            dirty = True
        if not team_settings.leadership_subtitle:
            team_settings.leadership_subtitle = "Visionary leaders guiding Sky Vision's strategy, culture, and client success."
            dirty = True
        if not team_settings.specialists_title:
            team_settings.specialists_title = "Our <span>Recruitment</span> Specialists"
            dirty = True
        if not team_settings.specialists_subtitle:
            team_settings.specialists_subtitle = "Skilled consultants dedicated to matching the right talent with the right opportunity."
            dirty = True
        if not team_settings.departments_title:
            team_settings.departments_title = "Our <span>Departments</span>"
            dirty = True
        if not team_settings.departments_subtitle:
            team_settings.departments_subtitle = "Specialized teams working together to deliver end-to-end recruitment and consulting solutions."
            dirty = True
        if not team_settings.trust_heading:
            team_settings.trust_heading = "Why Clients <span>Trust</span> Our Team"
            dirty = True
        if not team_settings.values_heading:
            team_settings.values_heading = "Our Core <span>Values</span>"
            dirty = True
        if not team_settings.quote_text:
            team_settings.quote_text = "Every great placement starts with listening — to the client's needs and the candidate's aspirations. Our team's commitment to that balance is what has made Sky Vision a trusted recruitment partner across industries."
            dirty = True
        if not team_settings.quote_author_name:
            team_settings.quote_author_name = "Ashvani Dubey"
            dirty = True
        if not team_settings.quote_author_role:
            team_settings.quote_author_role = "CEO & Founder, Sky Vision Group Consultancy"
            dirty = True
        if not team_settings.cta_heading:
            team_settings.cta_heading = "Want to Work With Us?"
            dirty = True
        if not team_settings.cta_description:
            team_settings.cta_description = "We're always looking for passionate professionals who want to make a difference in recruitment and HR consulting."
            dirty = True
        if not team_settings.cta_btn1_text:
            team_settings.cta_btn1_text = "Join Our Team"
            dirty = True
        if not team_settings.cta_btn1_url:
            team_settings.cta_btn1_url = "/careers/"
            dirty = True
        if not team_settings.cta_btn2_text:
            team_settings.cta_btn2_text = "Current Openings"
            dirty = True
        if not team_settings.cta_btn2_url:
            team_settings.cta_btn2_url = "/careers/"
            dirty = True
        if not team_settings.meta_title:
            team_settings.meta_title = "Our Leadership & Team — Sky Vision Group Consultancy"
            dirty = True
        if not team_settings.meta_description:
            team_settings.meta_description = "Meet the visionary leadership and expert recruitment team behind Sky Vision Group Consultancy in Lucknow."
            dirty = True
        if dirty:
            team_settings.save()

    # 2. TeamFeatureHighlight (4 items)
    if not TeamFeatureHighlight.objects.exists():
        features = [
            ("👥", "Expert Professionals", "Experienced recruiters and HR experts with in-depth industry knowledge.", 1),
            ("🎯", "Client Focused", "Building long-term partnerships and delivering value-driven solutions.", 2),
            ("💡", "People First Approach", "We believe in people, relationships, and creating meaningful opportunities.", 3),
            ("🛡️", "Integrity & Transparency", "Maintaining honesty and transparency in every interaction.", 4),
        ]
        for icon, title, desc, order in features:
            TeamFeatureHighlight.objects.create(
                icon=icon,
                title=title,
                description=desc,
                order=order,
                is_visible=True
            )

    # 3. TeamStat (6 items)
    if not TeamStat.objects.exists():
        stats = [
            ("👥", "50", "", "Recruitment Experts", "", 1),
            ("💼", "5000", "", "Candidates Placed", "", 2),
            ("🏢", "300", "", "Hiring Partners", "", 3),
            ("⭐", "95", "%", "Client Satisfaction", "", 4),
            ("🌐", "15", "", "Industries Served", "", 5),
            ("🎧", "", "", "Support Available", "24/7", 6),
        ]
        for icon, count, suffix, label, stext, order in stats:
            TeamStat.objects.create(
                icon=icon,
                count=count,
                suffix=suffix,
                label=label,
                static_text=stext,
                order=order,
                is_visible=True
            )

    # 4. TeamDepartment (10 items)
    if not TeamDepartment.objects.exists():
        depts = [
            ('Recruitment', '👔', 'End-to-end hiring solutions for permanent and contract roles.', 'https://images.unsplash.com/photo-1521737604893-d14cc237f11d?w=400&q=80', '15+ Members', 1),
            ('HR Consulting', '📋', 'Strategic HR advisory for policy, process, and workforce planning.', 'https://images.unsplash.com/photo-1600880292203-757bb62b4baf?w=400&q=80', '8+ Members', 2),
            ('IT Hiring', '💻', 'Specialized tech talent sourcing across engineering and IT roles.', 'https://images.unsplash.com/photo-1518770660439-4636190af475?w=400&q=80', '12+ Members', 3),
            ('BPO Hiring', '📞', 'High-volume staffing for voice and non-voice BPO operations.', 'https://images.unsplash.com/photo-1600880292089-90a7e086ee0c?w=400&q=80', '10+ Members', 4),
            ('Finance & Accounts', '📊', 'Skilled finance professionals for accounting and audit functions.', 'https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?w=400&q=80', '6+ Members', 5),
            ('Healthcare Recruitment', '🏥', 'Connecting hospitals and clinics with qualified healthcare talent.', 'https://images.unsplash.com/photo-1576091160399-112ba8d25d1d?w=400&q=80', '7+ Members', 6),
            ('Sales & Marketing', '📈', 'Building high-performing sales and marketing teams for growth.', 'https://images.unsplash.com/photo-1552664730-d307ca884978?w=400&q=80', '9+ Members', 7),
            ('Customer Support', '🎧', 'Reliable support staffing to keep client experience seamless.', 'https://images.unsplash.com/photo-1553877522-43269d4ea984?w=400&q=80', '8+ Members', 8),
            ('Training & Development', '🎓', 'Upskilling programs that prepare candidates for the workplace.', 'https://images.unsplash.com/photo-1543269865-cbf427effbad?w=400&q=80', '5+ Members', 9),
            ('Career Counseling', '🧭', 'Personalized guidance to help candidates find the right path.', 'https://images.unsplash.com/photo-1522202176988-66273c2fd55f?w=400&q=80', '6+ Members', 10),
        ]
        for name, icon, desc, img_url, size, order in depts:
            TeamDepartment.objects.create(
                name=name,
                icon=icon,
                description=desc,
                image_url=img_url,
                team_size=size,
                order=order,
                is_visible=True
            )

    # 5. TeamTrustPoint (8 items)
    if not TeamTrustPoint.objects.exists():
        points = [
            ("Experienced Recruitment Specialists", "✓", 1),
            ("Industry-Specific Hiring Expertise", "✓", 2),
            ("Dedicated Account Management", "✓", 3),
            ("Transparent Hiring Process", "✓", 4),
            ("Fast Turnaround Time", "✓", 5),
            ("Candidate-Centric Approach", "✓", 6),
            ("Nationwide Talent Network", "✓", 7),
            ("Long-Term Partnership Focus", "✓", 8),
        ]
        for title, icon, order in points:
            TeamTrustPoint.objects.create(
                title=title,
                icon_class=icon,
                order=order,
                is_visible=True
            )

    # 6. TeamCoreValue (4 items)
    if not TeamCoreValue.objects.exists():
        values = [
            ('🤝', 'Integrity', 'Building trust through honesty, ethics, and transparency.', 1),
            ('🏆', 'Excellence', 'Delivering consistent quality in every recruitment assignment.', 2),
            ('🔗', 'Collaboration', 'Working together with clients and candidates for shared success.', 3),
            ('💡', 'Innovation', 'Leveraging modern recruitment strategies and technology.', 4),
        ]
        for icon, title, desc, order in values:
            TeamCoreValue.objects.create(
                icon=icon,
                title=title,
                description=desc,
                order=order,
                is_visible=True
            )

    # 7. TeamMember (if empty, seed default members)
    if not TeamMember.objects.exists():
        initial_members = [
            {
                "name": "Ashvani Dubey",
                "role": "CEO & Founder",
                "category": "leadership",
                "static_photo_path": "images/team/CEO image.png",
                "bio": "Visionary leader with a passion for connecting talent with opportunities and building successful futures.",
                "linkedin_url": "https://www.linkedin.com/company/skyvisiongroup/",
                "email_url": "info@skyvisiongroup.in",
                "order": 1,
                "is_visible": True,
                "show_on_about_page": True,
                "about_page_order": 1
            },
            {
                "name": "Ruchi Singh",
                "role": "Managing Director",
                "category": "leadership",
                "static_photo_path": "images/team/Ruchi sigh.png",
                "bio": "Driving strategic growth and building strong partnerships across diverse industries and markets.",
                "linkedin_url": "https://www.linkedin.com/company/skyvisiongroup/",
                "email_url": "info@skyvisiongroup.in",
                "order": 2,
                "is_visible": True,
                "show_on_about_page": True,
                "about_page_order": 2
            },
            {
                "name": "Sweety",
                "role": "Director – HR",
                "category": "leadership",
                "static_photo_path": "images/services/hr .png",
                "bio": "Leading talent acquisition and HR consulting with a people-centric approach and strong leadership.",
                "linkedin_url": "https://www.linkedin.com/company/skyvisiongroup/",
                "email_url": "info@skyvisiongroup.in",
                "order": 3,
                "is_visible": True,
                "show_on_about_page": True,
                "about_page_order": 3
            },
            {
                "name": "Ajay Vishwakarma",
                "role": "Team Lead",
                "category": "leadership",
                "static_photo_path": "images/team/ajay_vishwakarma.png",
                "bio": "Ensuring operational excellence and delivering seamless recruitment solutions to our clients.",
                "linkedin_url": "https://www.linkedin.com/company/skyvisiongroup/",
                "email_url": "info@skyvisiongroup.in",
                "order": 4,
                "is_visible": True,
                "show_on_about_page": True,
                "about_page_order": 4
            },
            {
                "name": "Priya Sharma",
                "role": "Senior Recruitment Consultant",
                "category": "specialist",
                "static_photo_path": "images/team/female1.jpg",
                "experience_text": "Experience: 7+ Years",
                "linkedin_url": "https://www.linkedin.com/company/skyvisiongroup/",
                "email_url": "info@skyvisiongroup.in",
                "order": 5,
                "is_visible": True
            },
            {
                "name": "Amit Verma",
                "role": "IT Recruitment Consultant",
                "category": "specialist",
                "static_photo_path": "images/team/male1.avif",
                "experience_text": "Experience: 5+ Years",
                "linkedin_url": "https://www.linkedin.com/company/skyvisiongroup/",
                "email_url": "info@skyvisiongroup.in",
                "order": 6,
                "is_visible": True
            },
            {
                "name": "Sunita Rao",
                "role": "Operations & Compliance Manager",
                "category": "specialist",
                "static_photo_path": "images/team/female2.jpg",
                "experience_text": "Experience: 6+ Years",
                "linkedin_url": "https://www.linkedin.com/company/skyvisiongroup/",
                "email_url": "info@skyvisiongroup.in",
                "order": 7,
                "is_visible": True
            },
            {
                "name": "Vikram Malhotra",
                "role": "Talent Acquisition Specialist",
                "category": "specialist",
                "static_photo_path": "images/team/male2.avif",
                "experience_text": "Experience: 4+ Years",
                "linkedin_url": "https://www.linkedin.com/company/skyvisiongroup/",
                "email_url": "info@skyvisiongroup.in",
                "order": 8,
                "is_visible": True
            },
        ]
        for m in initial_members:
            TeamMember.objects.create(**m)


def reverse_noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0013_teamcorevalue_teamdepartment_teamfeaturehighlight_and_more'),
    ]

    operations = [
        migrations.RunPython(seed_our_team_page_data, reverse_noop),
    ]
