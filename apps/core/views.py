from django.shortcuts import render
from django.db.models import Q







from django.views.decorators.csrf import ensure_csrf_cookie







from django.core.cache import cache







from apps.jobs.models import Job, JobCategory







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







    AboutCompanySettings,







    AboutWhyCard,







    AboutTestimonial,







    AboutTestimonialStat,







    AboutTrustPoint,







    AboutPartnerLogo,







    AboutIndustryItem,







    CEOMessageSettings,







    CEOLeadershipPrinciple,







    CEOStatBadge,







    OurTeamSettings,







    TeamMember,







    TeamFeatureHighlight,







    TeamStat,







    TeamDepartment,







    TeamTrustPoint,







    TeamCoreValue,







    OurJourneySettings,







    JourneyMilestone,







    JourneyStoryParagraph,







    JourneyStoryCard,







    JourneyMilestoneCard,







    JourneyImpactItem,







    JourneyStat,







    JourneyFutureGoal,







    ManpowerSupplySettings,







    ManpowerChecklistItem,







    ManpowerServiceCard,







    ManpowerIndustryItem,







    ManpowerWhyChooseItem,







    ManpowerProcessStep,







    ManpowerStatItem,







    ManpowerFaqItem,







    ManpowerTrustItem,







    MANPOWER_SUPPLY_CACHE_KEY,







    RecruitmentPlacementSettings,







    RpWhyPartnerItem,







    RpServiceCard,







    RpProcessStep,







    RpWhyChooseItem,







    RpIndustryItem,







    RpPartnerItem,







    RpFaqItem,







    RECRUITMENT_PLACEMENT_CACHE_KEY,







    CONTRACT_STAFFING_CACHE_KEY,







    ContractStaffingSettings,







    CsServiceCard,







    CsIndustryItem,







    CsWhyChooseItem,







    CsProcessStep,







    CsBenefitEmployerItem,







    CsBenefitCandidateItem,







    CsFaqItem,







    EDUCATIONAL_CONSULTANCY_CACHE_KEY,







    EducationalConsultancySettings,







    EcServiceCard,







    EcWhyChooseItem,







    EcProcessStep,







    PAYROLL_OUTSOURCING_CACHE_KEY,







    PayrollOutsourcingSettings,







    PoServiceCard,







    PoIndustryItem,







    PoWhyChooseItem,







    PoProcessStep,







    PoEmployerBenefit,







    PoEmployeeBenefit,







    PoFaqItem,



    HR_SUPPORT_CACHE_KEY,



    HrSupportSettings,



    HrFeatureItem,



    HrServiceCard,



    HrAdditionalServiceItem,



    HrWhyChooseItem,



    HrProcessStep,



    HrEmployerBenefit,



    HrEmployeeBenefit,

    INTERNSHIP_CACHE_KEY,

    InternshipSettings,

    InternshipStripItem,

    InternshipTrackItem,

    InternshipHighlightItem,

    InternshipWhoCanApplyItem,

    InternshipWhatYouLearnItem,

    InternshipProcessStep,

    InternshipBenefitItem,

    InternshipFaqItem,

)























def seed_initial_about_industries():







    from apps.jobs.models import JobCategory







    if AboutIndustryItem.objects.exists():







        return







    job_industries = list(JobCategory.objects.filter(category_type='industry').order_by('order', 'id'))







    if job_industries:







        for idx, jc in enumerate(job_industries, 1):







            AboutIndustryItem.objects.create(







                name=jc.name,







                icon_class=jc.icon or 'fas fa-briefcase',







                order=idx,







                is_visible=True,







                link_url=f"/jobs/?industry={jc.name}"







            )







    else:







        defaults = [







            ("Information Technology (IT)", "fas fa-desktop", 1),







            ("Manufacturing & Production", "fas fa-industry", 2),







            ("Healthcare & Pharmaceuticals", "fas fa-heartbeat", 3),







            ("Banking & Finance", "fas fa-university", 4),







            ("Retail & E-commerce", "fas fa-store", 5),







            ("Education & Training", "fas fa-school", 6),







            ("Logistics & Supply Chain", "fas fa-truck", 7),







            ("Construction & Real Estate", "fas fa-hard-hat", 8),







            ("Hospitality & Tourism", "fas fa-users", 9),







            ("Corporate & Consulting", "fas fa-building", 10),







            ("Telecom & Networks", "fas fa-broadcast-tower", 11),







            ("Global Opportunities", "fas fa-globe", 12),







        ]







        for name, icon, order in defaults:







            AboutIndustryItem.objects.create(







                name=name,







                icon_class=icon,







                order=order,







                is_visible=True,







                link_url=f"/jobs/?industry={name}"







            )























def seed_initial_ceo_principles():







    items = [







        {"title": "Integrity First", "description": "We operate with honesty, transparency, and accountability in everything we do.", "icon_class": "fa-solid fa-shield-halved", "order": 1},







        {"title": "People-Centric Approach", "description": "Every client and candidate is treated with respect and professionalism.", "icon_class": "fa-solid fa-user-group", "order": 2},







        {"title": "Excellence in Service", "description": "We are committed to delivering high-quality recruitment solutions.", "icon_class": "fa-solid fa-medal", "order": 3},







        {"title": "Innovation & Growth", "description": "We continuously improve through technology and modern hiring practices.", "icon_class": "fa-solid fa-lightbulb", "order": 4},







        {"title": "Long-Term Partnerships", "description": "We focus on building relationships based on trust and mutual success.", "icon_class": "fa-solid fa-handshake", "order": 5},







    ]







    for it in items:







        CEOLeadershipPrinciple.objects.create(**it)























def seed_initial_ceo_badges():







    items = [







        {"value": "10+", "label": "Years Leadership", "icon_class": "fa-solid fa-award", "order": 1},







        {"value": "5,000+", "label": "Candidates Placed", "icon_class": "fa-solid fa-user-check", "order": 2},







        {"value": "250+", "label": "Corporate Partners", "icon_class": "fa-solid fa-building", "order": 3},







    ]







    for it in items:







        CEOStatBadge.objects.create(**it)































def seed_initial_team_members():







    members = [







        # Leadership







        {"name": "Ashvani Dubey", "role": "CEO & Founder", "category": "leadership", "static_photo_path": "images/team/CEO image.png", "bio": "Visionary leader with a passion for connecting talent with opportunities and building successful futures.", "order": 1},







        {"name": "Ruchi Singh", "role": "Managing Director", "category": "leadership", "static_photo_path": "images/team/Ruchi sigh.png", "bio": "Driving strategic growth and building strong partnerships across diverse industries and markets.", "order": 2},







        {"name": "Sweety", "role": "Director – HR", "category": "leadership", "static_photo_path": "images/services/hr .png", "bio": "Leading talent acquisition and HR consulting with a people-centric approach and strong leadership.", "order": 3},







        {"name": "Ajay Vishwakarma", "role": "Team Lead", "category": "leadership", "static_photo_path": "images/team/ajay_vishwakarma.png", "bio": "Ensuring operational excellence and delivering seamless recruitment solutions to our clients.", "order": 4},







        # Specialists







        {"name": "Priya Sharma", "role": "Senior Recruitment Consultant", "category": "specialist", "static_photo_path": "images/team/female1.jpg", "experience_text": "Experience: 7+ Years", "order": 5},







        {"name": "Amit Verma", "role": "IT Recruitment Consultant", "category": "specialist", "static_photo_path": "images/team/male1.avif", "experience_text": "Experience: 5+ Years", "order": 6},







        {"name": "Sunita Rao", "role": "Operations & Compliance Manager", "category": "specialist", "static_photo_path": "images/team/female2.jpg", "experience_text": "Experience: 6+ Years", "order": 7},







        {"name": "Vikram Malhotra", "role": "Talent Acquisition Specialist", "category": "specialist", "static_photo_path": "images/team/male2.avif", "experience_text": "Experience: 4+ Years", "order": 8},







    ]







    for m in members:







        TeamMember.objects.create(**m)























def seed_initial_journey_milestones():







    milestones = [







        {"year": "2022", "title": "Company Founded", "badge_label": "The Beginning", "icon_class": "fa-solid fa-flag", "description": "Sky Vision Group Consultancy was established in Lucknow with a mission to connect skilled talent with the right opportunities.", "order": 1},







        {"year": "2023", "title": "Expanding Our Services", "badge_label": "100+ Hiring Partners", "icon_class": "fa-solid fa-people-group", "description": "We broadened into contract staffing and payroll outsourcing, building lasting partnerships with growing businesses.", "order": 2},







        {"year": "2024", "title": "Technology & Pan-India Reach", "badge_label": "5000+ Placed", "icon_class": "fa-solid fa-chart-line", "description": "Adopted modern ATS software and expanded across North India, placing thousands of qualified job seekers.", "order": 3},







        {"year": "2025", "title": "Strategic Enterprise Solutions", "badge_label": "250+ Corporate Clients", "icon_class": "fa-solid fa-handshake-angle", "description": "Partnered with national corporates for executive hiring, bulk industrial staffing and customized HR solutions.", "order": 4},







        {"year": "2026", "title": "The Next Frontier", "badge_label": "Nationwide Growth", "icon_class": "fa-solid fa-rocket", "description": "Scaling digital recruitment platforms, regional franchise offices, and student skill-building internship centers.", "order": 5},







    ]







    for ms in milestones:







        JourneyMilestone.objects.create(**ms)























def seed_initial_team_highlights():







    features = [







        ("fa-solid fa-users", "Expert Professionals", "Experienced recruiters and HR experts with in-depth industry knowledge.", 1),







        ("fa-solid fa-bullseye", "Client Focused", "Building long-term partnerships and delivering value-driven solutions.", 2),







        ("fa-solid fa-lightbulb", "People First Approach", "We believe in people, relationships, and creating meaningful opportunities.", 3),







        ("fa-solid fa-shield-halved", "Integrity & Transparency", "Maintaining honesty and transparency in every interaction.", 4),







    ]







    for icon, title, desc, order in features:







        TeamFeatureHighlight.objects.create(







            icon=icon,







            title=title,







            description=desc,







            order=order,







            is_visible=True







        )























def seed_initial_team_values():







    values = [







        ('fa-solid fa-handshake', 'Integrity', 'Building trust through honesty, ethics, and transparency.', 1),







        ('fa-solid fa-trophy', 'Excellence', 'Delivering consistent quality in every recruitment assignment.', 2),







        ('fa-solid fa-link', 'Collaboration', 'Working together with clients and candidates for shared success.', 3),







        ('fa-solid fa-lightbulb', 'Innovation', 'Leveraging modern recruitment strategies and technology.', 4),







    ]







    for icon, title, desc, order in values:







        TeamCoreValue.objects.create(







            icon=icon,







            title=title,







            description=desc,







            order=order,







            is_visible=True







        )























def get_about_pages_context():







    data = cache.get('about_pages_context')







    if data is None:







        try:







            about_company = AboutCompanySettings.get_settings()







            why_cards = list(AboutWhyCard.objects.filter(is_visible=True).order_by('order', 'id'))







            candidate_testimonials = list(AboutTestimonial.objects.filter(is_visible=True, testimonial_type='candidate').order_by('order', 'id'))







            employer_testimonials = list(AboutTestimonial.objects.filter(is_visible=True, testimonial_type='employer').order_by('order', 'id'))







            testimonial_stats = list(AboutTestimonialStat.objects.filter(is_visible=True).order_by('order', 'id'))







            trust_points = list(AboutTrustPoint.objects.filter(is_visible=True).order_by('order', 'id'))







            partner_logos = list(AboutPartnerLogo.objects.filter(is_visible=True).order_by('order', 'id'))















            ceo_message = CEOMessageSettings.get_settings()







            if not CEOLeadershipPrinciple.objects.exists():







                seed_initial_ceo_principles()







            principles = list(CEOLeadershipPrinciple.objects.filter(is_visible=True).order_by('order', 'id'))















            if not CEOStatBadge.objects.exists():







                seed_initial_ceo_badges()







            ceo_stat_badges = list(CEOStatBadge.objects.filter(is_visible=True).order_by('order', 'id'))















            team_settings = OurTeamSettings.get_settings()







            if not TeamMember.objects.exists():







                seed_initial_team_members()







            team_members = list(TeamMember.objects.filter(is_visible=True).order_by('order', 'id'))















            leadership_all = [m for m in team_members if m.category == 'leadership']







            if team_settings.leadership_max_items and team_settings.leadership_max_items > 0:







                leadership_members = leadership_all[:team_settings.leadership_max_items]







            else:







                leadership_members = leadership_all















            specialist_all = [m for m in team_members if m.category == 'specialist']







            if team_settings.specialists_max_items and team_settings.specialists_max_items > 0:







                specialist_members = specialist_all[:team_settings.specialists_max_items]







            else:







                specialist_members = specialist_all















            if not TeamFeatureHighlight.objects.exists():







                seed_initial_team_highlights()







            team_highlights = list(TeamFeatureHighlight.objects.filter(is_visible=True).order_by('order', 'id'))







            team_stats = list(TeamStat.objects.filter(is_visible=True).order_by('order', 'id'))







            team_departments = list(TeamDepartment.objects.filter(is_visible=True).order_by('order', 'id'))







            team_trust_points = list(TeamTrustPoint.objects.filter(is_visible=True).order_by('order', 'id'))















            if not TeamCoreValue.objects.exists():







                seed_initial_team_values()







            team_values = list(TeamCoreValue.objects.filter(is_visible=True).order_by('order', 'id'))















            max_team = about_company.team_max_items or 20







            selected_team = list(TeamMember.objects.filter(is_visible=True, show_on_about_page=True).order_by('about_page_order', 'order', 'id'))







            if selected_team:







                if max_team <= 4 and len(selected_team) > max_team:







                    max_team = max(20, len(selected_team))







                about_team_members = selected_team[:max_team]







            else:







                about_team_members = [m for m in team_members if m.category == 'leadership'][:max_team]







                if not about_team_members:







                    about_team_members = team_members[:max_team]















            journey_settings = OurJourneySettings.get_settings()







            if not JourneyMilestone.objects.exists():







                seed_initial_journey_milestones()







            journey_milestones = list(JourneyMilestone.objects.filter(is_visible=True).order_by('order', 'id'))







            journey_story_paragraphs = list(JourneyStoryParagraph.objects.filter(is_visible=True).order_by('order', 'id'))







            journey_story_cards = list(JourneyStoryCard.objects.filter(is_visible=True).order_by('order', 'id'))







            journey_milestone_cards = list(JourneyMilestoneCard.objects.filter(is_visible=True).order_by('order', 'id'))







            journey_impact_items = list(JourneyImpactItem.objects.filter(is_visible=True).order_by('order', 'id'))







            journey_stats = list(JourneyStat.objects.filter(is_visible=True).order_by('order', 'id'))







            journey_future_goals = list(JourneyFutureGoal.objects.filter(is_visible=True).order_by('order', 'id'))















            if not AboutIndustryItem.objects.exists():







                seed_initial_about_industries()







            about_industries = list(AboutIndustryItem.objects.filter(is_visible=True).order_by('order', 'id'))















            data = {







                'about_company': about_company,







                'why_cards': why_cards,







                'about_industries': about_industries,







                'candidate_testimonials': candidate_testimonials,







                'employer_testimonials': employer_testimonials,







                'testimonial_stats': testimonial_stats,







                'trust_points': trust_points,







                'partner_logos': partner_logos,







                'about_team_members': about_team_members,







                'ceo_message': ceo_message,







                'ceo_principles': principles,







                'ceo_stat_badges': ceo_stat_badges,







                'team_settings': team_settings,







                'team_members': team_members,







                'leadership_members': leadership_members,







                'specialist_members': specialist_members,







                'team_highlights': team_highlights,







                'team_stats': team_stats,







                'team_departments': team_departments,







                'team_trust_points': team_trust_points,







                'team_values': team_values,







                'journey_settings': journey_settings,







                'journey_milestones': journey_milestones,







                'journey_timeline_items': journey_milestones,







                'journey_story_paragraphs': journey_story_paragraphs,







                'has_story_paragraphs': JourneyStoryParagraph.objects.exists(),







                'journey_story_cards': journey_story_cards,







                'journey_milestone_cards': journey_milestone_cards,







                'journey_impact_items': journey_impact_items,







                'journey_stats': journey_stats,







                'journey_future_goals': journey_future_goals,







            }







            cache.set('about_pages_context', data, 300)







        except Exception:







            data = {







                'about_company': AboutCompanySettings(),







                'why_cards': [],







                'about_industries': [],







                'candidate_testimonials': [],







                'employer_testimonials': [],







                'testimonial_stats': [],







                'trust_points': [],







                'partner_logos': [],







                'about_team_members': [],







                'ceo_message': CEOMessageSettings(),







                'ceo_principles': [],







                'ceo_stat_badges': [],







                'team_settings': OurTeamSettings(),







                'team_members': [],







                'leadership_members': [],







                'specialist_members': [],







                'team_highlights': [],







                'team_stats': [],







                'team_departments': [],







                'team_trust_points': [],







                'team_values': [],







                'journey_settings': OurJourneySettings(),







                'journey_milestones': [],







                'journey_timeline_items': [],







                'journey_story_paragraphs': [],







                'journey_story_cards': [],







                'journey_milestone_cards': [],







                'journey_impact_items': [],







                'journey_stats': [],







                'journey_future_goals': [],







            }







    return data































def get_home_page_context():







    """







    Retrieves cached home page content (5 min cache, invalidated instantly on save/delete).







    """







    data = cache.get('home_page_context')







    if data is None:







        try:







            home_settings = HomePageSettings.get_settings()







            hero_stats = list(HeroStat.objects.filter(is_visible=True).order_by('order', 'id'))







            growth_steps = list(GrowthStep.objects.filter(is_visible=True).order_by('order', 'step_number', 'id'))







            service_cards = list(HomeServiceCard.objects.filter(is_visible=True).order_by('order', 'id'))







            why_choose_items = list(WhyChooseItem.objects.filter(is_visible=True).order_by('order', 'id'))







            custom_industries = list(HomeIndustryItem.objects.filter(is_visible=True).order_by('order', 'id'))







            internship_cards = list(InternshipCard.objects.filter(is_visible=True).order_by('order', 'id'))







            internship_benefits = list(InternshipHighlight.objects.filter(is_visible=True, item_type='benefit').order_by('order', 'id'))







            internship_badges = list(InternshipHighlight.objects.filter(is_visible=True, item_type='bottom_badge').order_by('order', 'id'))







            featured_candidates = list(FeaturedCandidate.objects.filter(is_visible=True, show_publicly=True).order_by('order', 'id'))







            gallery_images = list(GalleryImage.objects.filter(is_visible=True, show_on_home=True).order_by('order', 'id'))







            gallery_info_boxes = list(GalleryInfoBox.objects.filter(is_visible=True).order_by('order', 'id'))















            data = {







                'home_settings': home_settings,







                'hero_stats': hero_stats,







                'growth_steps': growth_steps,







                'service_cards': service_cards,







                'why_choose_items': why_choose_items,







                'custom_industries': custom_industries,







                'internship_cards': internship_cards,







                'internship_benefits': internship_benefits,







                'internship_badges': internship_badges,







                'featured_candidates': featured_candidates,







                'gallery_images': gallery_images,







                'gallery_info_boxes': gallery_info_boxes,







            }







            cache.set('home_page_context', data, 300)







        except Exception:







            data = {







                'home_settings': HomePageSettings(),







                'hero_stats': [],







                'growth_steps': [],







                'service_cards': [],







                'why_choose_items': [],







                'custom_industries': [],







                'internship_cards': [],







                'internship_benefits': [],







                'internship_badges': [],







                'featured_candidates': [],







                'gallery_images': [],







                'gallery_info_boxes': [],







            }







    return data























def get_active_job_locations():
    """Returns unique, clean locations with active jobs, plus common regional hubs."""
    try:
        db_locs = Job.objects.live().values_list('location', flat=True).distinct()
    except Exception:
        db_locs = []
    cities = []
    seen = set()

    for loc in db_locs:
        if not loc:
            continue
        city = loc.split(',')[0].strip()
        if city and city.lower() not in seen:
            seen.add(city.lower())
            cities.append(city)

    popular = ['Ballia', 'Lucknow', 'Kanpur', 'Varanasi', 'Prayagraj', 'Gorakhpur', 'Noida', 'Bareilly', 'Ayodhya', 'Delhi NCR']
    for p in popular:
        if p.lower() not in seen:
            seen.add(p.lower())
            cities.append(p)

    return cities


def filter_active_jobs(request):
    """Filters active jobs according to search parameters from GET request."""
    location = (request.GET.get('location') or '').strip()
    category = (request.GET.get('category') or request.GET.get('field') or '').strip()
    q = (request.GET.get('q') or request.GET.get('keyword') or '').strip()
    job_type = (request.GET.get('job_type') or request.GET.get('type') or '').strip()
    experience = (request.GET.get('experience') or '').strip()

    qs = Job.objects.live()

    if location and location.lower() not in ['all', 'location', 'all locations']:
        qs = qs.filter(location__icontains=location)

    if category and category.lower() not in ['all', 'all categories', 'category']:
        cat_obj = JobCategory.objects.filter(field_slug__iexact=category).first()
        cat_name = cat_obj.name if cat_obj else category
        qs = qs.filter(
            Q(category__icontains=category) |
            Q(category__icontains=cat_name) |
            Q(department__icontains=category) |
            Q(department__icontains=cat_name) |
            Q(title__icontains=category) |
            Q(title__icontains=cat_name)
        )

    if q:
        qs = qs.filter(
            Q(title__icontains=q) |
            Q(description__icontains=q) |
            Q(requirements__icontains=q) |
            Q(category__icontains=q) |
            Q(department__icontains=q) |
            Q(company__name__icontains=q) |
            Q(employer__company_name__icontains=q) |
            Q(location__icontains=q)
        )

    if job_type and job_type.lower() not in ['all', 'all jobs', 'select type', 'select']:
        qs = qs.filter(employment_type__icontains=job_type)

    if experience and experience.lower() not in ['all', 'select experience']:
        qs = qs.filter(experience__icontains=experience)

    search_meta = {
        'search_location': location if location.lower() not in ['all', 'location', 'all locations'] else '',
        'search_category': category if category.lower() not in ['all', 'all categories', 'category'] else '',
        'search_query': q,
        'search_job_type': job_type if job_type.lower() not in ['all', 'all jobs', 'select type', 'select'] else '',
        'search_experience': experience if experience.lower() not in ['all', 'select experience'] else '',
    }
    return qs.order_by('-id'), search_meta


@ensure_csrf_cookie
def home(request):







    contact_submitted = False







    contact_message = None















    # Handle fallback if contact form was submitted via GET/POST directly to '/'







    name = (request.GET.get('name') or request.POST.get('name') or '').strip()







    phone = (request.GET.get('phone') or request.POST.get('phone') or '').strip()







    email = (request.GET.get('email') or request.POST.get('email') or '').strip()







    honeypot = (request.GET.get('website_url') or request.POST.get('website_url') or '').strip()















    if name and phone and email and not honeypot:







        try:







            from apps.enquiries.models import ContactEnquiry, log_activity







            from apps.enquiries.constants import classify_enquiry_type







            from django.utils import timezone







            from datetime import timedelta







            service = request.GET.get('service') or request.POST.get('service') or 'General Inquiry'







            message = request.GET.get('message') or request.POST.get('message') or ''















            ten_mins_ago = timezone.now() - timedelta(minutes=10)







            if not ContactEnquiry.objects.filter(email=email, message=message, created_at__gte=ten_mins_ago).exists():







                enq_type = classify_enquiry_type(service, message)







                ContactEnquiry.objects.create(







                    name=name,







                    email=email,







                    phone=phone,







                    service=service,







                    message=message,







                    enquiry_type=enq_type,







                    status='New',







                    notes=''







                )







                log_activity("general", "General enquiry received", f"From {name} ({email}) regarding {service}")







            contact_submitted = True







            contact_message = "Thank you! Your enquiry has been received. We will contact you soon."







        except Exception:







            pass















    home_context = get_home_page_context()







    custom_inds = home_context.get('custom_industries')







    if custom_inds:







        industries = custom_inds







    else:







        industries = JobCategory.objects.filter(category_type='industry', status='Active').order_by('order', 'id')















    available_locations = get_active_job_locations()
    job_pills = JobCategory.objects.filter(category_type='job_pill', status='Active').order_by('order', 'id')
    job_categories = JobCategory.objects.filter(category_type='job_category', status='Active').order_by('order', 'id')

    active_jobs, search_meta = filter_active_jobs(request)
    active_jobs = active_jobs[:12]

    existing_cat_names = set(c.name.lower() for c in job_categories)
    extra_categories = []
    try:
        for j_cat in Job.objects.live().values_list('category', flat=True).distinct():
            if j_cat and j_cat.strip() and j_cat.strip().lower() not in existing_cat_names:
                extra_categories.append(j_cat.strip())
                existing_cat_names.add(j_cat.strip().lower())
    except Exception:
        pass

    ctx = {
        'active_page': 'home',
        'active_jobs': active_jobs,
        'available_locations': available_locations,
        'extra_categories': extra_categories,
        **search_meta,







        'job_pills': job_pills,







        'industries': industries,







        'job_categories': job_categories,







        'contact_submitted': contact_submitted,







        'contact_message': contact_message,







        **home_context,







    }







    return render(request, 'pages/home.html', ctx)















def about(request):







    about_ctx = get_about_pages_context()







    industries = about_ctx.get('about_industries')







    if industries is None:







        industries = JobCategory.objects.filter(category_type='industry', status='Active').order_by('order', 'id')







    return render(request, 'pages/about.html', {







        'active_page': 'about',







        'industries': industries,







        'about_settings': about_ctx['about_company'],







        'team_members': about_ctx['team_members'],







        **about_ctx,







    })















def about_company(request):







    about_ctx = get_about_pages_context()







    return render(request, 'pages/about_company.html', {







        'active_page': 'about',







        'about_settings': about_ctx['about_company'],







        **about_ctx,







    })















def ourteam(request):







    about_ctx = get_about_pages_context()







    return render(request, 'pages/ourteam.html', {







        'active_page': 'about',







        'team_settings': about_ctx['team_settings'],







        'team_members': about_ctx['team_members'],







        'leadership_members': about_ctx['leadership_members'],







        'specialist_members': about_ctx['specialist_members'],







        **about_ctx,







    })















def ceo(request):







    about_ctx = get_about_pages_context()







    return render(request, 'pages/CEO.html', {







        'active_page': 'about',







        'ceo_settings': about_ctx['ceo_message'],







        'principles': about_ctx['ceo_principles'],







        'stat_badges': about_ctx['ceo_stat_badges'],







        **about_ctx,







    })















def ourjourney(request):







    about_ctx = get_about_pages_context()







    return render(request, 'pages/ourjourney.html', {







        'active_page': 'about',







        'journey_settings': about_ctx['journey_settings'],







        'milestones': about_ctx['journey_milestones'],







        'timeline_items': about_ctx['journey_milestones'],







        'story_paragraphs': about_ctx['journey_story_paragraphs'],







        'has_story_paragraphs': about_ctx.get('has_story_paragraphs', JourneyStoryParagraph.objects.exists()),







        'story_cards': about_ctx['journey_story_cards'],







        'milestone_cards': about_ctx['journey_milestone_cards'],







        'impact_items': about_ctx['journey_impact_items'],







        'stats': about_ctx['journey_stats'],







        'future_goals': about_ctx['journey_future_goals'],







        **about_ctx,







    })























def seed_initial_manpower_supply_data():







    ManpowerSupplySettings.get_settings()















    if not ManpowerChecklistItem.objects.exists():







        checklist_defaults = [







            ("Quality Manpower", "fa-solid fa-circle-check", 1),







            ("Verified Background", "fa-solid fa-circle-check", 2),







            ("Flexible Engagement", "fa-solid fa-circle-check", 3),







            ("Timely Delivery", "fa-solid fa-circle-check", 4),







            ("Pan India Services", "fa-solid fa-circle-check", 5),







        ]







        for text, icon, order in checklist_defaults:







            ManpowerChecklistItem.objects.create(text=text, icon_class=icon, order=order, is_visible=True)















    if not ManpowerServiceCard.objects.exists():







        service_defaults = [







            ("Skilled Manpower", "Well trained and experienced professionals for specialized job roles.", "fa-solid fa-people-group", "i-blue", 1),







            ("Unskilled Manpower", "Dependable and hardworking manpower for general and supporting tasks.", "fa-solid fa-user", "i-teal", 2),







            ("Industrial Workforce", "Industrial manpower for production, operations and maintenance.", "fa-solid fa-industry", "i-amber", 3),







            ("Factory Staff", "Reliable staff for factories, plants and manufacturing units.", "fa-solid fa-helmet-safety", "i-purple", 4),







            ("Office Staff", "Office assistants, executives and clerical staff to support daily operations.", "fa-solid fa-briefcase", "i-pink", 5),







            ("Contract Staffing", "Hire skilled manpower on contract basis as per your business needs.", "fa-solid fa-file-signature", "i-blue", 6),







            ("Temporary Manpower", "Short term manpower to handle temporary or seasonal workload.", "fa-regular fa-clock", "i-green", 7),







            ("Housekeeping Staff", "Trained housekeeping and support staff for clean, hygienic workplaces.", "fa-solid fa-broom", "i-teal", 8),







        ]







        for title, desc, icon, color, order in service_defaults:







            ManpowerServiceCard.objects.create(title=title, description=desc, icon_class=icon, color_class=color, order=order, is_visible=True)















    if not ManpowerIndustryItem.objects.exists():







        industry_defaults = [







            ("Manufacturing", "fa-solid fa-industry", 1),







            ("Construction", "fa-solid fa-hard-hat", 2),







            ("Logistics", "fa-solid fa-truck", 3),







            ("Healthcare", "fa-solid fa-heart-pulse", 4),







            ("Retail", "fa-solid fa-cart-shopping", 5),







            ("Hospitality", "fa-solid fa-bed", 6),







            ("BPO / KPO", "fa-solid fa-headset", 7),







            ("IT & ITES", "fa-solid fa-desktop", 8),







        ]







        for name, icon, order in industry_defaults:







            ManpowerIndustryItem.objects.create(name=name, icon_class=icon, order=order, is_visible=True)















    if not ManpowerWhyChooseItem.objects.exists():







        why_defaults = [







            ("Experienced Team", "fa-solid fa-user-group", 1),







            ("Verified Candidates", "fa-solid fa-circle-check", 2),







            ("Fast Recruitment", "fa-solid fa-bolt", 3),







            ("24x7 Support", "fa-solid fa-headset", 4),







            ("Affordable Cost", "fa-solid fa-indian-rupee-sign", 5),







            ("Pan India Hiring", "fa-solid fa-map-location-dot", 6),







        ]







        for title, icon, order in why_defaults:







            ManpowerWhyChooseItem.objects.create(title=title, icon_class=icon, order=order, is_visible=True)















    if not ManpowerProcessStep.objects.exists():







        process_defaults = [







            ("01", "Requirement Analysis", "fa-solid fa-clipboard-list", 1),







            ("02", "Screening & Shortlisting", "fa-solid fa-magnifying-glass", 2),







            ("03", "Interview & Evaluation", "fa-solid fa-comments", 3),







            ("04", "Selection & Verification", "fa-solid fa-user-check", 4),







            ("05", "Deployment & Onboarding", "fa-solid fa-user-shield", 5),







        ]







        for num, title, icon, order in process_defaults:







            ManpowerProcessStep.objects.create(step_number=num, title=title, icon_class=icon, order=order, is_visible=True)















    if not ManpowerStatItem.objects.exists():







        stat_defaults = [







            ("5000+", "Candidates Placed", "fa-solid fa-user-group", 1),







            ("300+", "Happy Clients", "fa-solid fa-building", 2),







            ("50+", "HR Experts", "fa-solid fa-people-group", 3),







            ("10+", "Years of Experience", "fa-solid fa-award", 4),







        ]







        for val, lbl, icon, order in stat_defaults:







            ManpowerStatItem.objects.create(value=val, label=lbl, icon_class=icon, order=order, is_visible=True)















    if not ManpowerFaqItem.objects.exists():







        faq_defaults = [







            ("How quickly can you provide manpower?", "We typically deploy manpower within 2–5 working days depending on the role and location.", 1),







            ("Do you provide contract manpower?", "Yes, we offer flexible contract staffing options tailored to your project duration and needs.", 2),







            ("What if the manpower leaves the job?", "We provide a quick replacement at no extra cost within the agreed replacement period.", 3),







            ("Do you provide manpower across India?", "Yes, we have Pan India reach and can deploy manpower across multiple states and cities.", 4),







            ("What documents do you provide?", "We provide verified ID proof, background verification reports and all statutory compliance documents.", 5),







        ]







        for q, a, order in faq_defaults:







            ManpowerFaqItem.objects.create(question=q, answer=a, order=order, is_visible=True)















    if not ManpowerTrustItem.objects.exists():







        trust_defaults = [







            ("Trusted by", "Top Companies", "fa-solid fa-award", 1),







            ("100% Compliance", "& Legal Support", "fa-solid fa-file-shield", 2),







            ("Timely Service", "Delivery", "fa-regular fa-clock", 3),







            ("Customer Satisfaction", "Our Priority", "fa-solid fa-face-smile", 4),







        ]







        for l1, l2, icon, order in trust_defaults:







            ManpowerTrustItem.objects.create(line1=l1, line2=l2, icon_class=icon, order=order, is_visible=True)























def get_manpower_supply_context():







    cached = cache.get(MANPOWER_SUPPLY_CACHE_KEY)







    if cached:







        return cached















    if not ManpowerServiceCard.objects.exists():







        seed_initial_manpower_supply_data()















    ms_settings = ManpowerSupplySettings.get_settings()







    ctx = {







        'ms_settings': ms_settings,







        'checklist_items': list(ManpowerChecklistItem.objects.filter(is_visible=True).order_by('order', 'id')),







        'service_cards': list(ManpowerServiceCard.objects.filter(is_visible=True).order_by('order', 'id')),







        'industry_items': list(ManpowerIndustryItem.objects.filter(is_visible=True).order_by('order', 'id')),







        'why_choose_items': list(ManpowerWhyChooseItem.objects.filter(is_visible=True).order_by('order', 'id')),







        'process_steps': list(ManpowerProcessStep.objects.filter(is_visible=True).order_by('order', 'id')),







        'stat_items': list(ManpowerStatItem.objects.filter(is_visible=True).order_by('order', 'id')),







        'faq_items': list(ManpowerFaqItem.objects.filter(is_visible=True).order_by('order', 'id')),







        'trust_items': list(ManpowerTrustItem.objects.filter(is_visible=True).order_by('order', 'id')),







    }







    cache.set(MANPOWER_SUPPLY_CACHE_KEY, ctx, 60 * 60)







    return ctx























def services(request):







    return render(request, 'pages/services.html', {'active_page': 'services'})































def seed_initial_recruitment_placement_data(force=False):







    if force:







        RecruitmentPlacementSettings.objects.all().delete()







        RpWhyPartnerItem.objects.all().delete()







        RpServiceCard.objects.all().delete()







        RpProcessStep.objects.all().delete()







        RpWhyChooseItem.objects.all().delete()







        RpIndustryItem.objects.all().delete()







        RpPartnerItem.objects.all().delete()







        RpFaqItem.objects.all().delete()















    RecruitmentPlacementSettings.get_settings()















    if not RpWhyPartnerItem.objects.exists():







        why_partner_defaults = [







            ("Faster turnaround time", "fa-solid fa-check", 1),







            ("Verified & quality candidates", "fa-solid fa-check", 2),







            ("Industry-specific expertise", "fa-solid fa-check", 3),







            ("Customized hiring solutions", "fa-solid fa-check", 4),







            ("End-to-end recruitment support", "fa-solid fa-check", 5),







        ]







        for text, icon, order in why_partner_defaults:







            RpWhyPartnerItem.objects.create(text=text, icon_class=icon, order=order, is_visible=True)















    if not RpServiceCard.objects.exists():







        service_defaults = [







            ("Permanent Hiring", "End-to-end permanent staffing solutions for all levels and domains.", "fa-solid fa-user", "i-blue", 1),







            ("Executive Hiring", "Hire experienced leaders and executives to drive your business forward.", "fa-solid fa-user-tie", "i-amber", 2),







            ("Bulk Hiring", "Large volume hiring solutions across multiple locations and roles.", "fa-solid fa-user-group", "i-green", 3),







            ("Campus Recruitment", "Connect with top talent through campus hiring and internship programs.", "fa-solid fa-graduation-cap", "i-purple", 4),







            ("Overseas Recruitment", "Global recruitment solutions with complete documentation support.", "fa-solid fa-globe", "i-teal", 5),







            ("HR Outsourcing", "Comprehensive HR outsourcing to streamline your operations and reduce costs.", "fa-solid fa-headset", "i-pink", 6),







        ]







        for title, desc, icon, color, order in service_defaults:







            RpServiceCard.objects.create(title=title, description=desc, icon_class=icon, color_class=color, order=order, is_visible=True)















    if not RpProcessStep.objects.exists():







        process_defaults = [







            ("01", "Requirement Collection", "fa-solid fa-clipboard-list", 1),







            ("02", "Candidate Sourcing", "fa-solid fa-user-group", 2),







            ("03", "Resume Screening", "fa-solid fa-file-lines", 3),







            ("04", "Interview & Assessment", "fa-solid fa-comments", 4),







            ("05", "Final Selection", "fa-solid fa-user-check", 5),







            ("06", "Joining & Support", "fa-solid fa-handshake", 6),







        ]







        for num, title, icon, order in process_defaults:







            RpProcessStep.objects.create(step_number=num, title=title, icon_class=icon, order=order, is_visible=True)















    if not RpWhyChooseItem.objects.exists():







        why_choose_defaults = [







            ("Verified & quality candidates", "fa-solid fa-circle-check", 1),







            ("Faster turnaround time", "fa-solid fa-circle-check", 2),







            ("Industry expert recruiters", "fa-solid fa-circle-check", 3),







            ("Pan India recruitment", "fa-solid fa-circle-check", 4),







            ("Cost effective solutions", "fa-solid fa-circle-check", 5),







            ("Dedicated HR team", "fa-solid fa-circle-check", 6),







            ("End-to-end support", "fa-solid fa-circle-check", 7),







            ("High success rate", "fa-solid fa-circle-check", 8),







        ]







        for text, icon, order in why_choose_defaults:







            RpWhyChooseItem.objects.create(text=text, icon_class=icon, order=order, is_visible=True)















    if not RpIndustryItem.objects.exists():







        industry_defaults = [







            ("IT & Software", "fa-solid fa-desktop", 1),







            ("Healthcare", "fa-solid fa-heart-pulse", 2),







            ("Manufacturing", "fa-solid fa-industry", 3),







            ("Construction", "fa-solid fa-hard-hat", 4),







            ("Retail", "fa-solid fa-cart-shopping", 5),







            ("Logistics", "fa-solid fa-truck", 6),







            ("Education", "fa-solid fa-graduation-cap", 7),







            ("Sales & Marketing", "fa-solid fa-bullhorn", 8),







            ("BPO", "fa-solid fa-headset", 9),







            ("Automobile", "fa-solid fa-car", 10),







        ]







        for name, icon, order in industry_defaults:







            RpIndustryItem.objects.create(name=name, icon_class=icon, order=order, is_visible=True)















    if not RpPartnerItem.objects.exists():







        partner_defaults = [







            ("TATA", 1),







            ("Infosys", 2),







            ("Wipro", 3),







            ("HDFC Bank", 4),







            ("Axis Bank", 5),







            ("Tech Mahindra", 6),







            ("Amazon", 7),







        ]







        for name, order in partner_defaults:







            RpPartnerItem.objects.create(name=name, order=order, is_visible=True)















    if not RpFaqItem.objects.exists():







        faq_defaults = [







            ("How long does the hiring process take?", "Typically our hiring process takes 7–15 working days depending on the role and requirements.", 1),







            ("Do you provide bulk hiring solutions?", "Yes, we specialize in bulk hiring across multiple locations for various industries.", 2),







            ("Do you hire freshers?", "Yes, we work with companies on campus recruitment and fresher hiring programs.", 3),







            ("Do you provide overseas recruitment?", "Yes, we offer end-to-end overseas recruitment support including documentation.", 4),







            ("What documents are required for overseas jobs?", "Passport, educational certificates, experience letters and a valid visa are typically required. Our team guides you through the entire process.", 5),







        ]







        for q, a, order in faq_defaults:







            RpFaqItem.objects.create(question=q, answer=a, order=order, is_visible=True)























def get_recruitment_placement_context():







    cached = cache.get(RECRUITMENT_PLACEMENT_CACHE_KEY)







    if cached:







        return cached















    if not RpServiceCard.objects.exists():







        seed_initial_recruitment_placement_data()















    rp_settings = RecruitmentPlacementSettings.get_settings()







    wp_items = list(RpWhyPartnerItem.objects.filter(is_visible=True).order_by('order', 'id'))







    s_cards = list(RpServiceCard.objects.filter(is_visible=True).order_by('order', 'id'))







    p_steps = list(RpProcessStep.objects.filter(is_visible=True).order_by('order', 'id'))







    wc_items = list(RpWhyChooseItem.objects.filter(is_visible=True).order_by('order', 'id'))







    ind_items = list(RpIndustryItem.objects.filter(is_visible=True).order_by('order', 'id'))







    prt_items = list(RpPartnerItem.objects.filter(is_visible=True).order_by('order', 'id'))







    f_items = list(RpFaqItem.objects.filter(is_visible=True).order_by('order', 'id'))















    ctx = {







        'rp_settings': rp_settings,







        'why_partner_items': wp_items,







        'service_cards': s_cards,







        'process_steps': p_steps,







        'why_choose_items': wc_items,







        'industry_items': ind_items,







        'partner_items': prt_items,







        'faq_items': f_items,







        'rp_why_partner_list': wp_items,







        'rp_services': s_cards,







        'rp_process_steps': p_steps,







        'rp_why_choose_list': wc_items,







        'rp_industries': ind_items,







        'rp_partners': prt_items,







        'rp_faqs': f_items,







    }







    cache.set(RECRUITMENT_PLACEMENT_CACHE_KEY, ctx, 60 * 60)







    return ctx























def manpower_supply(request):







    ms_ctx = get_manpower_supply_context()







    return render(request, 'pages/manpower-supply.html', {







        'active_page': 'services',







        **ms_ctx,







    })















def recruitment_placement(request):







    rp_ctx = get_recruitment_placement_context()







    return render(request, 'pages/recruitment-Placement.html', {







        'active_page': 'services',







        **rp_ctx,







    })







































def seed_initial_contract_staffing_data(force=False):







    if force:







        ContractStaffingSettings.objects.all().delete()







        CsServiceCard.objects.all().delete()







        CsIndustryItem.objects.all().delete()







        CsWhyChooseItem.objects.all().delete()







        CsProcessStep.objects.all().delete()







        CsBenefitEmployerItem.objects.all().delete()







        CsBenefitCandidateItem.objects.all().delete()







        CsFaqItem.objects.all().delete()















    ContractStaffingSettings.get_settings()















    if not CsServiceCard.objects.exists():







        service_defaults = [







            ("Temporary Staffing", "Quick hiring solutions for short-term business requirements.", "fa-regular fa-clock", 1),







            ("Project-Based Staffing", "Dedicated professionals for project-specific assignments.", "fa-solid fa-clipboard-list", 2),







            ("Skilled & Semi-Skilled Workforce", "Industrial workers, technicians, operators, supervisors, and office staff.", "fa-solid fa-helmet-safety", 3),







            ("Third-Party Payroll", "Complete payroll management, statutory compliance, attendance, and salary processing.", "fa-solid fa-sack-dollar", 4),







            ("Bulk Hiring", "Large-scale recruitment for factories, warehouses, logistics, and manufacturing companies.", "fa-solid fa-people-group", 5),







            ("Fast Candidate Deployment", "Ready-to-join candidates available within minimum turnaround time.", "fa-solid fa-rocket", 6),







        ]







        for title, desc, icon, order in service_defaults:







            CsServiceCard.objects.create(title=title, description=desc, icon_class=icon, order=order, is_visible=True)















    if not CsIndustryItem.objects.exists():







        industry_defaults = [







            ("Manufacturing", "fa-solid fa-industry", 1),







            ("Construction", "fa-solid fa-drafting-compass", 2),







            ("Automobile", "fa-solid fa-car", 3),







            ("Healthcare", "fa-solid fa-heart-pulse", 4),







            ("Logistics & Supply Chain", "fa-solid fa-truck", 5),







            ("IT & BPO", "fa-solid fa-desktop", 6),







            ("Warehousing", "fa-solid fa-warehouse", 7),







            ("Hospitality", "fa-solid fa-bed", 8),







            ("Retail", "fa-solid fa-cart-shopping", 9),







            ("Education", "fa-solid fa-graduation-cap", 10),







        ]







        for name, icon, order in industry_defaults:







            CsIndustryItem.objects.create(name=name, icon_class=icon, order=order, is_visible=True)















    if not CsWhyChooseItem.objects.exists():







        why_choose_defaults = [







            ("Experienced Recruitment Team", "fa-solid fa-circle-check", 1),







            ("Verified & Skilled Candidates", "fa-solid fa-circle-check", 2),







            ("Quick Hiring Process", "fa-solid fa-circle-check", 3),







            ("PAN India Manpower Support", "fa-solid fa-circle-check", 4),







            ("Payroll & Compliance Management", "fa-solid fa-circle-check", 5),







            ("Cost-Effective Staffing Solutions", "fa-solid fa-circle-check", 6),







            ("Dedicated Account Manager", "fa-solid fa-circle-check", 7),







            ("24x7 Client Support", "fa-solid fa-circle-check", 8),







        ]







        for text_val, icon, order in why_choose_defaults:







            CsWhyChooseItem.objects.create(text=text_val, icon_class=icon, order=order, is_visible=True)















    if not CsProcessStep.objects.exists():







        process_defaults = [







            ("01", "Requirement Discussion", "Understanding your manpower needs.", "fa-solid fa-comments", 1),







            ("02", "Candidate Sourcing", "Sourcing from our extensive database and job portals.", "fa-solid fa-magnifying-glass", 2),







            ("03", "Screening & Verification", "Shortlisting and verifying skills, experience & documents.", "fa-solid fa-clipboard-check", 3),







            ("04", "Client Interview", "Arranging interviews as per client convenience.", "fa-solid fa-user-group", 4),







            ("05", "Deployment", "Onboarding and deployment of selected candidates.", "fa-solid fa-user-check", 5),







            ("06", "Ongoing Support", "Continuous support and performance follow-up.", "fa-solid fa-headset", 6),







        ]







        for num, title, desc, icon, order in process_defaults:







            CsProcessStep.objects.create(step_number=num, title=title, description=desc, icon_class=icon, order=order, is_visible=True)















    if not CsBenefitEmployerItem.objects.exists():







        emp_defaults = [







            ("Faster Hiring", "fa-solid fa-circle-check", 1),







            ("Reduced Recruitment Cost", "fa-solid fa-circle-check", 2),







            ("Verified Workforce", "fa-solid fa-circle-check", 3),







            ("Compliance Support", "fa-solid fa-circle-check", 4),







            ("Flexible Workforce", "fa-solid fa-circle-check", 5),







        ]







        for text_val, icon, order in emp_defaults:







            CsBenefitEmployerItem.objects.create(text=text_val, icon_class=icon, order=order, is_visible=True)















    if not CsBenefitCandidateItem.objects.exists():







        cand_defaults = [







            ("Better Job Opportunities", "fa-solid fa-circle-check", 1),







            ("Career Growth", "fa-solid fa-circle-check", 2),







            ("Trusted Employers", "fa-solid fa-circle-check", 3),







            ("Timely Salary", "fa-solid fa-circle-check", 4),







            ("Professional Guidance", "fa-solid fa-circle-check", 5),







        ]







        for text_val, icon, order in cand_defaults:







            CsBenefitCandidateItem.objects.create(text=text_val, icon_class=icon, order=order, is_visible=True)















    if not CsFaqItem.objects.exists():







        faq_defaults = [







            ("How quickly can manpower be deployed?", "Depending on the role, we can deploy candidates within 2–7 working days.", 1),







            ("Do you provide payroll services?", "Yes, we handle complete third-party payroll, statutory compliance, and salary processing.", 2),







            ("Which industries do you serve?", "We serve manufacturing, construction, logistics, healthcare, IT, retail and more.", 3),







            ("Do you provide bulk hiring?", "Yes, we specialize in large-scale bulk hiring across multiple locations.", 4),







        ]







        for q, a, order in faq_defaults:







            CsFaqItem.objects.create(question=q, answer=a, order=order, is_visible=True)























def get_contract_staffing_context():







    cached = cache.get(CONTRACT_STAFFING_CACHE_KEY)







    if cached:







        return cached















    if not CsServiceCard.objects.exists():







        seed_initial_contract_staffing_data()















    cs_settings = ContractStaffingSettings.get_settings()







    s_cards = list(CsServiceCard.objects.filter(is_visible=True).order_by('order', 'id'))







    ind_items = list(CsIndustryItem.objects.filter(is_visible=True).order_by('order', 'id'))







    wc_items = list(CsWhyChooseItem.objects.filter(is_visible=True).order_by('order', 'id'))







    p_steps = list(CsProcessStep.objects.filter(is_visible=True).order_by('order', 'id'))







    emp_items = list(CsBenefitEmployerItem.objects.filter(is_visible=True).order_by('order', 'id'))







    cand_items = list(CsBenefitCandidateItem.objects.filter(is_visible=True).order_by('order', 'id'))







    f_items = list(CsFaqItem.objects.filter(is_visible=True).order_by('order', 'id'))















    ctx = {







        'cs_settings': cs_settings,







        'cs_services': s_cards,







        'cs_industries': ind_items,







        'cs_why_choose': wc_items,







        'cs_process_steps': p_steps,







        'cs_employer_benefits': emp_items,







        'cs_candidate_benefits': cand_items,







        'cs_faqs': f_items,







    }







    cache.set(CONTRACT_STAFFING_CACHE_KEY, ctx, 60 * 60)







    return ctx























def contract_staffing(request):







    ctx = get_contract_staffing_context()







    context = {'active_page': 'services'}







    context.update(ctx)







    return render(request, 'pages/contract-staffing.html', context)















def seed_initial_educational_consultancy_data(force=False):







    if force:







        EducationalConsultancySettings.objects.all().delete()







        EcServiceCard.objects.all().delete()







        EcWhyChooseItem.objects.all().delete()







        EcProcessStep.objects.all().delete()















    EducationalConsultancySettings.get_settings()















    if not EcServiceCard.objects.exists():







        service_defaults = [







            ("Admission Guidance", "End-to-end support for admission process, documentation and application.", "fa-solid fa-graduation-cap", "navy", 1),







            ("College & University Selection", "Helping you choose the best college or university based on your goals and preferences.", "fa-solid fa-building-columns", "amber", 2),







            ("Career Counselling", "Personalized career counselling to help you choose the right path for your future.", "fa-solid fa-user-tie", "navy", 3),







            ("Skill Development Programs", "Industry-relevant training and certification courses to upgrade your skills and knowledge.", "fa-solid fa-book-open", "amber", 4),







            ("Internship & Placement Support", "Connecting you with internship opportunities and placement assistance.", "fa-solid fa-user-group", "amber", 5),







        ]







        for title, desc, icon, theme, order in service_defaults:







            EcServiceCard.objects.create(







                title=title,







                description=desc,







                icon_class=icon,







                badge_theme=theme,







                order=order,







                is_visible=True,







            )















    if not EcWhyChooseItem.objects.exists():







        why_defaults = [







            ("Experienced Counselors", "Guidance from qualified and experienced experts.", "fa-solid fa-user-graduate", 1),







            ("Trusted Network", "Strong tie-ups with top colleges and universities.", "fa-solid fa-handshake", 2),







            ("Scholarship Assistance", "Help in finding and applying for scholarships.", "fa-solid fa-hand-holding-dollar", 3),







            ("Personalized Guidance", "Solutions tailored to your academic background and career goals.", "fa-solid fa-user-check", 4),







            ("End-to-End Support", "Complete support from counselling to admission and beyond.", "fa-solid fa-clipboard-check", 5),







            ("Affordable Consultation", "Quality guidance at reasonable and transparent consultation fees.", "fa-solid fa-indian-rupee-sign", 6),







        ]







        for title, desc, icon, order in why_defaults:







            EcWhyChooseItem.objects.create(







                title=title,







                description=desc,







                icon_class=icon,







                order=order,







                is_visible=True,







            )















    if not EcProcessStep.objects.exists():







        process_defaults = [







            ("01", "Student Counselling", "Understanding your interests and goals.", "fa-solid fa-comment-dots", 1),







            ("02", "Career Assessment", "Analyzing strengths and career interests.", "fa-solid fa-bullseye", 2),







            ("03", "Course Selection", "Choosing the right course and stream.", "fa-solid fa-book", 3),







            ("04", "College Recommendation", "Recommending the best institutions for you.", "fa-solid fa-building-columns", 4),







            ("05", "Admission Process", "Assistance with applications, documents and admission.", "fa-solid fa-file-circle-check", 5),







            ("06", "Career Support", "Guidance for placements, internships and future.", "fa-solid fa-user-check", 6),







        ]







        for step, title, desc, icon, order in process_defaults:







            EcProcessStep.objects.create(







                step_number=step,







                title=title,







                description=desc,







                icon_class=icon,







                order=order,







                is_visible=True,







            )























def get_educational_consultancy_context():







    cached_ctx = cache.get(EDUCATIONAL_CONSULTANCY_CACHE_KEY)







    if cached_ctx:







        return cached_ctx















    if not EcServiceCard.objects.exists():







        seed_initial_educational_consultancy_data()















    ec_settings = EducationalConsultancySettings.get_settings()







    s_cards = list(EcServiceCard.objects.filter(is_visible=True).order_by('order', 'id'))







    wc_items = list(EcWhyChooseItem.objects.filter(is_visible=True).order_by('order', 'id'))







    p_steps = list(EcProcessStep.objects.filter(is_visible=True).order_by('order', 'id'))















    ctx = {







        'ec_settings': ec_settings,







        'ec_services': s_cards,







        'ec_why_choose': wc_items,







        'ec_process_steps': p_steps,







    }







    cache.set(EDUCATIONAL_CONSULTANCY_CACHE_KEY, ctx, 60 * 60)







    return ctx























def educational_consultancy(request):







    ctx = get_educational_consultancy_context()







    context = {'active_page': 'services'}







    context.update(ctx)







    return render(request, 'pages/educational-consultancy.html', context)















def get_payroll_outsourcing_context():







    cached_ctx = cache.get(PAYROLL_OUTSOURCING_CACHE_KEY)







    if cached_ctx:







        return cached_ctx















    po_settings = PayrollOutsourcingSettings.get_settings()







    po_services = list(PoServiceCard.objects.filter(is_visible=True).order_by('order', 'id'))







    po_industries = list(PoIndustryItem.objects.filter(is_visible=True).order_by('order', 'id'))







    po_why_choose = list(PoWhyChooseItem.objects.filter(is_visible=True).order_by('order', 'id'))







    po_process_steps = list(PoProcessStep.objects.filter(is_visible=True).order_by('order', 'id'))







    po_employer_benefits = list(PoEmployerBenefit.objects.filter(is_visible=True).order_by('order', 'id'))







    po_employee_benefits = list(PoEmployeeBenefit.objects.filter(is_visible=True).order_by('order', 'id'))







    po_faqs = list(PoFaqItem.objects.filter(is_visible=True).order_by('order', 'id'))















    ctx = {







        'po_settings': po_settings,







        'po_services': po_services,







        'po_industries': po_industries,







        'po_why_choose': po_why_choose,







        'po_process_steps': po_process_steps,







        'po_employer_benefits': po_employer_benefits,







        'po_employee_benefits': po_employee_benefits,







        'po_faqs': po_faqs,







    }







    cache.set(PAYROLL_OUTSOURCING_CACHE_KEY, ctx, 60 * 60)







    return ctx























def payroll_outsourcing(request):







    ctx = get_payroll_outsourcing_context()







    context = {'active_page': 'services'}







    context.update(ctx)







    return render(request, 'pages/payroll-outsourcing.html', context)















def get_hr_support_context():



    cached_ctx = cache.get(HR_SUPPORT_CACHE_KEY)



    if cached_ctx:



        return cached_ctx







    hr_settings = HrSupportSettings.get_settings()



    hr_features = list(HrFeatureItem.objects.filter(is_visible=True).order_by('order', 'id'))



    hr_services = list(HrServiceCard.objects.filter(is_visible=True).order_by('order', 'id'))



    hr_additional = list(HrAdditionalServiceItem.objects.filter(is_visible=True).order_by('order', 'id'))



    hr_why_choose = list(HrWhyChooseItem.objects.filter(is_visible=True).order_by('order', 'id'))



    hr_process_steps = list(HrProcessStep.objects.filter(is_visible=True).order_by('order', 'id'))



    hr_employer_benefits = list(HrEmployerBenefit.objects.filter(is_visible=True).order_by('order', 'id'))



    hr_employee_benefits = list(HrEmployeeBenefit.objects.filter(is_visible=True).order_by('order', 'id'))







    ctx = {



        'hr_settings': hr_settings,



        'hr_features': hr_features,



        'hr_services': hr_services,



        'hr_additional': hr_additional,



        'hr_why_choose': hr_why_choose,



        'hr_process_steps': hr_process_steps,



        'hr_employer_benefits': hr_employer_benefits,



        'hr_employee_benefits': hr_employee_benefits,



    }



    cache.set(HR_SUPPORT_CACHE_KEY, ctx, 60 * 60)



    return ctx











def hr_support(request):



    ctx = get_hr_support_context()



    context = {'active_page': 'services'}



    context.update(ctx)



    return render(request, 'pages/hr-support.html', context)















def get_internship_context():

    cached_ctx = cache.get(INTERNSHIP_CACHE_KEY)

    if cached_ctx:

        return cached_ctx



    intern_settings = InternshipSettings.get_settings()

    intern_strip_items = list(InternshipStripItem.objects.filter(is_visible=True).order_by('order', 'id'))

    intern_tracks = list(InternshipTrackItem.objects.filter(is_visible=True).order_by('order', 'id'))

    intern_highlights = list(InternshipHighlightItem.objects.filter(is_visible=True).order_by('order', 'id'))

    intern_who_can_apply = list(InternshipWhoCanApplyItem.objects.filter(is_visible=True).order_by('order', 'id'))

    intern_what_you_learn = list(InternshipWhatYouLearnItem.objects.filter(is_visible=True).order_by('order', 'id'))

    intern_process_steps = list(InternshipProcessStep.objects.filter(is_visible=True).order_by('order', 'id'))

    intern_benefits = list(InternshipBenefitItem.objects.filter(is_visible=True).order_by('order', 'id'))

    intern_faqs = list(InternshipFaqItem.objects.filter(is_visible=True).order_by('order', 'id'))



    ctx = {

        'intern_settings': intern_settings,

        'intern_strip_items': intern_strip_items,

        'intern_tracks': intern_tracks,

        'intern_highlights': intern_highlights,

        'intern_who_can_apply': intern_who_can_apply,

        'intern_what_you_learn': intern_what_you_learn,

        'intern_process_steps': intern_process_steps,

        'intern_benefits': intern_benefits,

        'intern_faqs': intern_faqs,

    }

    cache.set(INTERNSHIP_CACHE_KEY, ctx, 60 * 60)

    return ctx





@ensure_csrf_cookie

def internship(request):

    from apps.internships.models import Internship

    open_internships = Internship.objects.filter(status="Open").order_by('-id')

    ctx = get_internship_context()

    context = {

        'active_page': 'services',

        'open_internships': open_internships,

    }

    context.update(ctx)

    return render(request, 'pages/internship.html', context)















@ensure_csrf_cookie







def careers(request):
    from apps.core.models import CareerPageSettings
    career_settings = CareerPageSettings.get_settings()
    return render(request, 'pages/careers.html', {
        'active_page': 'careers',
        'career_settings': career_settings,
    })















@ensure_csrf_cookie







def job(request):
    from apps.core.models import JobPageSettings

    active_jobs, search_meta = filter_active_jobs(request)
    job_categories = JobCategory.objects.filter(category_type='job_category', status='Active').order_by('order', 'id')
    job_types = JobCategory.objects.filter(category_type='job_type', status='Active').order_by('order', 'id')
    job_settings = JobPageSettings.get_settings()
    available_locations = get_active_job_locations()

    existing_cat_names = set(c.name.lower() for c in job_categories)
    extra_categories = []
    try:
        for j_cat in Job.objects.live().values_list('category', flat=True).distinct():
            if j_cat and j_cat.strip() and j_cat.strip().lower() not in existing_cat_names:
                extra_categories.append(j_cat.strip())
                existing_cat_names.add(j_cat.strip().lower())
    except Exception:
        pass

    return render(request, 'pages/job.html', {
        'active_page': 'job',
        'active_jobs': active_jobs,
        'job_categories': job_categories,
        'extra_categories': extra_categories,
        'job_types': job_types,
        'job_settings': job_settings,
        'available_locations': available_locations,
        **search_meta,
    })















@ensure_csrf_cookie







def gallery(request):
    from apps.core.models import GalleryPageSettings
    gallery_settings = GalleryPageSettings.get_settings()
    return render(request, 'pages/gallery.html', {
        'active_page': 'gallery',
        'gallery_settings': gallery_settings,
    })















def blog(request):
    from apps.core.models import BlogPageSettings
    blog_settings = BlogPageSettings.get_settings()
    return render(request, 'pages/blog.html', {
        'active_page': 'blog',
        'blog_settings': blog_settings,
    })















@ensure_csrf_cookie







def contact(request):
    from apps.core.models import ContactPageSettings
    contact_settings = ContactPageSettings.get_settings()
    return render(request, 'pages/contact.html', {
        'active_page': 'contact',
        'contact_settings': contact_settings,
    })







