const form = document.querySelector("form");

async function handleSubmit(event) {
    event.preventDefault();

    const name = document.getElementById("Name").value;
    const email = document.getElementById("Email").value;
    const password = document.getElementById("Password").value;
    
    const response = await fetch("http://127.0.0.1:8000/register", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({name, email, password})
    });

    const data = await response.json();
    console.log(data);
}

form.addEventListener("submit", handleSubmit);
