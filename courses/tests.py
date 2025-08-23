from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal
from datetime import timedelta
from .models import Category, Course, GlobalDiscount


class GlobalDiscountTestCase(TestCase):
    def setUp(self):
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Create test category
        self.category = Category.objects.create(
            name='Test Category',
            description='Test category description'
        )
        
        # Create test course
        self.course = Course.objects.create(
            title='Test Course',
            slug='test-course',
            description='Test course description',
            short_description='Test short description',
            category=self.category,
            instructor=self.user,
            price=Decimal('100.00'),
            duration='10 hours',
            difficulty='beginner',
            language='English',
            is_published=True
        )

    def test_global_discount_creation(self):
        """Test creating a global discount"""
        discount = GlobalDiscount.objects.create(
            title="Test Discount",
            description="Test description",
            discount_percentage=25,
            end_date=timezone.now() + timedelta(days=7),
            is_active=True
        )
        
        self.assertEqual(discount.title, "Test Discount")
        self.assertEqual(discount.discount_percentage, 25)
        self.assertTrue(discount.is_active)

    def test_global_discount_is_currently_active(self):
        """Test global discount active status"""
        # Active discount
        active_discount = GlobalDiscount.objects.create(
            title="Active Discount",
            discount_percentage=20,
            start_date=timezone.now() - timedelta(days=1),
            end_date=timezone.now() + timedelta(days=7),
            is_active=True
        )
        self.assertTrue(active_discount.is_currently_active())
        
        # Expired discount
        expired_discount = GlobalDiscount.objects.create(
            title="Expired Discount",
            discount_percentage=20,
            start_date=timezone.now() - timedelta(days=10),
            end_date=timezone.now() - timedelta(days=1),
            is_active=True
        )
        self.assertFalse(expired_discount.is_currently_active())
        
        # Future discount
        future_discount = GlobalDiscount.objects.create(
            title="Future Discount",
            discount_percentage=20,
            start_date=timezone.now() + timedelta(days=1),
            end_date=timezone.now() + timedelta(days=8),
            is_active=True
        )
        self.assertFalse(future_discount.is_currently_active())

    def test_global_discount_multiplier(self):
        """Test discount multiplier calculation"""
        discount = GlobalDiscount.objects.create(
            title="Test Discount",
            discount_percentage=30,
            end_date=timezone.now() + timedelta(days=7),
            is_active=True
        )
        
        self.assertEqual(discount.get_discount_multiplier(), Decimal('0.7'))

    def test_global_discount_apply_to_price(self):
        """Test applying global discount to price"""
        discount = GlobalDiscount.objects.create(
            title="Test Discount",
            discount_percentage=25,
            end_date=timezone.now() + timedelta(days=7),
            is_active=True
        )
        
        original_price = Decimal('100.00')
        discounted_price = discount.apply_to_price(original_price)
        self.assertEqual(discounted_price, Decimal('75.00'))

    def test_course_with_global_discount(self):
        """Test course price with global discount"""
        # Create active global discount
        global_discount = GlobalDiscount.objects.create(
            title="Global Sale",
            discount_percentage=20,
            end_date=timezone.now() + timedelta(days=7),
            is_active=True
        )
        
        # Course should have discounted price
        self.assertTrue(self.course.has_any_discount())
        self.assertEqual(self.course.get_current_price(), Decimal('80.00'))
        self.assertEqual(self.course.get_discount_percentage(), 20)

    def test_course_individual_discount_priority(self):
        """Test that individual course discount takes priority over global discount"""
        # Create global discount
        global_discount = GlobalDiscount.objects.create(
            title="Global Sale",
            discount_percentage=20,
            end_date=timezone.now() + timedelta(days=7),
            is_active=True
        )
        
        # Create individual course discount
        self.course.discount_price = Decimal('60.00')
        self.course.discount_start_date = timezone.now() - timedelta(days=1)
        self.course.discount_end_date = timezone.now() + timedelta(days=7)
        self.course.is_discount_active = True
        self.course.save()
        
        # Individual discount should take priority
        self.assertTrue(self.course.has_active_discount())
        self.assertEqual(self.course.get_current_price(), Decimal('60.00'))
        self.assertEqual(self.course.get_discount_percentage(), 40)

    def test_global_discount_remaining_time(self):
        """Test global discount remaining time calculation"""
        end_date = timezone.now() + timedelta(hours=2)
        discount = GlobalDiscount.objects.create(
            title="Test Discount",
            discount_percentage=25,
            end_date=end_date,
            is_active=True
        )
        
        remaining_time = discount.get_remaining_time()
        self.assertGreater(remaining_time, 0)
        self.assertLess(remaining_time, 8000)  # Less than ~2.2 hours in seconds (allowing for test execution time)


class DiscountTestCase(TestCase):
    def setUp(self):
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Create test category
        self.category = Category.objects.create(
            name='Test Category',
            description='Test category description'
        )
        
        # Create test course
        self.course = Course.objects.create(
            title='Test Course',
            slug='test-course',
            description='Test course description',
            short_description='Test short description',
            category=self.category,
            instructor=self.user,
            price=Decimal('100.00'),
            duration='10 hours',
            difficulty='beginner',
            language='English',
            is_published=True
        )

    def test_has_active_discount_no_discount(self):
        """Test that course has no active discount when no discount is set"""
        self.assertFalse(self.course.has_active_discount())
        self.assertEqual(self.course.get_current_price(), Decimal('100.00'))

    def test_has_active_discount_with_active_discount(self):
        """Test that course has active discount when discount is set and active"""
        now = timezone.now()
        end_date = now + timedelta(days=7)
        
        self.course.discount_price = Decimal('80.00')
        self.course.discount_start_date = now - timedelta(days=1)
        self.course.discount_end_date = end_date
        self.course.is_discount_active = True
        self.course.save()
        
        self.assertTrue(self.course.has_active_discount())
        self.assertEqual(self.course.get_current_price(), Decimal('80.00'))
        self.assertEqual(self.course.get_discount_percentage(), 20)

    def test_has_active_discount_expired(self):
        """Test that course has no active discount when discount has expired"""
        now = timezone.now()
        end_date = now - timedelta(days=1)  # Expired yesterday
        
        self.course.discount_price = Decimal('80.00')
        self.course.discount_start_date = now - timedelta(days=10)
        self.course.discount_end_date = end_date
        self.course.is_discount_active = True
        self.course.save()
        
        self.assertFalse(self.course.has_active_discount())
        self.assertEqual(self.course.get_current_price(), Decimal('100.00'))

    def test_has_active_discount_future_start(self):
        """Test that course has no active discount when start date is in future"""
        now = timezone.now()
        start_date = now + timedelta(days=1)  # Starts tomorrow
        end_date = now + timedelta(days=8)
        
        self.course.discount_price = Decimal('80.00')
        self.course.discount_start_date = start_date
        self.course.discount_end_date = end_date
        self.course.is_discount_active = True
        self.course.save()
        
        self.assertFalse(self.course.has_active_discount())
        self.assertEqual(self.course.get_current_price(), Decimal('100.00'))

    def test_discount_percentage_calculation(self):
        """Test discount percentage calculation"""
        self.course.discount_price = Decimal('75.00')  # 25% off
        self.course.discount_start_date = timezone.now() - timedelta(days=1)
        self.course.discount_end_date = timezone.now() + timedelta(days=7)
        self.course.is_discount_active = True
        self.course.save()
        
        self.assertEqual(self.course.get_discount_percentage(), 25)

    def test_discount_remaining_time(self):
        """Test discount remaining time calculation"""
        now = timezone.now()
        end_date = now + timedelta(hours=2)  # 2 hours from now
        
        self.course.discount_price = Decimal('80.00')
        self.course.discount_start_date = now - timedelta(days=1)
        self.course.discount_end_date = end_date
        self.course.is_discount_active = True
        self.course.save()
        
        remaining_time = self.course.get_discount_remaining_time()
        self.assertGreater(remaining_time, 0)
        self.assertLess(remaining_time, 7200)  # Less than 2 hours in seconds

    def test_free_course_discount(self):
        """Test that free courses handle discounts correctly"""
        self.course.price = Decimal('0.00')
        self.course.discount_price = Decimal('0.00')
        self.course.save()
        
        self.assertEqual(self.course.get_discount_percentage(), 0)
        self.assertEqual(self.course.get_current_price(), Decimal('0.00'))
