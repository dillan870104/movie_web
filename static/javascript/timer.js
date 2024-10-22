const emailBtn = document.querySelector(".emailBtn");
const countdownClockTitle = document.querySelector(".countdownTitle");


let countdown;

const showTimer = (inputSeconds) => {
    const minutes = Math.floor(inputSeconds / 60);
    const remainderSeconds = inputSeconds % 60;
    countdownClockTitle.textContent = `
        ${minutes}:${remainderSeconds < 10 
            ? "0" + remainderSeconds 
            : remainderSeconds}
    `;
}



function timer(inputSeconds){

    const now = Date.now();
    const done = now + inputSeconds * 1000;
    showTimer(inputSeconds);
    

    countdown = setInterval(()=>{
        const tiemleft = Math.round((done-Date.now())/ 1000);
        if(tiemleft<= 0){
            clearInterval(countdown);
            //window.location.assign(window.location.href);
        }
        showTimer(tiemleft)
    }, 1000)
} 
const resetTimer = ()=> {
    window.history.go(0)    
}

window.onload=timer(300)
// emailBtn.addEventListener("click", resetTimer())
