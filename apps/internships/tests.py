import json
from django.test import TestCase, Client
from apps.accounts.models import AdminUser
from apps.internships.models import InternshipEnquiry, InternshipProvider, Internship, InternshipApplication


class InternshipsModuleTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        # Create an admin user and log in via session
        self.admin = AdminUser.objects.create(
            email="admin@test.com",
            is_active=True
        )
        self.admin.set_password("admin123")
        self.admin.save()

        # Set session
        session = self.client.session
        session['admin_id'] = self.admin.id
        session.save()

    def test_internship_provider_crud(self):
        # 1. Create Provider
        res = self.client.post(
            '/api/internship-providers/',
            data=json.dumps({
                "name": "TechCorp Solutions",
                "contact_person": "John Doe",
                "email": "contact@techcorp.com",
                "phone": "+91 9876543210",
                "industry": "Software & IT"
            }),
            content_type="application/json"
        )
        self.assertEqual(res.status_code, 201)
        data = res.json()
        self.assertTrue(data.get("success"))
        provider_id = data["data"]["id"]

        # 2. List Providers
        res = self.client.get('/api/internship-providers/?q=TechCorp')
        self.assertEqual(res.status_code, 200)
        providers = res.json()
        self.assertEqual(len(providers), 1)

        # 3. Get Provider Detail
        res = self.client.get(f'/api/internship-providers/{provider_id}/')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["name"], "TechCorp Solutions")

        # 4. Update Provider
        res = self.client.put(
            f'/api/internship-providers/{provider_id}/',
            data=json.dumps({"name": "TechCorp Innovations"}),
            content_type="application/json"
        )
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["data"]["name"], "TechCorp Innovations")

        # 5. Delete Provider
        res = self.client.delete(f'/api/internship-providers/{provider_id}/')
        self.assertEqual(res.status_code, 200)
        self.assertFalse(InternshipProvider.objects.filter(id=provider_id).exists())

    def test_internship_crud_and_validation(self):
        # Create Provider
        provider = InternshipProvider.objects.create(name="Innovate Ltd", industry="AI & Data")

        # Validation: Title required
        res = self.client.post(
            '/api/internships/',
            data=json.dumps({"title": "", "seats": 2}),
            content_type="application/json"
        )
        self.assertEqual(res.status_code, 400)

        # Validation: End date < Start date
        res = self.client.post(
            '/api/internships/',
            data=json.dumps({
                "title": "Python Developer Intern",
                "start_date": "2026-10-15",
                "end_date": "2026-10-01"
            }),
            content_type="application/json"
        )
        self.assertEqual(res.status_code, 400)

        # Valid Create
        res = self.client.post(
            '/api/internships/',
            data=json.dumps({
                "title": "Python Developer Intern",
                "provider_id": provider.id,
                "mode": "Remote",
                "duration": "3 Months",
                "seats": 5,
                "status": "Open",
                "start_date": "2026-10-01",
                "end_date": "2026-12-31"
            }),
            content_type="application/json"
        )
        self.assertEqual(res.status_code, 201)
        internship_id = res.json()["data"]["id"]

        # List Internships
        res = self.client.get('/api/internships/?status=Open')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.json()), 1)

        # Change Status API
        res = self.client.post(
            f'/api/internships/{internship_id}/status/',
            data=json.dumps({"status": "Active"}),
            content_type="application/json"
        )
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["data"]["status"], "Active")

        # Delete Internship
        res = self.client.delete(f'/api/internships/{internship_id}/')
        self.assertEqual(res.status_code, 200)
        self.assertFalse(Internship.objects.filter(id=internship_id).exists())

    def test_public_apply_and_applications_workflow(self):
        internship = Internship.objects.create(title="Web Dev Intern", seats=3, status="Open")

        # 1. Public List Open Internships
        res = self.client.get('/api/public/internships/')
        self.assertEqual(res.status_code, 200)
        self.assertTrue(len(res.json()["data"]) >= 1)

        # 2. Public Apply
        res = self.client.post('/api/internship-apply/', data={
            "internship_id": internship.id,
            "full_name": "Rohan Mehra",
            "email": "rohan@example.com",
            "phone": "+91 9988776655",
            "college": "IIT Delhi",
            "course_stream": "B.Tech Computer Science",
            "skills": "JavaScript, React, Django"
        })
        self.assertEqual(res.status_code, 200)
        app_id = res.json()["data"]["id"]

        # 3. Admin List Applications
        res = self.client.get('/api/internship-applications/?status=Pending')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.json()), 1)

        # 4. Admin Change Application Status
        res = self.client.put(
            f'/api/internship-applications/{app_id}/',
            data=json.dumps({"status": "Selected", "notes": "Interview passed smoothly"}),
            content_type="application/json"
        )
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["data"]["status"], "Selected")

        # 5. Admin Delete Application
        res = self.client.delete(f'/api/internship-applications/{app_id}/')
        self.assertEqual(res.status_code, 200)
        self.assertFalse(InternshipApplication.objects.filter(id=app_id).exists())

    def test_convert_enquiry_to_application(self):
        enquiry = InternshipEnquiry.objects.create(
            full_name="Priya Sharma",
            email="priya@example.com",
            phone="+91 9876501234",
            college="Amity University",
            course_stream="MCA",
            duration="6 Months",
            status="New"
        )
        res = self.client.post(f'/api/internship-enquiry/{enquiry.id}/convert/')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["data"]["full_name"], "Priya Sharma")

        enquiry.refresh_from_db()
        self.assertEqual(enquiry.status, "Converted")

    def test_all_sidebar_urls(self):
        sidebar_urls = [
            '/admin-panel/internships/all/',
            '/admin-panel/internships/add/',
            '/admin-panel/internships/enquiries/',
            '/admin-panel/internships/applications/all/',
            '/admin-panel/internships/applications/pending/',
            '/admin-panel/internships/applications/shortlisted/',
            '/admin-panel/internships/applications/selected/',
            '/admin-panel/internships/applications/rejected/',
            '/admin-panel/internships/active/',
            '/admin-panel/internships/completed/',
            '/admin-panel/internships/providers/',
        ]
        for url in sidebar_urls:
            res = self.client.get(url)
            self.assertEqual(res.status_code, 200, f"Failed URL: {url}")
