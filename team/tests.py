from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.contrib.messages import get_messages
from datetime import date
from .models import Team, TeamMember, Payment

User = get_user_model()


class TeamViewsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        #self.user = User.objects.create_user('testuser@aaa.com', password='pass', is_staff=True)
        self.client.login(username='testuser@aaa.com', password='pass')
        self.team = Team.objects.create(name='Test Team', description='A test team')
        self.member_user = User.objects.create_user('member@example.com', password='pass', adi='Member', soyadi='User')
        self.member = TeamMember.objects.create(
            team=self.team,
            user=self.member_user,
            name='Member',
            surname='User',
            is_active=True
        )
        self.payment = Payment.objects.create(
            member=self.member,
            month=date.today().replace(day=1),
            amount=100.00,
            is_paid=False
        )

    def test_team_list(self):
        response = self.client.get(reverse('team:list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'team/team_list.html')
        self.assertIn('teams', response.context)
        self.assertIn('title', response.context)

    def test_team_detail(self):
        response = self.client.get(reverse('team:detail', kwargs={'pk': self.team.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'team/team_detail.html')
        self.assertIn('team', response.context)
        self.assertIn('members', response.context)
        self.assertEqual(response.context['team'], self.team)

    def test_team_create_get(self):
        response = self.client.get(reverse('team:create'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'team/team_form.html')
        self.assertIn('form', response.context)
        self.assertIn('title', response.context)

    def test_team_create_post_valid(self):
        data = {
            'name': 'New Team',
            'description': 'New team description',
            'founded_date': '2020-01-01'
        }
        response = self.client.post(reverse('team:create'), data)
        self.assertRedirects(response, reverse('team:detail', kwargs={'pk': Team.objects.get(name='New Team').pk}))
        messages_list = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages_list), 1)
        self.assertIn('başarıyla oluşturuldu', str(messages_list[0]))

    def test_team_create_post_invalid(self):
        data = {'name': ''}  # Invalid, name required
        response = self.client.post(reverse('team:create'), data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'team/team_form.html')
        self.assertFalse(response.context['form'].is_valid())

    def test_team_update_get(self):
        response = self.client.get(reverse('team:update', kwargs={'pk': self.team.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'team/team_form.html')
        self.assertIn('form', response.context)
        self.assertIn('team', response.context)
        self.assertEqual(response.context['team'], self.team)

    def test_team_update_post_valid(self):
        data = {
            'name': 'Updated Team',
            'description': 'Updated description',
            'founded_date': '2021-01-01'
        }
        response = self.client.post(reverse('team:update', kwargs={'pk': self.team.pk}), data)
        self.assertRedirects(response, reverse('team:detail', kwargs={'pk': self.team.pk}))
        self.team.refresh_from_db()
        self.assertEqual(self.team.name, 'Updated Team')
        messages_list = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages_list), 1)
        self.assertIn('başarıyla güncellendi', str(messages_list[0]))

    def test_team_members(self):
        response = self.client.get(reverse('team:members', kwargs={'pk': self.team.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'team/team_members.html')
        self.assertIn('team', response.context)
        self.assertIn('members', response.context)
        self.assertEqual(response.context['team'], self.team)

    def test_team_member_create_get(self):
        response = self.client.get(reverse('team:member_create', kwargs={'team_pk': self.team.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'team/team_member_form.html')
        self.assertIn('form', response.context)
        self.assertIn('team', response.context)

    def test_team_member_create_post_valid(self):
        new_user = User.objects.create_user(email='newmember@example.com', password='pass', adi='New', soyadi='Member')
        data = {
            'user': new_user.pk,
            'name': 'New',
            'surname': 'Member',
            'is_active': True
        }
        response = self.client.post(reverse('team:member_create', kwargs={'team_pk': self.team.pk}), data)
        self.assertRedirects(response, reverse('team:members', kwargs={'pk': self.team.pk}))
        new_member = TeamMember.objects.get(user=new_user)
        self.assertEqual(new_member.team, self.team)
        messages_list = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages_list), 1)
        self.assertIn('başarıyla takıma eklendi', str(messages_list[0]))

    def test_team_member_update_get(self):
        response = self.client.get(reverse('team:member_update', kwargs={'pk': self.member.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'team/team_member_form.html')
        self.assertIn('form', response.context)
        self.assertIn('member', response.context)
        self.assertEqual(response.context['member'], self.member)

    def test_team_member_update_post_valid(self):
        data = {
            'user': self.member_user.pk,
            'name': 'Updated',
            'surname': 'Name',
            'is_active': True
        }
        response = self.client.post(reverse('team:member_update', kwargs={'pk': self.member.pk}), data)
        self.assertRedirects(response, reverse('team:members', kwargs={'pk': self.team.pk}))
        self.member.refresh_from_db()
        self.assertEqual(self.member.name, 'Updated')
        messages_list = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages_list), 1)
        self.assertIn('bilgileri güncellendi', str(messages_list[0]))

    def test_team_member_delete_get(self):
        response = self.client.get(reverse('team:member_delete', kwargs={'pk': self.member.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'team/team_member_confirm_delete.html')
        self.assertIn('member', response.context)
        self.assertEqual(response.context['member'], self.member)

    def test_team_member_delete_post(self):
        response = self.client.post(reverse('team:member_delete', kwargs={'pk': self.member.pk}))
        self.assertRedirects(response, reverse('team:members', kwargs={'pk': self.team.pk}))
        self.assertFalse(TeamMember.objects.filter(pk=self.member.pk).exists())
        messages_list = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages_list), 1)
        self.assertIn('takımdan çıkarıldı', str(messages_list[0]))

    def test_payment_list(self):
        response = self.client.get(reverse('team:payment_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'team/payment_list.html')
        self.assertIn('team_summaries', response.context)
        self.assertIn('unpaid_by_team', response.context)

    def test_payment_create_get(self):
        response = self.client.get(reverse('team:payment_create'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'team/payment_form.html')
        self.assertIn('form', response.context)

    def test_payment_create_post_valid(self):
        data = {
            'member': self.member.pk,
            'month': '2023-01-01',
            'amount': '150.00',
            'is_paid': True,
            'paid_date': '2023-01-15'
        }
        response = self.client.post(reverse('team:payment_create'), data)
        self.assertRedirects(response, reverse('team:payment_list'))
        new_payment = Payment.objects.get(member=self.member, month='2023-01-01')
        self.assertEqual(new_payment.amount, 150.00)
        messages_list = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages_list), 1)
        self.assertIn('Ödeme başarıyla oluşturuldu', str(messages_list[0]))

    def test_payment_update_get(self):
        response = self.client.get(reverse('team:payment_update', kwargs={'pk': self.payment.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'team/payment_form.html')
        self.assertIn('form', response.context)
        self.assertIn('payment', response.context)
        self.assertEqual(response.context['payment'], self.payment)

    def test_payment_update_post_valid(self):
        data = {
            'member': self.member.pk,
            'month': self.payment.month.strftime('%Y-%m-%d'),
            'amount': '200.00',
            'is_paid': True,
            'paid_date': '2023-01-10'
        }
        response = self.client.post(reverse('team:payment_update', kwargs={'pk': self.payment.pk}), data)
        self.assertRedirects(response, reverse('team:payment_list'))
        self.payment.refresh_from_db()
        self.assertEqual(self.payment.amount, 200.00)
        self.assertTrue(self.payment.is_paid)
        messages_list = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages_list), 1)
        self.assertIn('Ödeme başarıyla güncellendi', str(messages_list[0]))

    def test_payment_delete_get(self):
        response = self.client.get(reverse('team:payment_delete', kwargs={'pk': self.payment.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'team/payment_confirm_delete.html')
        self.assertIn('payment', response.context)
        self.assertEqual(response.context['payment'], self.payment)

    def test_payment_delete_post(self):
        response = self.client.post(reverse('team:payment_delete', kwargs={'pk': self.payment.pk}))
        self.assertRedirects(response, reverse('team:payment_list'))
        self.assertFalse(Payment.objects.filter(pk=self.payment.pk).exists())
        messages_list = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages_list), 1)
        self.assertIn('Ödeme başarıyla silindi', str(messages_list[0]))
