(function stuckFormHandler(){
    const stuckForm = document.getElementById('stuck');
    stuckForm.onsubmit = function(e){
        e.preventDefault();
        fetchData('/team/candidate/stuck',function(data){
            showMsg('Success.You should now be able to interview the candidate again','success')
        },new PostFormData(stuckForm))
    }
})()