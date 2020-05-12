(function interviewDetails(){
    const editBtn = document.getElementById('edit');
    function toggleEditable(val){
        const editable = document.getElementsByClassName('editable');
        for(let i=0;i<editable.length;i++){
            editable[i].disabled = val;
        }
    }
    editBtn.onclick = function(){
        toggleEditable(false);
    };
    const candidateInfo = document.getElementById('candidateInfo');
    candidateInfo.onsubmit = function(e){
        e.preventDefault();
        fetchData('/team/completed/'+id,function(data){
            toggleEditable(true);
            window.history.back();
        },new PostFormData(candidateInfo))
    }
})();