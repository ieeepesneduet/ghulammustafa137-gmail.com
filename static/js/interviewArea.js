(function loadImage() {
    const img = document.getElementById('applicantImage');
    const request = new XMLHttpRequest();
    request.responseType = "blob";
    request.onload = function () {
        img.src = URL.createObjectURL(this.response)
    }
    request.open("GET", '/team/candidates/candidate/image');
    try{
        request.send();
    }catch(e){
        showMsg('failed to load the image');
    }
    const turnout = document.getElementById('turnout');
    turnout.onclick = function(){
        const experience = document.getElementById('experience').value;
        const interview = document.getElementById('interview').value;
        const potential = document.getElementById('potential').value;
        const remarks = document.getElementById('textkaarea').value;
        if(experience && interview && potential && remarks){
            showMsg('','danger');
            URL.revokeObjectURL(img.src);
            fetch(fetchUrl+'/team/candidates/candidate/turnout',{
                method:'post',
                headers: {
                    'Content-Type': 'application/json'
                },
                body:JSON.stringify({experience,interview,potential,remarks})
            })
                .then(response => {
                    if(!response.ok) throw new Error('Server encountered an error');
                    return response.json()
                })
                .then(data => {
                    if(data.err) throw new Error(data.err);
                    window.location = fetchUrl+'/team/candidates/All';
                })
                .catch(err => showMsg(err.message,'danger'))
        }else{
            showMsg('Incomplete form','danger')
        }
    }
})();