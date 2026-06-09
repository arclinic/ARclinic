# Active Schema.org Types (2024-2026)

## Always Active
- Organization
- LocalBusiness
- Article / BlogPosting / NewsArticle
- Product / ProductGroup / Offer
- Review / AggregateRating
- BreadcrumbList
- WebSite / WebPage
- Person / ProfilePage / ContactPage
- VideoObject / ImageObject
- Event
- JobPosting
- Course
- DiscussionForumPosting
- Reservation / OrderAction

## Restricted (use with caution)
- **FAQPage**: only for government & healthcare authority sites (since Aug 2023)

## Deprecated (do NOT use)
- **HowTo**: rich results removed September 2023
- **SpecialAnnouncement**: deprecated July 2025
- **ClaimReview**: retired June 2025
- **VehicleListing**: retired June 2025
- **EstimatedSalary**: retired June 2025
- **LearningVideo**: retired June 2025
- **CourseInfo carousel**: retired June 2025

## JSON-LD Best Practices
1. Use `@context: "https://schema.org"`
2. Use `@id` for cross-referencing between blocks
3. URLs must be absolute (https://...)
4. Dates in ISO 8601 (YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS)
5. Images with `width` and `height` as ImageObject
6. `sameAs` array for social profiles (minimum 2)
