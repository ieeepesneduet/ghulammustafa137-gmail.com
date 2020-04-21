(function handleTurnout(){
    const turnoutForm = document.getElementById('candidateInfo');
    turnoutForm.onsubmit = function(e){
        e.preventDefault();
        fetchData('/team/candidates/candidate/turnout',function(data){
            window.history.back();
        },new PostFormData(turnoutForm))
    }
    const dontBtn = document.getElementById('dont');
    dontBtn.onclick = function(){
        fetchData('/team/candidates/candidate/turnout',function(data){
            sessionStorage.removeItem('email');
            window.history.back();
        })
    }
})();