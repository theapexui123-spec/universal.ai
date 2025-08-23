# Global Discount Feature

## Overview

The AI Course Platform now supports **Global Discounts** - site-wide promotional offers that apply to all courses with a beautiful banner display and countdown timer, similar to the Figma design you provided. This feature allows administrators to create compelling promotional campaigns that drive sales across the entire platform.

## Features

### 1. Global Discount Banner
- **Prominent Display**: Eye-catching banner at the top of all pages
- **Countdown Timer**: Real-time countdown showing days, hours, minutes, and seconds
- **Customizable Colors**: Choose from orange, red, blue, green, or purple themes
- **Responsive Design**: Works perfectly on all devices
- **Dismissible**: Users can close the banner if desired

### 2. Automatic Price Calculation
- **Site-wide Application**: Automatically applies to all courses
- **Priority System**: Individual course discounts take priority over global discounts
- **Real-time Updates**: Prices update automatically when discounts expire
- **Payment Integration**: Seamlessly integrated with the payment system

### 3. Admin Management
- **Easy Setup**: Simple admin interface for creating and managing discounts
- **Flexible Timing**: Set start and end dates for precise control
- **Bulk Actions**: Activate/deactivate multiple discounts at once
- **Status Monitoring**: Real-time status updates

## Visual Design

### Banner Layout (Based on Figma Design)
```html
<div class="bg-gradient-to-r from-orange-500 to-red-500 text-white p-6 rounded-lg text-center">
    <h3 class="text-xl mb-2">Limited Time Offer!</h3>
    <p class="mb-4">Get 50% off all AI courses</p>
    <div class="flex justify-center space-x-4">
        <div class="bg-white/20 rounded-lg p-3 min-w-[60px]">
            <div class="text-2xl font-bold">6</div>
            <div class="text-sm">Days</div>
        </div>
        <div class="bg-white/20 rounded-lg p-3 min-w-[60px]">
            <div class="text-2xl font-bold">23</div>
            <div class="text-sm">Hours</div>
        </div>
        <div class="bg-white/20 rounded-lg p-3 min-w-[60px]">
            <div class="text-2xl font-bold">19</div>
            <div class="text-sm">Minutes</div>
        </div>
        <div class="bg-white/20 rounded-lg p-3 min-w-[60px]">
            <div class="text-2xl font-bold">58</div>
            <div class="text-sm">Seconds</div>
        </div>
    </div>
</div>
```

### CSS Styling
- **Gradient Backgrounds**: Beautiful gradient effects for each color theme
- **Glass Morphism**: Semi-transparent countdown boxes with backdrop blur
- **Responsive Design**: Adapts to mobile, tablet, and desktop screens
- **Smooth Animations**: Subtle hover effects and transitions

## Technical Implementation

### Database Model
```python
class GlobalDiscount(models.Model):
    title = models.CharField(max_length=200, default="Limited Time Offer!")
    description = models.CharField(max_length=300, default="Get amazing discounts on all AI courses")
    discount_percentage = models.PositiveIntegerField(help_text="Discount percentage (e.g., 50 for 50% off)")
    
    # Timing
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(help_text="When the discount expires")
    
    # Status
    is_active = models.BooleanField(default=False)
    
    # Display settings
    show_banner = models.BooleanField(default=True)
    banner_color = models.CharField(max_length=20, default="orange", choices=[
        ('orange', 'Orange'),
        ('red', 'Red'),
        ('blue', 'Blue'),
        ('green', 'Green'),
        ('purple', 'Purple'),
    ])
```

### Key Methods
- `is_currently_active()`: Checks if discount is currently active
- `get_remaining_time()`: Returns seconds remaining until expiration
- `get_discount_multiplier()`: Calculates discount multiplier (e.g., 0.5 for 50% off)
- `apply_to_price()`: Applies discount to a given price

### Context Processor
```python
def global_discount(request):
    """Add global discount information to all templates"""
    try:
        global_discount = GlobalDiscount.objects.filter(
            is_active=True,
            show_banner=True
        ).first()
        
        if global_discount and global_discount.is_currently_active():
            return {
                'global_discount': global_discount,
                'global_discount_active': True,
            }
    except:
        pass
    
    return {
        'global_discount': None,
        'global_discount_active': False,
    }
```

## Admin Interface

### Setting Up Global Discounts
1. Go to Django Admin → Courses → Global Discounts
2. Click "Add Global Discount"
3. Fill in the details:
   - **Title**: "Limited Time Offer!" (or your custom title)
   - **Description**: "Get 50% off all AI courses" (or your message)
   - **Discount Percentage**: 50 (or your desired percentage)
   - **Start Date**: Leave blank for immediate start, or set a future date
   - **End Date**: When the discount should expire
   - **Show Banner**: Check to display the banner on all pages
   - **Banner Color**: Choose from orange, red, blue, green, or purple
4. Save the discount

### Admin Features
- **Status Display**: Shows current status (Active, Expired, Inactive)
- **Bulk Actions**: Activate/deactivate multiple discounts
- **Real-time Updates**: Status updates automatically based on time
- **Color Preview**: See how the banner will look with different colors

## Frontend Integration

### Banner Display
The global discount banner appears on all pages when active:
- **Home Page**: Prominent display at the top
- **Course Listings**: Shows discounted prices on all course cards
- **Course Details**: Displays discounted prices in course information
- **Payment Pages**: Shows global discount in payment summary

### Price Display Logic
1. **Individual Course Discount**: Takes priority if active
2. **Global Discount**: Applied if no individual discount is active
3. **Original Price**: Shown if no discounts are active

### Visual Indicators
- **Individual Discounts**: Red badge with countdown timer
- **Global Discounts**: Orange/warning badge without timer (timer is in banner)
- **Strikethrough Prices**: Original prices shown with line-through
- **Highlighted Discounts**: Discounted prices shown in bold colors

## Management Commands

### Create Sample Global Discount
```bash
python manage.py add_global_discount --days 7 --percentage 50
```
Creates a 50% discount for 7 days.

### Update Global Discount Status
```bash
python manage.py update_global_discounts
```
Updates the active status of all global discounts based on current time.

## JavaScript Countdown Timer

### Real-time Updates
- Updates every second
- Shows days, hours, minutes, and seconds
- Automatically hides banner when discount expires
- Responsive design for all screen sizes

### Features
- **Zero Padding**: Numbers are padded with zeros (e.g., "05" instead of "5")
- **Automatic Expiration**: Banner disappears when countdown reaches zero
- **Smooth Animations**: Smooth transitions and hover effects
- **Mobile Optimized**: Touch-friendly design for mobile devices

## Usage Examples

### Flash Sale (24 Hours)
```bash
python manage.py add_global_discount --days 1 --percentage 75
```
Creates a 75% off flash sale for 24 hours.

### Weekend Sale (3 Days)
```bash
python manage.py add_global_discount --days 3 --percentage 30
```
Creates a 30% off weekend sale.

### Holiday Sale (7 Days)
```bash
python manage.py add_global_discount --days 7 --percentage 40
```
Creates a 40% off holiday sale for a week.

## Best Practices

### 1. Timing
- **Realistic Deadlines**: Don't create fake urgency with very short timers
- **Clear Communication**: Use descriptive titles and messages
- **Consistent Branding**: Match banner colors with your brand

### 2. Discount Strategy
- **Competitive Pricing**: Research market rates before setting discounts
- **Limited Availability**: Use countdown timers to create urgency
- **Clear Value**: Communicate the value proposition clearly

### 3. Technical Management
- **Regular Updates**: Run update commands regularly
- **Testing**: Always test discounts before going live
- **Monitoring**: Track performance and conversion rates

## Testing

### Run All Tests
```bash
python manage.py test courses.tests
```

### Test Specific Features
```bash
python manage.py test courses.tests.GlobalDiscountTestCase
python manage.py test courses.tests.DiscountTestCase
```

### Test Coverage
- Global discount creation and management
- Price calculation accuracy
- Timing and expiration logic
- Priority system (individual vs global discounts)
- Banner display and countdown functionality

## Future Enhancements

### Planned Features
- **Email Notifications**: Alert users about expiring discounts
- **Analytics Dashboard**: Track discount performance and conversion rates
- **A/B Testing**: Test different discount amounts and messaging
- **Scheduled Discounts**: Automatically schedule future discounts
- **Student Segmentation**: Target specific user groups with different discounts
- **Coupon Codes**: Integration with coupon code system
- **Social Sharing**: Share discount offers on social media

### Advanced Features
- **Dynamic Pricing**: Adjust discounts based on demand
- **Inventory Management**: Limit discount availability
- **Geographic Targeting**: Different discounts for different regions
- **Time-based Targeting**: Different discounts for different times of day
- **User Behavior Tracking**: Personalized discount offers

## Troubleshooting

### Common Issues
1. **Banner Not Showing**: Check if discount is active and show_banner is enabled
2. **Prices Not Updating**: Run the update_global_discounts command
3. **Countdown Not Working**: Check JavaScript console for errors
4. **Payment Issues**: Verify discount is applied correctly in payment flow

### Debug Commands
```bash
# Check active discounts
python manage.py shell
>>> from courses.models import GlobalDiscount
>>> GlobalDiscount.objects.filter(is_active=True)

# Update discount status
python manage.py update_global_discounts

# Test price calculation
python manage.py shell
>>> from courses.models import Course, GlobalDiscount
>>> course = Course.objects.first()
>>> course.get_current_price()
```

## Support

For technical support or questions about the global discount feature:
- Check the admin interface for discount status
- Run management commands to update discount status
- Review the test suite for examples of proper usage
- Consult the documentation for detailed implementation guides
