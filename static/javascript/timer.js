const emailBtn = document.querySelector(".emailBtn");
const countdownClockTitle = document.querySelector(".countdownTitle");
const submitBtn = document.getElementById("submitBtn")

let countdown;
const TIMER_DURATION = 5; // 計時器持續 30 秒

const showTimer = (seconds) => {
    const minutes = Math.floor(seconds / 60);
    const remainderSeconds = seconds % 60;
    countdownClockTitle.textContent = `${minutes}:${remainderSeconds < 10 ? "0" + remainderSeconds : remainderSeconds}`;
};

const startTimer = (inputSeconds) => {
    const endTime = Date.now() + inputSeconds * 1000;

    showTimer(inputSeconds);

    countdown = setInterval(() => {
        const timeLeft = Math.round((endTime - Date.now()) / 1000);

        if (timeLeft <= 0) {
            clearInterval(countdown);
            countdownClockTitle.textContent = "驗證碼已過期，請重新獲取驗證信";
            // alert("驗證碼已過期，請重新寄送驗證信");
            submitBtn.disabled = true;  
        } else {
            showTimer(timeLeft);
            submitBtn.disabled = false;
        }
    }, 1000);
};

const resetTimerAndSendEmail = () => {
    clearInterval(countdown);
    startTimer(TIMER_DURATION);
    // 在此處添加重新寄送驗證信的邏輯，例如：
    fetch("/verify/", { method: "GET" })
        .then(response => {
            if (response.ok) {
                alert("驗證信已重新寄送");
            } else {
                alert("重新寄送失敗，請稍後再試");
            }
        })
        .catch(() => alert("已經寄送驗證碼"));
};

window.onload = () => startTimer(TIMER_DURATION);
emailBtn.addEventListener("click", resetTimerAndSendEmail);
