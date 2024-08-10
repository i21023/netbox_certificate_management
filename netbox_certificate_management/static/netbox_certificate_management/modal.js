let selected_file = null;


//Check for file upload
document.getElementById('file_input').addEventListener('change', function(event) {
    const file = event.target.files[0];


    if (file && (file.name.endsWith('.p12') || file.name.endsWith('.pfx'))) {
        // Copy the selected file to the hidden file input
        selected_file = event.target.files;

        // Display the modal to ask for the password
        display_modal();
    } else {
        // Directly handle file upload without password
        console.log("file:" + file.name)
        handleFileUpload(file);
    }
});

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

        // Hide the modal
        $('#password_modal').modal('hide');
    } else {
        alert("Please select a valid file.");
    }
}

function display_modal(){
    console.log("displaying modal");
    $('#password_modal').modal('show');
}

function handleFileUpload(file, password = null) {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('password', password);

    $.ajax({
        url: uploadUrl,
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
            const response = jqXHR.responseJSON;
            if (response && response.error) {
                // Display the error message
                displayErrorMessage(response.error);
            } else {
                displayErrorMessage('An unexpected error occurred.');
            }
        }
    });
}

function displayErrorMessage(message) {
    // Create a new div element for the message
    const messageDiv = $('<div>', {
        class: 'alert alert-danger',
        role: 'alert',
        text: message
    });

    // Append the message div to the body or a specific container
    $('#message-container').html(messageDiv);
}
