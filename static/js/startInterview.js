(function startInterviewHandler(){
   const tbody = document.getElementById('tableBody');
    tbody.onclick = function(e){
        if(e.target.tagName === 'BUTTON'){
            fetchData('/team/candidates/candidate',function(data){
                window.location = fetchUrl+'/team/candidates/candidate';
            },new PostJsonData({email:e.target.getAttribute('data-email')}));
        }
    }
})()