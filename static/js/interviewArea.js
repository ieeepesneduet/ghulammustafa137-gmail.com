(function handleTurnout(){
    const turnoutForm = document.getElementById('candidateInfo');
    turnoutForm.onsubmit = function(e){
        e.preventDefault();
        fetch(fetchUrl+'/team/candidates/candidate/turnout',{
            method:'post',
            body: new FormData(turnoutForm)
        })
            .then(response => {
                if(!response.ok) throw new Error('Server encountered an error')
                return response.json()
            })
            .then(data => {
                if(data.err) throw new Error(data.err)
                window.history.back();
            })
            .catch(err => showMsg(err.message,'danger'))
    }
    const dontBtn = document.getElementById('dont');
    dontBtn.onclick = function(){
        fetch(fetchUrl+'/team/candidates/candidate/turnout')
            .then(response => {
                if(!response.ok) throw new Error('server encountered an error')
                sessionStorage.removeItem('email');
                window.history.back()
            }).catch(err => showMsg(err.message,'danger'))
    }
})();