// SuntynAI Homepage JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Initialize all components
    initSmoothScrolling();
    initScrollAnimations();
    initNavbarScrollEffect();
    initMobileNavigation();
});

// Smooth scrolling for navigation links
function initSmoothScrolling() {
    const smoothScrollLinks = document.querySelectorAll('a[href^="#"]');

    smoothScrollLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();

            const targetId = this.getAttribute('href');
            const targetElement = document.querySelector(targetId);

            if (targetElement) {
                const navbarHeight = document.querySelector('.navbar').offsetHeight;
                const targetPosition = targetElement.offsetTop - navbarHeight;

                window.scrollTo({
                    top: targetPosition,
                    behavior: 'smooth'
                });

                // Close mobile menu if open
                const navbarCollapse = document.querySelector('.navbar-collapse');
                if (navbarCollapse.classList.contains('show')) {
                    const navbarToggler = document.querySelector('.navbar-toggler');
                    navbarToggler.click();
                }
            }
        });
    });
}

// Animate elements on scroll
function initScrollAnimations() {
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -100px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
            }
        });
    }, observerOptions);

    // Add fade-in class to elements that should animate
    const animateElements = document.querySelectorAll('.feature-card, .testimonial-card, .contact-card');
    animateElements.forEach(el => {
        el.classList.add('fade-in');
        observer.observe(el);
    });
}

// Navbar scroll effect
function initNavbarScrollEffect() {
    const navbar = document.querySelector('.navbar');
    let lastScrollTop = 0;

    window.addEventListener('scroll', function() {
        const scrollTop = window.pageYOffset || document.documentElement.scrollTop;

        // Add/remove background based on scroll position
        if (scrollTop > 50) {
            navbar.style.background = 'rgba(13, 17, 23, 0.98)';
            navbar.style.boxShadow = '0 2px 20px rgba(0, 0, 0, 0.3)';
        } else {
            navbar.style.background = 'rgba(13, 17, 23, 0.95)';
            navbar.style.boxShadow = 'none';
        }

        // Hide/show navbar on scroll (optional)
        if (scrollTop > lastScrollTop && scrollTop > 100) {
            // Scrolling down
            navbar.style.transform = 'translateY(-100%)';
        } else {
            // Scrolling up
            navbar.style.transform = 'translateY(0)';
        }

        lastScrollTop = scrollTop;

        // Update active navigation item
        updateActiveNavItem();
    });
}

// Update active navigation item based on scroll position
function updateActiveNavItem() {
    const sections = document.querySelectorAll('section[id]');
    const navLinks = document.querySelectorAll('.nav-link[href^="#"]');

    let current = '';
    const scrollPosition = window.pageYOffset + 100;

    sections.forEach(section => {
        const sectionTop = section.offsetTop;
        const sectionHeight = section.clientHeight;

        if (scrollPosition >= sectionTop && scrollPosition < sectionTop + sectionHeight) {
            current = section.getAttribute('id');
        }
    });

    navLinks.forEach(link => {
        link.classList.remove('active');
        if (link.getAttribute('href') === `#${current}`) {
            link.classList.add('active');
        }
    });
}

// Mobile navigation improvements
function initMobileNavigation() {
    const navbarToggler = document.querySelector('.navbar-toggler');
    const navbarCollapse = document.querySelector('.navbar-collapse');

    // Close mobile menu when clicking outside
    document.addEventListener('click', function(e) {
        if (!navbarToggler.contains(e.target) && !navbarCollapse.contains(e.target)) {
            if (navbarCollapse.classList.contains('show')) {
                navbarToggler.click();
            }
        }
    });

    // Add touch-friendly hover effects for mobile
    if ('ontouchstart' in window) {
        const hoverElements = document.querySelectorAll('.feature-card, .testimonial-card, .btn');

        hoverElements.forEach(element => {
            element.addEventListener('touchstart', function() {
                this.classList.add('touch-hover');
            });

            element.addEventListener('touchend', function() {
                setTimeout(() => {
                    this.classList.remove('touch-hover');
                }, 300);
            });
        });
    }
}

// Add loading animation
window.addEventListener('load', function() {
    document.body.classList.add('loaded');

    // Trigger initial animations
    setTimeout(() => {
        const heroElements = document.querySelectorAll('.hero-content > *');
        heroElements.forEach((el, index) => {
            setTimeout(() => {
                el.style.opacity = '1';
                el.style.transform = 'translateY(0)';
            }, index * 200);
        });
    }, 100);
});

function processFile() {
    const fileInput = document.getElementById('fileInput');
    const file = fileInput.files[0];

    if (!file) {
        showAlert('Please select a file first.', 'error');
        return;
    }

    // Validate file type for images
    const toolId = document.body.dataset.toolId;
    if (toolId && toolId.includes('image')) {
        const validImageTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/bmp', 'image/webp'];
        if (!validImageTypes.includes(file.type)) {
            showAlert('Please select a valid image file (JPEG, PNG, GIF, BMP, WebP).', 'error');
            return;
        }
    }

    const formData = new FormData();
    formData.append('file', file);

    // Add tool-specific parameters with validation
    if (toolId) {
        const inputs = document.querySelectorAll('input, select, textarea');
        inputs.forEach(input => {
            if (input.id && input.value !== '') {
                let value = input.value;

                // Validate numeric inputs
                if (input.type === 'number' || input.type === 'range') {
                    const numValue = parseFloat(value);
                    if (!isNaN(numValue)) {
                        // Set reasonable limits
                        if (input.id === 'width' || input.id === 'height') {
                            value = Math.max(10, Math.min(5000, numValue)).toString();
                        } else if (input.id === 'quality') {
                            value = Math.max(10, Math.min(100, numValue)).toString();
                        } else if (input.id === 'angle') {
                            value = Math.max(-360, Math.min(360, numValue)).toString();
                        }
                        formData.append(input.id, value);
                    }
                } else {
                    formData.append(input.id, value);
                }
            } else if (input.type === 'checkbox') {
                formData.append(input.id, input.checked ? 'true' : 'false');
            }
        });

        // Add default values for image resize if not provided
        if (toolId === 'image-resize') {
            if (!formData.has('width')) formData.append('width', '800');
            if (!formData.has('height')) formData.append('height', '600');
        }

        // Add default quality for compression
        if (toolId === 'image-compress' && !formData.has('quality')) {
            formData.append('quality', '85');
        }
    }

    showSpinner(true);

    fetch(`/process/${toolId}`, {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        showSpinner(false);
        if (data.success) {
            showDownloadButton(data.download_url, data.filename);
            showAlert(data.message || 'File processed successfully!', 'success');
        } else {
            showAlert(data.error || 'Processing failed', 'error');
        }
    })
    .catch(error => {
        showSpinner(false);
        console.error('Error:', error);
        showAlert('An error occurred while processing the file.', 'error');
    });
}

// Add real-time validation for numeric inputs
document.addEventListener('DOMContentLoaded', function() {
    const numericInputs = document.querySelectorAll('input[type="number"], input[type="range"]');
    numericInputs.forEach(input => {
        input.addEventListener('input', function() {
            let value = parseFloat(this.value);

            if (this.id === 'width' || this.id === 'height') {
                if (value < 10) this.value = 10;
                if (value > 5000) this.value = 5000;
            } else if (this.id === 'quality') {
                if (value < 10) this.value = 10;
                if (value > 100) this.value = 100;
                // Update quality display
                const display = document.getElementById('qualityValue');
                if (display) display.textContent = this.value;
            } else if (this.id === 'angle') {
                if (value < -360) this.value = -360;
                if (value > 360) this.value = 360;
            }
        });
    });
});