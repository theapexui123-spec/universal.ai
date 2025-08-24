// Optimized navbar transparency effect
document.addEventListener('DOMContentLoaded', function() {
    const navbar = document.querySelector('.navbar');
    let ticking = false;
    
    function updateNavbar() {
        if (window.scrollY > 50) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }
        ticking = false;
    }
    
    function requestTick() {
        if (!ticking) {
            requestAnimationFrame(updateNavbar);
            ticking = true;
        }
    }
    
    window.addEventListener('scroll', requestTick, { passive: true });
});

// Optimized countdown timer with throttling
document.addEventListener('DOMContentLoaded', function() {
    const countdownTimers = document.querySelectorAll('.countdown-timer');
    
    if (countdownTimers.length === 0) return;
    
    // Throttle function to limit updates
    function throttle(func, limit) {
        let inThrottle;
        return function() {
            const args = arguments;
            const context = this;
            if (!inThrottle) {
                func.apply(context, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        }
    }
    
    countdownTimers.forEach(function(timer) {
        const endTimeStr = timer.getAttribute('data-end-time');
        const countdownText = timer.querySelector('.countdown-text');
        
        if (!endTimeStr || !countdownText) return;
        
        // Parse the end time
        const endTime = new Date(endTimeStr.replace(' ', 'T'));
        const now = new Date();
        
        function updateCountdown() {
            const now = new Date();
            const timeLeft = endTime - now;
            
            if (timeLeft <= 0) {
                countdownText.textContent = 'Discount Expired';
                timer.style.display = 'none';
                return;
            }
            
            // Calculate time components
            const days = Math.floor(timeLeft / (1000 * 60 * 60 * 24));
            const hours = Math.floor((timeLeft % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
            const minutes = Math.floor((timeLeft % (1000 * 60 * 60)) / (1000 * 60));
            const seconds = Math.floor((timeLeft % (1000 * 60)) / 1000);
            
            // Format the countdown text
            let countdownString = '';
            if (days > 0) {
                countdownString = `${days}d ${hours}h ${minutes}m`;
            } else if (hours > 0) {
                countdownString = `${hours}h ${minutes}m ${seconds}s`;
            } else if (minutes > 0) {
                countdownString = `${minutes}m ${seconds}s`;
            } else {
                countdownString = `${seconds}s`;
            }
            
            countdownText.textContent = countdownString;
        }
        
        // Update immediately
        updateCountdown();
        
        // Update every second with throttling
        const throttledUpdate = throttle(updateCountdown, 1000);
        setInterval(throttledUpdate, 1000);
    });
});

// Lazy loading for images
document.addEventListener('DOMContentLoaded', function() {
    if ('IntersectionObserver' in window) {
        const imageObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.src;
                    img.classList.remove('lazy');
                    imageObserver.unobserve(img);
                }
            });
        });
        
        document.querySelectorAll('img[data-src]').forEach(img => {
            imageObserver.observe(img);
        });
    }
});

// Lazy loading for courses
function initCourseLazyLoading() {
    let currentPage = 1;
    let isLoading = false;
    let hasMorePages = true;
    
    // Load more courses when user scrolls near bottom
    function loadMoreCourses() {
        if (isLoading || !hasMorePages) return;
        
        isLoading = true;
        currentPage++;
        
        // Show loading indicator
        const loadingHtml = `
            <div class="col-12 text-center py-4" id="loading-indicator">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
                <p class="mt-2 text-muted">Loading more courses...</p>
            </div>
        `;
        
        const courseContainer = document.querySelector('.course-container');
        if (courseContainer) {
            courseContainer.insertAdjacentHTML('beforeend', loadingHtml);
        }
        
        // Get current filters
        const urlParams = new URLSearchParams(window.location.search);
        const category = urlParams.get('category') || '';
        const difficulty = urlParams.get('difficulty') || '';
        const sort = urlParams.get('sort') || '';
        const query = urlParams.get('q') || '';
        
        // Make AJAX request
        fetch(`/courses/lazy-load/?page=${currentPage}&category=${category}&difficulty=${difficulty}&sort=${sort}&q=${query}`, {
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.html) {
                // Remove loading indicator
                const loadingIndicator = document.getElementById('loading-indicator');
                if (loadingIndicator) {
                    loadingIndicator.remove();
                }
                
                // Append new courses
                courseContainer.insertAdjacentHTML('beforeend', data.html);
                
                // Update pagination state
                hasMorePages = data.has_next;
                
                // Initialize animations for new content
                if (typeof AOS !== 'undefined') {
                    AOS.refresh();
                }
            }
        })
        .catch(error => {
            console.error('Error loading courses:', error);
            // Remove loading indicator
            const loadingIndicator = document.getElementById('loading-indicator');
            if (loadingIndicator) {
                loadingIndicator.remove();
            }
        })
        .finally(() => {
            isLoading = false;
        });
    }
    
    // Intersection Observer for infinite scroll
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting && hasMorePages) {
                loadMoreCourses();
            }
        });
    }, {
        rootMargin: '100px' // Load when user is 100px away from bottom
    });
    
    // Observe the last course card or a sentinel element
    function observeLastElement() {
        const courseCards = document.querySelectorAll('.course-card');
        if (courseCards.length > 0) {
            const lastCard = courseCards[courseCards.length - 1];
            observer.observe(lastCard);
        }
    }
    
    // Initialize lazy loading
    if (document.querySelector('.course-container')) {
        observeLastElement();
        
        // Re-observe after new content is loaded
        const courseContainer = document.querySelector('.course-container');
        const mutationObserver = new MutationObserver(() => {
            observeLastElement();
        });
        
        mutationObserver.observe(courseContainer, {
            childList: true,
            subtree: true
        });
    }
}

// Initialize lazy loading when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    initCourseLazyLoading();
});

// Debounced search for better performance
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Apply debouncing to search inputs
document.addEventListener('DOMContentLoaded', function() {
    const searchInputs = document.querySelectorAll('input[type="search"], input[name="q"]');
    
    searchInputs.forEach(input => {
        const debouncedSearch = debounce(function() {
            // Trigger search after user stops typing
            if (this.value.length >= 2) {
                // You can add AJAX search here if needed
                console.log('Searching for:', this.value);
            }
        }, 300);
        
        input.addEventListener('input', debouncedSearch);
    });
});
