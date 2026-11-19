import re

import os

import uuid

from django.db import models

from django.db.models.signals import post_save, post_delete

from django.dispatch import receiver

from django.core.cache import cache

from django.utils.safestring import mark_safe





def scramble_upload_path(instance, filename):

    ext = os.path.splitext(filename)[1].lower()

    return f"branding/{uuid.uuid4().hex[:16]}{ext}"





class SiteSettings(models.Model):

    # Singleton pattern

    site_name = models.CharField(max_length=150, default="Sky Vision Group of Consultancy")

    tagline = models.CharField(max_length=255, default="Right Talent, Bright Future.")

    logo_alt_text = models.CharField(max_length=150, default="Sky Vision Group Consultancy Logo")

    header_logo = models.ImageField(upload_to=scramble_upload_path, blank=True, null=True)

    footer_logo = models.ImageField(upload_to=scramble_upload_path, blank=True, null=True)

    favicon = models.ImageField(upload_to=scramble_upload_path, blank=True, null=True)



    # Topbar & Header

    topbar_address = models.CharField(max_length=255, default="Indira Nagar, Lucknow, UP", blank=True)

    support_email = models.EmailField(default="info@skyvisiongroup.in", blank=True)

    topbar_hours = models.CharField(max_length=120, default="Mon – Sat, 9:30 AM – 6:30 PM", blank=True)

    helpline_phone = models.CharField(max_length=50, default="+91 88531 11111", blank=True)

    secondary_phone = models.CharField(max_length=50, default="+91 7068115299", blank=True)

    announcement_text = models.CharField(

        max_length=255,

        default="🚀 Free Career Counselling & Interview Training available this week at Gomti Nagar office!",

        blank=True

    )

    show_announcement = models.BooleanField(default=True)

    franchise_url = models.CharField(max_length=255, default="/contact/", blank=True)

    show_franchise_btn = models.BooleanField(default=True)



    # Navbar

    navbar_call_text = models.CharField(max_length=50, default="+91 7068115299", blank=True)

    navbar_call_number = models.CharField(max_length=50, default="+917068115299", blank=True)

    show_login_btn = models.BooleanField(default=True)



    # Footer

    footer_about = models.TextField(

        default="Delivering excellence through personalized service and innovative solutions — bespoke recruitment, HR and consultancy that helps businesses and individuals grow with confidence.",

        blank=True

    )

    office_address = models.TextField(

        default="12/2 Arvindo Park Road, Sector 12, Indira Nagar, Lucknow, UP",

        blank=True

    )

    office_email = models.CharField(max_length=120, default="info@skyvisiongroup.in", blank=True)

    office_phone_1 = models.CharField(max_length=50, default="+91 7068115299", blank=True)

    office_phone_2 = models.CharField(max_length=50, default="+91 9532625299", blank=True)

    working_hours = models.CharField(max_length=120, default="Mon – Sat: 9:30 AM – 6:30 PM", blank=True)

    copyright_text = models.CharField(

        max_length=255,

        default="© 2026 Sky Vision Group Consultancy. All rights reserved.",

        blank=True

    )

    privacy_policy_url = models.CharField(max_length=255, default="#", blank=True)

    terms_url = models.CharField(max_length=255, default="#", blank=True)

    footer_credit = models.CharField(

        max_length=255,

        default="Designed with ❤️ by Allcore Solution",

        blank=True

    )



    # Floating buttons

    floating_call_number = models.CharField(max_length=50, default="+917068115299", blank=True)

    floating_whatsapp_url = models.CharField(

        max_length=255,

        default="https://whatsapp.com/channel/0029VamiX875K3zaWy6ysU31",

        blank=True

    )

    show_floating_buttons = models.BooleanField(default=True)



    updated_at = models.DateTimeField(auto_now=True)



    class Meta:

        db_table = 'site_settings'

        verbose_name = "Site Settings"

        verbose_name_plural = "Site Settings"



    def __str__(self):

        return f"{self.site_name} Settings"



    @classmethod

    def get_settings(cls):

        obj = cls.objects.first()

        if not obj:

            obj = cls.objects.create()

        return obj





class NavItem(models.Model):

    parent = models.ForeignKey(

        'self',

        on_delete=models.CASCADE,

        null=True,

        blank=True,

        related_name='children'

    )

    label = models.CharField(max_length=100)

    url = models.CharField(max_length=255, default="/")

    active_key = models.CharField(max_length=50, blank=True, default="")

    order = models.PositiveIntegerField(default=0)

    is_visible = models.BooleanField(default=True)

    new_tab = models.BooleanField(default=False)



    class Meta:

        db_table = 'nav_items'

        ordering = ['order', 'id']

        verbose_name = "Navigation Item"

        verbose_name_plural = "Navigation Items"



    def __str__(self):

        if self.parent:

            return f"{self.parent.label} -> {self.label}"

        return self.label





class FooterColumn(models.Model):

    title = models.CharField(max_length=100)

    order = models.PositiveIntegerField(default=0)

    is_visible = models.BooleanField(default=True)



    class Meta:

        db_table = 'footer_columns'

        ordering = ['order', 'id']

        verbose_name = "Footer Column"

        verbose_name_plural = "Footer Columns"



    def __str__(self):

        return self.title





class FooterLink(models.Model):

    column = models.ForeignKey(

        FooterColumn,

        on_delete=models.CASCADE,

        related_name='links'

    )

    label = models.CharField(max_length=100)

    url = models.CharField(max_length=255, default="/")

    order = models.PositiveIntegerField(default=0)

    is_visible = models.BooleanField(default=True)

    new_tab = models.BooleanField(default=False)



    class Meta:

        db_table = 'footer_links'

        ordering = ['order', 'id']

        verbose_name = "Footer Link"

        verbose_name_plural = "Footer Links"



    def __str__(self):

        return f"{self.column.title} -> {self.label}"





class SocialLink(models.Model):

    PLATFORM_CHOICES = [

        ('facebook', 'Facebook'),

        ('instagram', 'Instagram'),

        ('linkedin', 'LinkedIn'),

        ('youtube', 'YouTube'),

        ('twitter', 'X / Twitter'),

        ('whatsapp', 'WhatsApp'),

    ]

    platform = models.CharField(max_length=50, choices=PLATFORM_CHOICES)

    url = models.CharField(max_length=255)

    is_enabled = models.BooleanField(default=True)

    order = models.PositiveIntegerField(default=0)



    class Meta:

        db_table = 'social_links'

        ordering = ['order', 'id']

        verbose_name = "Social Link"

        verbose_name_plural = "Social Links"



    def __str__(self):

        return f"{self.get_platform_display()} ({self.url})"



    @property

    def icon_class(self):

        mapping = {

            'facebook': 'fab fa-facebook-f',

            'instagram': 'fab fa-instagram',

            'linkedin': 'fab fa-linkedin-in',

            'youtube': 'fab fa-youtube',

            'twitter': 'fab fa-x-twitter',

            'whatsapp': 'fab fa-whatsapp',

        }

        return mapping.get(self.platform, 'fas fa-link')





class FooterService(models.Model):

    name = models.CharField(max_length=150)

    url = models.CharField(max_length=255, default="/services/")

    order = models.PositiveIntegerField(default=0)

    is_visible = models.BooleanField(default=True)



    class Meta:

        db_table = 'footer_services'

        ordering = ['order', 'id']

        verbose_name = "Footer Service"

        verbose_name_plural = "Footer Services"



    def __str__(self):

        return self.name





# ==============================================================================

# HOME PAGE DYNAMIC MODELS

# ==============================================================================



class HomePageSettings(models.Model):

    # 1. Hero Section

    hero_visible = models.BooleanField(default=True)

    hero_unit_tag = models.CharField(max_length=150, default="A Unit of Radha Enterprises", blank=True)

    hero_eyebrow = models.CharField(max_length=150, default="Staffing · Recruitment · Consultancy", blank=True)

    hero_title = models.CharField(max_length=255, default="Find Your Dream Job For Your Future")

    hero_title_highlight = models.CharField(max_length=100, default="Future", blank=True)

    hero_subtitle = models.TextField(

        default="Manpower supply, recruitment, HR outsourcing, educational consultancy and career development — one team, across India.",

        blank=True

    )

    hero_cta_primary_label = models.CharField(max_length=50, default="Apply Now")

    hero_cta_primary_url = models.CharField(max_length=255, default="#")

    hero_cta_primary_visible = models.BooleanField(default=True)



    hero_cta_secondary_label = models.CharField(max_length=50, default="Hire Talent")

    hero_cta_secondary_url = models.CharField(max_length=255, default="/employer/hire-talent/")

    hero_cta_secondary_visible = models.BooleanField(default=True)



    hero_cta_internship_label = models.CharField(max_length=50, default="Apply Internship")

    hero_cta_internship_url = models.CharField(max_length=255, default="#")

    hero_cta_internship_visible = models.BooleanField(default=True)



    hero_image = models.ImageField(upload_to=scramble_upload_path, blank=True, null=True)

    hero_image_alt = models.CharField(max_length=150, default="Recruitment team illustration", blank=True)



    hero_search_visible = models.BooleanField(default=True)

    hero_growth_steps_visible = models.BooleanField(default=True)

    job_pills_visible = models.BooleanField(default=True)



    # 2. Services Section

    services_tag = models.CharField(max_length=100, default="What We Do", blank=True)

    services_title = models.CharField(max_length=150, default="Our professional services")

    services_subtitle = models.TextField(default="End-to-end workforce and business solutions tailored to your needs.", blank=True)

    services_visible = models.BooleanField(default=True)



    # 3. About Section

    about_tag = models.CharField(max_length=100, default="About Us", blank=True)

    about_heading = models.CharField(max_length=200, default="Welcome to Sky Vision Group Consultancy")

    about_heading_highlight = models.CharField(max_length=100, default="Sky Vision Group Consultancy", blank=True)

    about_content = models.TextField(

        default="At Sky Vision Group Consultancy, we are committed to delivering reliable and innovative workforce solutions that help businesses grow and professionals build successful careers. With expertise in Recruitment & Placement, Manpower Supply, Contract Staffing, Payroll & Outsourcing, HR Support, Educational Consultancy, Internship Programs, and Career Counseling, we provide end-to-end services tailored to the evolving needs of organizations across diverse industries."

    )

    about_badge_text = models.CharField(max_length=100, default="Trusted since 2014", blank=True)

    about_image = models.ImageField(upload_to=scramble_upload_path, blank=True, null=True)

    about_image_alt = models.CharField(max_length=150, default="Sky Vision Office & Team", blank=True)

    about_sub_title = models.CharField(max_length=150, default="6+ years placing India's workforce", blank=True)

    about_sub_snippet = models.CharField(

        max_length=255,

        default="5,000+ candidates placed across manufacturing, IT, healthcare, retail and BPO sectors.",

        blank=True

    )

    about_vision_title = models.CharField(max_length=100, default="Our Vision", blank=True)

    about_vision_desc = models.CharField(max_length=255, default="To become India's most trusted consultancy brand.", blank=True)

    about_mission_title = models.CharField(max_length=100, default="Our Mission", blank=True)

    about_mission_desc = models.CharField(max_length=255, default="Empowering businesses and professionals through smart workforce solutions.", blank=True)

    about_btn_label = models.CharField(max_length=50, default="Read More", blank=True)

    about_btn_url = models.CharField(max_length=255, default="/about-us/", blank=True)

    about_btn_visible = models.BooleanField(default=False)

    about_visible = models.BooleanField(default=True)



    # 4. Why Choose Us Section

    why_choose_tag = models.CharField(max_length=100, default="Our Advantage", blank=True)

    why_choose_title = models.CharField(max_length=150, default="Why choose us?")

    why_choose_subtitle = models.TextField(default="We provide reliable recruitment solutions with speed, quality and transparency.", blank=True)

    why_choose_visible = models.BooleanField(default=True)



    # 5. Industries Section

    industries_tag = models.CharField(max_length=100, default="Where We Work", blank=True)

    industries_title = models.CharField(max_length=150, default="Industries we serve")

    industries_subtitle = models.TextField(default="From factory floors to corporate offices, we staff the sectors that keep India running.", blank=True)

    industries_visible = models.BooleanField(default=True)



    # 6. Internship Programme Section

    internship_heading = models.CharField(max_length=150, default="Internship Programme")

    internship_subtitle = models.TextField(default="Build your career with professional internship opportunities.", blank=True)

    internship_box_title = models.CharField(max_length=150, default="90-Day Professional Internship Programme")

    internship_cta_label = models.CharField(max_length=50, default="Apply Now")

    internship_cta_url = models.CharField(max_length=255, default="#")

    internship_visible = models.BooleanField(default=True)



    # 7. Job Categories & Latest Jobs

    job_categories_visible = models.BooleanField(default=True)

    latest_jobs_visible = models.BooleanField(default=True)



    # 8. Featured Candidates Section

    candidates_tag = models.CharField(max_length=100, default="Meet The Talent", blank=True)

    candidates_title = models.CharField(max_length=150, default="Featured candidates")

    candidates_subtitle = models.TextField(default="Verified, job-ready professionals available for immediate placement.", blank=True)

    candidates_visible = models.BooleanField(default=True)



    # 9. Gallery Section

    gallery_tag = models.CharField(max_length=100, default="A Glimpse Inside", blank=True)

    gallery_title = models.CharField(max_length=150, default="Our gallery")

    gallery_subtitle = models.TextField(default="Moments from our placement drives, training sessions and team events.", blank=True)

    gallery_btn_label = models.CharField(max_length=50, default="View Full Gallery", blank=True)

    gallery_btn_url = models.CharField(max_length=255, default="/gallery/", blank=True)

    gallery_btn_visible = models.BooleanField(default=False)

    gallery_visible = models.BooleanField(default=True)



    # 10. Contact Section

    contact_title = models.CharField(max_length=150, default="Contact Information")

    contact_form_title = models.CharField(max_length=150, default="Send Us a Message")

    contact_map_url = models.TextField(

        default="https://www.google.com/maps?q=12/2+Arvindo+Park+Road+Sector+12+Indira+Nagar+Lucknow+Uttar+Pradesh+226016&output=embed",

        blank=True

    )

    contact_visible = models.BooleanField(default=True)



    # SEO & Meta

    meta_title = models.CharField(max_length=255, default="Sky Vision Group of Consultancy | Recruitment & Staffing Lucknow", blank=True)

    meta_description = models.TextField(

        default="Premier manpower staffing, recruitment, educational consultancy, and payroll outsourcing in Lucknow and nationwide.",

        blank=True

    )

    og_image = models.ImageField(upload_to=scramble_upload_path, blank=True, null=True)



    updated_at = models.DateTimeField(auto_now=True)



    class Meta:

        db_table = 'home_page_settings'

        verbose_name = "Home Page Settings"

        verbose_name_plural = "Home Page Settings"



    def __str__(self):

        return "Home Page Configuration"



    @classmethod

    def get_settings(cls):

        obj = cls.objects.first()

        if not obj:

            obj = cls.objects.create()

        return obj





class HeroStat(models.Model):

    icon_class = models.CharField(max_length=100, default="fa-solid fa-briefcase")

    value = models.CharField(max_length=50, default="10K+")

    label = models.CharField(max_length=100, default="Experience")

    order = models.PositiveIntegerField(default=0)

    is_visible = models.BooleanField(default=True)



    class Meta:

        db_table = 'hero_stats'

        ordering = ['order', 'id']

        verbose_name = "Hero Statistic"

        verbose_name_plural = "Hero Statistics"



    def __str__(self):

        return f"{self.value} - {self.label}"





class GrowthStep(models.Model):

    step_number = models.PositiveIntegerField(default=1)

    title = models.CharField(max_length=50, default="Connect")

    subtitle = models.CharField(max_length=100, default="We understand your needs")

    order = models.PositiveIntegerField(default=0)

    is_visible = models.BooleanField(default=True)



    class Meta:

        db_table = 'home_growth_steps'

        ordering = ['order', 'step_number', 'id']

        verbose_name = "Growth Step"

        verbose_name_plural = "Growth Steps"



    def __str__(self):

        return f"Step {self.step_number}: {self.title}"





class HomeServiceCard(models.Model):

    COLOR_CHOICES = [

        ('blue', 'Blue Icon Background'),

        ('red', 'Red Icon Background'),

    ]

    title = models.CharField(max_length=150)

    icon_class = models.CharField(max_length=100, default="fas fa-users")

    icon_color = models.CharField(max_length=20, default="blue", choices=COLOR_CHOICES)

    bullets = models.TextField(blank=True, default="", help_text="One bullet point per line")

    link_url = models.CharField(max_length=255, default="/services/")

    link_text = models.CharField(max_length=50, default="Read More")

    order = models.PositiveIntegerField(default=0)

    is_visible = models.BooleanField(default=True)



    class Meta:

        db_table = 'home_service_cards'

        ordering = ['order', 'id']

        verbose_name = "Home Service Card"

        verbose_name_plural = "Home Service Cards"



    def __str__(self):

        return self.title



    def get_bullet_list(self):

        if not self.bullets:

            return []

        return [b.strip() for b in self.bullets.splitlines() if b.strip()]





class WhyChooseItem(models.Model):

    title = models.CharField(max_length=150)

    icon_class = models.CharField(max_length=100, default="fas fa-users")

    description = models.TextField(default="")

    order = models.PositiveIntegerField(default=0)

    is_visible = models.BooleanField(default=True)



    class Meta:

        db_table = 'home_why_choose_items'

        ordering = ['order', 'id']

        verbose_name = "Why Choose Us Item"

        verbose_name_plural = "Why Choose Us Items"



    def __str__(self):

        return self.title





class HomeIndustryItem(models.Model):

    name = models.CharField(max_length=100)

    icon_class = models.CharField(max_length=100, default="fas fa-industry")

    link_url = models.CharField(max_length=255, blank=True, default="")

    order = models.PositiveIntegerField(default=0)

    is_visible = models.BooleanField(default=True)



    class Meta:

        db_table = 'home_industry_items'

        ordering = ['order', 'id']

        verbose_name = "Home Industry Item"

        verbose_name_plural = "Home Industry Items"



    def __str__(self):

        return self.name



    @property

    def icon(self):

        return self.icon_class or "fas fa-briefcase"



    def get_link(self):

        if self.link_url:

            return self.link_url

        import urllib.parse

        return f"/jobs/?industry={urllib.parse.quote(self.name)}"





class InternshipCard(models.Model):

    domain_name = models.CharField(max_length=100)

    icon_class = models.CharField(max_length=100, default="fa-solid fa-users")

    icon_color = models.CharField(max_length=20, default="#2563EB")

    bullets = models.TextField(default="", help_text="One bullet point per line")

    order = models.PositiveIntegerField(default=0)

    is_visible = models.BooleanField(default=True)



    class Meta:

        db_table = 'home_internship_cards'

        ordering = ['order', 'id']

        verbose_name = "Internship Domain Card"

        verbose_name_plural = "Internship Domain Cards"



    def __str__(self):

        return self.domain_name



    def get_bullet_list(self):

        if not self.bullets:

            return []

        return [b.strip() for b in self.bullets.splitlines() if b.strip()]





class InternshipHighlight(models.Model):

    TYPE_CHOICES = [

        ('benefit', '90-Day Programme Benefit (Bullet List)'),

        ('bottom_badge', 'Bottom Highlight Feature Badge'),

    ]

    item_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='benefit')

    text = models.CharField(max_length=150)

    icon_class = models.CharField(max_length=100, blank=True, default="fa-solid fa-check")

    order = models.PositiveIntegerField(default=0)

    is_visible = models.BooleanField(default=True)



    class Meta:

        db_table = 'home_internship_highlights'

        ordering = ['order', 'id']

        verbose_name = "Internship Highlight"

        verbose_name_plural = "Internship Highlights"



    def __str__(self):

        return f"[{self.get_item_type_display()}] {self.text}"





class FeaturedCandidate(models.Model):

    name = models.CharField(max_length=100)

    role = models.CharField(max_length=100, default="Java Programmer")

    experience = models.CharField(max_length=50, default="1 Yr Exp")

    avatar_color = models.CharField(max_length=100, default="linear-gradient(135deg,#5B7CFF,#2F3FA6)")

    photo = models.ImageField(upload_to=scramble_upload_path, blank=True, null=True)

    quote = models.TextField(blank=True, default="")

    company_placed = models.CharField(max_length=150, blank=True, default="")

    candidate_ref = models.ForeignKey('accounts.CandidateAccount', on_delete=models.SET_NULL, null=True, blank=True, related_name='featured_entries')

    show_publicly = models.BooleanField(default=True, help_text="Explicit candidate consent to display publicly on website")

    order = models.PositiveIntegerField(default=0)

    is_visible = models.BooleanField(default=True)



    class Meta:

        db_table = 'home_featured_candidates'

        ordering = ['order', 'id']

        verbose_name = "Featured Candidate"

        verbose_name_plural = "Featured Candidates"



    def __str__(self):

        return f"{self.name} ({self.role})"



    @property

    def initials(self):

        parts = self.name.strip().split()

        if len(parts) >= 2:

            return f"{parts[0][0]}{parts[1][0]}".upper()

        elif parts:

            return parts[0][:2].upper()

        return "CA"





class GalleryImage(models.Model):

    title = models.CharField(max_length=150, default="Corporate Events")

    image = models.ImageField(upload_to=scramble_upload_path, blank=True, null=True)

    static_image_path = models.CharField(max_length=255, blank=True, default="")

    category = models.CharField(max_length=100, default="Events")

    show_on_home = models.BooleanField(default=True)

    order = models.PositiveIntegerField(default=0)

    is_visible = models.BooleanField(default=True)



    class Meta:

        db_table = 'gallery_images'

        ordering = ['order', 'id']

        verbose_name = "Gallery Image"

        verbose_name_plural = "Gallery Images"



    def __str__(self):

        return self.title



    def get_image_url(self):

        if self.image:

            try:

                return self.image.url

            except Exception:

                pass

        if self.static_image_path:

            p = str(self.static_image_path).strip()

            if p.startswith('http://') or p.startswith('https://') or p.startswith('/media/') or p.startswith('/static/'):

                return p

            if p.startswith('media/'):

                return f"/{p}"

            return f"/static/{p.lstrip('/')}"

        return "/static/images/general/placement drives.png"





class GalleryInfoBox(models.Model):

    title = models.CharField(max_length=150)

    text = models.CharField(max_length=255)

    icon_class = models.CharField(max_length=100, default="fa-solid fa-bullseye")

    btn_label = models.CharField(max_length=100, default="Explore Now")

    btn_url = models.CharField(max_length=255, default="#")

    is_popup = models.BooleanField(default=False)

    order = models.PositiveIntegerField(default=0)

    is_visible = models.BooleanField(default=True)



    class Meta:

        db_table = 'home_gallery_info_boxes'

        ordering = ['order', 'id']

        verbose_name = "Gallery Info Box"

        verbose_name_plural = "Gallery Info Boxes"



    def __str__(self):

        return self.title







# ==============================================================================

# ABOUT US SUB-PAGES DYNAMIC MODELS (4 Pages)

# ==============================================================================



class AboutCompanySettings(models.Model):

    page_title = models.CharField(max_length=255, default="About Company of Sky Vision Group of Consultancy")

    page_eyebrow = models.CharField(max_length=150, default="Get To Know Us", blank=True)



    # Visual Left Side

    experience_badge = models.CharField(max_length=100, default="Trusted since 2014", blank=True)

    visual_image = models.ImageField(upload_to=scramble_upload_path, blank=True, null=True)

    static_visual_path = models.CharField(max_length=255, default="assets/images/blog image 2.png", blank=True)

    visual_heading = models.CharField(max_length=255, default="6+ years placing India's workforce")

    visual_subtext = models.TextField(

        default="5,000+ candidates placed across manufacturing, IT, healthcare, retail and BPO sectors.",

        blank=True

    )



    # Right Side Welcome Copy

    welcome_tag = models.CharField(max_length=100, default="About Us", blank=True)

    welcome_heading = models.CharField(max_length=255, default="Welcome to Sky Vision Group Consultancy")

    welcome_p1 = models.TextField(

        default="Sky Vision Group Consultancy is a leading HR, Recruitment and Business Consultancy organization dedicated to helping companies build strong teams and helping candidates build successful careers.",

        blank=True

    )

    welcome_p2 = models.TextField(

        default="We provide innovative workforce solutions across multiple industries and sectors, backed by a team that understands both sides of every hire.",

        blank=True

    )



    # Vision & Mission

    vision_title = models.CharField(max_length=120, default="Our Vision")

    vision_text = models.TextField(default="To become India's most trusted consultancy brand.", blank=True)

    mission_title = models.CharField(max_length=120, default="Our Mission")

    mission_text = models.TextField(default="Empowering businesses and professionals through smart workforce solutions.", blank=True)



    # 4 Counters

    stat_1_count = models.CharField(max_length=50, default="6")

    stat_1_label = models.CharField(max_length=100, default="Years of Experience")

    stat_2_count = models.CharField(max_length=50, default="500")

    stat_2_label = models.CharField(max_length=100, default="Successful Placements")

    stat_3_count = models.CharField(max_length=50, default="100")

    stat_3_label = models.CharField(max_length=100, default="Happy Clients")

    stat_4_count = models.CharField(max_length=50, default="24/7")

    stat_4_label = models.CharField(max_length=100, default="HR Support")



    # Why Choose Us

    why_tag = models.CharField(max_length=100, default="Our Advantage", blank=True)

    why_heading = models.CharField(max_length=255, default="Why choose us?")

    why_subtext = models.TextField(default="We provide reliable recruitment solutions with speed, quality and transparency.", blank=True)



    # 4 Core Pillars

    pillar_1 = models.CharField(max_length=150, default="Integrity & Ethics")

    pillar_2 = models.CharField(max_length=150, default="Excellence in Placement")

    pillar_3 = models.CharField(max_length=150, default="Client-First Focus")

    pillar_4 = models.CharField(max_length=150, default="Innovation & Speed")



    # Section Toggles

    why_visible = models.BooleanField(default=True)

    industries_visible = models.BooleanField(default=True)

    team_visible = models.BooleanField(default=True)

    testimonials_visible = models.BooleanField(default=True)

    logos_visible = models.BooleanField(default=True)

    cta_visible = models.BooleanField(default=True)



    # Industries Section

    industries_tag = models.CharField(max_length=100, default="Where We Work", blank=True)

    industries_heading = models.CharField(max_length=255, default="Industries we serve")

    industries_subtext = models.TextField(

        default="From factory floors to corporate offices, we staff the sectors that keep India running.",

        blank=True

    )



    # Team Section

    team_tag = models.CharField(max_length=100, default="Our Team", blank=True)

    team_heading_prefix = models.CharField(max_length=100, default="Meet the", blank=True)

    team_heading_highlight = models.CharField(max_length=100, default="Experts", blank=True)

    team_subtext = models.TextField(

        default="The passionate people behind your brand's success",

        blank=True

    )

    team_max_items = models.PositiveSmallIntegerField(default=20)



    # Testimonials Header

    tt_eyebrow = models.CharField(max_length=150, default="Client Testimonials", blank=True)

    tt_heading_prefix = models.CharField(max_length=100, default="Trusted by", blank=True)

    tt_highlight_1 = models.CharField(max_length=50, default="5,000+", blank=True)

    tt_heading_middle = models.CharField(max_length=100, default="Professionals &", blank=True)

    tt_highlight_2 = models.CharField(max_length=50, default="250+", blank=True)

    tt_heading_suffix = models.CharField(max_length=100, default="Hiring Partners", blank=True)

    tt_subheading = models.CharField(

        max_length=255,

        default="Building Careers. Empowering Businesses. Delivering Results.",

        blank=True

    )

    tt_description = models.TextField(

        default="For over a decade, Sky Vision Group Consultancy has helped thousands of professionals secure rewarding careers while enabling companies to hire exceptional talent through transparent and reliable recruitment services.",

        blank=True

    )



    # Google Card

    google_visible = models.BooleanField(default=True)

    google_label = models.CharField(max_length=100, default="Google Reviews", blank=True)

    google_rating = models.CharField(max_length=20, default="4.9", blank=True)

    google_review_count = models.PositiveIntegerField(default=1200)

    google_count_suffix = models.CharField(max_length=20, default="+", blank=True)

    google_verified_text = models.CharField(max_length=100, default="Verified Reviews", blank=True)



    # Sliders

    candidate_slider_title = models.CharField(max_length=150, default="What Our Candidates Say", blank=True)

    candidate_slider_subtitle = models.CharField(max_length=255, default="Real placements, real career moves", blank=True)

    employer_slider_title = models.CharField(max_length=150, default="What Our Hiring Partners Say", blank=True)

    employer_slider_subtitle = models.CharField(max_length=255, default="HR leaders on working with our team", blank=True)



    # Logos Marquee

    logos_title = models.CharField(max_length=150, default="Trusted by Leading Companies", blank=True)

    logos_subtitle = models.CharField(max_length=255, default="", blank=True)



    # CTA Section

    cta_heading = models.CharField(max_length=255, default="Start Your Success Story Today!")

    cta_text = models.TextField(

        default="Whether you're looking for your first job or your next hire, Sky Vision Group Consultancy is here to help.",

        blank=True

    )

    cta_primary_label = models.CharField(max_length=100, default="Explore Job Opportunities", blank=True)

    cta_primary_url = models.CharField(max_length=255, default="/jobs/", blank=True)

    cta_franchise_visible = models.BooleanField(default=True)

    cta_franchise_label = models.CharField(max_length=100, default="Apply Franchise", blank=True)

    cta_trophy_visible = models.BooleanField(default=True)



    updated_at = models.DateTimeField(auto_now=True)



    class Meta:

        db_table = 'about_company_settings'

        verbose_name = "About Company Settings"

        verbose_name_plural = "About Company Settings"



    def __str__(self):

        return "About Company Settings"



    @classmethod

    def get_settings(cls):

        obj = cls.objects.first()

        if not obj:

            obj = cls.objects.create()

        return obj



    def get_visual_image_url(self):

        if self.visual_image:

            try:

                return self.visual_image.url

            except Exception:

                pass

        if self.static_visual_path:

            p = str(self.static_visual_path).strip()

            if p.startswith('http://') or p.startswith('https://') or p.startswith('/media/') or p.startswith('/static/'):

                return p

            return f"/static/{p.lstrip('/')}"

        return "/static/images/general/placement drives.png"





class AboutWhyCard(models.Model):

    icon_class = models.CharField(max_length=100, default="fas fa-star")

    title = models.CharField(max_length=120)

    description = models.TextField()

    order = models.PositiveIntegerField(default=0)

    is_visible = models.BooleanField(default=True)



    class Meta:

        db_table = 'about_why_cards'

        ordering = ['order', 'id']

        verbose_name = "About Why Card"

        verbose_name_plural = "About Why Cards"



    def __str__(self):

        return self.title





class AboutTestimonial(models.Model):

    TYPE_CHOICES = (

        ('candidate', 'Candidate'),

        ('employer', 'Hiring Partner / Employer'),

    )

    testimonial_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='candidate')

    name = models.CharField(max_length=150)

    role = models.CharField(max_length=150)

    location = models.CharField(max_length=150, blank=True, default="")

    company = models.CharField(max_length=150, blank=True, default="")

    quote = models.TextField()

    rating = models.PositiveSmallIntegerField(default=5)

    photo = models.ImageField(upload_to=scramble_upload_path, blank=True, null=True)

    badge_text = models.CharField(max_length=100, default="Verified Candidate", blank=True)

    avatar_style = models.PositiveSmallIntegerField(default=1)

    order = models.PositiveIntegerField(default=0)

    is_visible = models.BooleanField(default=True)



    class Meta:

        db_table = 'about_testimonials'

        ordering = ['order', 'id']

        verbose_name = "About Testimonial"

        verbose_name_plural = "About Testimonials"



    def __str__(self):

        return f"{self.name} ({self.get_testimonial_type_display()})"



    @property

    def initials(self):

        parts = [p for p in (self.name or '').strip().split() if p]

        if not parts:

            return 'SV'

        if len(parts) == 1:

            return parts[0][:2].upper()

        return (parts[0][0] + parts[-1][0]).upper()





class AboutTestimonialStat(models.Model):

    COLOR_CHOICES = (

        ('blue', 'Blue'),

        ('purple', 'Purple'),

        ('green', 'Green'),

        ('gold', 'Gold'),

    )

    icon_class = models.CharField(max_length=100, default="fa-solid fa-chart-simple")

    color = models.CharField(max_length=20, choices=COLOR_CHOICES, default='blue')

    count = models.PositiveIntegerField(default=0)

    suffix = models.CharField(max_length=20, default="+", blank=True)

    label = models.CharField(max_length=120)

    order = models.PositiveIntegerField(default=0)

    is_visible = models.BooleanField(default=True)



    class Meta:

        db_table = 'about_testimonial_stats'

        ordering = ['order', 'id']

        verbose_name = "About Testimonial Stat"

        verbose_name_plural = "About Testimonial Stats"



    def __str__(self):

        return f"{self.label} ({self.count}{self.suffix})"





class AboutTrustPoint(models.Model):

    icon_class = models.CharField(max_length=100, default="fa-solid fa-check")

    title = models.CharField(max_length=150)

    text = models.TextField()

    order = models.PositiveIntegerField(default=0)

    is_visible = models.BooleanField(default=True)



    class Meta:

        db_table = 'about_trust_points'

        ordering = ['order', 'id']

        verbose_name = "About Trust Point"

        verbose_name_plural = "About Trust Points"



    def __str__(self):

        return self.title





class AboutPartnerLogo(models.Model):

    name = models.CharField(max_length=120)

    icon_class = models.CharField(max_length=100, blank=True, default="")

    logo_image = models.ImageField(upload_to=scramble_upload_path, blank=True, null=True)

    order = models.PositiveIntegerField(default=0)

    is_visible = models.BooleanField(default=True)



    class Meta:

        db_table = 'about_partner_logos'

        ordering = ['order', 'id']

        verbose_name = "About Partner Logo"

        verbose_name_plural = "About Partner Logos"



    def __str__(self):

        return self.name





class AboutIndustryItem(models.Model):

    name = models.CharField(max_length=120)

    icon_class = models.CharField(max_length=100, default="fas fa-industry")

    link_url = models.CharField(max_length=255, blank=True, default="")

    order = models.PositiveIntegerField(default=0)

    is_visible = models.BooleanField(default=True)



    class Meta:

        db_table = 'about_industry_items'

        ordering = ['order', 'id']

        verbose_name = "About Industry Item"

        verbose_name_plural = "About Industry Items"



    def __str__(self):

        return self.name



    @property

    def icon(self):

        return self.icon_class or "fas fa-industry"



    def get_link(self):

        if self.link_url:

            return self.link_url

        import urllib.parse

        return f"/jobs/?industry={urllib.parse.quote(self.name)}"





class CEOMessageSettings(models.Model):

    # Section Toggles

    hero_visible = models.BooleanField(default=True)

    profile_visible = models.BooleanField(default=True)

    message_visible = models.BooleanField(default=True)

    principles_visible = models.BooleanField(default=True)

    vm_visible = models.BooleanField(default=True)

    cta_visible = models.BooleanField(default=True)



    # Hero / Header Banner

    page_title = models.CharField(max_length=255, default="CEO & Founder Message")

    page_eyebrow = models.CharField(max_length=150, default="Get To Know Us", blank=True)

    hero_subtitle = models.TextField(

        blank=True,

        default="Driving innovation, excellence, and ethical talent solutions across industries."

    )

    hero_bg_image = models.ImageField(upload_to=scramble_upload_path, blank=True, null=True)

    breadcrumb_title = models.CharField(max_length=100, blank=True, default="CEO & Founder")



    # CEO Profile Card

    ceo_name = models.CharField(max_length=150, default="ASHVANI DUBEY")

    ceo_role = models.CharField(max_length=150, default="CEO & FOUNDER")

    ceo_org = models.CharField(max_length=255, default="Sky Vision Group of Consultancy")

    ceo_tagline = models.CharField(max_length=255, blank=True, default="Empowering Businesses. Transforming Careers.")

    ceo_photo = models.ImageField(upload_to=scramble_upload_path, blank=True, null=True)

    ceo_photo_alt = models.CharField(max_length=150, blank=True, default="Ashvani Dubey - CEO & Founder")

    static_photo_path = models.CharField(max_length=255, default="images/team/CEO image.png", blank=True)



    # Message Content

    title_eyebrow = models.CharField(max_length=100, default="MESSAGE FROM THE", blank=True)

    title_main = models.CharField(max_length=150, default="CEO & FOUNDER")

    message_p1 = models.TextField(

        default="At Sky Vision Group of Consultancy, our vision is simple—connecting the right talent with the right opportunities while helping businesses build stronger teams.",

        blank=True

    )

    message_p2 = models.TextField(

        default="As the CEO & Founder, I believe that recruitment is more than filling positions—it is about creating opportunities, empowering individuals, and driving organizational success.",

        blank=True

    )

    message_p3 = models.TextField(

        default="Our commitment to integrity, transparency, and excellence has helped us earn the trust of our clients and candidates across industries. From permanent staffing and executive search to HR outsourcing, internship programs, and workforce solutions, we continuously strive to deliver quality services that create long-term value.",

        blank=True

    )

    message_p4 = models.TextField(

        default="As the world of work evolves, we remain dedicated to innovation, technology-driven recruitment, and people-first solutions. Together with our team, clients, and partners, we will continue creating opportunities, empowering careers, and building a better future.",

        blank=True

    )

    quote_text = models.TextField(

        default="Great organizations are built by great people.\nOur purpose is to connect talent with opportunity and create lasting value for both employers and professionals.",

        blank=True

    )

    closing_text = models.CharField(max_length=150, blank=True, default="Warm regards,")

    signoff_text = models.CharField(max_length=150, blank=True, default="Ashvani Dubey — CEO & Founder")



    # Principles Section Heading

    principles_tag = models.CharField(max_length=100, blank=True, default="OUR LEADERSHIP")

    principles_title = models.CharField(max_length=150, blank=True, default="PRINCIPLES")

    principles_subtitle = models.TextField(

        blank=True,

        default="The core values that define our culture, decisions, and commitment to excellence."

    )



    # Vision & Mission

    vision_title = models.CharField(max_length=120, default="OUR VISION")

    vision_icon = models.CharField(max_length=100, default="fa-solid fa-eye")

    vision_text = models.TextField(

        default="To become one of India's most trusted recruitment and HR consulting organizations by delivering innovative workforce solutions that empower businesses and transform careers.",

        blank=True

    )

    mission_title = models.CharField(max_length=120, default="OUR MISSION")

    mission_icon = models.CharField(max_length=100, default="fa-solid fa-bullseye")

    mission_text = models.TextField(

        default="To connect the right talent with the right opportunities through ethical recruitment, professional excellence, and customer-centric services while creating sustainable value for employers and job seekers.",

        blank=True

    )



    # Signature & Contact

    signature_name = models.CharField(max_length=150, default="Ashvani Dubey")

    signature_image = models.ImageField(upload_to=scramble_upload_path, blank=True, null=True)

    linkedin_url = models.CharField(max_length=255, default="https://www.linkedin.com/company/skyvisiongroup/", blank=True)

    facebook_url = models.CharField(max_length=255, default="https://www.facebook.com/share/197C5xryds/", blank=True)

    twitter_url = models.CharField(max_length=255, blank=True, default="")

    instagram_url = models.CharField(max_length=255, blank=True, default="")

    email_address = models.CharField(max_length=150, default="hr@svgconsultancy.com", blank=True)



    # Bottom CTA Section

    cta_heading = models.CharField(

        max_length=255,

        default="Looking for the Right Talent or Career Opportunity?",

        blank=True

    )

    cta_text = models.TextField(

        default="Connect with Sky Vision Group of Consultancy today to discover tailored recruitment and workforce solutions.",

        blank=True

    )

    cta_btn_label = models.CharField(max_length=100, default="Explore Opportunities", blank=True)

    cta_btn_url = models.CharField(max_length=255, default="/jobs/", blank=True)

    cta_btn2_label = models.CharField(max_length=100, default="Contact Us", blank=True)

    cta_btn2_url = models.CharField(max_length=255, default="/contact/", blank=True)



    # SEO & Meta

    meta_title = models.CharField(

        max_length=255,

        blank=True,

        default="CEO & Founder Message — Sky Vision Group Consultancy"

    )

    meta_description = models.TextField(

        blank=True,

        default="Read the official message from Ashvani Dubey, CEO & Founder of Sky Vision Group of Consultancy. Learn about our vision, mission, and leadership principles."

    )

    og_image = models.ImageField(upload_to=scramble_upload_path, blank=True, null=True)



    updated_at = models.DateTimeField(auto_now=True)



    class Meta:

        db_table = 'ceo_message_settings'

        verbose_name = "CEO Message Settings"

        verbose_name_plural = "CEO Message Settings"



    def __str__(self):

        return f"CEO Message ({self.ceo_name})"



    @classmethod

    def get_settings(cls):

        obj = cls.objects.first()

        if not obj:

            obj = cls.objects.create()

        return obj



    def get_ceo_photo_url(self):

        if self.ceo_photo:

            try:

                return self.ceo_photo.url

            except Exception:

                pass

        if self.static_photo_path:

            p = str(self.static_photo_path).strip()

            if p.startswith('http://') or p.startswith('https://') or p.startswith('/media/') or p.startswith('/static/'):

                return p

            return f"/static/{p.lstrip('/')}"

        return "/static/images/team/CEO image.png"



    def get_hero_bg_url(self):

        if self.hero_bg_image:

            try:

                return self.hero_bg_image.url

            except Exception:

                pass

        return None



    def get_signature_image_url(self):

        if self.signature_image:

            try:

                return self.signature_image.url

            except Exception:

                pass

        return None



    def get_og_image_url(self):

        if self.og_image:

            try:

                return self.og_image.url

            except Exception:

                pass

        return self.get_ceo_photo_url()





class CEOLeadershipPrinciple(models.Model):

    title = models.CharField(max_length=150)

    description = models.TextField()

    icon_class = models.CharField(max_length=100, default="fa-solid fa-shield-halved")

    order = models.PositiveIntegerField(default=0)

    is_visible = models.BooleanField(default=True)



    class Meta:

        db_table = 'ceo_leadership_principles'

        ordering = ['order', 'id']

        verbose_name = "CEO Leadership Principle"

        verbose_name_plural = "CEO Leadership Principles"



    def __str__(self):

        return self.title





class CEOStatBadge(models.Model):

    icon_class = models.CharField(max_length=100, default="fa-solid fa-award")

    value = models.CharField(max_length=50)

    label = models.CharField(max_length=100)

    order = models.PositiveIntegerField(default=0)

    is_visible = models.BooleanField(default=True)



    class Meta:

        db_table = 'ceo_stat_badges'

        ordering = ['order', 'id']

        verbose_name = "CEO Stat Badge"

        verbose_name_plural = "CEO Stat Badges"



    def __str__(self):

        return f"{self.value} {self.label}"





class OurTeamSettings(models.Model):

    # Visibility toggles for all sections

    hero_visible = models.BooleanField(default=True)

    about_visible = models.BooleanField(default=True)

    leadership_visible = models.BooleanField(default=True)

    specialists_visible = models.BooleanField(default=True)

    departments_visible = models.BooleanField(default=True)

    stats_visible = models.BooleanField(default=True)

    trust_visible = models.BooleanField(default=True)

    values_visible = models.BooleanField(default=True)

    quote_visible = models.BooleanField(default=True)

    cta_visible = models.BooleanField(default=True)



    # Hero Banner

    breadcrumb_title = models.CharField(max_length=150, default="Our Team", blank=True)

    hero_eyebrow = models.CharField(max_length=150, default="Our Team", blank=True)

    hero_title = models.CharField(max_length=255, default="Meet Our Expert Team")

    hero_description = models.TextField(

        default="Behind every successful placement is a dedicated team of recruitment professionals committed to connecting exceptional talent with outstanding opportunities across every industry we serve.",

        blank=True

    )

    hero_btn1_text = models.CharField(max_length=100, default="Meet Our Leaders", blank=True)

    hero_btn1_url = models.CharField(max_length=255, default="#leadership", blank=True)

    hero_btn2_text = models.CharField(max_length=100, default="Join Our Team →", blank=True)

    hero_btn2_url = models.CharField(max_length=255, default="#join", blank=True)

    hero_image = models.ImageField(upload_to=scramble_upload_path, blank=True, null=True)

    hero_image_url_custom = models.CharField(max_length=255, default="https://images.unsplash.com/photo-1600880292203-757bb62b4baf?w=900&q=80", blank=True)

    hero_image_alt = models.CharField(max_length=255, default="Sky Vision recruitment team collaborating in the office", blank=True)



    # About Our Team

    about_eyebrow = models.CharField(max_length=150, default="About Our Team", blank=True)

    about_heading = models.CharField(max_length=255, default="The People Behind Sky Vision")

    about_description = models.TextField(

        default="At Sky Vision Group Consultancy, our team is the driving force behind every successful recruitment journey. With expertise across recruitment, HR consulting, career guidance, and client management, we work together to deliver exceptional hiring solutions for businesses and rewarding career opportunities for candidates.",

        blank=True

    )



    # Leadership Section Headers & Limits

    leadership_tag = models.CharField(max_length=150, default="Leadership Team", blank=True)

    leadership_title = models.CharField(max_length=255, default="Our <span>Leadership</span> Team", blank=True)

    leadership_subtitle = models.TextField(default="Visionary leaders guiding Sky Vision's strategy, culture, and client success.", blank=True)

    leadership_max_items = models.PositiveIntegerField(default=12, blank=True)



    # Recruitment Specialists Headers & Limits

    specialists_tag = models.CharField(max_length=150, default="Recruitment Specialists", blank=True)

    specialists_title = models.CharField(max_length=255, default="Our <span>Recruitment</span> Specialists", blank=True)

    specialists_subtitle = models.TextField(default="Skilled consultants dedicated to matching the right talent with the right opportunity.", blank=True)

    specialists_max_items = models.PositiveIntegerField(default=24, blank=True)



    # Departments Section Headers

    departments_tag = models.CharField(max_length=150, default="Our Departments", blank=True)

    departments_title = models.CharField(max_length=255, default="Our <span>Departments</span>", blank=True)

    departments_subtitle = models.TextField(default="Specialized teams working together to deliver end-to-end recruitment and consulting solutions.", blank=True)



    # Why Clients Trust Our Team & Core Values

    trust_tag = models.CharField(max_length=150, default="Why Choose Us", blank=True)

    trust_heading = models.CharField(max_length=255, default="Why Clients <span>Trust</span> Our Team", blank=True)

    trust_subtitle = models.TextField(default="Our team combines recruitment expertise, market knowledge, and client-first commitment to ensure successful hiring outcomes.", blank=True)

    trust_image = models.ImageField(upload_to=scramble_upload_path, blank=True, null=True)

    static_trust_image = models.CharField(max_length=255, default="images/services/manpower-supply 2.png", blank=True)



    values_tag = models.CharField(max_length=150, default="Core Values", blank=True)

    values_heading = models.CharField(max_length=255, default="Our Core <span>Values</span>", blank=True)

    values_subtitle = models.TextField(default="The guiding principles behind every decision, placement, and relationship we build.", blank=True)



    # Leadership Message / Quote Band

    quote_text = models.TextField(

        default="Every great placement starts with listening — to the client's needs and the candidate's aspirations. Our team's commitment to that balance is what has made Sky Vision a trusted recruitment partner across industries.",

        blank=True

    )

    quote_author_name = models.CharField(max_length=150, default="Ashvani Dubey", blank=True)

    quote_author_role = models.CharField(max_length=255, default="CEO & Founder, Sky Vision Group Consultancy", blank=True)

    quote_author_image = models.ImageField(upload_to=scramble_upload_path, blank=True, null=True)

    static_quote_image = models.CharField(max_length=255, default="images/team/CEO image.png", blank=True)



    # CTA Section

    cta_icon = models.CharField(max_length=50, default="👥", blank=True)

    cta_heading = models.CharField(max_length=255, default="Want to Work With Us?", blank=True)

    cta_description = models.TextField(

        default="We're always looking for passionate professionals who want to make a difference in recruitment and HR consulting.",

        blank=True

    )

    cta_btn1_text = models.CharField(max_length=100, default="Join Our Team", blank=True)

    cta_btn1_url = models.CharField(max_length=255, default="/careers/", blank=True)

    cta_btn2_text = models.CharField(max_length=100, default="Current Openings", blank=True)

    cta_btn2_url = models.CharField(max_length=255, default="/careers/", blank=True)



    # SEO & Meta

    meta_title = models.CharField(max_length=255, default="Our Leadership & Team — Sky Vision Group Consultancy", blank=True)

    meta_description = models.TextField(

        default="Meet the visionary leadership and expert recruitment team behind Sky Vision Group Consultancy in Lucknow.",

        blank=True

    )

    og_image = models.ImageField(upload_to=scramble_upload_path, blank=True, null=True)



    updated_at = models.DateTimeField(auto_now=True)



    class Meta:

        db_table = 'our_team_settings'

        verbose_name = "Our Team Settings"

        verbose_name_plural = "Our Team Settings"



    def __str__(self):

        return "Our Team Settings"



    @classmethod

    def get_settings(cls):

        obj = cls.objects.first()

        if not obj:

            obj = cls.objects.create()

        return obj



    def get_hero_image(self):

        if self.hero_image:

            try:

                return self.hero_image.url

            except Exception:

                pass

        return self.hero_image_url_custom or "https://images.unsplash.com/photo-1600880292203-757bb62b4baf?w=900&q=80"



    def get_about_image(self):

        if self.about_image:

            try:

                return self.about_image.url

            except Exception:

                pass

        return "https://images.unsplash.com/photo-1522071820081-009f0129c71c?w=900&q=80"



    def get_trust_image(self):

        if self.trust_image:

            try:

                return self.trust_image.url

            except Exception:

                pass

        if self.static_trust_image:

            p = str(self.static_trust_image).strip()

            if p.startswith('http://') or p.startswith('https://') or p.startswith('/media/') or p.startswith('/static/'):

                return p

            return f"/static/{p.lstrip('/')}"

        return "/static/images/services/manpower-supply 2.png"



    def get_quote_image(self):

        if self.quote_author_image:

            try:

                return self.quote_author_image.url

            except Exception:

                pass

        if self.static_quote_image:

            p = str(self.static_quote_image).strip()

            if p.startswith('http://') or p.startswith('https://') or p.startswith('/media/') or p.startswith('/static/'):

                return p

            return f"/static/{p.lstrip('/')}"

        return "/static/images/team/CEO image.png"



    def get_og_image_url(self):

        if self.og_image:

            try:

                return self.og_image.url

            except Exception:

                pass

        return self.get_hero_image()



    @property

    def about_title(self):

        return self.about_heading



    @about_title.setter

    def about_title(self, value):

        self.about_heading = value



    @property

    def trust_title(self):

        return self.trust_heading



    @trust_title.setter

    def trust_title(self, value):

        self.trust_heading = value



    @property

    def values_title(self):

        return self.values_heading



    @values_title.setter

    def values_title(self, value):

        self.values_heading = value



    @property

    def cta_text(self):

        return self.cta_description



    @cta_text.setter

    def cta_text(self, value):

        self.cta_description = value



    @staticmethod

    def _extract_clean_and_highlight(html_str):

        import re

        s = str(html_str or '')

        m = re.search(r'<span[^>]*>(.*?)</span>', s, re.IGNORECASE)

        highlight = m.group(1).strip() if m else ''

        clean = re.sub(r'<[^>]+>', '', s).strip()

        return clean, highlight



    @property

    def leadership_clean_title(self):

        clean, _ = self._extract_clean_and_highlight(self.leadership_title)

        return clean or 'Our Leadership Team'



    @property

    def leadership_highlight_word(self):

        _, hl = self._extract_clean_and_highlight(self.leadership_title)

        return hl or 'Leadership'



    @property

    def specialists_clean_title(self):

        clean, _ = self._extract_clean_and_highlight(self.specialists_title)

        return clean or 'Our Recruitment Specialists'



    @property

    def specialists_highlight_word(self):

        _, hl = self._extract_clean_and_highlight(self.specialists_title)

        return hl or 'Recruitment'



    @property

    def departments_clean_title(self):

        clean, _ = self._extract_clean_and_highlight(self.departments_title)

        return clean or 'Our Departments'



    @property

    def departments_highlight_word(self):

        _, hl = self._extract_clean_and_highlight(self.departments_title)

        return hl or 'Departments'



    @property

    def trust_clean_title(self):

        clean, _ = self._extract_clean_and_highlight(self.trust_heading)

        return clean or 'Why Clients Trust Our Team'



    @property

    def trust_highlight_word(self):

        _, hl = self._extract_clean_and_highlight(self.trust_heading)

        return hl or 'Trust'



    @property

    def values_clean_title(self):

        clean, _ = self._extract_clean_and_highlight(self.values_heading)

        return clean or 'Our Core Values'



    @property

    def values_highlight_word(self):

        _, hl = self._extract_clean_and_highlight(self.values_heading)

        return hl or 'Values'





class TeamFeatureHighlight(models.Model):

    icon = models.CharField(max_length=50, default="👥")

    title = models.CharField(max_length=150)

    description = models.TextField()

    order = models.PositiveIntegerField(default=0)

    is_visible = models.BooleanField(default=True)



    class Meta:

        db_table = 'team_feature_highlights'

        ordering = ['order', 'id']

        verbose_name = "Team Feature Highlight"

        verbose_name_plural = "Team Feature Highlights"



    def __str__(self):

        return self.title





class TeamStat(models.Model):

    icon = models.CharField(max_length=50, default="👥")

    count = models.CharField(max_length=50, default="50", blank=True)

    suffix = models.CharField(max_length=20, default="", blank=True)

    label = models.CharField(max_length=150)

    static_text = models.CharField(max_length=50, blank=True, default="")

    order = models.PositiveIntegerField(default=0)

    is_visible = models.BooleanField(default=True)



    class Meta:

        db_table = 'team_stats'

        ordering = ['order', 'id']

        verbose_name = "Team Stat Counter"

        verbose_name_plural = "Team Stat Counters"



    def __str__(self):

        return f"{self.count}{self.suffix} {self.label}"





class TeamDepartment(models.Model):

    name = models.CharField(max_length=150)

    icon = models.CharField(max_length=50, default="👔")

    description = models.TextField()

    image = models.ImageField(upload_to=scramble_upload_path, blank=True, null=True)

    image_url = models.CharField(max_length=255, blank=True, default="")

    team_size = models.CharField(max_length=50, blank=True, default="")

    order = models.PositiveIntegerField(default=0)

    is_visible = models.BooleanField(default=True)



    class Meta:

        db_table = 'team_departments'

        ordering = ['order', 'id']

        verbose_name = "Team Department"

        verbose_name_plural = "Team Departments"



    def __str__(self):

        return self.name



    def get_image_url(self):

        if self.image:

            try:

                return self.image.url

            except Exception:

                pass

        return self.image_url or "https://images.unsplash.com/photo-1521737604893-d14cc237f11d?w=400&q=80"





class TeamTrustPoint(models.Model):

    title = models.CharField(max_length=255)

    icon_class = models.CharField(max_length=50, default="✓", blank=True)

    order = models.PositiveIntegerField(default=0)

    is_visible = models.BooleanField(default=True)



    class Meta:

        db_table = 'team_trust_points'

        ordering = ['order', 'id']

        verbose_name = "Team Trust Point"

        verbose_name_plural = "Team Trust Points"



    def __str__(self):

        return self.title





class TeamCoreValue(models.Model):

    icon = models.CharField(max_length=50, default="🤝")

    title = models.CharField(max_length=150)

    description = models.TextField()

    order = models.PositiveIntegerField(default=0)

    is_visible = models.BooleanField(default=True)



    class Meta:

        db_table = 'team_core_values'

        ordering = ['order', 'id']

        verbose_name = "Team Core Value"

        verbose_name_plural = "Team Core Values"



    def __str__(self):

        return self.title





class TeamMember(models.Model):

    CATEGORY_CHOICES = (

        ('leadership', 'Leadership Team'),

        ('specialist', 'Recruitment Specialist'),

        ('support', 'Executive & Support'),

    )

    name = models.CharField(max_length=150)

    role = models.CharField(max_length=150)

    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='leadership')

    photo = models.ImageField(upload_to=scramble_upload_path, blank=True, null=True)

    static_photo_path = models.CharField(max_length=255, blank=True, default="")

    bio = models.TextField(blank=True, default="")

    experience_text = models.CharField(max_length=100, blank=True, default="")

    linkedin_url = models.CharField(max_length=255, blank=True, default="#")

    email_url = models.CharField(max_length=255, blank=True, default="#")

    order = models.PositiveIntegerField(default=0)

    is_visible = models.BooleanField(default=True)

    show_on_about_page = models.BooleanField(default=False)

    about_page_order = models.PositiveIntegerField(default=0)



    class Meta:

        db_table = 'team_members'

        ordering = ['order', 'id']

        verbose_name = "Team Member"

        verbose_name_plural = "Team Members"



    def __str__(self):

        return f"{self.name} ({self.role})"



    def get_photo_url(self):

        if self.photo:

            try:

                return self.photo.url

            except Exception:

                pass

        if self.static_photo_path:

            p = str(self.static_photo_path).strip()

            if p.startswith('http://') or p.startswith('https://') or p.startswith('/media/') or p.startswith('/static/'):

                return p

            return f"/static/{p.lstrip('/')}"

        return "/static/images/team/CEO image.png"





class OurJourneySettings(models.Model):

    # Section Visibility Toggles

    hero_visible = models.BooleanField(default=True)

    story_visible = models.BooleanField(default=True)

    timeline_visible = models.BooleanField(default=True)

    milestones_visible = models.BooleanField(default=True)

    impact_visible = models.BooleanField(default=True)

    numbers_visible = models.BooleanField(default=True)

    ahead_visible = models.BooleanField(default=True)



    # 1. Hero Banner

    hero_eyebrow = models.CharField(max_length=150, default="Our Journey", blank=True)

    hero_title = models.CharField(max_length=255, default="Growing Together, Building Careers, <span>Creating Success</span>")

    hero_highlight = models.CharField(max_length=150, default="Creating Success", blank=True)

    hero_description = models.TextField(

        default="Since our founding, Sky Vision Group Consultancy has been on a mission to connect talent with opportunity. Every placement, every partnership and every milestone reflects our commitment to businesses and professionals across India — a journey built on trust, consistency and genuine care for the people we serve.",

        blank=True

    )

    badge_num = models.CharField(max_length=50, default="6+", blank=True)

    badge_text = models.CharField(max_length=100, default="Years of Excellence", blank=True)

    hero_btn1_text = models.CharField(max_length=100, default="Explore Our Story", blank=True)

    hero_btn1_url = models.CharField(max_length=255, default="#oj-story", blank=True)

    hero_btn2_text = models.CharField(max_length=100, default="Contact Us", blank=True)

    hero_btn2_url = models.CharField(max_length=255, default="/contact/", blank=True)

    hero_image = models.ImageField(upload_to=scramble_upload_path, blank=True, null=True)

    hero_image_url_custom = models.CharField(max_length=255, default="https://images.unsplash.com/photo-1600880292203-757bb62b4baf?w=1000&q=80", blank=True)



    stat1_num = models.CharField(max_length=50, default="2022", blank=True)

    stat1_label = models.CharField(max_length=100, default="Founded", blank=True)

    stat2_num = models.CharField(max_length=50, default="5000+", blank=True)

    stat2_label = models.CharField(max_length=100, default="Placed", blank=True)

    stat3_num = models.CharField(max_length=50, default="300+", blank=True)

    stat3_label = models.CharField(max_length=100, default="Partners", blank=True)



    # 2. Our Story Section

    story_tag = models.CharField(max_length=100, default="Our Story", blank=True)

    story_title = models.CharField(max_length=255, default="A journey that began with a <span>vision</span>")

    story_highlight = models.CharField(max_length=150, default="vision", blank=True)

    story_p1 = models.TextField(

        default="Sky Vision Group Consultancy was founded on a simple belief — that the right people, in the right roles, can transform businesses and change lives. What started as a small team in Lucknow with a big vision has grown into a trusted consultancy serving clients and candidates across India.",

        blank=True

    )

    story_p2 = models.TextField(

        default="In our early years, we faced the same challenges every young consultancy does — building trust in a crowded market, proving our process, and earning our first long-term partnerships. We stayed close to our clients, listened to our candidates, and let consistent results speak for us.",

        blank=True

    )

    story_p3 = models.TextField(

        default="Today, that same founding spirit drives everything we do — from manpower supply and recruitment to HR outsourcing and career counselling. Every year has added a new capability, a new partnership and a new reason for our clients and candidates to trust us with their future.",

        blank=True

    )

    story_image = models.ImageField(upload_to=scramble_upload_path, blank=True, null=True)

    story_image_url_custom = models.CharField(max_length=255, default="https://images.unsplash.com/photo-1521737604893-d14cc237f11d?w=900&q=80", blank=True)



    # 3. Growth Timeline Section

    timeline_tag = models.CharField(max_length=100, default="How Far We've Come", blank=True)

    timeline_title = models.CharField(max_length=255, default="Our Growth <span>Timeline</span>", blank=True)

    timeline_highlight = models.CharField(max_length=150, default="Timeline", blank=True)

    timeline_subtitle = models.TextField(default="From a small vision to becoming a trusted recruitment consultancy.", blank=True)



    # 4. Our Milestones Section

    milestones_tag = models.CharField(max_length=100, default="What We've Achieved", blank=True)

    milestones_title = models.CharField(max_length=255, default="Our <span>Milestones</span>", blank=True)

    milestones_highlight = models.CharField(max_length=150, default="Milestones", blank=True)

    milestones_subtitle = models.TextField(default="Key moments that shaped our growth as a consultancy.", blank=True)



    # 5. Our Impact Section

    impact_tag = models.CharField(max_length=100, default="Our Impact", blank=True)

    impact_title = models.CharField(max_length=255, default="Real results for businesses and <span>professionals</span>", blank=True)

    impact_highlight = models.CharField(max_length=150, default="professionals", blank=True)

    impact_description = models.TextField(

        default="Our journey isn't just measured in years — it's measured in the businesses we've helped grow and the careers we've helped build. Every service we offer is designed around one goal: reliable, lasting impact.",

        blank=True

    )

    impact_image = models.ImageField(upload_to=scramble_upload_path, blank=True, null=True)

    impact_image_url_custom = models.CharField(max_length=255, default="https://images.unsplash.com/photo-1552664730-d307ca884978?w=900&q=80", blank=True)



    # 6. By The Numbers Section

    numbers_tag = models.CharField(max_length=100, default="By The Numbers", blank=True)

    numbers_title = models.CharField(max_length=255, default="Our Journey In <span>Numbers</span>", blank=True)

    numbers_highlight = models.CharField(max_length=150, default="Numbers", blank=True)

    numbers_subtitle = models.TextField(default="A snapshot of the trust we've built since 2022.", blank=True)



    # 7. Looking Ahead Section

    ahead_tag = models.CharField(max_length=100, default="Looking Ahead", blank=True)

    ahead_title = models.CharField(max_length=255, default="The next chapter of our <span>journey</span>", blank=True)

    ahead_highlight = models.CharField(max_length=150, default="journey", blank=True)

    ahead_description = models.TextField(

        default="Our story is far from over. As we look to the future, we remain committed to the same values that got us here — trust, quality and genuine care for the people we work with. Here's what's next for Sky Vision Group Consultancy.",

        blank=True

    )

    cta_btn1_text = models.CharField(max_length=100, default="Partner With Us", blank=True)

    cta_btn1_url = models.CharField(max_length=255, default="/contact/", blank=True)

    cta_btn2_text = models.CharField(max_length=100, default="Contact Our Team", blank=True)

    cta_btn2_url = models.CharField(max_length=255, default="/contact/", blank=True)



    # SEO & Social Meta

    meta_title = models.CharField(max_length=255, default="Our Journey — Sky Vision Group Consultancy", blank=True)

    meta_description = models.TextField(

        default="Explore the journey of Sky Vision Group Consultancy since 2022. Discover our milestones, impact, and vision for connecting talent across India.",

        blank=True

    )

    og_image = models.ImageField(upload_to=scramble_upload_path, blank=True, null=True)



    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    updated_at = models.DateTimeField(auto_now=True)



    class Meta:

        db_table = 'our_journey_settings'

        verbose_name = "Our Journey Settings"

        verbose_name_plural = "Our Journey Settings"



    def __str__(self):

        return "Our Journey Settings"



    @classmethod

    def get_settings(cls):

        obj = cls.objects.first()

        if not obj:

            obj = cls.objects.create()

        return obj



    def get_hero_image(self):

        if self.hero_image:

            try:

                return self.hero_image.url

            except Exception:

                pass

        return self.hero_image_url_custom or "https://images.unsplash.com/photo-1600880292203-757bb62b4baf?w=1000&q=80"



    def get_story_image(self):

        if self.story_image:

            try:

                return self.story_image.url

            except Exception:

                pass

        return self.story_image_url_custom or "https://images.unsplash.com/photo-1521737604893-d14cc237f11d?w=900&q=80"



    def get_impact_image(self):

        if self.impact_image:

            try:

                return self.impact_image.url

            except Exception:

                pass

        return self.impact_image_url_custom or "https://images.unsplash.com/photo-1552664730-d307ca884978?w=900&q=80"



    def get_og_image_url(self):

        if self.og_image:

            try:

                return self.og_image.url

            except Exception:

                pass

        return self.get_hero_image()



    @staticmethod

    def _extract_clean_and_highlight(html_str):

        import re

        s = str(html_str or '')

        m = re.search(r'<span[^>]*>(.*?)</span>', s, re.IGNORECASE)

        highlight = m.group(1).strip() if m else ''

        clean = re.sub(r'<[^>]+>', '', s).strip()

        return clean, highlight



    @property

    def hero_clean_title(self):

        clean, _ = self._extract_clean_and_highlight(self.hero_title)

        return clean or "Growing Together, Building Careers, Creating Success"



    @property

    def hero_highlight_word(self):

        _, hl = self._extract_clean_and_highlight(self.hero_title)

        return hl or self.hero_highlight or "Creating Success"



    @property

    def story_clean_title(self):

        clean, _ = self._extract_clean_and_highlight(self.story_title)

        return clean or "A journey that began with a vision"



    @property

    def story_highlight_word(self):

        _, hl = self._extract_clean_and_highlight(self.story_title)

        return hl or self.story_highlight or "vision"



    @property

    def timeline_clean_title(self):

        clean, _ = self._extract_clean_and_highlight(self.timeline_title)

        return clean or "Our Growth Timeline"



    @property

    def timeline_highlight_word(self):

        _, hl = self._extract_clean_and_highlight(self.timeline_title)

        return hl or self.timeline_highlight or "Timeline"



    @property

    def milestones_clean_title(self):

        clean, _ = self._extract_clean_and_highlight(self.milestones_title)

        return clean or "Our Milestones"



    @property

    def milestones_highlight_word(self):

        _, hl = self._extract_clean_and_highlight(self.milestones_title)

        return hl or self.milestones_highlight or "Milestones"



    @property

    def impact_clean_title(self):

        clean, _ = self._extract_clean_and_highlight(self.impact_title)

        return clean or "Real results for businesses and professionals"



    @property

    def impact_highlight_word(self):

        _, hl = self._extract_clean_and_highlight(self.impact_title)

        return hl or self.impact_highlight or "professionals"



    @property

    def numbers_clean_title(self):

        clean, _ = self._extract_clean_and_highlight(self.numbers_title)

        return clean or "Our Journey In Numbers"



    @property

    def numbers_highlight_word(self):

        _, hl = self._extract_clean_and_highlight(self.numbers_title)

        return hl or self.numbers_highlight or "Numbers"



    @property

    def ahead_clean_title(self):

        clean, _ = self._extract_clean_and_highlight(self.ahead_title)

        return clean or "The next chapter of our journey"



    @property

    def ahead_highlight_word(self):

        _, hl = self._extract_clean_and_highlight(self.ahead_title)

        return hl or self.ahead_highlight or "journey"





# Alias for JourneyPageSettings

JourneyPageSettings = OurJourneySettings





class JourneyStoryParagraph(models.Model):

    text = models.TextField()

    order = models.PositiveIntegerField(default=0)

    is_visible = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    updated_at = models.DateTimeField(auto_now=True)



    class Meta:

        db_table = 'journey_story_paragraphs'

        ordering = ['order', 'id']

        verbose_name = "Journey Story Paragraph"

        verbose_name_plural = "Journey Story Paragraphs"



    @property

    def paragraph_text(self):

        return self.text



    @paragraph_text.setter

    def paragraph_text(self, value):

        self.text = value



    @property

    def is_highlight(self):

        if hasattr(self, '_is_highlight'):

            return self._is_highlight

        return self.order == 1



    @is_highlight.setter

    def is_highlight(self, value):

        self._is_highlight = bool(value)



    @property

    def is_active(self):

        return self.is_visible



    @is_active.setter

    def is_active(self, value):

        self.is_visible = bool(value)



    def __str__(self):

        return f"Paragraph #{self.order}: {self.text[:40]}..."





class JourneyStoryCard(models.Model):

    title = models.CharField(max_length=150)

    description = models.TextField()

    icon = models.CharField(max_length=100, default="fa-solid fa-shield-halved")

    color = models.CharField(max_length=50, default="blue") # blue or red

    order = models.PositiveIntegerField(default=0)

    is_visible = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    updated_at = models.DateTimeField(auto_now=True)



    class Meta:

        db_table = 'journey_story_cards'

        ordering = ['order', 'id']

        verbose_name = "Journey Story Feature Card"

        verbose_name_plural = "Journey Story Feature Cards"



    @property

    def is_active(self):

        return self.is_visible



    @is_active.setter

    def is_active(self, value):

        self.is_visible = bool(value)



    def __str__(self):

        return self.title





class JourneyMilestone(models.Model):

    year = models.CharField(max_length=30, default="2022")

    title = models.CharField(max_length=150)

    description = models.TextField()

    icon_class = models.CharField(max_length=100, default="fa-solid fa-flag")

    badge_label = models.CharField(max_length=100, default="Milestone", blank=True)

    order = models.PositiveIntegerField(default=0)

    is_visible = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    updated_at = models.DateTimeField(auto_now=True)



    class Meta:

        db_table = 'journey_milestones'

        ordering = ['order', 'id']

        verbose_name = "Journey Milestone"

        verbose_name_plural = "Journey Milestones"



    @property

    def is_active(self):

        return self.is_visible



    @is_active.setter

    def is_active(self, value):

        self.is_visible = bool(value)



    def __str__(self):

        return f"{self.year} — {self.title}"





# Alias JourneyTimelineItem for JourneyMilestone

JourneyTimelineItem = JourneyMilestone





class JourneyMilestoneCard(models.Model):

    year = models.CharField(max_length=50, default="2022")

    title = models.CharField(max_length=150)

    description = models.TextField()

    icon_class = models.CharField(max_length=100, default="fa-solid fa-trophy")

    order = models.PositiveIntegerField(default=0)

    is_visible = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    updated_at = models.DateTimeField(auto_now=True)



    class Meta:

        db_table = 'journey_milestone_cards'

        ordering = ['order', 'id']

        verbose_name = "Journey Milestone Card"

        verbose_name_plural = "Journey Milestone Cards"



    @property

    def is_active(self):

        return self.is_visible



    @is_active.setter

    def is_active(self, value):

        self.is_visible = bool(value)



    def __str__(self):

        return f"{self.year} — {self.title}"





class JourneyImpactItem(models.Model):

    title = models.CharField(max_length=150)

    description = models.TextField()

    icon = models.CharField(max_length=100, default="fa-solid fa-check")

    order = models.PositiveIntegerField(default=0)

    is_visible = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    updated_at = models.DateTimeField(auto_now=True)



    class Meta:

        db_table = 'journey_impact_items'

        ordering = ['order', 'id']

        verbose_name = "Journey Impact Item"

        verbose_name_plural = "Journey Impact Items"



    @property

    def is_active(self):

        return self.is_visible



    @is_active.setter

    def is_active(self, value):

        self.is_visible = bool(value)



    def __str__(self):

        return self.title





class JourneyStat(models.Model):

    count = models.CharField(max_length=50, default="6")

    suffix = models.CharField(max_length=20, default="+", blank=True)

    label = models.CharField(max_length=150)

    icon = models.CharField(max_length=100, default="fa-solid fa-calendar-check")

    order = models.PositiveIntegerField(default=0)

    is_visible = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    updated_at = models.DateTimeField(auto_now=True)



    class Meta:

        db_table = 'journey_stats'

        ordering = ['order', 'id']

        verbose_name = "Journey Number Stat"

        verbose_name_plural = "Journey Number Stats"



    @property

    def is_active(self):

        return self.is_visible



    @is_active.setter

    def is_active(self, value):

        self.is_visible = bool(value)



    def __str__(self):

        return f"{self.count}{self.suffix} {self.label}"





class JourneyFutureGoal(models.Model):

    text = models.CharField(max_length=255)

    icon = models.CharField(max_length=100, default="fa-solid fa-circle-check")

    order = models.PositiveIntegerField(default=0)

    is_visible = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    updated_at = models.DateTimeField(auto_now=True)



    class Meta:

        db_table = 'journey_future_goals'

        ordering = ['order', 'id']

        verbose_name = "Journey Future Goal"

        verbose_name_plural = "Journey Future Goals"



    @property

    def is_active(self):

        return self.is_visible



    @is_active.setter

    def is_active(self, value):

        self.is_visible = bool(value)



    def __str__(self):

        return self.text





# ==============================================================================

# CACHE INVALIDATION SIGNALS

# ==============================================================================

CACHE_KEY = 'public_site_context'

HOME_CACHE_KEY = 'home_page_context'

ABOUT_CACHE_KEY = 'about_pages_context'



@receiver([post_save, post_delete], sender=SiteSettings)

@receiver([post_save, post_delete], sender=NavItem)

@receiver([post_save, post_delete], sender=FooterColumn)

@receiver([post_save, post_delete], sender=FooterLink)

@receiver([post_save, post_delete], sender=SocialLink)

@receiver([post_save, post_delete], sender=FooterService)

def invalidate_site_context_cache(sender, **kwargs):

    cache.delete(CACHE_KEY)

    cache.delete(HOME_CACHE_KEY)

    cache.delete(ABOUT_CACHE_KEY)





@receiver([post_save, post_delete], sender=HomePageSettings)

@receiver([post_save, post_delete], sender=HeroStat)

@receiver([post_save, post_delete], sender=GrowthStep)

@receiver([post_save, post_delete], sender=HomeServiceCard)

@receiver([post_save, post_delete], sender=WhyChooseItem)

@receiver([post_save, post_delete], sender=HomeIndustryItem)

@receiver([post_save, post_delete], sender=InternshipCard)

@receiver([post_save, post_delete], sender=InternshipHighlight)

@receiver([post_save, post_delete], sender=FeaturedCandidate)

@receiver([post_save, post_delete], sender=GalleryImage)

@receiver([post_save, post_delete], sender=GalleryInfoBox)

def invalidate_home_context_cache(sender, **kwargs):

    cache.delete(HOME_CACHE_KEY)





@receiver([post_save, post_delete], sender=AboutCompanySettings)

@receiver([post_save, post_delete], sender=AboutWhyCard)

@receiver([post_save, post_delete], sender=AboutTestimonial)

@receiver([post_save, post_delete], sender=AboutTestimonialStat)

@receiver([post_save, post_delete], sender=AboutTrustPoint)

@receiver([post_save, post_delete], sender=AboutPartnerLogo)

@receiver([post_save, post_delete], sender=AboutIndustryItem)

@receiver([post_save, post_delete], sender=CEOMessageSettings)

@receiver([post_save, post_delete], sender=CEOLeadershipPrinciple)

@receiver([post_save, post_delete], sender=CEOStatBadge)

@receiver([post_save, post_delete], sender=OurTeamSettings)

@receiver([post_save, post_delete], sender=TeamMember)

@receiver([post_save, post_delete], sender=TeamFeatureHighlight)

@receiver([post_save, post_delete], sender=TeamStat)

@receiver([post_save, post_delete], sender=TeamDepartment)

@receiver([post_save, post_delete], sender=TeamTrustPoint)

@receiver([post_save, post_delete], sender=TeamCoreValue)

@receiver([post_save, post_delete], sender=OurJourneySettings)

@receiver([post_save, post_delete], sender=JourneyMilestone)

@receiver([post_save, post_delete], sender=JourneyStoryParagraph)

@receiver([post_save, post_delete], sender=JourneyStoryCard)

@receiver([post_save, post_delete], sender=JourneyMilestoneCard)

@receiver([post_save, post_delete], sender=JourneyImpactItem)

@receiver([post_save, post_delete], sender=JourneyStat)

@receiver([post_save, post_delete], sender=JourneyFutureGoal)

def invalidate_about_pages_cache(sender, **kwargs):

    cache.delete(ABOUT_CACHE_KEY)





# ==============================================================================

# MANPOWER SUPPLY SERVICE MODELS (SECTION-WISE DYNAMIC)

# ==============================================================================

MANPOWER_SUPPLY_CACHE_KEY = 'svg_manpower_supply_context'





class ManpowerSupplySettings(models.Model):

    # 1. Hero Section

    hero_visible = models.BooleanField(default=True)

    hero_eyebrow = models.CharField(max_length=150, default="Workforce Solutions", blank=True)

    hero_title = models.CharField(max_length=255, default="Manpower Supply <em>Services</em>")

    hero_subtitle = models.TextField(

        default="Professional workforce solutions for every business — the right people, the right skills, right on time.",

        blank=True

    )

    hero_badge_text = models.CharField(max_length=150, default="Verified Workforce", blank=True)

    hero_enquire_btn_text = models.CharField(max_length=100, default="Enquire Now", blank=True)

    hero_enquire_btn_url = models.CharField(max_length=255, default="/contact/", blank=True)

    hero_call_btn_text = models.CharField(max_length=100, default="Call Now", blank=True)

    hero_call_phone = models.CharField(max_length=50, default="+91 88531 11111", blank=True)

    hero_feat1_icon = models.CharField(max_length=100, default="fa-solid fa-user-group", blank=True)

    hero_feat1_text = models.CharField(max_length=150, default="Right People,<br>Right Skills", blank=True)

    hero_feat2_icon = models.CharField(max_length=100, default="fa-solid fa-shield-halved", blank=True)

    hero_feat2_text = models.CharField(max_length=150, default="Verified &amp;<br>Trained Workforce", blank=True)

    hero_feat3_icon = models.CharField(max_length=100, default="fa-regular fa-clock", blank=True)

    hero_feat3_text = models.CharField(max_length=150, default="On Time,<br>Every Time", blank=True)

    hero_image = models.ImageField(upload_to=scramble_upload_path, blank=True, null=True)

    hero_image_url_custom = models.CharField(max_length=255, default="/static/images/services/manpower-supply.png", blank=True)



    # 2. About Section

    about_visible = models.BooleanField(default=True)

    about_tag = models.CharField(max_length=150, default="About Manpower Supply", blank=True)

    about_title = models.CharField(max_length=255, default="Powering Businesses with the Right Workforce")

    about_description = models.TextField(

        default="At Sky Vision Group Consultancy, we provide reliable, efficient and cost-effective manpower supply services to industries and organizations across India. We supply skilled, unskilled and semi-skilled manpower tailored to your requirements.",

        blank=True

    )

    about_image = models.ImageField(upload_to=scramble_upload_path, blank=True, null=True)

    about_image_url_custom = models.CharField(max_length=255, default="/static/images/services/manpower-supply 1.png", blank=True)



    # 3. Services Grid Section

    services_visible = models.BooleanField(default=True)

    services_tag = models.CharField(max_length=150, default="Our Manpower Supply Services", blank=True)

    services_title = models.CharField(max_length=255, default="We Provide the Best Manpower Solutions")



    # 4. Split Section: Industries We Serve & Why Choose

    industries_why_visible = models.BooleanField(default=True)

    industries_tag = models.CharField(max_length=150, default="Industries We Serve", blank=True)

    industries_title = models.CharField(max_length=255, default="Serving a Wide Range of Industries")

    why_choose_tag = models.CharField(max_length=150, default="Why Choose Sky Vision", blank=True)

    why_choose_title = models.CharField(max_length=255, default="Your Trusted Manpower Partner")



    # 5. Recruitment Process Section

    process_visible = models.BooleanField(default=True)

    process_tag = models.CharField(max_length=150, default="Our Recruitment Process", blank=True)

    process_title = models.CharField(max_length=255, default="Simple Process to Find the Right People")

    process_subtitle = models.TextField(

        default="A clear, structured pipeline we follow for every manpower requirement.",

        blank=True

    )



    # 6. Stats Section

    stats_visible = models.BooleanField(default=True)



    # 7. FAQ + CTA Card Section

    faq_cta_visible = models.BooleanField(default=True)

    faq_tag = models.CharField(max_length=150, default="Frequently Asked Questions", blank=True)

    cta_tag = models.CharField(max_length=150, default="Need Manpower For Your Business?", blank=True)

    cta_title = models.CharField(max_length=255, default="We are Ready to Help You!")

    cta_subtitle = models.TextField(

        default="Get the right people for the right job. Contact us today for a customized solution.",

        blank=True

    )

    cta_call_btn_text = models.CharField(max_length=100, default="Call Now", blank=True)

    cta_call_phone = models.CharField(max_length=50, default="+91 88531 11111", blank=True)

    cta_enquire_btn_text = models.CharField(max_length=100, default="Send Enquiry", blank=True)

    cta_enquire_url = models.CharField(max_length=255, default="/contact/", blank=True)

    cta_image = models.ImageField(upload_to=scramble_upload_path, blank=True, null=True)

    cta_image_url_custom = models.CharField(max_length=255, default="/static/images/services/manpower-supply 2.png", blank=True)



    # 8. Trust Strip

    trust_visible = models.BooleanField(default=True)



    # SEO & Social Meta

    meta_title = models.CharField(max_length=255, default="Manpower Supply Services — Sky Vision Group Consultancy", blank=True)

    meta_description = models.TextField(

        default="Leading manpower supply and workforce solutions provider across India. Skilled, semi-skilled, and industrial manpower on demand.",

        blank=True

    )

    og_image = models.ImageField(upload_to=scramble_upload_path, blank=True, null=True)



    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    updated_at = models.DateTimeField(auto_now=True)



    class Meta:

        db_table = 'manpower_supply_settings'

        verbose_name = "Manpower Supply Settings"

        verbose_name_plural = "Manpower Supply Settings"



    def __str__(self):

        return "Manpower Supply Settings"



    @classmethod

    def get_settings(cls):

        obj = cls.objects.first()

        if not obj:

            obj = cls.objects.create()

        return obj



    def get_hero_image(self):

        if self.hero_image:

            try:

                return self.hero_image.url

            except Exception:

                pass

        return self.hero_image_url_custom or "/static/images/services/manpower-supply.png"



    def get_about_image(self):

        if self.about_image:

            try:

                return self.about_image.url

            except Exception:

                pass

        return self.about_image_url_custom or "/static/images/services/manpower-supply 1.png"



    def get_cta_image(self):

        if self.cta_image:

            try:

                return self.cta_image.url

            except Exception:

                pass

        return self.cta_image_url_custom or "/static/images/services/manpower-supply 2.png"



    def get_og_image_url(self):

        if self.og_image:

            try:

                return self.og_image.url

            except Exception:

                pass

        return self.get_about_image()





class ManpowerChecklistItem(models.Model):

    text = models.CharField(max_length=150)

    icon_class = models.CharField(max_length=100, default="fa-solid fa-circle-check")

    order = models.PositiveIntegerField(default=0)

    is_visible = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    updated_at = models.DateTimeField(auto_now=True)



    class Meta:

        db_table = 'manpower_checklist_items'

        ordering = ['order', 'id']

        verbose_name = "Manpower Checklist Item"

        verbose_name_plural = "Manpower Checklist Items"



    def __str__(self):

        return self.text





class ManpowerServiceCard(models.Model):

    title = models.CharField(max_length=150)

    description = models.TextField()

    icon_class = models.CharField(max_length=100, default="fa-solid fa-people-group")

    color_class = models.CharField(max_length=50, default="i-blue")  # i-blue, i-teal, i-amber, i-purple, i-pink, i-green

    order = models.PositiveIntegerField(default=0)

    is_visible = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    updated_at = models.DateTimeField(auto_now=True)



    class Meta:

        db_table = 'manpower_service_cards'

        ordering = ['order', 'id']

        verbose_name = "Manpower Service Card"

        verbose_name_plural = "Manpower Service Cards"



    def __str__(self):

        return self.title





class ManpowerIndustryItem(models.Model):

    name = models.CharField(max_length=100)

    icon_class = models.CharField(max_length=100, default="fa-solid fa-industry")

    order = models.PositiveIntegerField(default=0)

    is_visible = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    updated_at = models.DateTimeField(auto_now=True)



    class Meta:

        db_table = 'manpower_industry_items'

        ordering = ['order', 'id']

        verbose_name = "Manpower Industry Item"

        verbose_name_plural = "Manpower Industry Items"



    def __str__(self):

        return self.name





class ManpowerWhyChooseItem(models.Model):

    title = models.CharField(max_length=120)

    icon_class = models.CharField(max_length=100, default="fa-solid fa-user-group")

    order = models.PositiveIntegerField(default=0)

    is_visible = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    updated_at = models.DateTimeField(auto_now=True)



    class Meta:

        db_table = 'manpower_why_choose_items'

        ordering = ['order', 'id']

        verbose_name = "Manpower Why Choose Item"

        verbose_name_plural = "Manpower Why Choose Items"



    def __str__(self):

        return self.title





class ManpowerProcessStep(models.Model):

    step_number = models.CharField(max_length=10, default="01")

    title = models.CharField(max_length=150)

    icon_class = models.CharField(max_length=100, default="fa-solid fa-clipboard-list")

    order = models.PositiveIntegerField(default=0)

    is_visible = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    updated_at = models.DateTimeField(auto_now=True)



    class Meta:

        db_table = 'manpower_process_steps'

        ordering = ['order', 'id']

        verbose_name = "Manpower Process Step"

        verbose_name_plural = "Manpower Process Steps"



    def __str__(self):

        return f"{self.step_number} - {self.title}"





class ManpowerStatItem(models.Model):

    value = models.CharField(max_length=50, default="5000+")

    label = models.CharField(max_length=120, default="Candidates Placed")

    icon_class = models.CharField(max_length=100, default="fa-solid fa-user-group")

    order = models.PositiveIntegerField(default=0)

    is_visible = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    updated_at = models.DateTimeField(auto_now=True)



    class Meta:

        db_table = 'manpower_stat_items'

        ordering = ['order', 'id']

        verbose_name = "Manpower Stat Item"

        verbose_name_plural = "Manpower Stat Items"



    def __str__(self):

        return f"{self.value} {self.label}"





class ManpowerFaqItem(models.Model):

    question = models.CharField(max_length=255)

    answer = models.TextField()

    order = models.PositiveIntegerField(default=0)

    is_visible = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    updated_at = models.DateTimeField(auto_now=True)



    class Meta:

        db_table = 'manpower_faq_items'

        ordering = ['order', 'id']

        verbose_name = "Manpower FAQ Item"

        verbose_name_plural = "Manpower FAQ Items"



    def __str__(self):

        return self.question





class ManpowerTrustItem(models.Model):

    line1 = models.CharField(max_length=100, default="Trusted by")

    line2 = models.CharField(max_length=100, default="Top Companies")

    icon_class = models.CharField(max_length=100, default="fa-solid fa-award")

    order = models.PositiveIntegerField(default=0)

    is_visible = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    updated_at = models.DateTimeField(auto_now=True)



    class Meta:

        db_table = 'manpower_trust_items'

        ordering = ['order', 'id']

        verbose_name = "Manpower Trust Item"

        verbose_name_plural = "Manpower Trust Items"



    def __str__(self):

        return f"{self.line1} {self.line2}"





@receiver([post_save, post_delete], sender=ManpowerSupplySettings)

@receiver([post_save, post_delete], sender=ManpowerChecklistItem)

@receiver([post_save, post_delete], sender=ManpowerServiceCard)

@receiver([post_save, post_delete], sender=ManpowerIndustryItem)

@receiver([post_save, post_delete], sender=ManpowerWhyChooseItem)

@receiver([post_save, post_delete], sender=ManpowerProcessStep)

@receiver([post_save, post_delete], sender=ManpowerStatItem)

@receiver([post_save, post_delete], sender=ManpowerFaqItem)

@receiver([post_save, post_delete], sender=ManpowerTrustItem)

def invalidate_manpower_supply_cache(sender, **kwargs):

    cache.delete(MANPOWER_SUPPLY_CACHE_KEY)





# ==============================================================================

# RECRUITMENT & PLACEMENT SERVICE MODELS (SECTION-WISE DYNAMIC)

# ==============================================================================

RECRUITMENT_PLACEMENT_CACHE_KEY = 'svg_recruitment_placement_context'





class RecruitmentPlacementSettings(models.Model):

    # Master Visibility Switches

    hero_visible = models.BooleanField(default=True)

    about_visible = models.BooleanField(default=True)

    why_partner_visible = models.BooleanField(default=True)

    services_visible = models.BooleanField(default=True)

    process_visible = models.BooleanField(default=True)

    insights_visible = models.BooleanField(default=True)

    partners_visible = models.BooleanField(default=True)

    faq_visible = models.BooleanField(default=True)

    cta_visible = models.BooleanField(default=True)



    # 1. Hero Section

    hero_eyebrow = models.CharField(max_length=150, default="Connecting Talent · Creating Futures", blank=True)

    hero_title = models.CharField(max_length=255, default="Recruitment &amp; Placement, <em>done the right way.</em>")

    hero_subtitle = models.TextField(

        default="We help businesses build high-performing teams and help job seekers find the right opportunities — with a process built for speed, fit and follow-through.",

        blank=True

    )

    hero_hire_btn_text = models.CharField(max_length=100, default="Hire Talent", blank=True)

    hero_hire_btn_url = models.CharField(max_length=255, default="/employer/hire-talent/", blank=True)

    hero_jobs_btn_text = models.CharField(max_length=100, default="Find Jobs", blank=True)

    hero_jobs_btn_url = models.CharField(max_length=255, default="/jobs/", blank=True)

    # 4 Hero stat counters

    hero_stat1_value = models.CharField(max_length=50, default="10K+", blank=True)

    hero_stat1_label = models.CharField(max_length=100, default="Active Candidates", blank=True)

    hero_stat2_value = models.CharField(max_length=50, default="500+", blank=True)

    hero_stat2_label = models.CharField(max_length=100, default="Happy Clients", blank=True)

    hero_stat3_value = models.CharField(max_length=50, default="25K+", blank=True)

    hero_stat3_label = models.CharField(max_length=100, default="Successful Placements", blank=True)

    hero_stat4_value = models.CharField(max_length=50, default="15+", blank=True)

    hero_stat4_label = models.CharField(max_length=100, default="Industries Served", blank=True)



    # 2. About Section

    about_tag = models.CharField(max_length=150, default="About Us", blank=True)

    about_title = models.CharField(max_length=255, default="Sky Vision Group Consultancy")

    about_desc1 = models.TextField(

        default="Sky Vision Group Consultancy is a trusted recruitment and placement partner for businesses across India and abroad. With over a decade of experience, we specialize in delivering end-to-end hiring solutions tailored to diverse industry needs.",

        blank=True

    )

    about_desc2 = models.TextField(

        default="Our mission is to connect the right talent with the right opportunities and drive growth for both businesses and individuals.",

        blank=True

    )

    about_exp_years = models.CharField(max_length=50, default="12+", blank=True)

    about_exp_label = models.CharField(max_length=100, default="Years of<br>Experience", blank=True)

    about_feat1_text = models.CharField(max_length=150, default="Expert HR Team", blank=True)

    about_feat1_icon = models.CharField(max_length=100, default="fa-solid fa-user-tie", blank=True)

    about_feat2_text = models.CharField(max_length=150, default="Client-Centric Approach", blank=True)

    about_feat2_icon = models.CharField(max_length=100, default="fa-solid fa-handshake", blank=True)

    about_feat3_text = models.CharField(max_length=150, default="Ethical & Transparent", blank=True)

    about_feat3_icon = models.CharField(max_length=100, default="fa-solid fa-shield-halved", blank=True)

    about_feat4_text = models.CharField(max_length=150, default="Pan India Presence", blank=True)

    about_feat4_icon = models.CharField(max_length=100, default="fa-solid fa-map-location-dot", blank=True)



    # 3. Why Partner Card (Inside About Grid)

    why_partner_title = models.CharField(max_length=150, default="Why Partner With Us?", blank=True)

    why_partner_learn_btn_text = models.CharField(max_length=100, default="Learn More About Us", blank=True)

    why_partner_learn_btn_url = models.CharField(max_length=255, default="/about/journey/", blank=True)



    # 4. Services Grid Section Header

    services_tag = models.CharField(max_length=150, default="What We Do", blank=True)

    services_title = models.CharField(max_length=255, default="Our Recruitment Services")

    services_subtitle = models.TextField(

        default="Purpose-built hiring solutions for every stage of your team's growth.",

        blank=True

    )



    # 5. Process Section

    process_tag = models.CharField(max_length=150, default="Our Process", blank=True)

    process_title = models.CharField(max_length=255, default="From requirement to joining, in six steps")

    process_subtitle = models.TextField(

        default="A structured pipeline we follow for every mandate — nothing skipped, nothing rushed.",

        blank=True

    )



    # 6. Insights Grid - Card Titles & Achievements & Testimonial

    why_choose_title = models.CharField(max_length=150, default="Why Choose Us?", blank=True)

    achievements_title = models.CharField(max_length=150, default="Our Achievements", blank=True)

    achieve1_value = models.CharField(max_length=50, default="10,000+", blank=True)

    achieve1_label = models.CharField(max_length=100, default="Candidates Deployed", blank=True)

    achieve1_icon = models.CharField(max_length=100, default="fa-solid fa-user-group", blank=True)

    achieve1_color = models.CharField(max_length=50, default="blue", blank=True)

    achieve2_value = models.CharField(max_length=50, default="500+", blank=True)

    achieve2_label = models.CharField(max_length=100, default="Happy Clients", blank=True)

    achieve2_icon = models.CharField(max_length=100, default="fa-solid fa-building", blank=True)

    achieve2_color = models.CharField(max_length=50, default="amber", blank=True)

    achieve3_value = models.CharField(max_length=50, default="25,000+", blank=True)

    achieve3_label = models.CharField(max_length=100, default="Successful Recruitments", blank=True)

    achieve3_icon = models.CharField(max_length=100, default="fa-solid fa-award", blank=True)

    achieve3_color = models.CharField(max_length=50, default="green", blank=True)

    achieve4_value = models.CharField(max_length=50, default="15+", blank=True)

    achieve4_label = models.CharField(max_length=100, default="Industries Presence", blank=True)

    achieve4_icon = models.CharField(max_length=100, default="fa-solid fa-chart-column", blank=True)

    achieve4_color = models.CharField(max_length=50, default="purple", blank=True)



    industries_title = models.CharField(max_length=150, default="Industries We Serve", blank=True)



    testimonial_title = models.CharField(max_length=150, default="What Our Clients Say", blank=True)

    testimonial_quote = models.TextField(

        default="Sky Vision Group Consultancy has been a valuable partner in our growth. Their professional approach and quality candidates have helped us achieve our hiring goals consistently.",

        blank=True

    )

    testimonial_author = models.CharField(max_length=150, default="Rahul Sharma", blank=True)

    testimonial_role = models.CharField(max_length=200, default="HR Manager, Tech Solutions Pvt. Ltd.", blank=True)

    testimonial_avatar = models.CharField(max_length=10, default="RS", blank=True)



    # 7. Partners Section

    partners_title = models.CharField(max_length=150, default="Our Trusted Partners", blank=True)



    # 8. FAQ Section

    faq_tag = models.CharField(max_length=150, default="Questions", blank=True)

    faq_title = models.CharField(max_length=255, default="Frequently Asked Questions")



    # 9. Bottom CTA Section

    cta_title = models.CharField(max_length=255, default="Ready to hire the best talent?")

    cta_subtitle = models.TextField(

        default="Let us help you build a stronger team for a better tomorrow.",

        blank=True

    )

    cta_btn_text = models.CharField(max_length=100, default="Contact Us Today", blank=True)

    cta_btn_url = models.CharField(max_length=255, default="/contact/", blank=True)



    # 10. SEO & Meta

    meta_title = models.CharField(max_length=255, default="Recruitment & Placement Services — Sky Vision Group Consultancy", blank=True)

    meta_description = models.TextField(

        default="Leading recruitment, permanent placement, and executive staffing firm across India. We connect qualified talent with top employers.",

        blank=True

    )

    og_image = models.ImageField(upload_to=scramble_upload_path, blank=True, null=True)



    updated_at = models.DateTimeField(auto_now=True)



    class Meta:

        db_table = 'recruitment_placement_settings'

        verbose_name = "Recruitment & Placement Settings"

        verbose_name_plural = "Recruitment & Placement Settings"



    @classmethod

    def get_settings(cls):

        obj, _ = cls.objects.get_or_create(id=1)

        return obj



    def __str__(self):

        return "Recruitment & Placement Page Settings"



    @property

    def hero_title_plain(self):

        clean = re.sub(r'<[^>]+>', '', self.hero_title or '')

        clean = clean.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')

        return re.sub(r'\s+', ' ', clean).strip()



    @property

    def formatted_hero_title(self):

        raw = (self.hero_title or '').strip()

        if '<em>' in raw or '<span' in raw:

            return raw

        clean = self.hero_title_plain

        if not clean:

            return 'Recruitment &amp; Placement, <em>done the right way.</em>'

        if ',' in clean:

            parts = clean.split(',', 1)

            first = parts[0].strip().replace('&', '&amp;')

            second = parts[1].strip()

            return f"{first}, <em>{second}</em>"

        words = clean.split()

        if len(words) >= 3:

            return f"{' '.join(words[:-3])} <em>{' '.join(words[-3:])}</em>"

        return clean



    @property

    def about_exp_label_plain(self):

        clean = re.sub(r'<[^>]+>', ' ', self.about_exp_label or '')

        return re.sub(r'\s+', ' ', clean).strip()



    @property

    def formatted_about_exp_label(self):

        raw = (self.about_exp_label or '').strip()

        if '<br>' in raw:

            return raw

        clean = self.about_exp_label_plain

        if not clean:

            return 'Years of<br>Experience'

        words = clean.split()

        if len(words) == 3 and words[0].lower() == 'years' and words[1].lower() == 'of':

            return f"Years of<br>{words[2]}"

        if len(words) >= 2:

            return f"{' '.join(words[:-1])}<br>{words[-1]}"

        return clean





class RpWhyPartnerItem(models.Model):

    text = models.CharField(max_length=150)

    icon_class = models.CharField(max_length=100, default="fa-solid fa-check")

    order = models.PositiveIntegerField(default=0)

    is_visible = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    updated_at = models.DateTimeField(auto_now=True)



    class Meta:

        db_table = 'rp_why_partner_items'

        ordering = ['order', 'id']

        verbose_name = "RP Why Partner Item"

        verbose_name_plural = "RP Why Partner Items"



    def __str__(self):

        return self.text





class RpServiceCard(models.Model):

    title = models.CharField(max_length=150)

    description = models.TextField()

    icon_class = models.CharField(max_length=100, default="fa-solid fa-user")

    color_class = models.CharField(max_length=50, default="i-blue")  # i-blue, i-amber, i-green, i-purple, i-teal, i-pink

    order = models.PositiveIntegerField(default=0)

    is_visible = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    updated_at = models.DateTimeField(auto_now=True)



    class Meta:

        db_table = 'rp_service_cards'

        ordering = ['order', 'id']

        verbose_name = "RP Service Card"

        verbose_name_plural = "RP Service Cards"



    def __str__(self):

        return self.title





class RpProcessStep(models.Model):

    step_number = models.CharField(max_length=10, default="01")

    title = models.CharField(max_length=150)

    icon_class = models.CharField(max_length=100, default="fa-solid fa-clipboard-list")

    order = models.PositiveIntegerField(default=0)

    is_visible = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    updated_at = models.DateTimeField(auto_now=True)



    class Meta:

        db_table = 'rp_process_steps'

        ordering = ['order', 'id']

        verbose_name = "RP Process Step"

        verbose_name_plural = "RP Process Steps"



    def __str__(self):

        return f"{self.step_number} - {self.title}"





class RpWhyChooseItem(models.Model):

    text = models.CharField(max_length=150)

    icon_class = models.CharField(max_length=100, default="fa-solid fa-circle-check")

    order = models.PositiveIntegerField(default=0)

    is_visible = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    updated_at = models.DateTimeField(auto_now=True)



    class Meta:

        db_table = 'rp_why_choose_items'

        ordering = ['order', 'id']

        verbose_name = "RP Why Choose Item"

        verbose_name_plural = "RP Why Choose Items"



    def __str__(self):

        return self.text





class RpIndustryItem(models.Model):

    name = models.CharField(max_length=100)

    icon_class = models.CharField(max_length=100, default="fa-solid fa-desktop")

    order = models.PositiveIntegerField(default=0)

    is_visible = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    updated_at = models.DateTimeField(auto_now=True)



    class Meta:

        db_table = 'rp_industry_items'

        ordering = ['order', 'id']

        verbose_name = "RP Industry Item"

        verbose_name_plural = "RP Industry Items"



    def __str__(self):

        return self.name





class RpPartnerItem(models.Model):

    name = models.CharField(max_length=100)

    order = models.PositiveIntegerField(default=0)

    is_visible = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    updated_at = models.DateTimeField(auto_now=True)



    class Meta:

        db_table = 'rp_partner_items'

        ordering = ['order', 'id']

        verbose_name = "RP Partner Item"

        verbose_name_plural = "RP Partner Items"



    def __str__(self):

        return self.name





class RpFaqItem(models.Model):

    question = models.CharField(max_length=255)

    answer = models.TextField()

    order = models.PositiveIntegerField(default=0)

    is_visible = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    updated_at = models.DateTimeField(auto_now=True)



    class Meta:

        db_table = 'rp_faq_items'

        ordering = ['order', 'id']

        verbose_name = "RP FAQ Item"

        verbose_name_plural = "RP FAQ Items"



    def __str__(self):

        return self.question





@receiver([post_save, post_delete], sender=RecruitmentPlacementSettings)

@receiver([post_save, post_delete], sender=RpWhyPartnerItem)

@receiver([post_save, post_delete], sender=RpServiceCard)

@receiver([post_save, post_delete], sender=RpProcessStep)

@receiver([post_save, post_delete], sender=RpWhyChooseItem)

@receiver([post_save, post_delete], sender=RpIndustryItem)

@receiver([post_save, post_delete], sender=RpPartnerItem)

@receiver([post_save, post_delete], sender=RpFaqItem)

def invalidate_recruitment_placement_cache(sender, **kwargs):

    cache.delete(RECRUITMENT_PLACEMENT_CACHE_KEY)









# ==============================================================================

# CONTRACT STAFFING SERVICE DYNAMIC MODELS

# ==============================================================================

CONTRACT_STAFFING_CACHE_KEY = 'contract_staffing_context'





class ContractStaffingSettings(models.Model):

    # Master Visibility Switches

    hero_visible = models.BooleanField(default=True)

    about_visible = models.BooleanField(default=True)

    services_visible = models.BooleanField(default=True)

    industries_why_visible = models.BooleanField(default=True)

    process_visible = models.BooleanField(default=True)

    benefits_visible = models.BooleanField(default=True)

    faq_visible = models.BooleanField(default=True)

    cta_visible = models.BooleanField(default=True)



    # 1. Hero Section

    hero_eyebrow = models.CharField(max_length=150, default="Contract Staffing Services", blank=True)

    hero_eyebrow_icon = models.CharField(max_length=100, default="fa-solid fa-people-group", blank=True)

    hero_title = models.CharField(max_length=255, default="Flexible Workforce.<br><em>Stronger Business.</em>")

    hero_subtitle = models.TextField(default="We provide skilled, semi-skilled, and unskilled manpower on contract to help your business stay agile, productive, and cost-effective.")

    hero_req_btn_text = models.CharField(max_length=100, default="Request Manpower", blank=True)

    hero_req_btn_url = models.CharField(max_length=255, default="#contact", blank=True)

    hero_contact_btn_text = models.CharField(max_length=100, default="Contact Us", blank=True)

    hero_contact_btn_url = models.CharField(max_length=255, default="/contact/", blank=True)

    hero_image = models.ImageField(upload_to="services/contract_staffing/hero/", blank=True, null=True)



    # 2. About Section + 3 Stat Rows

    about_tag = models.CharField(max_length=150, default="About Contract Staffing", blank=True)

    about_title = models.CharField(max_length=255, default="Flexible Workforce Solutions for Every Business")

    about_description = models.TextField(default="At Sky Vision Group Consultancy, we provide reliable contract staffing services that enable organizations to hire qualified professionals without long-term employment commitments. Whether you require manpower for a short-term project, seasonal demand, or ongoing operations, our staffing experts ensure fast deployment of skilled candidates.")

    

    about_stat1_value = models.CharField(max_length=50, default="10,000+", blank=True)

    about_stat1_label = models.CharField(max_length=100, default="Candidates Deployed", blank=True)

    about_stat1_icon = models.CharField(max_length=100, default="fa-solid fa-user-group", blank=True)



    about_stat2_value = models.CharField(max_length=50, default="500+", blank=True)

    about_stat2_label = models.CharField(max_length=100, default="Clients Served", blank=True)

    about_stat2_icon = models.CharField(max_length=100, default="fa-solid fa-building", blank=True)



    about_stat3_value = models.CharField(max_length=50, default="15+", blank=True)

    about_stat3_label = models.CharField(max_length=100, default="Years of Experience", blank=True)

    about_stat3_icon = models.CharField(max_length=100, default="fa-solid fa-award", blank=True)



    # 3. Services Grid Header

    services_tag = models.CharField(max_length=150, default="Our Contract Staffing Services", blank=True)



    # 4. Industries & Why Choose Section Headers & Visual

    industries_tag = models.CharField(max_length=150, default="Industries We Serve", blank=True)

    center_image = models.ImageField(upload_to="services/contract_staffing/", blank=True, null=True)

    why_choose_tag = models.CharField(max_length=150, default="Why Choose Sky Vision Group Consultancy?", blank=True)



    # 5. Process Section

    process_tag = models.CharField(max_length=150, default="Our Staffing Process", blank=True)

    process_title = models.CharField(max_length=255, default="A Clear Path From Requirement to Deployment")

    process_subtitle = models.CharField(max_length=255, default="Every engagement follows the same disciplined six-step pipeline.", blank=True)



    # 6. Benefits & FAQs Section Headers

    benefits_tag = models.CharField(max_length=150, default="Our Benefits", blank=True)

    benefits_employer_title = models.CharField(max_length=150, default="For Employers", blank=True)

    benefits_candidate_title = models.CharField(max_length=150, default="For Candidates", blank=True)

    faq_tag = models.CharField(max_length=150, default="Frequently Asked Questions", blank=True)



    # 7. Bottom CTA Banner

    cta_tag = models.CharField(max_length=150, default="Looking for Reliable Contract Staffing?", blank=True)

    cta_title = models.CharField(max_length=255, default="Partner with Sky Vision Group Consultancy")

    cta_subtitle = models.TextField(default="for efficient, compliant, and cost-effective workforce solutions tailored to your business needs.")

    cta_btn1_text = models.CharField(max_length=100, default="Get Free Consultation", blank=True)

    cta_btn1_url = models.CharField(max_length=255, default="/contact/", blank=True)

    cta_btn2_text = models.CharField(max_length=100, default="Contact Our Team", blank=True)

    cta_btn2_url = models.CharField(max_length=255, default="/contact/", blank=True)



    # 8. SEO & Social Meta

    meta_title = models.CharField(max_length=255, default="Contract Staffing · Sky Vision Group Consultancy", blank=True)

    meta_description = models.TextField(default="Flexible and agile contract staffing models for short-term and project-based demands across India.", blank=True)

    og_image = models.ImageField(upload_to="services/contract_staffing/seo/", blank=True, null=True)



    updated_at = models.DateTimeField(auto_now=True)



    class Meta:

        db_table = 'contract_staffing_settings'

        verbose_name = "Contract Staffing Settings"

        verbose_name_plural = "Contract Staffing Settings"



    def __str__(self):

        return "Contract Staffing Page Settings"



    @classmethod

    def get_settings(cls):

        obj, created = cls.objects.get_or_create(pk=1)

        return obj



    @property

    def get_hero_image(self):

        if self.hero_image and hasattr(self.hero_image, 'url'):

            return self.hero_image.url

        return "/static/images/services/manpower-supply 2.png"



    @property

    def get_center_image(self):

        if self.center_image and hasattr(self.center_image, 'url'):

            return self.center_image.url

        return "/static/images/general/team activities.png"



    @property

    def hero_title_plain(self):

        clean = re.sub(r'<[^>]+>', ' ', self.hero_title or '')

        clean = clean.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')

        return re.sub(r'\s+', ' ', clean).strip()



    @property

    def formatted_hero_title(self):

        raw = (self.hero_title or '').strip()

        if '<br>' in raw or '<em>' in raw:

            return raw

        clean = self.hero_title_plain

        if not clean:

            return 'Flexible Workforce.<br><em>Stronger Business.</em>'

        if '.' in clean:

            parts = clean.split('.', 1)

            first = parts[0].strip()

            second = parts[1].strip()

            if second:

                return f"{first}.<br><em>{second}</em>"

            return f"{first}."

        words = clean.split()

        if len(words) >= 2:

            return f"{' '.join(words[:-1])}<br><em>{words[-1]}</em>"

        return f"<em>{clean}</em>"





class CsServiceCard(models.Model):

    title = models.CharField(max_length=200)

    description = models.TextField(blank=True)

    icon_class = models.CharField(max_length=100, default="fa-regular fa-clock")

    order = models.PositiveIntegerField(default=0)

    is_visible = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    updated_at = models.DateTimeField(auto_now=True)



    class Meta:

        db_table = 'cs_service_cards'

        ordering = ['order', 'id']

        verbose_name = "CS Service Card"

        verbose_name_plural = "CS Service Cards"



    def __str__(self):

        return self.title





class CsIndustryItem(models.Model):

    name = models.CharField(max_length=150)

    icon_class = models.CharField(max_length=100, default="fa-solid fa-industry")

    order = models.PositiveIntegerField(default=0)

    is_visible = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    updated_at = models.DateTimeField(auto_now=True)



    class Meta:

        db_table = 'cs_industry_items'

        ordering = ['order', 'id']

        verbose_name = "CS Industry Item"

        verbose_name_plural = "CS Industry Items"



    def __str__(self):

        return self.name





class CsWhyChooseItem(models.Model):

    text = models.CharField(max_length=255)

    icon_class = models.CharField(max_length=100, default="fa-solid fa-circle-check")

    order = models.PositiveIntegerField(default=0)

    is_visible = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    updated_at = models.DateTimeField(auto_now=True)



    class Meta:

        db_table = 'cs_why_choose_items'

        ordering = ['order', 'id']

        verbose_name = "CS Why Choose Item"

        verbose_name_plural = "CS Why Choose Items"



    def __str__(self):

        return self.text





class CsProcessStep(models.Model):

    step_number = models.CharField(max_length=20, default="01")

    title = models.CharField(max_length=200)

    description = models.CharField(max_length=255, blank=True)

    icon_class = models.CharField(max_length=100, default="fa-solid fa-comments")

    order = models.PositiveIntegerField(default=0)

    is_visible = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    updated_at = models.DateTimeField(auto_now=True)



    class Meta:

        db_table = 'cs_process_steps'

        ordering = ['order', 'id']

        verbose_name = "CS Process Step"

        verbose_name_plural = "CS Process Steps"



    def __str__(self):

        return f"{self.step_number} - {self.title}"





class CsBenefitEmployerItem(models.Model):

    text = models.CharField(max_length=255)

    icon_class = models.CharField(max_length=100, default="fa-solid fa-circle-check")

    order = models.PositiveIntegerField(default=0)

    is_visible = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    updated_at = models.DateTimeField(auto_now=True)



    class Meta:

        db_table = 'cs_benefit_employer_items'

        ordering = ['order', 'id']

        verbose_name = "CS Benefit Employer Item"

        verbose_name_plural = "CS Benefit Employer Items"



    def __str__(self):

        return self.text





class CsBenefitCandidateItem(models.Model):

    text = models.CharField(max_length=255)

    icon_class = models.CharField(max_length=100, default="fa-solid fa-circle-check")

    order = models.PositiveIntegerField(default=0)

    is_visible = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    updated_at = models.DateTimeField(auto_now=True)



    class Meta:

        db_table = 'cs_benefit_candidate_items'

        ordering = ['order', 'id']

        verbose_name = "CS Benefit Candidate Item"

        verbose_name_plural = "CS Benefit Candidate Items"



    def __str__(self):

        return self.text





class CsFaqItem(models.Model):

    question = models.CharField(max_length=255)

    answer = models.TextField()

    order = models.PositiveIntegerField(default=0)

    is_visible = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    updated_at = models.DateTimeField(auto_now=True)



    class Meta:

        db_table = 'cs_faq_items'

        ordering = ['order', 'id']

        verbose_name = "CS FAQ Item"

        verbose_name_plural = "CS FAQ Items"



    def __str__(self):

        return self.question





@receiver([post_save, post_delete], sender=ContractStaffingSettings)

@receiver([post_save, post_delete], sender=CsServiceCard)

@receiver([post_save, post_delete], sender=CsIndustryItem)

@receiver([post_save, post_delete], sender=CsWhyChooseItem)

@receiver([post_save, post_delete], sender=CsProcessStep)

@receiver([post_save, post_delete], sender=CsBenefitEmployerItem)

@receiver([post_save, post_delete], sender=CsBenefitCandidateItem)

@receiver([post_save, post_delete], sender=CsFaqItem)

def invalidate_contract_staffing_cache(sender, **kwargs):

    cache.delete(CONTRACT_STAFFING_CACHE_KEY)





# ==============================================================================

# EDUCATIONAL CONSULTANCY SERVICE PAGE MODELS

# ==============================================================================



EDUCATIONAL_CONSULTANCY_CACHE_KEY = 'educational_consultancy_context'





class EducationalConsultancySettings(models.Model):

    # Master Visibility Switches

    hero_visible = models.BooleanField(default=True)

    services_visible = models.BooleanField(default=True)

    why_choose_visible = models.BooleanField(default=True)

    process_visible = models.BooleanField(default=True)

    stats_visible = models.BooleanField(default=True)

    cta_visible = models.BooleanField(default=True)



    # 1. Hero Section

    hero_eyebrow = models.CharField(max_length=150, default="Guiding Futures, One Student at a Time", blank=True)

    hero_title = models.CharField(max_length=255, default="Educational Consultancy <em>Services</em>")

    hero_subhead = models.CharField(max_length=255, default="Build Your Future with Expert Educational Guidance", blank=True)

    hero_subtitle = models.TextField(default="We help students achieve their academic and career goals with the right guidance, admission support, and skill development programs.")

    hero_counsel_btn_text = models.CharField(max_length=100, default="Get Free Counselling", blank=True)

    hero_counsel_btn_url = models.CharField(max_length=255, default="#contact", blank=True)

    hero_contact_btn_text = models.CharField(max_length=100, default="Contact Us", blank=True)

    hero_contact_btn_url = models.CharField(max_length=255, default="/contact/", blank=True)

    hero_image = models.ImageField(upload_to="services/educational_consultancy/hero/", blank=True, null=True)



    # 2. Services Section

    services_tag = models.CharField(max_length=100, default="Our Educational Consultancy", blank=True)

    services_title = models.CharField(max_length=255, default='Our Educational Consultancy <span class="ec-accent">Services</span>')



    # 3. Why Choose Section

    why_choose_title = models.CharField(max_length=255, default='Why Choose <span class="ec-accent">Sky Vision?</span>')

    why_choose_image = models.ImageField(upload_to="services/educational_consultancy/why/", blank=True, null=True)



    # 4. Our Process

    process_tag = models.CharField(max_length=100, default="How We Work", blank=True)

    process_title = models.CharField(max_length=255, default='Our <span class="ec-accent">Process</span>')



    # 5. Stats Bar

    stat1_value = models.CharField(max_length=50, default="5000+")

    stat1_label = models.CharField(max_length=100, default="Students Guided")

    stat1_icon = models.CharField(max_length=100, default="fa-solid fa-graduation-cap")

    stat2_value = models.CharField(max_length=50, default="200+")

    stat2_label = models.CharField(max_length=100, default="Colleges & Universities")

    stat2_icon = models.CharField(max_length=100, default="fa-solid fa-building-columns")

    stat3_value = models.CharField(max_length=50, default="15+")

    stat3_label = models.CharField(max_length=100, default="Countries Partners")

    stat3_icon = models.CharField(max_length=100, default="fa-solid fa-globe")

    stat4_value = models.CharField(max_length=50, default="98%")

    stat4_label = models.CharField(max_length=100, default="Student Satisfaction")

    stat4_icon = models.CharField(max_length=100, default="fa-solid fa-shield-halved")



    # 6. Bottom CTA & SEO

    cta_title = models.CharField(max_length=255, default="Start Your Educational Journey Today!")

    cta_subtitle = models.TextField(default="Let our experts help you achieve your academic and career dreams.")

    cta_btn_text = models.CharField(max_length=100, default="Book Free Consultation", blank=True)

    cta_btn_url = models.CharField(max_length=255, default="/contact/", blank=True)

    cta_btn2_text = models.CharField(max_length=100, default="Apply Now", blank=True)

    cta_btn2_url = models.CharField(max_length=255, default="/contact/", blank=True)



    meta_title = models.CharField(max_length=255, default="Educational Consultancy — Sky Vision Group Consultancy", blank=True)

    meta_description = models.TextField(default="Guiding Futures, One Student at a Time. Build Your Future with Expert Educational Guidance from Sky Vision Group Consultancy.", blank=True)

    meta_keywords = models.CharField(max_length=255, default="Educational Consultancy, Student Counselling, College Admissions, Career Guidance, Study Abroad, Lucknow", blank=True)



    updated_at = models.DateTimeField(auto_now=True)



    class Meta:

        db_table = 'educational_consultancy_settings'

        verbose_name = "Educational Consultancy Settings"

        verbose_name_plural = "Educational Consultancy Settings"



    def __str__(self):

        return "Educational Consultancy Page Settings"



    @classmethod

    def get_settings(cls):

        obj, _ = cls.objects.get_or_create(id=1)

        return obj



    @property

    def get_hero_image(self):

        if self.hero_image and hasattr(self.hero_image, 'url'):

            return self.hero_image.url

        return "/static/images/services/educational consultancy.png"



    @property

    def get_why_image(self):

        if self.why_choose_image and hasattr(self.why_choose_image, 'url'):

            return self.why_choose_image.url

        return "/static/images/services/educational consultancy 1.png"



    @property

    def hero_title_plain(self):

        clean = re.sub(r'<[^>]+>', '', self.hero_title or '')

        clean = clean.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')

        return re.sub(r'\s+', ' ', clean).strip()



    @property

    def formatted_hero_title(self):

        raw = (self.hero_title or '').strip()

        if '<em>' in raw or '<span' in raw:

            return raw

        clean = self.hero_title_plain

        if not clean:

            return 'Educational Consultancy <em>Services</em>'

        words = clean.split()

        if len(words) >= 2:

            return f"{' '.join(words[:-1])} <em>{words[-1]}</em>"

        return f"<em>{clean}</em>"



    @property

    def services_title_plain(self):

        clean = re.sub(r'<[^>]+>', '', self.services_title or '')

        clean = clean.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')

        return re.sub(r'\s+', ' ', clean).strip()



    @property

    def formatted_services_title(self):

        raw = (self.services_title or '').strip()

        if '<span' in raw or '<em>' in raw:

            return raw

        clean = self.services_title_plain

        if not clean:

            return 'Our Educational Consultancy <span class="ec-accent">Services</span>'

        words = clean.split()

        if len(words) >= 2:

            return f"{' '.join(words[:-1])} <span class='ec-accent'>{words[-1]}</span>"

        return f"<span class='ec-accent'>{clean}</span>"



    @property

    def why_choose_title_plain(self):

        clean = re.sub(r'<[^>]+>', '', self.why_choose_title or '')

        clean = clean.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')

        return re.sub(r'\s+', ' ', clean).strip()



    @property

    def formatted_why_choose_title(self):

        raw = (self.why_choose_title or '').strip()

        if '<span' in raw or '<em>' in raw:

            return raw

        clean = self.why_choose_title_plain

        if not clean:

            return 'Why Choose <span class="ec-accent">Sky Vision?</span>'

        if 'Sky Vision' in clean:

            idx = clean.find('Sky Vision')

            prefix = clean[:idx].strip()

            accent = clean[idx:].strip()

            return f"{prefix} <span class='ec-accent'>{accent}</span>"

        words = clean.split()

        if len(words) >= 2:

            return f"{' '.join(words[:-1])} <span class='ec-accent'>{words[-1]}</span>"

        return clean



    @property

    def process_title_plain(self):

        clean = re.sub(r'<[^>]+>', '', self.process_title or '')

        clean = clean.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')

        return re.sub(r'\s+', ' ', clean).strip()



    @property

    def formatted_process_title(self):

        raw = (self.process_title or '').strip()

        if '<span' in raw or '<em>' in raw:

            return raw

        clean = self.process_title_plain

        if not clean:

            return 'Our <span class="ec-accent">Process</span>'

        words = clean.split()

        if len(words) >= 2:

            return f"{' '.join(words[:-1])} <span class='ec-accent'>{words[-1]}</span>"

        return f"<span class='ec-accent'>{clean}</span>"





class EcServiceCard(models.Model):

    title = models.CharField(max_length=200)

    description = models.TextField()

    icon_class = models.CharField(max_length=100, default="fa-solid fa-graduation-cap")

    badge_theme = models.CharField(max_length=50, default="navy")

    order = models.PositiveIntegerField(default=0)

    is_visible = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    updated_at = models.DateTimeField(auto_now=True)



    class Meta:

        db_table = 'ec_service_cards'

        ordering = ['order', 'id']

        verbose_name = "EC Service Card"

        verbose_name_plural = "EC Service Cards"



    def __str__(self):

        return self.title





class EcWhyChooseItem(models.Model):

    title = models.CharField(max_length=200)

    description = models.TextField()

    icon_class = models.CharField(max_length=100, default="fa-solid fa-user-graduate")

    order = models.PositiveIntegerField(default=0)

    is_visible = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    updated_at = models.DateTimeField(auto_now=True)



    class Meta:

        db_table = 'ec_why_choose_items'

        ordering = ['order', 'id']

        verbose_name = "EC Why Choose Item"

        verbose_name_plural = "EC Why Choose Items"



    def __str__(self):

        return self.title





class EcProcessStep(models.Model):

    step_number = models.CharField(max_length=20, default="01")

    title = models.CharField(max_length=200)

    description = models.TextField()

    icon_class = models.CharField(max_length=100, default="fa-solid fa-comment-dots")

    order = models.PositiveIntegerField(default=0)

    is_visible = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    updated_at = models.DateTimeField(auto_now=True)



    class Meta:

        db_table = 'ec_process_steps'

        ordering = ['order', 'id']

        verbose_name = "EC Process Step"

        verbose_name_plural = "EC Process Steps"



    def __str__(self):

        return f"{self.step_number} - {self.title}"





@receiver([post_save, post_delete], sender=EducationalConsultancySettings)

@receiver([post_save, post_delete], sender=EcServiceCard)

@receiver([post_save, post_delete], sender=EcWhyChooseItem)

@receiver([post_save, post_delete], sender=EcProcessStep)

def invalidate_educational_consultancy_cache(sender, **kwargs):

    cache.delete(EDUCATIONAL_CONSULTANCY_CACHE_KEY)





# =============================================================================

# 11. PAYROLL & OUTSOURCING SERVICE SETTINGS & REPEATERS

# =============================================================================

PAYROLL_OUTSOURCING_CACHE_KEY = 'payroll_outsourcing_page_context'



class PayrollOutsourcingSettings(models.Model):

    # Master Visibility Switches

    hero_visible = models.BooleanField(default=True)

    about_visible = models.BooleanField(default=True)

    services_visible = models.BooleanField(default=True)

    panel_visible = models.BooleanField(default=True)

    compare_visible = models.BooleanField(default=True)

    faq_visible = models.BooleanField(default=True)

    cta_visible = models.BooleanField(default=True)



    # 1. Hero Section

    hero_eyebrow = models.CharField(max_length=150, default="Payroll & Outsourcing", blank=True)

    hero_title = models.CharField(max_length=255, default="Payroll & Outsourcing Services")

    hero_subtitle = models.TextField(default="Streamline your payroll operations, ensure compliance, and manage your workforce efficiently with our expert payroll & outsourcing solutions.")

    hero_primary_btn_text = models.CharField(max_length=100, default="Get Free Consultation", blank=True)

    hero_primary_btn_url = models.CharField(max_length=255, default="#contact", blank=True)

    hero_secondary_btn_text = models.CharField(max_length=100, default="Contact Us", blank=True)

    hero_secondary_btn_url = models.CharField(max_length=255, default="/contact/", blank=True)

    hero_image = models.ImageField(upload_to="services/payroll_outsourcing/hero/", blank=True, null=True)



    # 2. About Section

    about_tag = models.CharField(max_length=100, default="About Our Services", blank=True)

    about_title = models.CharField(max_length=255, default="Complete Payroll & HR Outsourcing Solutions")

    about_description = models.TextField(default="We provide end-to-end payroll and outsourcing services that help businesses reduce operational burden, ensure accuracy, and stay 100% compliant with statutory regulations.")

    about_image = models.ImageField(upload_to="services/payroll_outsourcing/about/", blank=True, null=True)



    # 3. Services Grid Section

    services_title = models.CharField(max_length=255, default="Our Payroll & Outsourcing Services")



    # 4. Triple Panel Section (Industries / Why Choose / Process)

    industries_tag = models.CharField(max_length=100, default="Industries We Serve", blank=True)

    why_choose_tag = models.CharField(max_length=100, default="Why Choose Us?", blank=True)

    process_tag = models.CharField(max_length=100, default="Our Payroll Process", blank=True)



    # 5. Employers vs Employees Comparison Section

    employers_badge = models.CharField(max_length=100, default="For Employers", blank=True)

    employees_badge = models.CharField(max_length=100, default="For Employees", blank=True)



    # 6. FAQ Section

    faq_title = models.CharField(max_length=255, default="Frequently Asked Questions")



    # 7. Bottom CTA & SEO

    cta_title = models.CharField(max_length=255, default="Focus On Growing Your Business We'll Handle Your Payroll!")

    cta_subtitle = models.TextField(default="Partner with us for secure, compliant and hassle-free payroll & outsourcing services.")

    cta_primary_btn_text = models.CharField(max_length=100, default="Get Free Consultation", blank=True)

    cta_primary_btn_url = models.CharField(max_length=255, default="#contact", blank=True)

    cta_secondary_btn_text = models.CharField(max_length=100, default="Contact Our Team", blank=True)

    cta_secondary_btn_url = models.CharField(max_length=255, default="/contact/", blank=True)



    meta_title = models.CharField(max_length=255, default="Payroll & Outsourcing Services — Sky Vision Group Consultancy", blank=True)

    meta_description = models.TextField(default="Streamline your payroll operations, ensure compliance, and manage your workforce efficiently with our expert payroll & outsourcing solutions.", blank=True)

    meta_keywords = models.CharField(max_length=255, default="payroll outsourcing, payroll processing, statutory compliance, PF ESI management, HR outsourcing", blank=True)



    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    updated_at = models.DateTimeField(auto_now=True)



    class Meta:

        db_table = 'payroll_outsourcing_settings'

        verbose_name = "Payroll & Outsourcing Settings"

        verbose_name_plural = "Payroll & Outsourcing Settings"



    def __str__(self):

        return "Payroll & Outsourcing Settings"



    @classmethod

    def get_settings(cls):

        obj = cls.objects.first()

        if not obj:

            obj = cls.objects.create()

        return obj



    @property

    def hero_title_plain(self):

        clean = re.sub(r'<[^>]+>', '', self.hero_title or '')

        return re.sub(r'\s+', ' ', clean).strip()



    @property

    def formatted_hero_title(self):

        plain = self.hero_title_plain

        if not plain:

            return mark_safe("Payroll & Outsourcing <em>Services</em>")

        parts = plain.rsplit(' ', 1)

        if len(parts) == 2:

            return mark_safe(f"{parts[0]} <em>{parts[1]}</em>")

        return mark_safe(f"<em>{plain}</em>")



    @property

    def cta_title_plain(self):

        clean = re.sub(r'<[^>]+>', '', self.cta_title or '')

        return re.sub(r'\s+', ' ', clean).strip()



    @property

    def formatted_cta_title(self):

        plain = self.cta_title_plain

        if not plain:

            return mark_safe("Focus On Growing Your Business <span class='cc-accent'>We\'ll Handle Your Payroll!</span>")

        keyword = "We'll Handle Your Payroll!"

        if keyword.lower() in plain.lower():

            idx = plain.lower().index(keyword.lower())

            before = plain[:idx].strip()

            accent = plain[idx:].strip()

            return mark_safe(f"{before} <span class='cc-accent'>{accent}</span>")

        words = plain.split()

        if len(words) > 5:

            mid = 5

            return mark_safe(f"{' '.join(words[:mid])} <span class='cc-accent'>{' '.join(words[mid:])}</span>")

        return mark_safe(f"<span class='cc-accent'>{plain}</span>")



    @property

    def get_hero_image(self):

        if self.hero_image and hasattr(self.hero_image, 'url'):

            try:

                return self.hero_image.url

            except Exception:

                pass

        return '/static/images/services/educational consultancy 1.png'



    @property

    def get_about_image(self):

        if self.about_image and hasattr(self.about_image, 'url'):

            try:

                return self.about_image.url

            except Exception:

                pass

        return '/static/images/services/manpower-supply 1.png'





class PoServiceCard(models.Model):

    title = models.CharField(max_length=200)

    description = models.TextField()

    icon_class = models.CharField(max_length=100, default="fa-solid fa-file-invoice")

    badge_theme = models.CharField(max_length=50, default="navy")

    order = models.PositiveIntegerField(default=0)

    is_visible = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    updated_at = models.DateTimeField(auto_now=True)



    class Meta:

        db_table = 'po_service_cards'

        ordering = ['order', 'id']

        verbose_name = "PO Service Card"

        verbose_name_plural = "PO Service Cards"



    def __str__(self):

        return self.title





class PoIndustryItem(models.Model):

    name = models.CharField(max_length=150)

    order = models.PositiveIntegerField(default=0)

    is_visible = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    updated_at = models.DateTimeField(auto_now=True)



    class Meta:

        db_table = 'po_industry_items'

        ordering = ['order', 'id']

        verbose_name = "PO Industry Item"

        verbose_name_plural = "PO Industry Items"



    def __str__(self):

        return self.name





class PoWhyChooseItem(models.Model):

    title = models.CharField(max_length=200)

    order = models.PositiveIntegerField(default=0)

    is_visible = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    updated_at = models.DateTimeField(auto_now=True)



    class Meta:

        db_table = 'po_why_choose_items'

        ordering = ['order', 'id']

        verbose_name = "PO Why Choose Item"

        verbose_name_plural = "PO Why Choose Items"



    def __str__(self):

        return self.title





class PoProcessStep(models.Model):

    step_number = models.CharField(max_length=20, default="01")

    title = models.CharField(max_length=200)

    icon_class = models.CharField(max_length=100, default="fa-solid fa-database")

    order = models.PositiveIntegerField(default=0)

    is_visible = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    updated_at = models.DateTimeField(auto_now=True)



    class Meta:

        db_table = 'po_process_steps'

        ordering = ['order', 'id']

        verbose_name = "PO Process Step"

        verbose_name_plural = "PO Process Steps"



    def __str__(self):

        return f"{self.step_number} - {self.title}"





class PoEmployerBenefit(models.Model):

    title = models.CharField(max_length=200)

    order = models.PositiveIntegerField(default=0)

    is_visible = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    updated_at = models.DateTimeField(auto_now=True)



    class Meta:

        db_table = 'po_employer_benefits'

        ordering = ['order', 'id']

        verbose_name = "PO Employer Benefit"

        verbose_name_plural = "PO Employer Benefits"



    def __str__(self):

        return self.title





class PoEmployeeBenefit(models.Model):

    title = models.CharField(max_length=200)

    order = models.PositiveIntegerField(default=0)

    is_visible = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    updated_at = models.DateTimeField(auto_now=True)



    class Meta:

        db_table = 'po_employee_benefits'

        ordering = ['order', 'id']

        verbose_name = "PO Employee Benefit"

        verbose_name_plural = "PO Employee Benefits"



    def __str__(self):

        return self.title





class PoFaqItem(models.Model):

    question = models.CharField(max_length=255)

    answer = models.TextField()

    order = models.PositiveIntegerField(default=0)

    is_visible = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    updated_at = models.DateTimeField(auto_now=True)



    class Meta:

        db_table = 'po_faq_items'

        ordering = ['order', 'id']

        verbose_name = "PO FAQ Item"

        verbose_name_plural = "PO FAQ Items"



    def __str__(self):

        return self.question





@receiver([post_save, post_delete], sender=PayrollOutsourcingSettings)

@receiver([post_save, post_delete], sender=PoServiceCard)

@receiver([post_save, post_delete], sender=PoIndustryItem)

@receiver([post_save, post_delete], sender=PoWhyChooseItem)

@receiver([post_save, post_delete], sender=PoProcessStep)

@receiver([post_save, post_delete], sender=PoEmployerBenefit)

@receiver([post_save, post_delete], sender=PoEmployeeBenefit)

@receiver([post_save, post_delete], sender=PoFaqItem)

def invalidate_payroll_outsourcing_cache(sender, **kwargs):

    cache.delete(PAYROLL_OUTSOURCING_CACHE_KEY)

    cache.delete('public_site_context')



# =============================================================================
# HR SUPPORT SERVICES DYNAMIC MODULE
# =============================================================================

HR_SUPPORT_CACHE_KEY = 'hr_support_full_data'


class HrSupportSettings(models.Model):
    # Master Visibility Switches
    hero_visible = models.BooleanField(default=True)
    about_visible = models.BooleanField(default=True)
    services_visible = models.BooleanField(default=True)
    additional_visible = models.BooleanField(default=True)
    why_choose_visible = models.BooleanField(default=True)
    process_visible = models.BooleanField(default=True)
    benefits_visible = models.BooleanField(default=True)
    cta_visible = models.BooleanField(default=True)

    # 1. Hero Section
    hero_eyebrow = models.CharField(max_length=150, default="HR Support Services", blank=True)
    hero_title = models.CharField(max_length=255, default="Empowering People. Strengthening Organizations.")
    hero_subtitle = models.TextField(default="We provide end-to-end HR support to help businesses build a motivated workforce, ensure compliance, and create a positive work environment.")
    hero_primary_btn_text = models.CharField(max_length=100, default="Get Free Consultation", blank=True)
    hero_primary_btn_url = models.CharField(max_length=255, default="#contact", blank=True)
    hero_secondary_btn_text = models.CharField(max_length=100, default="Contact Us", blank=True)
    hero_secondary_btn_url = models.CharField(max_length=255, default="/contact/", blank=True)
    hero_image = models.ImageField(upload_to="services/hr_support/hero/", blank=True, null=True)

    # 2. About Section
    about_tag = models.CharField(max_length=100, default="About HR Support Services", blank=True)
    about_title = models.CharField(max_length=255, default="Complete HR Solutions for Your Business")
    about_description = models.TextField(default="Our HR experts help you streamline HR operations, develop effective policies, engage employees, manage performance, and maintain accurate documentation.")

    # 3. Services Grid Section (What We Offer)
    services_tag = models.CharField(max_length=100, default="What We Offer", blank=True)
    services_title = models.CharField(max_length=255, default="Our HR Support Services")

    # 4. Additional HR Services Section
    additional_title = models.CharField(max_length=255, default="Additional HR Services")

    # 5. Why Choose Us Section
    why_choose_tag = models.CharField(max_length=100, default="Why Choose Us?", blank=True)
    why_choose_image = models.ImageField(upload_to="services/hr_support/why/", blank=True, null=True)

    # 6. Our HR Support Process Section
    process_tag = models.CharField(max_length=100, default="Our HR Support Process", blank=True)

    # 7. Benefits Section (Employers & Employees)
    benefits_tag = models.CharField(max_length=100, default="Benefits", blank=True)
    employers_badge = models.CharField(max_length=100, default="For Employers", blank=True)
    employees_badge = models.CharField(max_length=100, default="For Employees", blank=True)

    # 8. Bottom CTA Banner & SEO
    cta_title = models.CharField(max_length=255, default="Build a Stronger Workforce with Professional HR Support")
    cta_subtitle = models.TextField(default="Let us handle your HR processes while you focus on growing your business.")
    cta_primary_btn_text = models.CharField(max_length=100, default="Get Free Consultation", blank=True)
    cta_primary_btn_url = models.CharField(max_length=255, default="/contact/", blank=True)
    cta_secondary_btn_text = models.CharField(max_length=100, default="Contact Our HR Team", blank=True)
    cta_secondary_btn_url = models.CharField(max_length=255, default="/contact/", blank=True)

    meta_title = models.CharField(max_length=255, default="HR Support Services — Sky Vision Group Consultancy", blank=True)
    meta_description = models.TextField(default="We provide end-to-end HR support to help businesses build a motivated workforce, ensure compliance, and create a positive work environment.", blank=True)
    meta_keywords = models.CharField(max_length=255, default="hr support, workplace policies, onboarding systems, hr advisory, employee engagement, performance management", blank=True)

    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'hr_support_settings'
        verbose_name = "HR Support Settings"
        verbose_name_plural = "HR Support Settings"

    def __str__(self):
        return "HR Support Settings"

    @classmethod
    def get_settings(cls):
        obj = cls.objects.first()
        if not obj:
            obj = cls.objects.create()
        return obj

    @property
    def hero_title_plain(self):
        clean = re.sub(r'<[^>]+>', '', self.hero_title or '')
        return re.sub(r'\s+', ' ', clean).strip()

    @property
    def formatted_hero_title(self):
        plain = self.hero_title_plain
        if not plain:
            return mark_safe("Empowering People.<br><em>Strengthening Organizations.</em>")
        if '.' in plain:
            parts = plain.split('.', 1)
            p1 = parts[0].strip()
            p2 = parts[1].strip()
            if p2:
                return mark_safe(f"{p1}.<br><em>{p2}</em>")
            return mark_safe(f"{p1}.")
        words = plain.split()
        if len(words) > 2:
            return mark_safe(f"{' '.join(words[:2])}<br><em>{' '.join(words[2:])}</em>")
        return mark_safe(f"<em>{plain}</em>")

    @property
    def cta_title_plain(self):
        clean = re.sub(r'<[^>]+>', '', self.cta_title or '')
        return re.sub(r'\s+', ' ', clean).strip()

    @property
    def formatted_cta_title(self):
        plain = self.cta_title_plain
        if not plain:
            return mark_safe("Build a Stronger Workforce <span class='cc-accent'>with Professional HR Support</span>")
        keyword = "with Professional HR Support"
        if keyword.lower() in plain.lower():
            idx = plain.lower().index(keyword.lower())
            before = plain[:idx].strip()
            accent = plain[idx:].strip()
            return mark_safe(f"{before} <span class='cc-accent'>{accent}</span>")
        words = plain.split()
        if len(words) > 4:
            return mark_safe(f"{' '.join(words[:4])} <span class='cc-accent'>{' '.join(words[4:])}</span>")
        return mark_safe(f"<span class='cc-accent'>{plain}</span>")

    @property
    def get_hero_image(self):
        if self.hero_image and hasattr(self.hero_image, 'url'):
            try:
                return self.hero_image.url
            except Exception:
                pass
        return "/static/images/services/educational consultancy 1.png"

    @property
    def get_why_choose_image(self):
        if self.why_choose_image and hasattr(self.why_choose_image, 'url'):
            try:
                return self.why_choose_image.url
            except Exception:
                pass
        return "/static/images/services/manpower-supply 2.png"


class HrFeatureItem(models.Model):
    title = models.CharField(max_length=255)
    icon_class = models.CharField(max_length=100, default="fa-solid fa-check", blank=True)
    order = models.PositiveIntegerField(default=0)
    is_visible = models.BooleanField(default=True)

    class Meta:
        db_table = 'hr_feature_items'
        ordering = ['order', 'id']
        verbose_name = "HR Feature Item"
        verbose_name_plural = "HR Feature Items"

    def __str__(self):
        return self.title


class HrServiceCard(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    icon_class = models.CharField(max_length=100, default="fa-solid fa-file-signature", blank=True)
    order = models.PositiveIntegerField(default=0)
    is_visible = models.BooleanField(default=True)

    class Meta:
        db_table = 'hr_service_cards'
        ordering = ['order', 'id']
        verbose_name = "HR Service Card"
        verbose_name_plural = "HR Service Cards"

    def __str__(self):
        return self.title


class HrAdditionalServiceItem(models.Model):
    title = models.CharField(max_length=255)
    icon_class = models.CharField(max_length=100, default="fa-solid fa-briefcase", blank=True)
    order = models.PositiveIntegerField(default=0)
    is_visible = models.BooleanField(default=True)

    class Meta:
        db_table = 'hr_additional_service_items'
        ordering = ['order', 'id']
        verbose_name = "HR Additional Service Item"
        verbose_name_plural = "HR Additional Service Items"

    def __str__(self):
        return self.title


class HrWhyChooseItem(models.Model):
    title = models.CharField(max_length=255)
    order = models.PositiveIntegerField(default=0)
    is_visible = models.BooleanField(default=True)

    class Meta:
        db_table = 'hr_why_choose_items'
        ordering = ['order', 'id']
        verbose_name = "HR Why Choose Item"
        verbose_name_plural = "HR Why Choose Items"

    def __str__(self):
        return self.title


class HrProcessStep(models.Model):
    step_number = models.CharField(max_length=50, default="Step 1")
    title = models.CharField(max_length=255)
    icon_class = models.CharField(max_length=100, default="fa-solid fa-clipboard-list", blank=True)
    order = models.PositiveIntegerField(default=0)
    is_visible = models.BooleanField(default=True)

    class Meta:
        db_table = 'hr_process_steps'
        ordering = ['order', 'id']
        verbose_name = "HR Process Step"
        verbose_name_plural = "HR Process Steps"

    def __str__(self):
        return f"{self.step_number}: {self.title}"


class HrEmployerBenefit(models.Model):
    title = models.CharField(max_length=255)
    order = models.PositiveIntegerField(default=0)
    is_visible = models.BooleanField(default=True)

    class Meta:
        db_table = 'hr_employer_benefits'
        ordering = ['order', 'id']
        verbose_name = "HR Employer Benefit"
        verbose_name_plural = "HR Employer Benefits"

    def __str__(self):
        return self.title


class HrEmployeeBenefit(models.Model):
    title = models.CharField(max_length=255)
    order = models.PositiveIntegerField(default=0)
    is_visible = models.BooleanField(default=True)

    class Meta:
        db_table = 'hr_employee_benefits'
        ordering = ['order', 'id']
        verbose_name = "HR Employee Benefit"
        verbose_name_plural = "HR Employee Benefits"

    def __str__(self):
        return self.title


@receiver([post_save, post_delete], sender=HrSupportSettings)
@receiver([post_save, post_delete], sender=HrFeatureItem)
@receiver([post_save, post_delete], sender=HrServiceCard)
@receiver([post_save, post_delete], sender=HrAdditionalServiceItem)
@receiver([post_save, post_delete], sender=HrWhyChooseItem)
@receiver([post_save, post_delete], sender=HrProcessStep)
@receiver([post_save, post_delete], sender=HrEmployerBenefit)
@receiver([post_save, post_delete], sender=HrEmployeeBenefit)
def invalidate_hr_support_cache(sender, **kwargs):
    cache.delete(HR_SUPPORT_CACHE_KEY)
    cache.delete('public_site_context')


# ==============================================================================
# INTERNSHIP PROGRAMME DYNAMIC SERVICE MODELS
# ==============================================================================

INTERNSHIP_CACHE_KEY = "internship_settings_data"


class InternshipSettings(models.Model):
    # Master Visibility Switches
    hero_visible = models.BooleanField(default=True)
    strip_visible = models.BooleanField(default=True)
    domains_visible = models.BooleanField(default=True)
    highlights_visible = models.BooleanField(default=True)
    who_can_apply_visible = models.BooleanField(default=True)
    what_you_learn_visible = models.BooleanField(default=True)
    process_visible = models.BooleanField(default=True)
    benefits_visible = models.BooleanField(default=True)
    faqs_visible = models.BooleanField(default=True)
    openings_visible = models.BooleanField(default=True)
    cta_visible = models.BooleanField(default=True)

    # 1. Hero Section
    hero_eyebrow = models.CharField(max_length=150, default="Internship Programme", blank=True)
    hero_title = models.CharField(max_length=255, default="Launch your career from day one.")
    hero_tagline = models.CharField(max_length=255, default="LEARN • GROW • SUCCEED", blank=True)
    hero_subtitle = models.TextField(default="Real projects, real mentors, real outcomes. Build the skills employers actually ask for — with a certificate and placement support waiting at the finish line.")
    hero_primary_btn_text = models.CharField(max_length=100, default="Apply Today", blank=True)
    hero_primary_btn_url = models.CharField(max_length=255, default="#contact", blank=True)
    hero_secondary_btn_text = models.CharField(max_length=100, default="See how it works", blank=True)
    hero_secondary_btn_url = models.CharField(max_length=255, default="#process", blank=True)
    hero_image = models.ImageField(upload_to="services/internship/hero/", blank=True, null=True)
    hero_badge_text = models.CharField(max_length=100, default="Mission: Hired", blank=True)

    # 2. Explore / Pick your mission (Domains / Tracks)
    domains_tag = models.CharField(max_length=100, default="Explore", blank=True)
    domains_title = models.CharField(max_length=255, default="Pick your mission")
    domains_subtitle = models.TextField(default="Seven tracks, one goal — hands-on experience that actually shows up on your résumé.", blank=True)

    # 3. Programme Highlights
    highlights_tag = models.CharField(max_length=100, default="Programme Highlights", blank=True)

    # 4. Triple Panel (Who Can Apply, What You'll Learn, Flight Path)
    who_can_apply_title = models.CharField(max_length=255, default="Who Can Apply?")
    what_you_learn_title = models.CharField(max_length=255, default="What You'll Learn")
    process_tag = models.CharField(max_length=100, default="Flight Path", blank=True)
    process_title = models.CharField(max_length=255, default="Our Internship Process")

    # 5. Benefits & FAQs
    benefits_tag = models.CharField(max_length=100, default="Benefits of Joining", blank=True)
    benefits_title = models.CharField(max_length=255, default="Why interns choose us")
    faqs_tag = models.CharField(max_length=100, default="FAQs", blank=True)
    faqs_title = models.CharField(max_length=255, default="Common questions")

    # 6. Live Openings
    openings_tag = models.CharField(max_length=100, default="Live Openings", blank=True)
    openings_title = models.CharField(max_length=255, default="Available Internship Positions")
    openings_subtitle = models.TextField(default="Explore current open roles and apply directly with your resume.", blank=True)

    # 7. Bottom CTA & SEO
    cta_title = models.CharField(max_length=255, default="Build Skills. Gain Experience. Get Hired.")
    cta_subtitle = models.TextField(default="Join our Internship Programme today and transform your potential into professional success.")
    cta_primary_btn_text = models.CharField(max_length=100, default="Apply Now", blank=True)
    cta_primary_btn_url = models.CharField(max_length=255, default="#", blank=True)
    cta_secondary_btn_text = models.CharField(max_length=100, default="Contact Us", blank=True)
    cta_secondary_btn_url = models.CharField(max_length=255, default="/contact/", blank=True)

    meta_title = models.CharField(max_length=255, default="Internship Programme — Sky Vision Group Consultancy", blank=True)
    meta_description = models.TextField(default="Real projects, real mentors, real outcomes. Build the skills employers actually ask for — with a certificate and placement support waiting at the finish line.", blank=True)
    meta_keywords = models.CharField(max_length=255, default="internship programme, hr internship, it internship, web development, finance internship, digital marketing internship", blank=True)

    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'internship_settings'
        verbose_name = "Internship Settings"
        verbose_name_plural = "Internship Settings"

    def __str__(self):
        return "Internship Settings"

    @classmethod
    def get_settings(cls):
        obj = cls.objects.first()
        if not obj:
            obj = cls.objects.create()
        return obj

    @property
    def hero_title_plain(self):
        clean = re.sub(r'<[^>]+>', '', self.hero_title or '')
        return re.sub(r'\s+', ' ', clean).strip()

    @property
    def formatted_hero_title(self):
        plain = self.hero_title_plain
        if not plain:
            return mark_safe("Launch your career<br><em>from day one.</em>")
        keyword = "from day one"
        if keyword.lower() in plain.lower():
            idx = plain.lower().index(keyword.lower())
            p1 = plain[:idx].strip()
            p2 = plain[idx:].strip()
            return mark_safe(f"{p1}<br><em>{p2}</em>")
        words = plain.split()
        if len(words) > 3:
            return mark_safe(f"{' '.join(words[:3])}<br><em>{' '.join(words[3:])}</em>")
        return mark_safe(f"<em>{plain}</em>")

    @property
    def cta_title_plain(self):
        clean = re.sub(r'<[^>]+>', '', self.cta_title or '')
        return re.sub(r'\s+', ' ', clean).strip()

    @property
    def formatted_cta_title(self):
        plain = self.cta_title_plain
        if not plain:
            return mark_safe("<i class='fa-solid fa-rocket' style='color:var(--amber-2);margin-right:10px'></i>Build Skills. Gain Experience. Get Hired.")
        return mark_safe(f"<i class='fa-solid fa-rocket' style='color:var(--amber-2);margin-right:10px'></i>{plain}")

    @property
    def get_hero_image(self):
        if self.hero_image and hasattr(self.hero_image, 'url'):
            try:
                return self.hero_image.url
            except Exception:
                pass
        return "/static/images/general/workshop.png"


class InternshipStripItem(models.Model):
    title = models.CharField(max_length=255)
    icon_class = models.CharField(max_length=100, default="fa-solid fa-people-group", blank=True)
    order = models.PositiveIntegerField(default=0)
    is_visible = models.BooleanField(default=True)

    class Meta:
        db_table = 'internship_strip_items'
        ordering = ['order', 'id']
        verbose_name = "Internship Strip Item"
        verbose_name_plural = "Internship Strip Items"

    def __str__(self):
        return self.title


class InternshipTrackItem(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    icon_class = models.CharField(max_length=100, default="fa-solid fa-user-group", blank=True)
    badge_number = models.CharField(max_length=20, default="01", blank=True)
    card_style = models.CharField(max_length=50, default="d1", blank=True)
    order = models.PositiveIntegerField(default=0)
    is_visible = models.BooleanField(default=True)

    class Meta:
        db_table = 'internship_track_items'
        ordering = ['order', 'id']
        verbose_name = "Internship Track Item"
        verbose_name_plural = "Internship Track Items"

    def __str__(self):
        return self.title


class InternshipHighlightItem(models.Model):
    title = models.CharField(max_length=255)
    icon_class = models.CharField(max_length=100, default="fa-solid fa-circle-check", blank=True)
    order = models.PositiveIntegerField(default=0)
    is_visible = models.BooleanField(default=True)

    class Meta:
        db_table = 'internship_highlight_items'
        ordering = ['order', 'id']
        verbose_name = "Internship Highlight Item"
        verbose_name_plural = "Internship Highlight Items"

    def __str__(self):
        return self.title


class InternshipWhoCanApplyItem(models.Model):
    title = models.CharField(max_length=255)
    icon_class = models.CharField(max_length=100, default="fa-solid fa-circle-check", blank=True)
    order = models.PositiveIntegerField(default=0)
    is_visible = models.BooleanField(default=True)

    class Meta:
        db_table = 'internship_who_can_apply_items'
        ordering = ['order', 'id']
        verbose_name = "Internship Who Can Apply Item"
        verbose_name_plural = "Internship Who Can Apply Items"

    def __str__(self):
        return self.title


class InternshipWhatYouLearnItem(models.Model):
    title = models.CharField(max_length=255)
    icon_class = models.CharField(max_length=100, default="fa-solid fa-circle-check", blank=True)
    order = models.PositiveIntegerField(default=0)
    is_visible = models.BooleanField(default=True)

    class Meta:
        db_table = 'internship_what_you_learn_items'
        ordering = ['order', 'id']
        verbose_name = "Internship What You Learn Item"
        verbose_name_plural = "Internship What You Learn Items"

    def __str__(self):
        return self.title


class InternshipProcessStep(models.Model):
    step_number = models.CharField(max_length=50, default="Step 1")
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, default="")
    icon_class = models.CharField(max_length=100, default="fa-solid fa-file-signature", blank=True)
    is_final = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)
    is_visible = models.BooleanField(default=True)

    class Meta:
        db_table = 'internship_process_steps'
        ordering = ['order', 'id']
        verbose_name = "Internship Process Step"
        verbose_name_plural = "Internship Process Steps"

    def __str__(self):
        return f"{self.step_number}: {self.title}"


class InternshipBenefitItem(models.Model):
    title = models.CharField(max_length=255)
    icon_class = models.CharField(max_length=100, default="fa-solid fa-chart-line", blank=True)
    order = models.PositiveIntegerField(default=0)
    is_visible = models.BooleanField(default=True)

    class Meta:
        db_table = 'internship_benefit_items'
        ordering = ['order', 'id']
        verbose_name = "Internship Benefit Item"
        verbose_name_plural = "Internship Benefit Items"

    def __str__(self):
        return self.title


class InternshipFaqItem(models.Model):
    question = models.CharField(max_length=350)
    answer = models.TextField()
    order = models.PositiveIntegerField(default=0)
    is_visible = models.BooleanField(default=True)

    class Meta:
        db_table = 'internship_faq_items'
        ordering = ['order', 'id']
        verbose_name = "Internship FAQ Item"
        verbose_name_plural = "Internship FAQ Items"

    def __str__(self):
        return self.question


@receiver([post_save, post_delete], sender=InternshipSettings)
@receiver([post_save, post_delete], sender=InternshipStripItem)
@receiver([post_save, post_delete], sender=InternshipTrackItem)
@receiver([post_save, post_delete], sender=InternshipHighlightItem)
@receiver([post_save, post_delete], sender=InternshipWhoCanApplyItem)
@receiver([post_save, post_delete], sender=InternshipWhatYouLearnItem)
@receiver([post_save, post_delete], sender=InternshipProcessStep)
@receiver([post_save, post_delete], sender=InternshipBenefitItem)
@receiver([post_save, post_delete], sender=InternshipFaqItem)
def invalidate_internship_cache(sender, **kwargs):
    cache.delete(INTERNSHIP_CACHE_KEY)
    cache.delete('public_site_context')


# =============================================================================
# JOB PAGE (EXPLORE JOB OPPORTUNITIES /job/) SETTINGS
# =============================================================================
JOB_PAGE_CACHE_KEY = 'job_page_settings_data'

class JobPageSettings(models.Model):
    # Master Visibility Switches
    hero_visible = models.BooleanField(default=True)
    search_visible = models.BooleanField(default=True)
    job_types_visible = models.BooleanField(default=True)
    categories_visible = models.BooleanField(default=True)
    latest_jobs_visible = models.BooleanField(default=True)
    industries_visible = models.BooleanField(default=True)
    locations_visible = models.BooleanField(default=True)
    why_choose_visible = models.BooleanField(default=True)

    # 1. Hero Section
    hero_chip = models.CharField(max_length=150, default="Thousands of opportunities. One destination.", blank=True)
    hero_title = models.CharField(max_length=255, default="Find Your Dream Job")
    hero_title_highlight = models.CharField(max_length=100, default="Dream", blank=True)
    hero_subtitle = models.TextField(default="Explore thousands of verified job opportunities across top companies and start your career today.")
    hero_image = models.ImageField(upload_to="pages/job/hero/", blank=True, null=True)
    hero_btn1_text = models.CharField(max_length=50, default="Apply Now", blank=True)
    hero_btn1_url = models.CharField(max_length=255, default="#", blank=True)
    hero_btn2_text = models.CharField(max_length=50, default="Hire Talent", blank=True)
    hero_btn2_url = models.CharField(max_length=255, default="/employer/hire-talent/", blank=True)
    hero_btn3_text = models.CharField(max_length=50, default="Apply Internship", blank=True)
    hero_btn3_url = models.CharField(max_length=255, default="#", blank=True)

    search_keyword_placeholder = models.CharField(max_length=150, default="Enter Skills / designations / companies", blank=True)
    search_location_placeholder = models.CharField(max_length=150, default="Location", blank=True)
    search_btn_text = models.CharField(max_length=50, default="Search Jobs", blank=True)

    # Hero 3 Features
    feature_1_title = models.CharField(max_length=100, default="100% Verified Jobs")
    feature_1_desc = models.CharField(max_length=150, default="Genuine & trusted job openings")
    feature_2_title = models.CharField(max_length=100, default="For Everyone")
    feature_2_desc = models.CharField(max_length=150, default="Freshers, experienced & professionals")
    feature_3_title = models.CharField(max_length=100, default="Faster Career Growth")
    feature_3_desc = models.CharField(max_length=150, default="The right job can take you places")

    # Hero 4 Stats
    stat_1_num = models.CharField(max_length=50, default="50K+")
    stat_1_label = models.CharField(max_length=50, default="Active Jobs")
    stat_2_num = models.CharField(max_length=50, default="25K+")
    stat_2_label = models.CharField(max_length=50, default="Companies")
    stat_3_num = models.CharField(max_length=50, default="10L+")
    stat_3_label = models.CharField(max_length=50, default="Happy Candidates")
    stat_4_num = models.CharField(max_length=50, default="24/7")
    stat_4_label = models.CharField(max_length=50, default="Support")

    # 2. Section Headings
    types_title = models.CharField(max_length=255, default="Job Type")
    types_view_all_text = models.CharField(max_length=50, default="View All", blank=True)
    types_view_all_url = models.CharField(max_length=255, default="/jobs/", blank=True)
    categories_view_all_text = models.CharField(max_length=50, default="View All Categories", blank=True)
    categories_view_all_url = models.CharField(max_length=255, default="/jobs/", blank=True)
    latest_view_all_text = models.CharField(max_length=50, default="View All Jobs", blank=True)
    industries_view_all_text = models.CharField(max_length=50, default="View All", blank=True)
    industries_view_all_url = models.CharField(max_length=255, default="/jobs/", blank=True)
    locations_view_all_text = models.CharField(max_length=50, default="View All", blank=True)
    locations_view_all_url = models.CharField(max_length=255, default="/jobs/", blank=True)
    categories_title = models.CharField(max_length=255, default="Job Categories")
    latest_eyebrow = models.CharField(max_length=100, default="Fresh Openings", blank=True)
    latest_title = models.CharField(max_length=255, default="Latest Jobs")
    latest_subtitle = models.TextField(default="Find your dream job from the latest vacancies.")

    # 3. Triple Panel Headings
    industries_title = models.CharField(max_length=255, default="Popular Industries")
    locations_title = models.CharField(max_length=255, default="Jobs by Location")
    why_choose_title = models.CharField(max_length=255, default="Why Choose Sky Vision?")

    # 4. JSON repeaters for triple panel
    popular_industries_json = models.TextField(blank=True, default="")
    jobs_by_location_json = models.TextField(blank=True, default="")
    why_choose_json = models.TextField(blank=True, default="")

    # 5. Commitment & CTA Sections
    commit_visible = models.BooleanField(default=True)
    commit_title = models.CharField(max_length=255, default="We are Committed to Your Success")
    commit_stats_json = models.TextField(blank=True, default="")
    commit_image = models.ImageField(upload_to="pages/job/commit/", blank=True, null=True)

    cta_visible = models.BooleanField(default=True)
    cta_title = models.CharField(max_length=255, default="Ready to Take the Next Step?")
    cta_subtitle = models.TextField(default="Create your profile, apply to jobs and kickstart your career journey today!")
    cta_btn_text = models.CharField(max_length=100, default="Create Your Profile Now")
    cta_btn_url = models.CharField(max_length=255, default="/contact/")
    cta_steps_json = models.TextField(blank=True, default="")
    cta_image = models.ImageField(upload_to="pages/job/cta/", blank=True, null=True)

    # 6. SEO & Meta
    meta_title = models.CharField(max_length=255, default="Explore Job Opportunities — Sky Vision Group Consultancy", blank=True)
    meta_description = models.TextField(default="Find your dream job from verified vacancies across top companies. Apply now for full-time, part-time, and work-from-home jobs.", blank=True)
    meta_keywords = models.CharField(max_length=255, default="jobs in lucknow, verified jobs, full time jobs, part time jobs, work from home", blank=True)

    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_popular_industries(self, visible_only=True):
        import json
        data = None
        if self.popular_industries_json:
            try:
                parsed = json.loads(self.popular_industries_json)
                if isinstance(parsed, list) and len(parsed) > 0:
                    data = parsed
            except Exception:
                pass
        if data is None:
            data = [
                {"name": "Information Technology", "icon": "fa-solid fa-desktop", "link": "/jobs/?field=it", "is_visible": True},
                {"name": "Manufacturing", "icon": "fa-solid fa-industry", "link": "/jobs/?field=manufacturing", "is_visible": True},
                {"name": "Healthcare", "icon": "fa-solid fa-heart-pulse", "link": "/jobs/?field=healthcare", "is_visible": True},
                {"name": "Automobile", "icon": "fa-solid fa-car", "link": "/jobs/?field=automobile", "is_visible": True},
                {"name": "Banking & Finance", "icon": "fa-solid fa-building-columns", "link": "/jobs/?field=banking-finance", "is_visible": True},
                {"name": "E-commerce", "icon": "fa-solid fa-cart-shopping", "link": "/jobs/?field=ecommerce", "is_visible": True},
                {"name": "Telecom", "icon": "fa-solid fa-phone", "link": "/jobs/?field=telecom", "is_visible": True},
                {"name": "Education", "icon": "fa-solid fa-graduation-cap", "link": "/jobs/?field=education", "is_visible": True},
                {"name": "Retail", "icon": "fa-solid fa-store", "link": "/jobs/?field=retail", "is_visible": True},
                {"name": "Construction", "icon": "fa-solid fa-hard-hat", "link": "/jobs/?field=construction", "is_visible": True},
                {"name": "Hospitality", "icon": "fa-solid fa-hotel", "link": "/jobs/?field=hospitality", "is_visible": True},
                {"name": "Logistics", "icon": "fa-solid fa-truck", "link": "/jobs/?field=logistics", "is_visible": True},
            ]
        if visible_only:
            return [d for d in data if d.get('is_visible', True) is not False]
        return data

    def get_jobs_by_location(self, visible_only=True):
        import json
        data = None
        if self.jobs_by_location_json:
            try:
                parsed = json.loads(self.jobs_by_location_json)
                if isinstance(parsed, list) and len(parsed) > 0:
                    data = parsed
            except Exception:
                pass
        if data is None:
            data = [
                {"city": "Noida", "count": "2,450+ Jobs", "icon": "fa-solid fa-location-dot", "is_visible": True},
                {"city": "Kanpur", "count": "750+ Jobs", "icon": "fa-solid fa-location-dot", "is_visible": True},
                {"city": "Greater Noida", "count": "1,850+ Jobs", "icon": "fa-solid fa-location-dot", "is_visible": True},
                {"city": "Pune", "count": "1,300+ Jobs", "icon": "fa-solid fa-location-dot", "is_visible": True},
                {"city": "Gurugram", "count": "1,650+ Jobs", "icon": "fa-solid fa-location-dot", "is_visible": True},
                {"city": "Bangalore", "count": "2,150+ Jobs", "icon": "fa-solid fa-location-dot", "is_visible": True},
                {"city": "Delhi", "count": "3,200+ Jobs", "icon": "fa-solid fa-location-dot", "is_visible": True},
                {"city": "Hyderabad", "count": "1,800+ Jobs", "icon": "fa-solid fa-location-dot", "is_visible": True},
                {"city": "Ghaziabad", "count": "1,250+ Jobs", "icon": "fa-solid fa-location-dot", "is_visible": True},
                {"city": "Mumbai", "count": "2,750+ Jobs", "icon": "fa-solid fa-location-dot", "is_visible": True},
                {"city": "Lucknow", "count": "950+ Jobs", "icon": "fa-solid fa-location-dot", "is_visible": True},
                {"city": "Chennai", "count": "1,450+ Jobs", "icon": "fa-solid fa-location-dot", "is_visible": True},
            ]
        if visible_only:
            return [d for d in data if d.get('is_visible', True) is not False]
        return data

    def get_why_choose(self, visible_only=True):
        import json
        data = None
        if self.why_choose_json:
            try:
                parsed = json.loads(self.why_choose_json)
                if isinstance(parsed, list) and len(parsed) > 0:
                    data = parsed
            except Exception:
                pass
        if data is None:
            data = [
                {"title": "Verified Companies", "desc": "All companies are verified for your safety.", "icon": "fa-solid fa-shield-halved", "is_visible": True},
                {"title": "100% Free Service", "desc": "Our services are completely free for job seekers.", "icon": "fa-solid fa-hand-holding-dollar", "is_visible": True},
                {"title": "Expert Career Guidance", "desc": "Get professional guidance to grow your career.", "icon": "fa-solid fa-compass", "is_visible": True},
                {"title": "Interview Support", "desc": "We help you prepare & crack interviews.", "icon": "fa-solid fa-comments", "is_visible": True},
                {"title": "Resume Assistance", "desc": "Get your resume reviewed by experts.", "icon": "fa-solid fa-file-lines", "is_visible": True},
                {"title": "Faster Hiring", "desc": "Quick response and fast hiring process.", "icon": "fa-solid fa-bolt", "is_visible": True},
            ]
        if visible_only:
            return [d for d in data if d.get('is_visible', True) is not False]
        return data

    def get_commit_stats(self, visible_only=True):
        import json
        data = None
        if self.commit_stats_json:
            try:
                parsed = json.loads(self.commit_stats_json)
                if isinstance(parsed, list) and len(parsed) > 0:
                    data = parsed
            except Exception:
                pass
        if data is None:
            data = [
                {"num": "50K+", "label": "Active Jobs", "is_visible": True},
                {"num": "25K+", "label": "Trusted Companies", "is_visible": True},
                {"num": "10L+", "label": "Happy Candidates", "is_visible": True},
                {"num": "15+", "label": "Years of Experience", "is_visible": True},
                {"num": "24/7", "label": "Customer Support", "is_visible": True},
            ]
        if visible_only:
            return [d for d in data if d.get('is_visible', True) is not False]
        return data

    def get_cta_steps(self, visible_only=True):
        import json
        data = None
        if self.cta_steps_json:
            try:
                parsed = json.loads(self.cta_steps_json)
                if isinstance(parsed, list) and len(parsed) > 0:
                    data = parsed
            except Exception:
                pass
        if data is None:
            data = [
                {"title": "Create Profile", "desc": "Build your professional profile in just a few minutes", "icon": "fa-solid fa-user", "is_visible": True},
                {"title": "Apply Jobs", "desc": "Apply to thousands of jobs that match your skills", "icon": "fa-solid fa-paper-plane", "is_visible": True},
                {"title": "Get Hired", "desc": "Connect with top companies and get hired faster", "icon": "fa-solid fa-handshake", "is_visible": True},
            ]
        if visible_only:
            return [d for d in data if d.get('is_visible', True) is not False]
        return data

    @property
    def clean_hero_title(self):
        import re
        raw = self.hero_title or "Find Your Dream Job"
        return re.sub(r'<[^>]+>', '', raw).strip()

    def get_rendered_hero_title(self):
        import re
        clean_title = self.clean_hero_title
        hl = (self.hero_title_highlight or "Dream").strip()
        if hl and hl in clean_title:
            return clean_title.replace(hl, f'<span class="highlight">{hl}</span>', 1)
        return clean_title

    class Meta:
        db_table = 'job_page_settings'
        verbose_name = "Job Page Settings"
        verbose_name_plural = "Job Page Settings"

    def __str__(self):
        return "Job Page Settings"

    @classmethod
    def get_settings(cls):
        cached = cache.get(JOB_PAGE_CACHE_KEY)
        if cached:
            return cached
        obj, created = cls.objects.get_or_create(id=1)
        cache.set(JOB_PAGE_CACHE_KEY, obj, timeout=86400)
        return obj


@receiver([post_save, post_delete], sender=JobPageSettings)
def invalidate_job_page_cache(sender, **kwargs):
    cache.delete(JOB_PAGE_CACHE_KEY)
    cache.delete('public_site_context')


# =============================================================================
# CAREERS PAGE SETTINGS (DYNAMIC SECTION-WISE MANAGEMENT)
# =============================================================================
CAREER_PAGE_CACHE_KEY = 'career_page_settings_data'

class CareerPageSettings(models.Model):
    # Master Visibility Switches
    hero_visible = models.BooleanField(default=True)
    openings_visible = models.BooleanField(default=True)
    resume_cta_visible = models.BooleanField(default=True)
    why_build_visible = models.BooleanField(default=True)
    career_areas_visible = models.BooleanField(default=True)
    journey_visible = models.BooleanField(default=True)
    look_for_visible = models.BooleanField(default=True)
    benefits_visible = models.BooleanField(default=True)
    cta_visible = models.BooleanField(default=True)

    # 1. Hero Section
    hero_eyebrow = models.CharField(max_length=150, default="Careers at Sky Vision", blank=True)
    hero_title = models.CharField(max_length=255, default="Find your direction. Build your future.")
    hero_title_highlight = models.CharField(max_length=100, default="Build your future.", blank=True)
    hero_subtitle = models.TextField(default="Great opportunities don't happen — you create them. Explore roles across HR, IT, Finance, Marketing and more, with mentors who help you navigate every step.")
    hero_image = models.ImageField(upload_to="pages/careers/hero/", blank=True, null=True)
    hero_rating_badge = models.CharField(max_length=100, default="4.8/5 team rating", blank=True)
    hero_placed_badge = models.CharField(max_length=100, default="500+ careers placed", blank=True)
    hero_btn1_text = models.CharField(max_length=50, default="Explore Openings", blank=True)
    hero_btn1_url = models.CharField(max_length=255, default="#openings", blank=True)
    hero_btn2_text = models.CharField(max_length=50, default="How It Works", blank=True)
    hero_btn2_url = models.CharField(max_length=255, default="#journey", blank=True)

    # Hero 4 Features
    feature_1_icon = models.CharField(max_length=60, default="fa-solid fa-bullseye", blank=True)
    feature_1_title = models.CharField(max_length=100, default="Right Opportunities")
    feature_1_desc = models.CharField(max_length=150, default="Roles that fit your goals")

    feature_2_icon = models.CharField(max_length=60, default="fa-solid fa-chart-line", blank=True)
    feature_2_title = models.CharField(max_length=100, default="Career Growth")
    feature_2_desc = models.CharField(max_length=150, default="Skills that compound")

    feature_3_icon = models.CharField(max_length=60, default="fa-solid fa-user-group", blank=True)
    feature_3_title = models.CharField(max_length=100, default="Expert Guidance")
    feature_3_desc = models.CharField(max_length=150, default="Mentors who've been there")

    feature_4_icon = models.CharField(max_length=60, default="fa-solid fa-award", blank=True)
    feature_4_title = models.CharField(max_length=100, default="Bright Future")
    feature_4_desc = models.CharField(max_length=150, default="A path, not just a job")

    # 2. Current Openings Jobs Section
    openings_eyebrow = models.CharField(max_length=100, default="— CAREER —", blank=True)
    openings_title = models.CharField(max_length=255, default="Current Openings Jobs")
    openings_subtitle = models.CharField(max_length=255, default="Join Our Growing Team", blank=True)
    openings_desc = models.TextField(default="We are always looking for passionate and talented individuals to join our team. Whether you're an experienced professional or a motivated fresher, we offer opportunities across multiple industries. Browse our current openings and apply for the role that best matches your skills and career goals.")
    openings_json = models.TextField(blank=True, default="")

    # 3. Didn't Find the Right Job? (Resume CTA Banner)
    resume_cta_icon = models.CharField(max_length=60, default="fa-solid fa-file-arrow-up", blank=True)
    resume_cta_title = models.CharField(max_length=255, default="Didn't Find the Right Job?")
    resume_cta_desc = models.TextField(default="Upload your resume today, and our recruitment team will contact you when a suitable opportunity becomes available.")
    resume_btn_text = models.CharField(max_length=100, default="Upload Resume", blank=True)
    resume_contact_btn_text = models.CharField(max_length=100, default="Contact Recruitment", blank=True)
    resume_contact_btn_url = models.CharField(max_length=255, default="#contact", blank=True)

    # 4. Why Build Here (Triple Panel 1)
    why_build_tag = models.CharField(max_length=100, default="Why Build Here", blank=True)
    why_build_title = models.CharField(max_length=255, default="A place that invests in you")
    why_build_json = models.TextField(blank=True, default="")

    # 5. Career Areas (Triple Panel 2)
    career_areas_tag = models.CharField(max_length=100, default="Career Areas", blank=True)
    career_areas_title = models.CharField(max_length=255, default="Six ways in")
    career_areas_json = models.TextField(blank=True, default="")

    # 6. Your Career Journey (Triple Panel 3)
    journey_tag = models.CharField(max_length=100, default="Your Career Journey", blank=True)
    journey_title = models.CharField(max_length=255, default="Five clear steps")
    journey_steps_json = models.TextField(blank=True, default="")

    # 7. What We Look For (Strip Box 1)
    look_for_tag = models.CharField(max_length=100, default="What We Look For", blank=True)
    look_for_json = models.TextField(blank=True, default="")

    # 8. Employee Benefits (Strip Box 2)
    benefits_tag = models.CharField(max_length=100, default="Employee Benefits", blank=True)
    benefits_json = models.TextField(blank=True, default="")

    # 9. Bottom CTA Banner (Your future starts here.)
    cta_title = models.CharField(max_length=255, default="Your future starts here.")
    cta_subtitle = models.TextField(default="Take the next step towards a rewarding career. We'd love to have you on the team.")
    cta_icon = models.CharField(max_length=60, default="fa-solid fa-person-hiking", blank=True)
    cta_btn1_text = models.CharField(max_length=100, default="Explore Openings", blank=True)
    cta_btn1_url = models.CharField(max_length=255, default="/jobs/", blank=True)
    cta_btn2_text = models.CharField(max_length=100, default="Contact Us", blank=True)
    cta_btn2_url = models.CharField(max_length=255, default="/contact/", blank=True)

    # 10. SEO & Meta
    meta_title = models.CharField(max_length=255, default="Careers & Counseling — Sky Vision Group Consultancy", blank=True)
    meta_description = models.TextField(default="Explore rewarding career opportunities at Sky Vision Group Consultancy. Join our growing team across HR, IT, Marketing, Sales and more.", blank=True)
    meta_keywords = models.CharField(max_length=255, default="careers, sky vision careers, hr recruiter jobs, jobs in lucknow, career counseling", blank=True)

    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_openings(self, visible_only=True):
        import json
        data = None
        if self.openings_json:
            try:
                parsed = json.loads(self.openings_json)
                if isinstance(parsed, list) and len(parsed) > 0:
                    data = parsed
            except Exception:
                pass
        if data is None:
            data = [
                {"title": "HR Recruiter", "icon": "fa-solid fa-user-tie", "color": "blue", "location": "Noida", "experience": "Fresher / 1+ Year", "employment": "Full-Time", "salary": "₹18,000 – ₹30,000 / Month", "is_visible": True},
                {"title": "Customer Support Executive", "icon": "fa-solid fa-headset", "color": "purple", "location": "Delhi NCR", "experience": "Fresher", "employment": "Full-Time", "salary": "₹15,000 – ₹25,000 / Month", "is_visible": True},
                {"title": "Sales Executive", "icon": "fa-solid fa-chart-line", "color": "green", "location": "Noida", "experience": "1–3 Years", "employment": "Full-Time", "salary": "₹20,000 – ₹35,000 / Month", "is_visible": True},
                {"title": "Data Entry Operator", "icon": "fa-solid fa-file-lines", "color": "amber", "location": "Ghaziabad", "experience": "Fresher", "employment": "Full-Time", "salary": "₹14,000 – ₹22,000 / Month", "is_visible": True},
                {"title": "Delivery Executive", "icon": "fa-solid fa-motorcycle", "color": "blue", "location": "Multiple Locations", "experience": "Fresher", "employment": "Full-Time", "salary": "₹20,000 – ₹35,000 + Incentives", "is_visible": True},
                {"title": "IT Support Executive", "icon": "fa-solid fa-desktop", "color": "red", "location": "Noida", "experience": "0–2 Years", "employment": "Full-Time", "salary": "₹22,000 – ₹40,000 / Month", "is_visible": True},
            ]
        if visible_only:
            return [d for d in data if d.get('is_visible', True) is not False]
        return data

    def get_why_build(self, visible_only=True):
        import json
        data = None
        if self.why_build_json:
            try:
                parsed = json.loads(self.why_build_json)
                if isinstance(parsed, list) and len(parsed) > 0:
                    data = parsed
            except Exception:
                pass
        if data is None:
            data = [
                {"title": "Diverse Opportunities", "desc": "Work across roles and industries.", "icon": "fa-solid fa-clipboard-list", "is_visible": True},
                {"title": "Mentorship", "desc": "Guidance from experienced professionals.", "icon": "fa-solid fa-user-tie", "is_visible": True},
                {"title": "Learning & Development", "desc": "Continuous learning to upgrade your skills.", "icon": "fa-solid fa-award", "is_visible": True},
                {"title": "Recognition & Rewards", "desc": "Your hard work is valued and rewarded.", "icon": "fa-solid fa-hand-holding-dollar", "is_visible": True},
                {"title": "Supportive Environment", "desc": "A collaborative, inclusive culture.", "icon": "fa-solid fa-people-group", "is_visible": True},
                {"title": "Career Advancement", "desc": "A clear growth path forward.", "icon": "fa-solid fa-arrow-trend-up", "is_visible": True},
            ]
        if visible_only:
            return [d for d in data if d.get('is_visible', True) is not False]
        return data

    def get_career_areas(self, visible_only=True):
        import json
        data = None
        if self.career_areas_json:
            try:
                parsed = json.loads(self.career_areas_json)
                if isinstance(parsed, list) and len(parsed) > 0:
                    data = parsed
            except Exception:
                pass
        if data is None:
            data = [
                {"title": "Human Resource", "desc": "Build people-first solutions.", "icon": "fa-solid fa-people-group", "is_visible": True},
                {"title": "Marketing", "desc": "Drive brand success.", "icon": "fa-solid fa-bullhorn", "is_visible": True},
                {"title": "Information Technology", "desc": "Build the future.", "icon": "fa-solid fa-code", "is_visible": True},
                {"title": "Finance", "desc": "Manage growth with insight.", "icon": "fa-solid fa-chart-simple", "is_visible": True},
                {"title": "Sales & BD", "desc": "Create real opportunities.", "icon": "fa-solid fa-handshake", "is_visible": True},
                {"title": "Customer Support", "desc": "Deliver lasting relationships.", "icon": "fa-solid fa-headset", "is_visible": True},
            ]
        if visible_only:
            return [d for d in data if d.get('is_visible', True) is not False]
        return data

    def get_journey_steps(self, visible_only=True):
        import json
        data = None
        if self.journey_steps_json:
            try:
                parsed = json.loads(self.journey_steps_json)
                if isinstance(parsed, list) and len(parsed) > 0:
                    data = parsed
            except Exception:
                pass
        if data is None:
            data = [
                {"step": "1", "title": "Explore Opportunities", "desc": "Find the role that matches your skills.", "is_visible": True},
                {"step": "2", "title": "Apply", "desc": "Submit your application and let's connect.", "is_visible": True},
                {"step": "3", "title": "Interview", "desc": "Meet our team and show your talent.", "is_visible": True},
                {"step": "4", "title": "Get Hired", "desc": "Start your journey with Sky Vision.", "is_visible": True},
                {"step": "5", "title": "Grow & Succeed", "desc": "Learn and achieve new milestones.", "is_visible": True},
            ]
        if visible_only:
            return [d for d in data if d.get('is_visible', True) is not False]
        return data

    def get_look_for(self, visible_only=True):
        import json
        data = None
        if self.look_for_json:
            try:
                parsed = json.loads(self.look_for_json)
                if isinstance(parsed, list) and len(parsed) > 0:
                    data = parsed
            except Exception:
                pass
        if data is None:
            data = [
                {"title": "Positive Attitude", "icon": "fa-solid fa-face-smile", "is_visible": True},
                {"title": "Willingness to Learn", "icon": "fa-solid fa-lightbulb", "is_visible": True},
                {"title": "Team Player", "icon": "fa-solid fa-people-group", "is_visible": True},
                {"title": "Passion & Commitment", "icon": "fa-solid fa-bullseye", "is_visible": True},
                {"title": "Good Communication", "icon": "fa-solid fa-comments", "is_visible": True},
                {"title": "Integrity & Responsibility", "icon": "fa-solid fa-scale-balanced", "is_visible": True},
            ]
        if visible_only:
            return [d for d in data if d.get('is_visible', True) is not False]
        return data

    def get_benefits(self, visible_only=True):
        import json
        data = None
        if self.benefits_json:
            try:
                parsed = json.loads(self.benefits_json)
                if isinstance(parsed, list) and len(parsed) > 0:
                    data = parsed
            except Exception:
                pass
        if data is None:
            data = [
                {"title": "Competitive Salary", "icon": "fa-solid fa-sack-dollar", "is_visible": True},
                {"title": "Health Insurance", "icon": "fa-solid fa-briefcase-medical", "is_visible": True},
                {"title": "Training & Certification", "icon": "fa-solid fa-graduation-cap", "is_visible": True},
                {"title": "Flexible Work Culture", "icon": "fa-regular fa-calendar-days", "is_visible": True},
                {"title": "Performance Bonuses", "icon": "fa-solid fa-trophy", "is_visible": True},
                {"title": "Work-Life Balance", "icon": "fa-solid fa-people-arrows", "is_visible": True},
            ]
        if visible_only:
            return [d for d in data if d.get('is_visible', True) is not False]
        return data

    @property
    def clean_hero_title(self):
        import re
        raw = self.hero_title or "Find your direction. Build your future."
        return re.sub(r'<[^>]+>', '', raw).strip()

    def get_rendered_hero_title(self):
        clean_title = self.clean_hero_title
        hl = (self.hero_title_highlight or "Build your future.").strip()
        if hl and hl in clean_title:
            return clean_title.replace(hl, f'<span class="cr-accent">{hl}</span>', 1)
        return clean_title

    class Meta:
        db_table = 'career_page_settings'
        verbose_name = "Career Page Settings"
        verbose_name_plural = "Career Page Settings"

    def __str__(self):
        return "Career Page Settings"

    @classmethod
    def get_settings(cls):
        cached = cache.get(CAREER_PAGE_CACHE_KEY)
        if cached:
            return cached
        obj, created = cls.objects.get_or_create(id=1)
        cache.set(CAREER_PAGE_CACHE_KEY, obj, timeout=86400)
        return obj


@receiver([post_save, post_delete], sender=CareerPageSettings)
def invalidate_career_page_cache(sender, **kwargs):
    cache.delete(CAREER_PAGE_CACHE_KEY)
    cache.delete('public_site_context')



# =============================================================================
# BLOG PAGE SETTINGS (DYNAMIC SECTION-WISE MANAGEMENT)
# =============================================================================
BLOG_PAGE_CACHE_KEY = 'blog_page_settings_data'

class BlogPageSettings(models.Model):
    # Master Visibility Switches
    hero_visible = models.BooleanField(default=True)
    featured_article_visible = models.BooleanField(default=True)
    categories_visible = models.BooleanField(default=True)
    latest_posts_visible = models.BooleanField(default=True)
    newsletter_visible = models.BooleanField(default=True)
    recent_posts_visible = models.BooleanField(default=True)
    dream_cta_visible = models.BooleanField(default=True)
    stats_visible = models.BooleanField(default=True)

    # 1. Hero Section
    hero_chip = models.CharField(max_length=150, default="Insights · Career Tips · Recruitment Trends", blank=True)
    hero_title = models.CharField(max_length=255, default="Blog & Industry Insights")
    hero_title_highlight = models.CharField(max_length=100, default="Insights", blank=True)
    hero_subtitle = models.TextField(default="Stay updated with the latest job opportunities, recruitment trends, career tips, interview guidance, and professional development resources.")
    hero_image = models.ImageField(upload_to="pages/blog/hero/", blank=True, null=True)
    hero_btn1_text = models.CharField(max_length=50, default="Explore Articles", blank=True)
    hero_btn1_url = models.CharField(max_length=255, default="#latestPosts", blank=True)
    hero_btn2_text = models.CharField(max_length=50, default="Latest Jobs", blank=True)
    hero_btn2_url = models.CharField(max_length=255, default="/jobs/", blank=True)

    hero_badge_num = models.CharField(max_length=50, default="150+", blank=True)
    hero_badge_label = models.CharField(max_length=100, default="Articles Published", blank=True)
    hero_badge_icon = models.CharField(max_length=60, default="fa-solid fa-pen-nib", blank=True)

    # 2. Featured Article
    featured_section_title = models.CharField(max_length=150, default="Featured Article", blank=True)
    featured_tag = models.CharField(max_length=80, default="Career Tips", blank=True)
    featured_title = models.CharField(max_length=255, default="How to Prepare for Your First Job Interview")
    featured_desc = models.TextField(default="Starting your career can be exciting and challenging. Learn how to prepare for interviews, answer common questions confidently, dress professionally, and make a positive first impression.")
    featured_date = models.CharField(max_length=50, default="May 15, 2025", blank=True)
    featured_read_time = models.CharField(max_length=50, default="5 min read", blank=True)
    featured_link_url = models.CharField(max_length=255, default="#", blank=True)
    featured_btn_text = models.CharField(max_length=50, default="Read More", blank=True)
    featured_image = models.ImageField(upload_to="pages/blog/featured/", blank=True, null=True)

    # 3. Sidebar: Search & Popular Categories
    categories_title = models.CharField(max_length=150, default="Popular Categories", blank=True)
    popular_categories_json = models.TextField(blank=True, default="")

    # 4. Latest Blog Posts Grid
    latest_posts_title = models.CharField(max_length=150, default="Latest Blog Posts", blank=True)
    latest_view_more_text = models.CharField(max_length=50, default="View More Articles", blank=True)
    latest_view_more_url = models.CharField(max_length=255, default="#", blank=True)
    latest_posts_json = models.TextField(blank=True, default="")

    # 5. Sidebar: Newsletter Box
    newsletter_title = models.CharField(max_length=255, default="Stay Updated with the Latest Career Opportunities")
    newsletter_desc = models.TextField(default="Subscribe to receive the latest job openings, recruitment news, interview tips, and career guidance.")
    newsletter_placeholder = models.CharField(max_length=100, default="Enter your email", blank=True)
    newsletter_btn_text = models.CharField(max_length=50, default="Subscribe Now", blank=True)

    # 6. Sidebar: Recent Posts
    recent_posts_title = models.CharField(max_length=150, default="Recent Posts", blank=True)
    recent_posts_json = models.TextField(blank=True, default="")

    # 7. Looking for Your Dream Job? (Dream CTA Banner)
    dream_cta_title = models.CharField(max_length=255, default="Looking for Your Dream Job?")
    dream_cta_desc = models.TextField(default="Whether you're a fresher or an experienced professional, Sky Vision Group Consultancy connects talented candidates with trusted employers across multiple industries.")
    dream_btn1_text = models.CharField(max_length=50, default="Find Jobs", blank=True)
    dream_btn1_url = models.CharField(max_length=255, default="/jobs/", blank=True)
    dream_btn2_text = models.CharField(max_length=50, default="Contact Us", blank=True)
    dream_btn2_url = models.CharField(max_length=255, default="/contact/", blank=True)
    dream_image = models.ImageField(upload_to="pages/blog/cta/", blank=True, null=True)

    # 4 Dream CTA Features
    dream_feat_1_icon = models.CharField(max_length=60, default="fa-solid fa-building-shield", blank=True)
    dream_feat_1_title = models.CharField(max_length=100, default="Trusted by Employers", blank=True)
    dream_feat_1_desc = models.CharField(max_length=150, default="We work with top companies across industries.", blank=True)

    dream_feat_2_icon = models.CharField(max_length=60, default="fa-solid fa-shield-halved", blank=True)
    dream_feat_2_title = models.CharField(max_length=100, default="Verified Opportunities", blank=True)
    dream_feat_2_desc = models.CharField(max_length=150, default="100% genuine job openings and verified employers.", blank=True)

    dream_feat_3_icon = models.CharField(max_length=60, default="fa-solid fa-people-arrows", blank=True)
    dream_feat_3_title = models.CharField(max_length=100, default="Career Support", blank=True)
    dream_feat_3_desc = models.CharField(max_length=150, default="Expert guidance for interviews, resume & career growth.", blank=True)

    dream_feat_4_icon = models.CharField(max_length=60, default="fa-solid fa-diagram-project", blank=True)
    dream_feat_4_title = models.CharField(max_length=100, default="Wide Job Network", blank=True)
    dream_feat_4_desc = models.CharField(max_length=150, default="Thousands of job opportunities across India.", blank=True)

    # 8. Stats Counter Bar
    stat_1_num = models.CharField(max_length=50, default="1000", blank=True)
    stat_1_label = models.CharField(max_length=100, default="Job Seekers Placed", blank=True)
    stat_1_icon = models.CharField(max_length=60, default="fa-solid fa-user-group", blank=True)

    stat_2_num = models.CharField(max_length=50, default="500", blank=True)
    stat_2_label = models.CharField(max_length=100, default="Hiring Partners", blank=True)
    stat_2_icon = models.CharField(max_length=60, default="fa-solid fa-handshake", blank=True)

    stat_3_num = models.CharField(max_length=50, default="20", blank=True)
    stat_3_label = models.CharField(max_length=100, default="Industries Covered", blank=True)
    stat_3_icon = models.CharField(max_length=60, default="fa-solid fa-industry", blank=True)

    stat_4_num = models.CharField(max_length=50, default="15", blank=True)
    stat_4_label = models.CharField(max_length=100, default="Years of Experience", blank=True)
    stat_4_icon = models.CharField(max_length=60, default="fa-solid fa-award", blank=True)

    # 9. SEO & Meta
    meta_title = models.CharField(max_length=255, default="Latest Insights & Blog — Sky Vision Group Consultancy", blank=True)
    meta_description = models.TextField(default="Stay updated with the latest job opportunities, recruitment trends, career tips, interview guidance, and professional development resources.", blank=True)
    meta_keywords = models.CharField(max_length=255, default="sky vision blog, career tips, recruitment trends, interview guidance, jobs lucknow", blank=True)

    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_popular_categories(self, visible_only=True):
        import json
        data = None
        if self.popular_categories_json:
            try:
                parsed = json.loads(self.popular_categories_json)
                if isinstance(parsed, list) and len(parsed) > 0:
                    data = parsed
            except Exception:
                pass
        if data is None:
            data = [
                {"name": "Career Guidance", "icon": "fa-solid fa-compass", "count": "18", "link": "#", "is_visible": True},
                {"name": "Interview Tips", "icon": "fa-solid fa-comments", "count": "15", "link": "#", "is_visible": True},
                {"name": "Resume Writing", "icon": "fa-solid fa-file-lines", "count": "12", "link": "#", "is_visible": True},
                {"name": "IT Jobs", "icon": "fa-solid fa-laptop-code", "count": "20", "link": "#", "is_visible": True},
                {"name": "BPO Jobs", "icon": "fa-solid fa-headset", "count": "10", "link": "#", "is_visible": True},
                {"name": "Sales & Marketing", "icon": "fa-solid fa-chart-line", "count": "14", "link": "#", "is_visible": True},
                {"name": "Healthcare Jobs", "icon": "fa-solid fa-heart-pulse", "count": "09", "link": "#", "is_visible": True},
                {"name": "Driver Jobs", "icon": "fa-solid fa-car", "count": "08", "link": "#", "is_visible": True},
                {"name": "Delivery Jobs", "icon": "fa-solid fa-truck", "count": "07", "link": "#", "is_visible": True},
                {"name": "HR & Recruitment", "icon": "fa-solid fa-users", "count": "11", "link": "#", "is_visible": True},
                {"name": "Work From Home", "icon": "fa-solid fa-house-laptop", "count": "16", "link": "#", "is_visible": True},
                {"name": "Government Jobs", "icon": "fa-solid fa-landmark", "count": "13", "link": "#", "is_visible": True},
            ]
        if visible_only:
            return [d for d in data if d.get('is_visible', True) is not False]
        return data

    def get_latest_posts(self, visible_only=True):
        import json
        data = None
        if self.latest_posts_json:
            try:
                parsed = json.loads(self.latest_posts_json)
                if isinstance(parsed, list) and len(parsed) > 0:
                    data = parsed
            except Exception:
                pass
        if data is None:
            data = [
                {"title": "Top 10 Interview Questions and Best Answers", "tag": "Interview Tips", "icon": "fa-solid fa-comments", "date": "May 14, 2025", "read_time": "4 min read", "image": "images/blog/blog image 2.png", "link": "#", "is_visible": True},
                {"title": "Resume Writing Tips That Get You Hired", "tag": "Resume Writing", "icon": "fa-solid fa-file-lines", "date": "May 13, 2025", "read_time": "5 min read", "image": "images/blog/blog image 9.png", "link": "#", "is_visible": True},
                {"title": "Work From Home Jobs: Opportunities and Benefits", "tag": "Work From Home", "icon": "fa-solid fa-house-laptop", "date": "May 12, 2025", "read_time": "6 min read", "image": "images/blog/blog image 1.png", "link": "#", "is_visible": True},
                {"title": "Career Growth in the IT Industry", "tag": "IT Jobs", "icon": "fa-solid fa-laptop-code", "date": "May 11, 2025", "read_time": "5 min read", "image": "images/blog/blog image 3.png", "link": "#", "is_visible": True},
                {"title": "How to Improve Communication Skills for Job Interviews", "tag": "Career Tips", "icon": "fa-solid fa-lightbulb", "date": "May 10, 2025", "read_time": "4 min read", "image": "images/blog/blog image 2.png", "link": "#", "is_visible": True},
                {"title": "Full-Time vs Part-Time Jobs: Which One Is Right for You?", "tag": "Career Guidance", "icon": "fa-solid fa-scale-balanced", "date": "May 09, 2025", "read_time": "5 min read", "image": "images/blog/blog image 4.png", "link": "#", "is_visible": True},
            ]
        if visible_only:
            return [d for d in data if d.get('is_visible', True) is not False]
        return data

    def get_recent_posts(self, visible_only=True):
        import json
        data = None
        if self.recent_posts_json:
            try:
                parsed = json.loads(self.recent_posts_json)
                if isinstance(parsed, list) and len(parsed) > 0:
                    data = parsed
            except Exception:
                pass
        if data is None:
            data = [
                {"title": "Soft Skills Every Employer Looks For in 2025", "date": "May 08, 2025", "image": "images/blog/blog image 6.png", "link": "#", "is_visible": True},
                {"title": "How Freshers Can Kickstart Their Career in 2025", "date": "May 07, 2025", "image": "images/blog/blog image 8.png", "link": "#", "is_visible": True},
                {"title": "The Importance of LinkedIn for Job Seekers", "date": "May 06, 2025", "image": "images/blog/blog image 7.png", "link": "#", "is_visible": True},
            ]
        if visible_only:
            return [d for d in data if d.get('is_visible', True) is not False]
        return data

    @property
    def clean_hero_title(self):
        import re
        raw = self.hero_title or "Blog & Industry Insights"
        return re.sub(r'<[^>]+>', '', raw).strip()

    def get_rendered_hero_title(self):
        clean_title = self.clean_hero_title
        hl = (self.hero_title_highlight or "Insights").strip()
        if hl and hl in clean_title:
            return clean_title.replace(hl, f'<span class="highlight">{hl}</span>', 1)
        return clean_title

    class Meta:
        db_table = 'blog_page_settings'
        verbose_name = "Blog Page Settings"
        verbose_name_plural = "Blog Page Settings"

    def __str__(self):
        return "Blog Page Settings"

    @classmethod
    def get_settings(cls):
        cached = cache.get(BLOG_PAGE_CACHE_KEY)
        if cached:
            return cached
        obj, created = cls.objects.get_or_create(id=1)
        cache.set(BLOG_PAGE_CACHE_KEY, obj, timeout=86400)
        return obj


@receiver([post_save, post_delete], sender=BlogPageSettings)
def invalidate_blog_page_cache(sender, **kwargs):
    cache.delete(BLOG_PAGE_CACHE_KEY)
    cache.delete('public_site_context')


# =============================================================================
# GALLERY PAGE SETTINGS (DYNAMIC SECTION-WISE MANAGEMENT)
# =============================================================================
GALLERY_PAGE_CACHE_KEY = 'gallery_page_settings_data'

class GalleryPageSettings(models.Model):
    # Master Visibility Switches
    header_visible = models.BooleanField(default=True)
    gallery_visible = models.BooleanField(default=True)
    info_boxes_visible = models.BooleanField(default=True)
    contact_visible = models.BooleanField(default=True)
    info_cards_visible = models.BooleanField(default=True)

    # 1. Header Banner
    header_eyebrow = models.CharField(max_length=150, default="Get To Know Us", blank=True)
    header_title = models.CharField(max_length=255, default="Gallary of Sky Vision Group of Consultancy")
    header_breadcrumb_root = models.CharField(max_length=100, default="Home", blank=True)
    header_breadcrumb_sub = models.CharField(max_length=100, default="About Us", blank=True)

    # 2. Our Gallery Section
    gallery_title = models.CharField(max_length=150, default="OUR GALLERY")
    gallery_items_json = models.TextField(blank=True, default="")

    # 3. Gallery Info Boxes (3 Boxes)
    box1_icon = models.CharField(max_length=60, default="fa-solid fa-bullseye", blank=True)
    box1_color = models.CharField(max_length=30, default="red-icon", blank=True)
    box1_title = models.CharField(max_length=255, default="LOOKING FOR THE RIGHT TALENT")
    box1_text = models.TextField(default="We help you build real skills and grow faster.", blank=True)
    box1_btn_text = models.CharField(max_length=80, default="VIEW PROGRAMS", blank=True)
    box1_btn_url = models.CharField(max_length=255, default="/services/", blank=True)

    box2_icon = models.CharField(max_length=60, default="fa-solid fa-globe", blank=True)
    box2_color = models.CharField(max_length=30, default="blue-icon", blank=True)
    box2_title = models.CharField(max_length=255, default="LOOKING FOR A GREAT OPPORTUNITY")
    box2_text = models.TextField(default="Explore our specialized programs for you.", blank=True)
    box2_btn_text = models.CharField(max_length=80, default="EXPLORE NOW", blank=True)
    box2_btn_url = models.CharField(max_length=255, default="/jobs/", blank=True)

    box3_icon = models.CharField(max_length=60, default="fa-solid fa-graduation-cap", blank=True)
    box3_color = models.CharField(max_length=30, default="blue-icon", blank=True)
    box3_title = models.CharField(max_length=255, default="PARTICIPATE IN OUR INTERNSHIP PROGRAM")
    box3_text = models.TextField(default="Gain hands-on experience and kickstart your career.", blank=True)
    box3_btn_text = models.CharField(max_length=80, default="APPLY INTERNSHIP", blank=True)
    box3_btn_url = models.CharField(max_length=255, default="/services/internship-training/", blank=True)

    # 4. Get In Touch & Send Message Form
    contact_title = models.CharField(max_length=150, default="GET IN TOUCH")
    contact_phone = models.CharField(max_length=50, default="+91 9120333299", blank=True)
    contact_email = models.CharField(max_length=120, default="info@skyvisiongroup.in", blank=True)
    contact_website = models.CharField(max_length=120, default="www.skyvisiongroup.in", blank=True)
    contact_address = models.TextField(default="12/2 Arvindo Park Road,\nSector 12, Indira Nagar,\nLucknow, Uttar Pradesh", blank=True)

    social_facebook = models.CharField(max_length=255, default="https://facebook.com", blank=True)
    social_instagram = models.CharField(max_length=255, default="https://instagram.com", blank=True)
    social_linkedin = models.CharField(max_length=255, default="https://linkedin.com", blank=True)
    social_youtube = models.CharField(max_length=255, default="https://youtube.com", blank=True)

    form_title = models.CharField(max_length=150, default="SEND US A MESSAGE")
    form_btn_text = models.CharField(max_length=80, default="Submit Now", blank=True)

    # 5. Info Cards Section (Address, Call Us, Email Us)
    card_address_title = models.CharField(max_length=150, default="Address & Location")
    card_address_text = models.TextField(default="12/2 Arvindo Park Road, Sector 12,\nIndira Nagar, Lucknow, UP 226016", blank=True)
    card_address_map_url = models.TextField(default="https://www.google.com/maps?q=12/2+Arvindo+Park+Road+Sector+12+Indira+Nagar+Lucknow+Uttar+Pradesh+226016&output=embed", blank=True)
    card_address_map_badge_url = models.TextField(default="https://www.google.com/maps/search/?api=1&query=12%2F2+Arvindo+Park+Road+Sector+12+Indira+Nagar+Lucknow+UP+226016", blank=True)
    card_address_directions_url = models.TextField(default="https://www.google.com/maps/dir/?api=1&destination=12%2F2+Arvindo+Park+Road+Sector+12+Indira+Nagar+Lucknow+UP+226016", blank=True)
    card_address_directions_text = models.CharField(max_length=80, default="Get Directions", blank=True)

    card_call_title = models.CharField(max_length=150, default="Call Us")
    call_rows_json = models.TextField(blank=True, default="")

    card_email_title = models.CharField(max_length=150, default="Email Us")
    email_rows_json = models.TextField(blank=True, default="")

    # 6. SEO & Meta Tags
    meta_title = models.CharField(max_length=255, default="Our Gallery & Life at Sky Vision — Sky Vision Group Consultancy", blank=True)
    meta_description = models.TextField(default="Explore our photo gallery showcasing corporate events, placement drives, interview rounds, team activities and life at Sky Vision.", blank=True)
    meta_keywords = models.CharField(max_length=255, default="sky vision gallery, placement drives, corporate events, interview rounds, lucknow consultancy photos", blank=True)

    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_gallery_items(self, visible_only=True):
        import json
        data = None
        if self.gallery_items_json:
            try:
                parsed = json.loads(self.gallery_items_json)
                if isinstance(parsed, list) and len(parsed) > 0:
                    data = parsed
            except Exception:
                pass
        if data is None:
            data = [
                {"title": "Corporate Events", "image": "images/general/corporate event.png", "is_visible": True, "order": 1},
                {"title": "Interview Rounds", "image": "images/general/interview round.png", "is_visible": True, "order": 2},
                {"title": "Placement Drives", "image": "images/general/placement drives.png", "is_visible": True, "order": 3},
                {"title": "Training Sessions", "image": "images/general/training session.png", "is_visible": True, "order": 4},
                {"title": "Workshops", "image": "images/general/workshop.png", "is_visible": True, "order": 5},
                {"title": "Team Activities", "image": "images/general/team activities.png", "is_visible": True, "order": 6},
            ]
        if visible_only:
            return [d for d in data if d.get('is_visible', True) is not False]
        return data

    def get_call_rows(self, visible_only=True):
        import json
        data = None
        if self.call_rows_json:
            try:
                parsed = json.loads(self.call_rows_json)
                if isinstance(parsed, list) and len(parsed) > 0:
                    data = parsed
            except Exception:
                pass
        if data is None:
            data = [
                {"label": "Manager", "phone": "+91 9120335299", "href": "tel:+919120335299", "is_visible": True, "order": 1},
                {"label": "WhatsApp", "phone": "7068115299", "href": "https://wa.me/919120335299", "is_visible": True, "order": 2},
                {"label": "HR", "phone": "+91 7068115299", "href": "tel:+917068115299", "is_visible": True, "order": 3},
                {"label": "BDM", "phone": "+91 9532625299", "href": "tel:+919532625299", "is_visible": True, "order": 4},
                {"label": "Landline", "phone": "+91 0522 422 7633", "href": "tel:+915224227633", "is_visible": True, "order": 5},
            ]
        if visible_only:
            return [d for d in data if d.get('is_visible', True) is not False]
        return data

    def get_email_rows(self, visible_only=True):
        import json
        data = None
        if self.email_rows_json:
            try:
                parsed = json.loads(self.email_rows_json)
                if isinstance(parsed, list) and len(parsed) > 0:
                    data = parsed
            except Exception:
                pass
        if data is None:
            data = [
                {"label": "Manager", "email": "hr@svgconsultancy.com", "href": "mailto:hr@svgconsultancy.com", "is_visible": True, "order": 1},
                {"label": "HR", "email": "hrsvg.lkc@gmail.com", "href": "mailto:hrsvg.lkc@gmail.com", "is_visible": True, "order": 2},
                {"label": "CEO", "email": "enquiry@svgconsultancy.com", "href": "mailto:enquiry@svgconsultancy.com", "is_visible": True, "order": 3},
                {"label": "Support", "email": "enquiry.svgc@gmail.com", "href": "mailto:enquiry.svgc@gmail.com", "is_visible": True, "order": 4},
            ]
        if visible_only:
            return [d for d in data if d.get('is_visible', True) is not False]
        return data

    class Meta:
        db_table = 'gallery_page_settings'
        verbose_name = "Gallery Page Settings"
        verbose_name_plural = "Gallery Page Settings"

    def __str__(self):
        return "Gallery Page Settings"

    @classmethod
    def get_settings(cls):
        cached = cache.get(GALLERY_PAGE_CACHE_KEY)
        if cached:
            return cached
        obj, created = cls.objects.get_or_create(id=1)
        cache.set(GALLERY_PAGE_CACHE_KEY, obj, timeout=86400)
        return obj


@receiver([post_save, post_delete], sender=GalleryPageSettings)
def invalidate_gallery_page_cache(sender, **kwargs):
    cache.delete(GALLERY_PAGE_CACHE_KEY)
    cache.delete('public_site_context')


# =====================================================================
# CONTACT US PAGE SETTINGS (SINGLETON)
# =====================================================================
CONTACT_PAGE_CACHE_KEY = 'contact_page_settings_obj'

class ContactPageSettings(models.Model):
    # Master Visibility Switches
    header_visible = models.BooleanField(default=True)
    contact_section_visible = models.BooleanField(default=True)
    info_cards_visible = models.BooleanField(default=True)

    # 1. Page Header Banner
    header_eyebrow = models.CharField(max_length=150, default="Get To Know Us")
    header_title = models.CharField(max_length=255, default="Contact Company of Sky Vision Group of Consultancy")
    header_breadcrumb_root = models.CharField(max_length=100, default="Home")
    header_breadcrumb_sub = models.CharField(max_length=100, default="contact Us")

    # 2. Contact Section (Left Info, Form, Right Location Badge)
    contact_phone = models.CharField(max_length=50, default="+91 7068115299", blank=True)
    contact_email = models.CharField(max_length=120, default="hr@svgconsultancy.com", blank=True)
    contact_website = models.CharField(max_length=120, default="www.skyvisiongroup.in", blank=True)
    contact_address = models.TextField(default="12/2 Arvindo Park Road, Sector 12, Indira Nagar, Lucknow, UP", blank=True)

    social_facebook = models.CharField(max_length=255, default="https://www.facebook.com/share/197C5xryds/", blank=True)
    social_instagram = models.CharField(max_length=255, default="https://www.instagram.com/skyvisiongroupconsultancy?igsh=NGpkb2NnZ2hhM21k", blank=True)
    social_linkedin = models.CharField(max_length=255, default="https://www.linkedin.com/company/skyvisiongroup/", blank=True)
    social_youtube = models.CharField(max_length=255, default="https://youtube.com/@skyvisiongroupconsultancy?si=-b8dk8MV6SzJfhM1", blank=True)

    form_title = models.CharField(max_length=150, default="SEND US A MESSAGE")
    form_btn_text = models.CharField(max_length=80, default="Submit Now", blank=True)

    location_badge_title = models.CharField(max_length=150, default="Sky Vision Group Consultancy", blank=True)
    location_badge_address = models.TextField(default="12/2 Arvindo Park Road,\nSector 12, Indira Nagar,\nLucknow, Uttar Pradesh 226016", blank=True)
    location_badge_image = models.CharField(max_length=255, default="images/hero/map image.png", blank=True)
    location_map_url = models.TextField(default="https://maps.google.com/maps?q=12/2+Arvindo+Park+Road+Sector+12+Indira+Nagar+Lucknow+Uttar+Pradesh+226016&t=&z=15&ie=UTF8&iwloc=&output=embed", blank=True)

    # 3. Contact Info Cards (Address, Call Us, Email Us)
    card_address_title = models.CharField(max_length=150, default="Address & Location")
    card_address_text = models.TextField(default="12/2 Arvindo Park Road, Sector 12,\nIndira Nagar, Lucknow, UP 226016", blank=True)
    card_address_map_url = models.TextField(default="https://maps.google.com/maps?q=12/2+Arvindo+Park+Road+Sector+12+Indira+Nagar+Lucknow+Uttar+Pradesh+226016&t=&z=15&ie=UTF8&iwloc=&output=embed", blank=True)
    card_address_map_badge_url = models.TextField(default="https://www.google.com/maps/search/?api=1&query=12%2F2+Arvindo+Park+Road+Sector+12+Indira+Nagar+Lucknow+UP+226016", blank=True)
    card_address_directions_url = models.TextField(default="https://www.google.com/maps/dir/?api=1&destination=12%2F2+Arvindo+Park+Road+Sector+12+Indira+Nagar+Lucknow+UP+226016", blank=True)
    card_address_directions_text = models.CharField(max_length=80, default="Get Directions", blank=True)

    card_call_title = models.CharField(max_length=150, default="Call Us")
    call_rows_json = models.TextField(blank=True, default="")

    card_email_title = models.CharField(max_length=150, default="Email Us")
    email_rows_json = models.TextField(blank=True, default="")

    def get_call_rows(self, visible_only=True):
        import json
        if self.call_rows_json:
            try:
                data = json.loads(self.call_rows_json)
            except Exception:
                data = []
        else:
            data = [
                {"label": "Manager", "phone": "+91 9120335299", "href": "tel:+919120335299", "is_visible": True, "order": 1},
                {"label": "WhatsApp", "phone": "7068115299", "href": "https://wa.me/917068115299", "is_visible": True, "order": 2},
                {"label": "HR", "phone": "+91 7068115299", "href": "tel:+917068115299", "is_visible": True, "order": 3},
                {"label": "BDM", "phone": "+91 9532625299", "href": "tel:+919532625299", "is_visible": True, "order": 4},
                {"label": "Landline", "phone": "+91 0522 422 7633", "href": "tel:+915224227633", "is_visible": True, "order": 5},
            ]
        if visible_only:
            return [d for d in data if d.get('is_visible', True) is not False]
        return data

    def get_email_rows(self, visible_only=True):
        import json
        if self.email_rows_json:
            try:
                data = json.loads(self.email_rows_json)
            except Exception:
                data = []
        else:
            data = [
                {"label": "Manager", "email": "hr@svgconsultancy.com", "href": "mailto:info@skyvisiongroup.in", "is_visible": True, "order": 1},
                {"label": "HR", "email": "hrsvg.lkc@gmail.com", "href": "mailto:hr@skyvisiongroup.in", "is_visible": True, "order": 2},
                {"label": "CEO", "email": "enquiry@svgconsultancy.com", "href": "mailto:ceo@skyvisiongroup.in", "is_visible": True, "order": 3},
                {"label": "Support", "email": "enquiry.svgc@gmail.com", "href": "mailto:support@skyvisiongroup.in", "is_visible": True, "order": 4},
            ]
        if visible_only:
            return [d for d in data if d.get('is_visible', True) is not False]
        return data

    class Meta:
        db_table = 'contact_page_settings'
        verbose_name = "Contact Page Settings"
        verbose_name_plural = "Contact Page Settings"

    def __str__(self):
        return "Contact Page Settings"

    @classmethod
    def get_settings(cls):
        cached = cache.get(CONTACT_PAGE_CACHE_KEY)
        if cached:
            return cached
        obj, created = cls.objects.get_or_create(id=1)
        cache.set(CONTACT_PAGE_CACHE_KEY, obj, timeout=86400)
        return obj


@receiver([post_save, post_delete], sender=ContactPageSettings)
def invalidate_contact_page_cache(sender, **kwargs):
    cache.delete(CONTACT_PAGE_CACHE_KEY)
    cache.delete('public_site_context')
