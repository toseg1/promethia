/**
 * Profile Page JavaScript - Image cropping and form handling
 */

let cropper;
let currentImageFile;

document.addEventListener('DOMContentLoaded', function() {
    // Initialize Bootstrap tooltips
    $('[data-toggle="tooltip"]').tooltip();
    
    const imageInput = document.getElementById('profile-image-input');
    const cropImage = document.getElementById('crop-image');
    const cropperModal = $('#cropperModal');
    const cropAndSaveBtn = document.getElementById('crop-and-save');
    
    // Handle file selection
    imageInput.addEventListener('change', function(e) {
        const file = e.target.files[0];
        if (file) {
            currentImageFile = file;
            
            if (!file.type.startsWith('image/')) {
                alert('Please select an image file.');
                return;
            }
            
            if (file.size > 5 * 1024 * 1024) {
                alert('Image must be smaller than 5MB.');
                return;
            }
            
            const reader = new FileReader();
            reader.onload = function(event) {
                cropImage.src = event.target.result;
                cropperModal.modal('show');
                
                cropperModal.on('shown.bs.modal', function() {
                    if (cropper) {
                        cropper.destroy();
                    }
                    
                    cropper = new Cropper(cropImage, {
                        aspectRatio: 1,
                        viewMode: 2,
                        minCropBoxWidth: 100,
                        minCropBoxHeight: 100,
                        responsive: true,
                        restore: false,
                        checkCrossOrigin: false,
                        checkOrientation: false,
                        cropBoxMovable: true,
                        cropBoxResizable: true,
                        toggleDragModeOnDblclick: false,
                    });
                });
            };
            reader.readAsDataURL(file);
        }
    });
    
    // Handle crop and save
    cropAndSaveBtn.addEventListener('click', function() {
        if (cropper) {
            const canvas = cropper.getCroppedCanvas({
                width: 300,
                height: 300,
                imageSmoothingEnabled: true,
                imageSmoothingQuality: 'high',
            });
            
            canvas.toBlob(function(blob) {
                const formData = new FormData();
                formData.append('profile_picture', blob, 'profile.jpg');
                formData.append('csrfmiddlewaretoken', document.querySelector('[name=csrfmiddlewaretoken]').value);
                
                // Add all form fields
                const form = document.getElementById('profile-form');
                const formInputs = form.querySelectorAll('input, textarea, select');
                formInputs.forEach(input => {
                    if (input.name && input.name !== 'profile_picture' && input.name !== 'csrfmiddlewaretoken') {
                        formData.append(input.name, input.value);
                    }
                });
                
                cropAndSaveBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Saving...';
                cropAndSaveBtn.disabled = true;
                
                fetch(window.location.href, {
                    method: 'POST',
                    body: formData,
                })
                .then(response => {
                    if (response.ok) {
                        window.location.reload();
                    } else {
                        throw new Error('Upload failed');
                    }
                })
                .catch(error => {
                    alert('Error uploading image. Please try again.');
                    cropAndSaveBtn.innerHTML = 'Crop & Save';
                    cropAndSaveBtn.disabled = false;
                });
            }, 'image/jpeg', 0.9);
        }
    });
    
    // Handle remove picture
    const removePictureBtn = document.getElementById('remove-picture-btn');
    if (removePictureBtn) {
        removePictureBtn.addEventListener('click', function() {
            if (confirm('Are you sure you want to remove your profile picture?')) {
                const formData = new FormData();
                formData.append('remove_picture', 'true');
                formData.append('csrfmiddlewaretoken', document.querySelector('[name=csrfmiddlewaretoken]').value);
                
                // Add all form fields
                const form = document.getElementById('profile-form');
                const formInputs = form.querySelectorAll('input, textarea, select');
                formInputs.forEach(input => {
                    if (input.name && input.name !== 'profile_picture' && input.name !== 'csrfmiddlewaretoken') {
                        formData.append(input.name, input.value);
                    }
                });
                
                removePictureBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Removing...';
                removePictureBtn.disabled = true;
                
                fetch(window.location.href, {
                    method: 'POST',
                    body: formData,
                })
                .then(response => {
                    if (response.ok) {
                        window.location.reload();
                    } else {
                        throw new Error('Remove failed');
                    }
                })
                .catch(error => {
                    alert('Error removing image. Please try again.');
                    removePictureBtn.innerHTML = '<i class="fas fa-trash"></i> Remove Photo';
                    removePictureBtn.disabled = false;
                });
            }
        });
    }
    
    // Clean up cropper when modal is hidden
    cropperModal.on('hidden.bs.modal', function() {
        if (cropper) {
            cropper.destroy();
            cropper = null;
        }
        imageInput.value = '';
    });
});