document.addEventListener('DOMContentLoaded', function() {
    var carousel = new bootstrap.Carousel(document.getElementById('imageCarousel'), {
        interval: false  // Disable auto-sliding
    });

    // Add click events for navigation dots if needed
    var indicators = document.querySelectorAll('.carousel-indicators button');
    indicators.forEach(function(indicator, index) {
        indicator.addEventListener('click', function() {
            carousel.to(index);
        });
    });
});

