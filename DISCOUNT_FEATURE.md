# Time-Limited Discount Feature

## Overview

The AI Course Platform now supports time-limited discounts for courses. This feature allows administrators to create promotional offers with specific start and end dates, automatically displaying discounted prices with countdown timers to create urgency.

## Features

### 1. Discount Management
- **Discount Price**: Set a reduced price for the course during the promotion period
- **Start Date**: Optional start date for when the discount becomes active
- **End Date**: Required end date when the discount expires
- **Automatic Status**: Discount status is automatically updated based on current time

### 2. Visual Display
- **Strikethrough Original Price**: Original price is shown with a line through it
- **Highlighted Discount Price**: Discounted price is prominently displayed in red
- **Discount Percentage Badge**: Shows the percentage saved (e.g., "Save 20%")
- **Countdown Timer**: Real-time countdown showing time remaining until discount expires

### 3. Payment Integration
- **Automatic Price Calculation**: Payment system automatically uses discounted price when active
- **Payment Summary**: Shows both original and discounted prices in payment flow
- **Expired Discount Handling**: Automatically reverts to original price when discount expires

## Admin Interface

### Setting Up Discounts
1. Go to Django Admin → Courses → Course
2. Select a course to edit
3. In the "Discount Settings" section:
   - Set `Discount Price` (e.g., 80.00 for 20% off a 100.00 course)
   - Set `Discount Start Date` (optional, leave blank for immediate start)
   - Set `Discount End Date` (required)
   - Check `Is Discount Active` to enable the discount
4. Save the course

### Admin Actions
- **Activate Discounts**: Bulk activate discounts for selected courses
- **Deactivate Discounts**: Bulk deactivate discounts for selected courses
- **Discount Status**: View current discount status in the course list

## Frontend Display

### Course Cards
Discounts are displayed on:
- Home page featured courses
- Course listing page
- Course detail page

### Countdown Timer
- Updates every second
- Shows days, hours, minutes, and seconds remaining
- Automatically hides when discount expires
- Uses monospace font for better readability

## Technical Implementation

### Database Fields
```python
discount_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
discount_start_date = models.DateTimeField(null=True, blank=True)
discount_end_date = models.DateTimeField(null=True, blank=True)
is_discount_active = models.BooleanField(default=False)
```

### Model Methods
- `has_active_discount()`: Checks if discount is currently active
- `get_current_price()`: Returns discounted price if active, otherwise original price
- `get_discount_percentage()`: Calculates discount percentage
- `get_discount_remaining_time()`: Returns seconds remaining until discount expires

### JavaScript Countdown
- Real-time countdown timer
- Automatic expiration handling
- Responsive display updates

## Management Commands

### Update Discount Status
```bash
python manage.py update_discounts
```
Updates the `is_discount_active` field for all courses based on current time.

### Add Sample Discounts
```bash
python manage.py add_sample_discounts --days 7
```
Adds 20% discounts to the first 3 published courses for testing.

## CSS Styling

### Discount Elements
```css
.discount-price-container {
    text-align: center;
}

.countdown-timer {
    font-weight: 600;
}

.countdown-timer .countdown-text {
    font-family: 'Courier New', monospace;
    font-weight: bold;
}

.discount-badge {
    animation: pulse 2s infinite;
}
```

## Testing

Run the discount tests:
```bash
python manage.py test courses.tests.DiscountTestCase
```

Tests cover:
- Active/inactive discount status
- Expired discounts
- Future start dates
- Percentage calculations
- Remaining time calculations
- Free course handling

## Usage Examples

### Creating a 24-Hour Flash Sale
1. Set discount price to 50% off
2. Set start date to current time
3. Set end date to 24 hours from now
4. Activate the discount

### Creating a Weekend Sale
1. Set discount price to 30% off
2. Set start date to Friday 9 AM
3. Set end date to Sunday 11:59 PM
4. Activate the discount

### Creating a Limited-Time Offer
1. Set discount price to 25% off
2. Leave start date blank (immediate start)
3. Set end date to 7 days from now
4. Activate the discount

## Best Practices

1. **Clear Communication**: Use descriptive discount messages
2. **Realistic Timeframes**: Don't create fake urgency with very short timers
3. **Regular Updates**: Run the update_discounts command regularly
4. **Testing**: Always test discounts before going live
5. **Monitoring**: Keep track of discount performance and conversion rates

## Future Enhancements

Potential improvements:
- Email notifications for expiring discounts
- Bulk discount creation tools
- Discount analytics and reporting
- Coupon code integration
- Student-specific discounts
- Automatic discount scheduling
