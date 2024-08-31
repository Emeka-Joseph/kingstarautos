document.addEventListener('DOMContentLoaded', function() {
    // Initialize the carousel
    $('.carousel').carousel({
        interval: 3000
    });
});




document.addEventListener('DOMContentLoaded', function() {
    var video = document.getElementById('myVideo');
    video.muted = true;
    video.play().catch(function(error) {
      console.log("Autoplay was prevented:", error);
    });
  });


/* for posting of lisitngs  */
$(document).ready(function() {
        $('#postPremiumAdForm').on('submit', function(e) {
            e.preventDefault();
            var formData = new FormData(this);
            
            $.ajax({
    url: '/post_premium_ad',
    type: 'POST',
    data: formData,
    success: function(response) {
        if (response.success) {
            alert('Premium Ad posted successfully!');
            $('#postPremiumAdModal').modal('hide');
            location.reload();
        } else {
            alert('Error: ' + response.message);
        }
    },
    error: function(jqXHR, textStatus, errorThrown) {
        console.error('AJAX Error:', textStatus, errorThrown);
        alert('Error posting Premium Ad. Please check the console and try again.');
    },
    cache: false,
    contentType: false,
    processData: false,
    });
        });
    });

    
    