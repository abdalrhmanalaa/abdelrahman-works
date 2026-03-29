async function sendMsg() {
    let input = document.getElementById("userInput").value;
    let res = document.getElementById("response");

    let r = await fetch("/chat", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({message: input})
    });

    let data = await r.json();

    res.innerHTML += `<p>${input}</p>`;
    res.innerHTML += `<p>${data.reply}</p>`;
}