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
        fetchData('/team/completed/'+id,function(data){
            togleEditable(true);
            showMsg('Changes saves succesfully','primary')
        },new PostFormData(candidateInfo))
    }
})();