from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from courses.models import Category, Course, Lesson
from payment_system.models import PaymentMethod, PaymentSettings
from accounts.models import UserProfile
import random

class Command(BaseCommand):
    help = 'Populate the database with sample data for testing'

    def handle(self, *args, **options):
        self.stdout.write('Creating sample data...')

        # Create superuser if not exists
        if not User.objects.filter(username='admin').exists():
            admin_user = User.objects.create_superuser(
                username='admin',
                email='admin@example.com',
                password='admin123'
            )
            self.stdout.write(f'Created superuser: {admin_user.username}')

        # Create instructor
        instructor, created = User.objects.get_or_create(
            username='instructor',
            defaults={
                'email': 'instructor@example.com',
                'first_name': 'John',
                'last_name': 'Doe',
                'is_staff': True
            }
        )
        if created:
            instructor.set_password('instructor123')
            instructor.save()
            self.stdout.write(f'Created instructor: {instructor.username}')

        # Create categories
        categories_data = [
            {'name': 'Machine Learning', 'description': 'Learn the fundamentals of machine learning algorithms and techniques.'},
            {'name': 'Deep Learning', 'description': 'Master neural networks and deep learning frameworks.'},
            {'name': 'Data Science', 'description': 'Comprehensive data science and analytics courses.'},
            {'name': 'Computer Vision', 'description': 'Learn image processing and computer vision techniques.'},
            {'name': 'Natural Language Processing', 'description': 'Master NLP and text processing technologies.'},
        ]

        categories = []
        for cat_data in categories_data:
            category, created = Category.objects.get_or_create(
                name=cat_data['name'],
                defaults={'description': cat_data['description']}
            )
            categories.append(category)
            if created:
                self.stdout.write(f'Created category: {category.name}')

        # Create courses
        courses_data = [
            {
                'title': 'Introduction to Machine Learning',
                'slug': 'introduction-to-machine-learning',
                'description': 'A comprehensive introduction to machine learning concepts, algorithms, and practical applications. This course covers supervised and unsupervised learning, model evaluation, and real-world projects.',
                'short_description': 'Learn the fundamentals of machine learning with hands-on projects.',
                'price': 99.99,
                'duration': '20 hours',
                'difficulty': 'beginner',
                'what_you_will_learn': '• Understand machine learning fundamentals\n• Implement various ML algorithms\n• Work with real datasets\n• Build and evaluate models\n• Deploy ML solutions',
                'requirements': '• Basic Python knowledge\n• High school mathematics\n• No prior ML experience required',
                'target_audience': 'Beginners interested in machine learning, data science enthusiasts, and professionals looking to upskill.',
                'is_published': True,
                'is_featured': True,
            },
            {
                'title': 'Deep Learning with Neural Networks',
                'slug': 'deep-learning-neural-networks',
                'description': 'Master deep learning concepts and build sophisticated neural networks. This course covers CNN, RNN, LSTM, and transformer architectures with practical implementations.',
                'short_description': 'Master deep learning and neural network architectures.',
                'price': 149.99,
                'duration': '30 hours',
                'difficulty': 'intermediate',
                'what_you_will_learn': '• Build neural networks from scratch\n• Implement CNN, RNN, LSTM\n• Use popular frameworks (TensorFlow, PyTorch)\n• Handle real-world deep learning problems\n• Optimize model performance',
                'requirements': '• Python programming\n• Basic machine learning knowledge\n• Linear algebra fundamentals',
                'target_audience': 'Intermediate learners, ML practitioners, and developers interested in deep learning.',
                'is_published': True,
                'is_featured': True,
            },
            {
                'title': 'Data Science Fundamentals',
                'slug': 'data-science-fundamentals',
                'description': 'Complete data science course covering data analysis, visualization, statistical modeling, and machine learning. Learn to extract insights from data and make data-driven decisions.',
                'short_description': 'Complete data science course with practical applications.',
                'price': 129.99,
                'duration': '25 hours',
                'difficulty': 'beginner',
                'what_you_will_learn': '• Data analysis and visualization\n• Statistical modeling\n• Predictive analytics\n• Data storytelling\n• Business intelligence',
                'requirements': '• Basic Python knowledge\n• High school statistics\n• Curiosity about data',
                'target_audience': 'Data analysts, business professionals, and anyone interested in data science.',
                'is_published': True,
                'is_featured': False,
            },
            {
                'title': 'Computer Vision Masterclass',
                'slug': 'computer-vision-masterclass',
                'description': 'Learn computer vision techniques including image processing, object detection, face recognition, and video analysis. Build real-world computer vision applications.',
                'short_description': 'Master computer vision and image processing techniques.',
                'price': 179.99,
                'duration': '35 hours',
                'difficulty': 'advanced',
                'what_you_will_learn': '• Image processing fundamentals\n• Object detection and recognition\n• Face recognition systems\n• Video analysis\n• Real-time computer vision',
                'requirements': '• Python programming\n• Basic ML knowledge\n• Understanding of linear algebra',
                'target_audience': 'Advanced learners, computer vision researchers, and AI engineers.',
                'is_published': True,
                'is_featured': False,
            },
            {
                'title': 'Natural Language Processing',
                'slug': 'natural-language-processing',
                'description': 'Comprehensive NLP course covering text processing, sentiment analysis, language models, and transformer architectures. Build chatbots and language understanding systems.',
                'short_description': 'Master NLP and build language understanding systems.',
                'price': 159.99,
                'duration': '28 hours',
                'difficulty': 'intermediate',
                'what_you_will_learn': '• Text preprocessing techniques\n• Sentiment analysis\n• Language models (BERT, GPT)\n• Named entity recognition\n• Chatbot development',
                'requirements': '• Python programming\n• Basic ML concepts\n• Understanding of probability',
                'target_audience': 'NLP enthusiasts, developers, and researchers in computational linguistics.',
                'is_published': True,
                'is_featured': False,
            },
        ]

        courses = []
        for i, course_data in enumerate(courses_data):
            course, created = Course.objects.get_or_create(
                slug=course_data['slug'],
                defaults={
                    'title': course_data['title'],
                    'description': course_data['description'],
                    'short_description': course_data['short_description'],
                    'category': categories[i % len(categories)],
                    'instructor': instructor,
                    'price': course_data['price'],
                    'duration': course_data['duration'],
                    'difficulty': course_data['difficulty'],
                    'what_you_will_learn': course_data['what_you_will_learn'],
                    'requirements': course_data['requirements'],
                    'target_audience': course_data['target_audience'],
                    'is_published': course_data['is_published'],
                    'is_featured': course_data['is_featured'],
                    'students_enrolled': random.randint(50, 500),
                    'rating': round(random.uniform(3.5, 5.0), 2),
                    'total_ratings': random.randint(10, 100),
                }
            )
            courses.append(course)
            if created:
                self.stdout.write(f'Created course: {course.title}')

        # Create lessons for each course
        lesson_titles = [
            'Introduction and Course Overview',
            'Setting Up Your Development Environment',
            'Basic Concepts and Fundamentals',
            'Hands-on Practice Session',
            'Advanced Techniques and Methods',
            'Real-world Applications',
            'Project Implementation',
            'Testing and Evaluation',
            'Optimization and Best Practices',
            'Final Project and Deployment',
        ]

        for course in courses:
            for i, title in enumerate(lesson_titles[:6]):  # 6 lessons per course
                lesson, created = Lesson.objects.get_or_create(
                    course=course,
                    title=title,
                    defaults={
                        'description': f'Learn about {title.lower()} in this comprehensive lesson.',
                        'duration': random.randint(15, 45),
                        'order': i + 1,
                        'is_free': i < 2,  # First 2 lessons are free
                    }
                )
                if created:
                    self.stdout.write(f'Created lesson: {lesson.title} for {course.title}')

        # Create payment methods
        payment_methods_data = [
            {'name': 'easypaisa', 'account_number': '03001234567', 'account_title': 'AI Course Platform'},
            {'name': 'jazzcash', 'account_number': '03001234567', 'account_title': 'AI Course Platform'},
            {'name': 'bank_transfer', 'account_number': '1234-5678-9012-3456', 'account_title': 'AI Course Platform'},
        ]

        for method_data in payment_methods_data:
            method, created = PaymentMethod.objects.get_or_create(
                name=method_data['name'],
                defaults={
                    'account_number': method_data['account_number'],
                    'account_title': method_data['account_title'],
                    'is_active': True,
                }
            )
            if created:
                self.stdout.write(f'Created payment method: {method.get_name_display()}')

        # Create payment settings
        settings, created = PaymentSettings.objects.get_or_create(
            defaults={
                'platform_name': 'AI Course Platform',
                'platform_email': 'admin@aicourseplatform.com',
                'platform_phone': '+92 300 1234567',
                'easypaisa_instructions': 'Send payment to EasyPaisa account 03001234567 with reference "AI Course".',
                'jazzcash_instructions': 'Send payment to JazzCash account 03001234567 with reference "AI Course".',
                'bank_transfer_instructions': 'Transfer to bank account 1234-5678-9012-3456 with reference "AI Course".',
                'auto_approve_payments': False,
                'notify_admin_on_payment': True,
                'notify_student_on_approval': True,
            }
        )
        if created:
            self.stdout.write('Created payment settings')

        self.stdout.write(
            self.style.SUCCESS('Successfully created sample data!')
        )
        self.stdout.write('\nLogin credentials:')
        self.stdout.write('Admin: admin / admin123')
        self.stdout.write('Instructor: instructor / instructor123')
