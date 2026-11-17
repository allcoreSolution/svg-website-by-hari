from django.db import migrations


def seed_journey_page_data(apps, schema_editor):
    OurJourneySettings = apps.get_model('core', 'OurJourneySettings')
    JourneyStoryParagraph = apps.get_model('core', 'JourneyStoryParagraph')
    JourneyStoryCard = apps.get_model('core', 'JourneyStoryCard')
    JourneyMilestone = apps.get_model('core', 'JourneyMilestone')
    JourneyMilestoneCard = apps.get_model('core', 'JourneyMilestoneCard')
    JourneyImpactItem = apps.get_model('core', 'JourneyImpactItem')
    JourneyStat = apps.get_model('core', 'JourneyStat')
    JourneyFutureGoal = apps.get_model('core', 'JourneyFutureGoal')

    # 1. OurJourneySettings
    js = OurJourneySettings.objects.first()
    if not js:
        js = OurJourneySettings.objects.create(
            hero_visible=True,
            story_visible=True,
            timeline_visible=True,
            milestones_visible=True,
            impact_visible=True,
            numbers_visible=True,
            ahead_visible=True,
            hero_eyebrow="Our Journey",
            hero_title="Growing Together, Building Careers, <span>Creating Success</span>",
            hero_highlight="Creating Success",
            hero_description="Since our founding, Sky Vision Group Consultancy has been on a mission to connect talent with opportunity. Every placement, every partnership and every milestone reflects our commitment to businesses and professionals across India — a journey built on trust, consistency and genuine care for the people we serve.",
            badge_num="6+",
            badge_text="Years of Excellence",
            hero_btn1_text="Explore Our Story",
            hero_btn1_url="#oj-story",
            hero_btn2_text="Contact Us",
            hero_btn2_url="/contact/",
            hero_image_url_custom="https://images.unsplash.com/photo-1600880292203-757bb62b4baf?w=1000&q=80",
            stat1_num="2022",
            stat1_label="Founded",
            stat2_num="5000+",
            stat2_label="Placed",
            stat3_num="300+",
            stat3_label="Partners",
            story_tag="Our Story",
            story_title="A journey that began with a <span>vision</span>",
            story_highlight="vision",
            story_p1="Sky Vision Group Consultancy was founded on a simple belief — that the right people, in the right roles, can transform businesses and change lives. What started as a small team in Lucknow with a big vision has grown into a trusted consultancy serving clients and candidates across India.",
            story_p2="In our early years, we faced the same challenges every young consultancy does — building trust in a crowded market, proving our process, and earning our first long-term partnerships. We stayed close to our clients, listened to our candidates, and let consistent results speak for us.",
            story_p3="Today, that same founding spirit drives everything we do — from manpower supply and recruitment to HR outsourcing and career counselling. Every year has added a new capability, a new partnership and a new reason for our clients and candidates to trust us with their future.",
            story_image_url_custom="https://images.unsplash.com/photo-1521737604893-d14cc237f11d?w=900&q=80",
            timeline_tag="How Far We've Come",
            timeline_title="Our Growth <span>Timeline</span>",
            timeline_highlight="Timeline",
            timeline_subtitle="From a small vision to becoming a trusted recruitment consultancy.",
            milestones_tag="What We've Achieved",
            milestones_title="Our <span>Milestones</span>",
            milestones_highlight="Milestones",
            milestones_subtitle="Key moments that shaped our growth as a consultancy.",
            impact_tag="Our Impact",
            impact_title="Real results for businesses and <span>professionals</span>",
            impact_highlight="professionals",
            impact_description="Our journey isn't just measured in years — it's measured in the businesses we've helped grow and the careers we've helped build. Every service we offer is designed around one goal: reliable, lasting impact.",
            impact_image_url_custom="https://images.unsplash.com/photo-1552664730-d307ca884978?w=900&q=80",
            numbers_tag="By The Numbers",
            numbers_title="Our Journey In <span>Numbers</span>",
            numbers_highlight="Numbers",
            numbers_subtitle="A snapshot of the trust we've built since 2022.",
            ahead_tag="Looking Ahead",
            ahead_title="The next chapter of our <span>journey</span>",
            ahead_highlight="journey",
            ahead_description="Our story is far from over. As we look to the future, we remain committed to the same values that got us here — trust, quality and genuine care for the people we work with. Here's what's next for Sky Vision Group Consultancy.",
            cta_btn1_text="Partner With Us",
            cta_btn1_url="/contact/",
            cta_btn2_text="Contact Our Team",
            cta_btn2_url="/contact/",
            meta_title="Our Journey — Sky Vision Group Consultancy",
            meta_description="Explore the journey of Sky Vision Group Consultancy since 2022. Discover our milestones, impact, and vision for connecting talent across India."
        )
    else:
        # Populate empty fields if any
        dirty = False
        if not js.hero_title or "<span>" not in js.hero_title:
            js.hero_title = "Growing Together, Building Careers, <span>Creating Success</span>"
            dirty = True
        if not js.hero_highlight:
            js.hero_highlight = "Creating Success"
            dirty = True
        if not js.hero_btn1_text:
            js.hero_btn1_text = "Explore Our Story"
            dirty = True
        if not js.hero_btn1_url:
            js.hero_btn1_url = "#oj-story"
            dirty = True
        if not js.hero_btn2_text:
            js.hero_btn2_text = "Contact Us"
            dirty = True
        if not js.hero_btn2_url:
            js.hero_btn2_url = "/contact/"
            dirty = True
        if not js.story_title or "<span>" not in js.story_title:
            js.story_title = "A journey that began with a <span>vision</span>"
            dirty = True
        if not js.story_highlight:
            js.story_highlight = "vision"
            dirty = True
        if not js.timeline_tag:
            js.timeline_tag = "How Far We've Come"
            dirty = True
        if not js.timeline_title:
            js.timeline_title = "Our Growth <span>Timeline</span>"
            dirty = True
        if not js.timeline_highlight:
            js.timeline_highlight = "Timeline"
            dirty = True
        if not js.timeline_subtitle:
            js.timeline_subtitle = "From a small vision to becoming a trusted recruitment consultancy."
            dirty = True
        if not js.milestones_tag:
            js.milestones_tag = "What We've Achieved"
            dirty = True
        if not js.milestones_title:
            js.milestones_title = "Our <span>Milestones</span>"
            dirty = True
        if not js.milestones_highlight:
            js.milestones_highlight = "Milestones"
            dirty = True
        if not js.milestones_subtitle:
            js.milestones_subtitle = "Key moments that shaped our growth as a consultancy."
            dirty = True
        if not js.impact_tag:
            js.impact_tag = "Our Impact"
            dirty = True
        if not js.impact_title:
            js.impact_title = "Real results for businesses and <span>professionals</span>"
            dirty = True
        if not js.impact_highlight:
            js.impact_highlight = "professionals"
            dirty = True
        if not js.impact_description:
            js.impact_description = "Our journey isn't just measured in years — it's measured in the businesses we've helped grow and the careers we've helped build. Every service we offer is designed around one goal: reliable, lasting impact."
            dirty = True
        if not js.impact_image_url_custom:
            js.impact_image_url_custom = "https://images.unsplash.com/photo-1552664730-d307ca884978?w=900&q=80"
            dirty = True
        if not js.numbers_tag:
            js.numbers_tag = "By The Numbers"
            dirty = True
        if not js.numbers_title:
            js.numbers_title = "Our Journey In <span>Numbers</span>"
            dirty = True
        if not js.numbers_highlight:
            js.numbers_highlight = "Numbers"
            dirty = True
        if not js.numbers_subtitle:
            js.numbers_subtitle = "A snapshot of the trust we've built since 2022."
            dirty = True
        if not js.ahead_tag:
            js.ahead_tag = "Looking Ahead"
            dirty = True
        if not js.ahead_title:
            js.ahead_title = "The next chapter of our <span>journey</span>"
            dirty = True
        if not js.ahead_highlight:
            js.ahead_highlight = "journey"
            dirty = True
        if not js.ahead_description:
            js.ahead_description = "Our story is far from over. As we look to the future, we remain committed to the same values that got us here — trust, quality and genuine care for the people we work with. Here's what's next for Sky Vision Group Consultancy."
            dirty = True
        if not js.cta_btn1_text:
            js.cta_btn1_text = "Partner With Us"
            dirty = True
        if not js.cta_btn1_url:
            js.cta_btn1_url = "/contact/"
            dirty = True
        if not js.cta_btn2_text:
            js.cta_btn2_text = "Contact Our Team"
            dirty = True
        if not js.cta_btn2_url:
            js.cta_btn2_url = "/contact/"
            dirty = True
        if not js.meta_title:
            js.meta_title = "Our Journey — Sky Vision Group Consultancy"
            dirty = True
        if not js.meta_description:
            js.meta_description = "Explore the journey of Sky Vision Group Consultancy since 2022. Discover our milestones, impact, and vision for connecting talent across India."
            dirty = True
        if dirty:
            js.save()

    # 2. JourneyStoryParagraph
    if JourneyStoryParagraph.objects.count() == 0:
        paragraphs = [
            (1, "Sky Vision Group Consultancy was founded on a simple belief — that the right people, in the right roles, can transform businesses and change lives. What started as a small team in Lucknow with a big vision has grown into a trusted consultancy serving clients and candidates across India."),
            (2, "In our early years, we faced the same challenges every young consultancy does — building trust in a crowded market, proving our process, and earning our first long-term partnerships. We stayed close to our clients, listened to our candidates, and let consistent results speak for us."),
            (3, "Today, that same founding spirit drives everything we do — from manpower supply and recruitment to HR outsourcing and career counselling. Every year has added a new capability, a new partnership and a new reason for our clients and candidates to trust us with their future.")
        ]
        for ord_val, text_val in paragraphs:
            JourneyStoryParagraph.objects.create(order=ord_val, text=text_val, is_visible=True)

    # 3. JourneyStoryCard
    if JourneyStoryCard.objects.count() == 0:
        cards = [
            (1, "Trusted Consultancy", "Ethical, transparent recruitment built on long-term relationships.", "fa-solid fa-shield-halved", "blue"),
            (2, "Customer First Approach", "Every decision starts with what's right for our clients and candidates.", "fa-solid fa-heart", "red")
        ]
        for ord_val, t, d, ic, col in cards:
            JourneyStoryCard.objects.create(order=ord_val, title=t, description=d, icon=ic, color=col, is_visible=True)

    # 4. JourneyMilestone (Growth Timeline)
    if JourneyMilestone.objects.count() == 0:
        milestones = [
            (1, "2022", "Company Founded", "Sky Vision Group Consultancy was established in Lucknow with a mission to connect skilled talent with the right opportunities.", "fa-solid fa-flag", "Day 1"),
            (2, "2023", "Rapid Expansion", "Expanded into industrial manpower and executive search across Northern India.", "fa-solid fa-chart-line", "Growth"),
            (3, "2024", "5000+ Placements", "Reached a milestone of 5,000+ professionals successfully placed in top tier companies.", "fa-solid fa-users", "Milestone"),
            (4, "2025", "Digital Transformation", "Launched streamlined client portals and candidate career support systems.", "fa-solid fa-laptop-code", "Tech"),
            (5, "2026", "Pan-India Reach", "Serving over 300+ corporate partners across 15+ industries nationwide.", "fa-solid fa-award", "Present")
        ]
        for ord_val, yr, t, d, ic, b in milestones:
            JourneyMilestone.objects.create(order=ord_val, year=yr, title=t, description=d, icon_class=ic, badge_label=b, is_visible=True)

    # 5. JourneyMilestoneCard
    if JourneyMilestoneCard.objects.count() == 0:
        milestone_cards = [
            (1, "2022", "Company Founded", "Started in Lucknow with a clear mission and a small, dedicated team.", "fa-solid fa-trophy"),
            (2, "2023", "First 50 Corporate Clients", "Built trusted recruitment relationships with leading manufacturing and IT firms.", "fa-solid fa-handshake"),
            (3, "2024", "5,000+ Professionals Placed", "Crossed a major career milestone, transforming thousands of livelihoods.", "fa-solid fa-users"),
            (4, "2025", "Excellence in HR Outsourcing", "Recognized as one of the fastest-growing staffing firms in Uttar Pradesh.", "fa-solid fa-star")
        ]
        for ord_val, yr, t, d, ic in milestone_cards:
            JourneyMilestoneCard.objects.create(order=ord_val, year=yr, title=t, description=d, icon_class=ic, is_visible=True)

    # 6. JourneyImpactItem
    if JourneyImpactItem.objects.count() == 0:
        impacts = [
            (1, "Helping Businesses Grow", "Reliable workforce solutions that scale with our clients' needs.", "fa-solid fa-check"),
            (2, "Connecting Skilled Professionals", "Matching candidates with roles where they can genuinely thrive.", "fa-solid fa-check"),
            (3, "Supporting Career Development", "Career counselling and internships that build real, lasting skills.", "fa-solid fa-check"),
            (4, "Delivering Reliable Workforce Solutions", "Consistent, on-time delivery that businesses can depend on.", "fa-solid fa-check")
        ]
        for ord_val, t, d, ic in impacts:
            JourneyImpactItem.objects.create(order=ord_val, title=t, description=d, icon=ic, is_visible=True)

    # 7. JourneyStat
    if JourneyStat.objects.count() == 0:
        stats = [
            (1, "6", "+", "Years of Excellence", "fa-solid fa-calendar-check"),
            (2, "5000", "+", "Candidates Placed", "fa-solid fa-user-group"),
            (3, "300", "+", "Hiring Partners", "fa-solid fa-building"),
            (4, "15", "+", "Industries Served", "fa-solid fa-industry"),
            (5, "98", "%", "Client Satisfaction", "fa-solid fa-face-smile"),
            (6, "100", "%", "Commitment to Quality", "fa-solid fa-medal")
        ]
        for ord_val, cnt, sfx, lbl, ic in stats:
            JourneyStat.objects.create(order=ord_val, count=cnt, suffix=sfx, label=lbl, icon=ic, is_visible=True)

    # 8. JourneyFutureGoal
    if JourneyFutureGoal.objects.count() == 0:
        goals = [
            (1, "Expand across India", "fa-solid fa-circle-check"),
            (2, "Build stronger partnerships", "fa-solid fa-circle-check"),
            (3, "Empower more professionals", "fa-solid fa-circle-check"),
            (4, "Deliver innovative workforce solutions", "fa-solid fa-circle-check"),
            (5, "Create long-term client relationships", "fa-solid fa-circle-check")
        ]
        for ord_val, txt, ic in goals:
            JourneyFutureGoal.objects.create(order=ord_val, text=txt, icon=ic, is_visible=True)


def unseed_journey_page_data(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0016_journey_full_dynamic_models'),
    ]

    operations = [
        migrations.RunPython(seed_journey_page_data, unseed_journey_page_data),
    ]
