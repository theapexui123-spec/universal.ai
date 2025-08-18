# 🎓 AI Course Platform

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Django](https://img.shields.io/badge/Django-4.2.7-green.svg)](https://www.djangoproject.com/)
[![Bootstrap](https://img.shields.io/badge/Bootstrap-5.0+-purple.svg)](https://getbootstrap.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Production%20Ready-brightgreen.svg)]()

A comprehensive Django web application for selling and managing online courses with integrated payment processing. Built with modern web technologies and designed for scalability.

## 🌟 Features

### 🎓 Course Management
- **Course Creation & Management**: Create, edit, and manage courses with rich content
- **Lesson System**: Organize courses into lessons with video content
- **Categories**: Categorize courses for easy discovery
- **Difficulty Levels**: Beginner, Intermediate, and Advanced course levels
- **Course Ratings & Reviews**: Student feedback and rating system
- **Search & Filter**: Advanced course discovery with multiple filters

### 👥 User Management
- **User Registration & Authentication**: Secure user registration and login
- **User Profiles**: Extended user profiles with additional information
- **Student Dashboard**: Track learning progress and enrolled courses
- **Instructor Management**: Dedicated instructor accounts and course management
- **Role-based Access**: Different permissions for students, instructors, and admins

### 💳 Payment System
- **Multiple Payment Methods**: EasyPaisa, JazzCash, and Bank Transfer support
- **Payment Verification**: Admin approval system for payments
- **Payment History**: Complete payment tracking and history
- **Screenshot Upload**: Students can upload payment confirmations
- **Payment Instructions**: Detailed guides for each payment method

### 📊 Learning Management
- **Course Enrollment**: Easy course enrollment system
- **Progress Tracking**: Track lesson completion and course progress
- **Learning Interface**: Dedicated learning environment for students
- **Certificate System**: Course completion tracking
- **Course Analytics**: Detailed insights into student progress

### 🎨 Modern UI/UX
- **Responsive Design**: Mobile-friendly Bootstrap 5 interface
- **Modern Styling**: Clean, professional design with smooth animations
- **Font Awesome Icons**: Rich iconography throughout the application
- **Google Fonts**: Inter font family for better readability
- **Cross-browser Compatibility**: Works on all modern browsers

## 🛠️ Technology Stack

### Backend
- **Django 4.2.7**: Modern Python web framework
- **Python 3.8+**: Latest Python features and security
- **SQLite**: Development database (PostgreSQL ready for production)
- **Django Crispy Forms**: Beautiful form rendering

### Frontend
- **Bootstrap 5**: Responsive CSS framework
- **HTML5 & CSS3**: Modern web standards
- **JavaScript**: Interactive user experience
- **Font Awesome 6**: Professional icons
- **Google Fonts**: Typography optimization

### Additional Tools
- **Pillow**: Image processing and manipulation
- **Django Admin**: Powerful admin interface
- **Virtual Environment**: Isolated Python environment

## 📋 Prerequisites

Before running this application, make sure you have:

- **Python 3.8 or higher**
- **pip** (Python package installer)
- **Git** (for version control)

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/ai-course-platform.git
cd ai-course-platform
```

### 2. Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run Database Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Create Sample Data
```bash
python manage.py populate_sample_data
```

### 6. Run Development Server
```bash
python manage.py runserver
```

### 7. Access the Application
- **Main site**: http://127.0.0.1:8000/
- **Admin panel**: http://127.0.0.1:8000/admin/

## 🔐 Default Login Credentials

After running the sample data command, you can use these credentials:

### Admin User
- **Username**: `admin`
- **Password**: `admin123`
- **Access**: Full admin privileges

### Instructor User
- **Username**: `instructor`
- **Password**: `instructor123`
- **Access**: Course management capabilities

## 📁 Project Structure

```
ai-course-platform/
├── course_platform/          # Main Django project
│   ├── settings.py          # Project settings
│   ├── urls.py              # Main URL configuration
│   └── wsgi.py              # WSGI configuration
├── courses/                  # Courses app
│   ├── models.py            # Course, Lesson, Category models
│   ├── views.py             # Course-related views
│   ├── admin.py             # Django admin configuration
│   ├── urls.py              # Course URL patterns
│   └── management/          # Custom management commands
│       └── commands/
│           └── populate_sample_data.py
├── accounts/                 # User management app
│   ├── models.py            # UserProfile model
│   ├── views.py             # User-related views
│   ├── forms.py             # User forms
│   └── urls.py              # Account URL patterns
├── payment_system/           # Payment processing app
│   ├── models.py            # Payment models
│   ├── views.py             # Payment views
│   ├── admin.py             # Payment admin
│   └── urls.py              # Payment URL patterns
├── templates/                # HTML templates
│   ├── base.html            # Base template
│   ├── courses/             # Course templates
│   ├── accounts/            # Account templates
│   ├── payment_system/      # Payment templates
│   └── registration/        # Authentication templates
├── static/                   # Static files (CSS, JS, images)
├── media/                    # User-uploaded files
├── requirements.txt          # Python dependencies
├── manage.py                # Django management script
├── .gitignore               # Git ignore rules
└── README.md                # Project documentation
```

## 🎯 Key Features Explained

### Course Management
- **Categories**: Organize courses into logical groups
- **Difficulty Levels**: Help students choose appropriate courses
- **Rich Content**: Support for course descriptions, requirements, and learning outcomes
- **Video Integration**: YouTube/Vimeo video embedding support
- **Course Analytics**: Track enrollment, completion rates, and student engagement

### Payment Processing
- **Manual Payment Verification**: Admin reviews payment screenshots
- **Multiple Payment Methods**: Support for local payment systems
- **Payment Tracking**: Complete audit trail of all transactions
- **Status Management**: Pending, Approved, Rejected payment states
- **Payment Instructions**: Detailed guides for each payment method

### User Experience
- **Responsive Design**: Works on all device sizes
- **Intuitive Navigation**: Easy-to-use interface
- **Progress Tracking**: Visual progress indicators
- **Search & Filter**: Find courses quickly
- **Personalized Dashboard**: Customized user experience

## 🔧 Customization

### Adding New Payment Methods
1. Add new choices to `PaymentMethod.PAYMENT_CHOICES`
2. Update payment instructions in `PaymentSettings`
3. Modify payment templates as needed
4. Update admin interface for new methods

### Styling Customization
- Modify `templates/base.html` for global styling
- Update CSS variables in the base template
- Customize Bootstrap theme colors
- Add custom CSS in `static/css/` directory

### Adding New Features
- Create new Django apps for additional functionality
- Follow the existing app structure and patterns
- Update URL configurations and admin interfaces
- Add appropriate tests for new features

## 🚀 Deployment

### Production Settings
1. Update `settings.py` for production environment
2. Set `DEBUG = False`
3. Configure database (PostgreSQL recommended)
4. Set up static file serving
5. Configure email settings
6. Set up SSL/HTTPS

### Environment Variables
```bash
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=your-domain.com,www.your-domain.com
DATABASE_URL=postgresql://user:pass@host:port/db
EMAIL_HOST=smtp.your-email-provider.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@domain.com
EMAIL_HOST_PASSWORD=your-email-password
```

### Recommended Hosting Platforms
- **Heroku**: Easy deployment with PostgreSQL
- **DigitalOcean**: VPS with full control
- **AWS**: Scalable cloud infrastructure
- **Vercel**: Modern deployment platform

## 🧪 Testing

### Running Tests
```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test courses
python manage.py test accounts
python manage.py test payment_system

# Run with coverage
coverage run --source='.' manage.py test
coverage report
coverage html
```

### Test Coverage
- Unit tests for models and views
- Integration tests for payment flow
- User authentication tests
- Admin interface tests

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Make your changes**
4. **Add tests** if applicable
5. **Commit your changes**
   ```bash
   git commit -m "Add: your feature description"
   ```
6. **Push to the branch**
   ```bash
   git push origin feature/your-feature-name
   ```
7. **Submit a pull request**

### Contribution Guidelines
- Follow PEP 8 Python style guide
- Write clear commit messages
- Add tests for new features
- Update documentation as needed
- Ensure all tests pass before submitting

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

### Getting Help
- **Documentation**: Check this README and inline code comments
- **Issues**: Report bugs and feature requests on GitHub
- **Discussions**: Use GitHub Discussions for questions

### Contact Information
- **Email**: support@aicourseplatform.com
- **Phone**: +92 300 1234567
- **Support Hours**: 24/7 Available

### Common Issues
- **Port already in use**: Use `python manage.py runserver 8080`
- **Database errors**: Run `python manage.py migrate`
- **Static files not loading**: Run `python manage.py collectstatic`

## 🏆 Acknowledgments

- **Django Community**: For the amazing web framework
- **Bootstrap Team**: For the responsive CSS framework
- **Font Awesome**: For the beautiful icons
- **Contributors**: Everyone who helps improve this project

## 📈 Roadmap

### Upcoming Features
- [ ] **Video Streaming**: Integrated video player
- [ ] **Live Classes**: Real-time video conferencing
- [ ] **Mobile App**: Native mobile application
- [ ] **Advanced Analytics**: Detailed learning analytics
- [ ] **Multi-language Support**: Internationalization
- [ ] **API Development**: RESTful API for mobile apps
- [ ] **Advanced Payment Gateways**: Stripe, PayPal integration
- [ ] **Certificate Generation**: Automated certificate creation

### Version History
- **v1.0.0**: Initial release with core features
- **v1.1.0**: Enhanced payment system
- **v1.2.0**: Improved user interface
- **v2.0.0**: Major feature additions (planned)

---

## ⭐ Star This Repository

If you find this project helpful, please give it a star on GitHub!

**Built with ❤️ using Django and Bootstrap 5**

---

*For more information, visit our [documentation](docs/) or [website](https://aicourseplatform.com).*
