document.getElementById('resume-upload-form').addEventListener('submit', function(event) {
    event.preventDefault();

    const formData = new FormData();
    const fileInput = document.getElementById('resume');
    formData.append('resume', fileInput.files[0]);

    fetch('/upload', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        const resultDiv = document.getElementById('result');
        if (data.skills_found) {
            resultDiv.innerHTML = `
                <h3>Matching Skills:</h3>
                <ul>${data.skills_found.map(skill => `<li>${skill}</li>`).join('')}</ul>
                <p><strong>Improvement Suggestions:</strong> ${data.suggestions}</p>
                <p><strong>Resume Score:</strong> ${data.score}/100</p>
            `;
        } else {
            resultDiv.innerHTML = `<p>${data.message}</p>`;
        }
    })
    .catch(error => {
        document.getElementById('result').innerHTML = '<p>Error processing your request.</p>';
        console.error('Error:', error);
    });
});
