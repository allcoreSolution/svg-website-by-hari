// Resume modal submission is handled in script.js with full validation and custom success UI.

async function deleteResume(id) {

    if (!confirm("Delete this resume?")) return;

    const response = await fetch(
        `/api/resume/${id}`,
        {
            method: "DELETE",
            headers: {
                "X-CSRFToken": (typeof getCookie === 'function' ? getCookie('csrftoken') : '') || ''
            }
        }
    );

    const result = await response.json();

    alert(result.message);
}