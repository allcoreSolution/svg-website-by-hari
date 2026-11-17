from django.contrib import admin
from .models import (
    SiteSettings, NavItem, FooterColumn, FooterLink, SocialLink, FooterService,
    HomePageSettings, HeroStat, GrowthStep, HomeServiceCard, WhyChooseItem,
    HomeIndustryItem, InternshipCard, InternshipHighlight, FeaturedCandidate,
    GalleryImage, GalleryInfoBox
)

@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ('site_name', 'helpline_phone', 'support_email', 'updated_at')

@admin.register(NavItem)
class NavItemAdmin(admin.ModelAdmin):
    list_display = ('label', 'url', 'parent', 'order', 'is_visible', 'new_tab')
    list_filter = ('is_visible', 'parent')
    ordering = ('order', 'id')

class FooterLinkInline(admin.TabularInline):
    model = FooterLink
    extra = 1

@admin.register(FooterColumn)
class FooterColumnAdmin(admin.ModelAdmin):
    list_display = ('title', 'order', 'is_visible')
    inlines = [FooterLinkInline]

@admin.register(SocialLink)
class SocialLinkAdmin(admin.ModelAdmin):
    list_display = ('platform', 'url', 'is_enabled', 'order')
    list_editable = ('is_enabled', 'order')

@admin.register(FooterService)
class FooterServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'url', 'order', 'is_visible')
    list_editable = ('order', 'is_visible')

@admin.register(HomePageSettings)
class HomePageSettingsAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'hero_title', 'updated_at')

@admin.register(HeroStat)
class HeroStatAdmin(admin.ModelAdmin):
    list_display = ('value', 'label', 'order', 'is_visible')
    list_editable = ('order', 'is_visible')

@admin.register(GrowthStep)
class GrowthStepAdmin(admin.ModelAdmin):
    list_display = ('step_number', 'title', 'subtitle', 'order', 'is_visible')
    list_editable = ('order', 'is_visible')

@admin.register(HomeServiceCard)
class HomeServiceCardAdmin(admin.ModelAdmin):
    list_display = ('title', 'icon_color', 'link_url', 'order', 'is_visible')
    list_editable = ('order', 'is_visible')

@admin.register(WhyChooseItem)
class WhyChooseItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'order', 'is_visible')
    list_editable = ('order', 'is_visible')

@admin.register(HomeIndustryItem)
class HomeIndustryItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'link_url', 'order', 'is_visible')
    list_editable = ('order', 'is_visible')

@admin.register(InternshipCard)
class InternshipCardAdmin(admin.ModelAdmin):
    list_display = ('domain_name', 'icon_color', 'order', 'is_visible')
    list_editable = ('order', 'is_visible')

@admin.register(InternshipHighlight)
class InternshipHighlightAdmin(admin.ModelAdmin):
    list_display = ('text', 'item_type', 'order', 'is_visible')
    list_filter = ('item_type', 'is_visible')
    list_editable = ('order', 'is_visible')

@admin.register(FeaturedCandidate)
class FeaturedCandidateAdmin(admin.ModelAdmin):
    list_display = ('name', 'role', 'experience', 'show_publicly', 'order', 'is_visible')
    list_filter = ('show_publicly', 'is_visible')
    list_editable = ('show_publicly', 'order', 'is_visible')

@admin.register(GalleryImage)
class GalleryImageAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'show_on_home', 'order', 'is_visible')
    list_filter = ('category', 'show_on_home', 'is_visible')
    list_editable = ('show_on_home', 'order', 'is_visible')

@admin.register(GalleryInfoBox)
class GalleryInfoBoxAdmin(admin.ModelAdmin):
    list_display = ('title', 'btn_label', 'btn_url', 'order', 'is_visible')
    list_editable = ('order', 'is_visible')


from .models import (
    AboutCompanySettings, AboutWhyCard, AboutTestimonial,
    AboutTestimonialStat, AboutTrustPoint, AboutPartnerLogo,
    AboutIndustryItem, CEOMessageSettings, CEOLeadershipPrinciple,
    CEOStatBadge
)

@admin.register(AboutCompanySettings)
class AboutCompanySettingsAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'page_title', 'updated_at')

@admin.register(AboutWhyCard)
class AboutWhyCardAdmin(admin.ModelAdmin):
    list_display = ('title', 'icon_class', 'order', 'is_visible')
    list_editable = ('order', 'is_visible')

@admin.register(AboutIndustryItem)
class AboutIndustryItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'icon_class', 'link_url', 'order', 'is_visible')
    list_editable = ('order', 'is_visible')

@admin.register(AboutTestimonial)
class AboutTestimonialAdmin(admin.ModelAdmin):
    list_display = ('name', 'testimonial_type', 'role', 'rating', 'order', 'is_visible')
    list_filter = ('testimonial_type', 'is_visible')
    list_editable = ('order', 'is_visible')

@admin.register(AboutTestimonialStat)
class AboutTestimonialStatAdmin(admin.ModelAdmin):
    list_display = ('label', 'count', 'suffix', 'color', 'order', 'is_visible')
    list_editable = ('order', 'is_visible')

@admin.register(AboutTrustPoint)
class AboutTrustPointAdmin(admin.ModelAdmin):
    list_display = ('title', 'icon_class', 'order', 'is_visible')
    list_editable = ('order', 'is_visible')

@admin.register(AboutPartnerLogo)
class AboutPartnerLogoAdmin(admin.ModelAdmin):
    list_display = ('name', 'icon_class', 'order', 'is_visible')
    list_editable = ('order', 'is_visible')

@admin.register(CEOMessageSettings)
class CEOMessageSettingsAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'ceo_name', 'page_title', 'updated_at')

@admin.register(CEOLeadershipPrinciple)
class CEOLeadershipPrincipleAdmin(admin.ModelAdmin):
    list_display = ('title', 'icon_class', 'order', 'is_visible')
    list_editable = ('order', 'is_visible')

@admin.register(CEOStatBadge)
class CEOStatBadgeAdmin(admin.ModelAdmin):
    list_display = ('label', 'value', 'icon_class', 'order', 'is_visible')
    list_editable = ('order', 'is_visible')


from .models import (
    OurTeamSettings, TeamMember, TeamFeatureHighlight,
    TeamStat, TeamDepartment, TeamTrustPoint, TeamCoreValue
)

@admin.register(OurTeamSettings)
class OurTeamSettingsAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'hero_title', 'updated_at')

@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ('name', 'role', 'category', 'order', 'is_visible', 'show_on_about_page')
    list_filter = ('category', 'is_visible', 'show_on_about_page')
    list_editable = ('order', 'is_visible', 'show_on_about_page')

@admin.register(TeamFeatureHighlight)
class TeamFeatureHighlightAdmin(admin.ModelAdmin):
    list_display = ('title', 'icon', 'order', 'is_visible')
    list_editable = ('order', 'is_visible')

@admin.register(TeamStat)
class TeamStatAdmin(admin.ModelAdmin):
    list_display = ('label', 'count', 'suffix', 'order', 'is_visible')
    list_editable = ('order', 'is_visible')

@admin.register(TeamDepartment)
class TeamDepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'icon', 'order', 'is_visible')
    list_editable = ('order', 'is_visible')

@admin.register(TeamTrustPoint)
class TeamTrustPointAdmin(admin.ModelAdmin):
    list_display = ('title', 'icon_class', 'order', 'is_visible')
    list_editable = ('order', 'is_visible')

@admin.register(TeamCoreValue)
class TeamCoreValueAdmin(admin.ModelAdmin):
    list_display = ('title', 'icon', 'order', 'is_visible')
    list_editable = ('order', 'is_visible')


from .models import (
    OurJourneySettings, JourneyMilestone, JourneyStoryParagraph,
    JourneyStoryCard, JourneyMilestoneCard, JourneyImpactItem,
    JourneyStat, JourneyFutureGoal
)

@admin.register(OurJourneySettings)
class OurJourneySettingsAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'hero_title', 'updated_at')

@admin.register(JourneyMilestone)
class JourneyMilestoneAdmin(admin.ModelAdmin):
    list_display = ('year', 'title', 'badge_label', 'icon_class', 'order', 'is_visible')
    list_editable = ('order', 'is_visible')

@admin.register(JourneyStoryParagraph)
class JourneyStoryParagraphAdmin(admin.ModelAdmin):
    list_display = ('id', 'text', 'order', 'is_visible')
    list_editable = ('order', 'is_visible')

@admin.register(JourneyStoryCard)
class JourneyStoryCardAdmin(admin.ModelAdmin):
    list_display = ('title', 'icon', 'color', 'order', 'is_visible')
    list_editable = ('order', 'is_visible')

@admin.register(JourneyMilestoneCard)
class JourneyMilestoneCardAdmin(admin.ModelAdmin):
    list_display = ('year', 'title', 'icon_class', 'order', 'is_visible')
    list_editable = ('order', 'is_visible')

@admin.register(JourneyImpactItem)
class JourneyImpactItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'icon', 'order', 'is_visible')
    list_editable = ('order', 'is_visible')

@admin.register(JourneyStat)
class JourneyStatAdmin(admin.ModelAdmin):
    list_display = ('count', 'suffix', 'label', 'icon', 'order', 'is_visible')
    list_editable = ('order', 'is_visible')

@admin.register(JourneyFutureGoal)
class JourneyFutureGoalAdmin(admin.ModelAdmin):
    list_display = ('text', 'icon', 'order', 'is_visible')
    list_editable = ('order', 'is_visible')



