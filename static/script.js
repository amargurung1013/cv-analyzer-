const uploadLabel = document.querySelector(".upload-label");
const fileInput = document.querySelector("#resume-upload");
const uploadIcon = document.querySelector(".upload-icon");
const uploadTitle = document.querySelector(".upload-title");
const uploadHint = document.querySelector(".upload-hint");
const preview = document.getElementById("file-preview");

if (uploadLabel && fileInput && uploadIcon && uploadTitle && uploadHint && preview) {
    
    // Function to format file size in a human-readable format
    const formatBytes = (bytes, decimals = 2) => {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const dm = decimals < 0 ? 0 : decimals;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
    };

    // Main function to update UI state based on selected files
    const updateUI = () => {
        const files = Array.from(fileInput.files);
        preview.innerHTML = "";

        if (files.length > 0) {
            uploadLabel.classList.add("has-file");
            uploadIcon.textContent = "";
            uploadTitle.textContent = `${files.length} resume${files.length > 1 ? 's' : ''} selected`;
            uploadHint.textContent = "Click or drop to update selection";

            files.forEach((file, index) => {
                const card = document.createElement("div");
                card.className = "file-card";
                
                // Set full filename as title attribute for tooltip on hover
                card.setAttribute("title", file.name);

                card.innerHTML = `
                    <div class="file-icon">
                        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                            <path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"></path>
                            <polyline points="14 2 14 8 20 8"></polyline>
                        </svg>
                    </div>
                    <div class="file-info">
                        <span class="file-card-name">${file.name}</span>
                        <span class="file-card-size">${formatBytes(file.size)}</span>
                    </div>
                    <button type="button" class="file-remove" aria-label="Remove file">
                        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                            <line x1="18" y1="6" x2="6" y2="18"></line>
                            <line x1="6" y1="6" x2="18" y2="18"></line>
                        </svg>
                    </button>
                `;

                // Add delete functionality
                const removeBtn = card.querySelector(".file-remove");
                removeBtn.addEventListener("click", (event) => {
                    event.preventDefault();
                    event.stopPropagation(); // Avoid triggering any label behavior just in case
                    
                    const dt = new DataTransfer();
                    const currentFiles = fileInput.files;
                    for (let i = 0; i < currentFiles.length; i++) {
                        if (i !== index) {
                            dt.items.add(currentFiles[i]);
                        }
                    }
                    fileInput.files = dt.files;
                    updateUI();
                });

                preview.appendChild(card);
            });
        } else {
            uploadLabel.classList.remove("has-file");
            uploadIcon.textContent = "↑";
            uploadTitle.textContent = "Drop your resumes";
            uploadHint.textContent = "Upload one or more PDFs • OCR Supported";
        }
    };

    // Native file input change
    fileInput.addEventListener("change", updateUI);

    // Drag-and-drop state styling
    uploadLabel.addEventListener("dragover", (event) => {
        event.preventDefault();
        uploadLabel.classList.add("is-dragging");
    });

    uploadLabel.addEventListener("dragleave", () => {
        uploadLabel.classList.remove("is-dragging");
    });

    // Drop handler
    uploadLabel.addEventListener("drop", (event) => {
        event.preventDefault();
        uploadLabel.classList.remove("is-dragging");

        if (event.dataTransfer.files.length > 0) {
            fileInput.files = event.dataTransfer.files;
            updateUI();
        }
    });
}