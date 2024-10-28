let selected_file = null;

// Function to attach the event listener
function attachFileInputListener() {
    const fileInput = document.getElementById('file_input');
    fileInput.addEventListener('change', handleFileInputChange);
}

// Handle file input change
function handleFileInputChange(event) {
    const file = event.target.files[0];


    if (file && (file.name.endsWith('.p12') || file.name.endsWith('.pfx'))) {
        // Copy the selected file to the hidden file input
        selected_file = event.target.files;

        // Display the modal to ask for the password
        display_modal();
    } else {
        // Directly handle file upload without password
        console.log("file:" + file.name);
        handleFileUpload(file);
    }
}

// Attach the event listener initially
attachFileInputListener();

function submitPasswordForm() {
    // Get the password from the input field
    const password = $('#password').val();

    // Get the file from the hidden input field
    const fileInput = selected_file;

    // Ensure the file input is valid before accessing the files property
    if (fileInput && fileInput.length > 0) {
        const file = fileInput[0];

        // Proceed with the file upload, passing the password
        handleFileUpload(file, password);

        // Hide the modal and reset fields
        $('#password_modal').modal('hide');
        reset_modal();
    } else {
        console.log("Please select a valid file.");
    }
}

function display_modal() {
    console.log("displaying modal");
    $('#password_modal').modal('show');
}

function hide_modal() {
    $('#password_modal').modal('hide');
    reset_modal();
}

function reset_modal() {
    // Reset the modal state
    $('#password').val('');
    selected_file = null;
    $('#password_modal').on('hidden.bs.modal', function () {
        $(this).find('form').trigger('reset');
    });

    // Reset the file input element
    const fileInput = document.getElementById('file_input');
    fileInput.value = ''; // Clear the input value to allow re-triggering the change event
    attachFileInputListener(); // Reattach the event listener
}

function handleFileUpload(file, password = null) {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('password', password);
    
    const type=$('#button_identifier')

    $.ajax({
        url: `${uploadUrl}?pk_id=${type.val()}`,
        type: 'POST',
        data: formData,
        processData: false,
        contentType: false,
        headers: {
            "X-CSRFToken": csfrToken,
        },
        success: function(response) {
            if (response.redirect) {
                window.location.href = response.redirect;  // Redirect to the new URL
            } else {
                console.error("Redirect URL not provided.");
            }
        },
        error: function(jqXHR, textStatus, errorThrown) {
            displayErrorMessage(jqXHR.responseJSON.error);
        }
    });
}

function displayErrorMessage(message) {
    const errorContainer = document.getElementById('django-messages');
    const toast = document.createElement('div');
    toast.className = 'toast toast-dark border-0 shadow-sm fade show';
    toast.setAttribute('role', 'alert');
    toast.setAttribute('aria-live', 'assertive');
    toast.setAttribute('aria-atomic', 'true');
    toast.setAttribute('data-bs-delay', '10000'); // 10 seconds delay

    toast.innerHTML = `
        <div class="toast-header text-bg-danger">
            <i class="mdi mdi-alert me-1"></i>
            Error
            <button type="button" class="btn-close me-0 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
        </div>
        <div class="toast-body">
            ${message}
        </div>
    `;

    errorContainer.appendChild(toast);
}
