document.addEventListener('DOMContentLoaded', function() {
    const blogBodyContent = document.getElementById('blog-body-content');
    const blogBodyTextarea = document.querySelector('textarea[name="blog_body"]');
    const addSubheadingBtn = document.getElementById('add-subheading');
    const addImageBtn = document.getElementById('add-image');

    addSubheadingBtn.addEventListener('click', function() {
        const subheadingDiv = document.createElement('div');
        subheadingDiv.className = 'subheading-container';
        subheadingDiv.innerHTML = `
            <input type="text" class="form-control subheading-text" placeholder="Enter subheading">
            <textarea class="form-control subheading-content" rows="3" placeholder="Enter content"></textarea>
        `;
        blogBodyContent.appendChild(subheadingDiv);
    });

    addImageBtn.addEventListener('click', function() {
        const imageDiv = document.createElement('div');
        imageDiv.className = 'image-container';
        imageDiv.innerHTML = `
            <input type="file" class="form-control-file image-upload" accept="image/*">
            <input type="text" class="form-control image-caption" placeholder="Enter image caption">
        `;
        blogBodyContent.appendChild(imageDiv);
    });

    // Function to compile content before form submission
    function compileContent() {
        let compiledContent = '';
        blogBodyContent.querySelectorAll('.subheading-container, .image-container').forEach(element => {
            if (element.classList.contains('subheading-container')) {
                const subheading = element.querySelector('.subheading-text').value;
                const content = element.querySelector('.subheading-content').value;
                compiledContent += `<h3>${subheading}</h3><p>${content}</p>`;
            } else if (element.classList.contains('image-container')) {
                const imageFile = element.querySelector('.image-upload').files[0];
                const caption = element.querySelector('.image-caption').value;
                if (imageFile) {
                    compiledContent += `<img src="${URL.createObjectURL(imageFile)}" alt="${caption}"><p>${caption}</p>`;
                }
            }
        });
        blogBodyTextarea.value = compiledContent;
    }

    // Attach the compileContent function to the form submission event
    document.querySelector('form').addEventListener('submit', compileContent);
});