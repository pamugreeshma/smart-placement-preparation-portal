let timeLeft = 60;

function startTimer() {
    let timer = document.getElementById("timer");
    if (!timer) return;

    let countdown = setInterval(function () {
        timeLeft--;
        if (timer) {
            timer.innerHTML = "⏰ Time Left: " + timeLeft + " seconds";
        }
        if (timeLeft <= 0) {
            clearInterval(countdown);
            if (timer) {
                timer.innerHTML = "⏰ Time's Up!";
            }
        }
    }, 1000);
}

document.addEventListener("DOMContentLoaded", startTimer);
