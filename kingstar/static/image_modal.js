document.addEventListener('DOMContentLoaded', function() {
    const images = document.querySelectorAll('.image-clickable');
    const modalImage = document.getElementById('modalImage');
    const prevButton = document.getElementById('prevButton');
    const nextButton = document.getElementById('nextButton');
    let currentIndex = 0;

    images.forEach((img, index) => {
        img.addEventListener('click', function() {
            currentIndex = parseInt(this.getAttribute('data-index'));
            updateModalImage();
        });
    });

    prevButton.addEventListener('click', function() {
        currentIndex = (currentIndex - 1 + images.length) % images.length;
        updateModalImage();
    });

    nextButton.addEventListener('click', function() {
        currentIndex = (currentIndex + 1) % images.length;
        updateModalImage();
    });

    function updateModalImage() {
        modalImage.src = images[currentIndex].src;
    }
});