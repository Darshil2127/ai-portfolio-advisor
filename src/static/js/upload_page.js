// Client-side JavaScript for the Upload Page (index.html)
// Currently, no specific client-side logic is implemented beyond standard form submission.
// This file is included for future enhancements, such as:
// - Client-side validation of the file type or size before upload.
// - AJAX form submission to provide a smoother UX without full page reloads (though current backend redirects).
// - Displaying more interactive loading indicators.

document.addEventListener("DOMContentLoaded", function() {
    const form = document.querySelector("form");
    if (form) {
        form.addEventListener("submit", function() {
            const button = form.querySelector("button[type='submit']");
            if (button) {
                button.disabled = true;
                button.textContent = "Processing...";
            }
        });
    }
});

