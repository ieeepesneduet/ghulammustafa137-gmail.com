(function interviewDetails(){
    const editBtn = document.getElementById('edit');
    function togleEditable(val){
        const editable = document.getElementsByClassName('editable');
        for(let i=0;i<editable.length;i++){
            editable[i].disabled = val;
        }
    }
    editBtn.onclick = function(){
        togleEditable(false);
    };
    const candidateInfo = document.getElementById('candidateInfo');
    candidateInfo.onsubmit = function(e){
        e.preventDefault();
        fetch(fetchUrl+'/team/completed/'+id,{
            method:'post',
            body: new FormData(candidateInfo)
        })
            .then(response => {
                if(!response.ok) throw new Error('Server encountered an error')
                return response.json()
            })
            .then(data => {
                if(data.err) throw new Error(data.err)
                togleEditable(true);
                showMsg('Changes saves succesfully','primary')
            })
            .catch(err => showMsg(err.message,'danger'))
    }

})();