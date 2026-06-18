const uploadLabel = document.querySelector(".upload-label");
const fileInput = document.querySelector("#resume-upload");
const uploadIcon = document.querySelector(".upload-icon");
const uploadTitle = document.querySelector(".upload-title");
const uploadHint = document.querySelector(".upload-hint");

if (uploadLabel && fileInput && uploadIcon && uploadTitle && uploadHint) {
    const showFileName = () => {
        const file = fileInput.files[0];

        if (file) {
            uploadLabel.classList.add("has-file");
            uploadIcon.textContent = "";
            uploadTitle.textContent = file.name;
            uploadHint.textContent = "PDF selected";
        }
    };

    fileInput.addEventListener("change", showFileName);

    uploadLabel.addEventListener("dragover", (event) => {
        event.preventDefault();
        uploadLabel.classList.add("is-dragging");
    });

    uploadLabel.addEventListener("dragleave", () => {
        uploadLabel.classList.remove("is-dragging");
    });

    uploadLabel.addEventListener("drop", (event) => {
        event.preventDefault();
        uploadLabel.classList.remove("is-dragging");

        if (event.dataTransfer.files.length > 0) {
            fileInput.files = event.dataTransfer.files;
            showFileName();
        }
    });
}
