//* Marko Dasic 2022/0731


/////////////////////////////////////////////////////////// Marko //////////////////////////////////////////////////////////////////////////////

document.addEventListener("DOMContentLoaded", function() {
    const dropdownButton = document.querySelector(".dropdown-button");
    const dropdownMenu = document.querySelector(".dropdown-menu");

    document.addEventListener("click", function(event) {
        if (event.target.closest(".dropdown-button")) {
            dropdownMenu.classList.toggle("show");
        }
    });
});

// Upload Image
const photoInput = document.querySelector("#avatar");
const photoPreview = document.querySelector("#preview-avatar");

if (photoInput)
    photoInput.onchange = () => {
        const [file] = photoInput.files;
        if (file) {
        photoPreview.src = URL.createObjectURL(file);
        }
    };


/////////////////////////////////////////////////////////// Pavle //////////////////////////////////////////////////////////////////////////////


/////////////////////////////////////////////////////////// Vladana //////////////////////////////////////////////////////////////////////////////


/////////////////////////////////////////////////////////// Nina //////////////////////////////////////////////////////////////////////////////
