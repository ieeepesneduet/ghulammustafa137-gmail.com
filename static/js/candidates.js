(function handleLoadMore(){
    let offset = 10;
    const loadMoreBtn = document.getElementById('loadMoreBtn');
    loadMoreBtn.onclick = function(){
        const match = /\/candidate\/(All|First|Second|Third|Fourth)/.exec(window.location);
        const next = document.getElementById('numRecords').value || 10;
        fetch(fetchUrl+`/team/candidate/${match[1]}/loadmore`,{
            method:'post',
            headers: {
                    'Content-Type': 'application/json'
            },
            body:JSON.stringify({offset,next})
        })
            .then(response => {
                if(!response.ok) throw new Error('Server encountered an error');
                return response.json();
            })
            .then(data => {
                if(data.err) throw new Error(data.err);
                let html = '';
                for(let i=0;i<data.length;i++){
                    html += `<tr>                                                                  
                                <th scope="row">${i+1+offset}</th>                             
                                <td>${data[i].name}</td>                                     
                                <td>${data[i].email}</td>                                    
                                <td>${data[i].phone_number}</td>                             
                                <td>${match[1] === 'All'? data[i].year:match[1]}</td>                                     
                                <td>${data[i].discipline}</td>                               
                                <td>                                                              
                                    <button id="${data[i].email}" type="button" class="btn btn-success turninBtn">Turn In</button>
                                </td>                                                             
                            </tr>`;
                }
                if(data.length < next)
                    loadMoreBtn.disabled = true;
                document.getElementById('tableBody').insertAdjacentHTML('beforeend',html);
                offset += data.length;
            })
            .catch(err => showMsg(err.message,'danger'))
    }
    const inputRecords = document.getElementById('numRecords');
    inputRecords.onkeypress = function(e){
        if(e.code === 'Enter' && !loadMoreBtn.disabled){
            loadMoreBtn.click();
        }
    }

    const tbody = document.getElementById('tableBody');
    tbody.onclick = function(e){
        if(e.target.tagName === 'BUTTON'){
            fetch(fetchUrl+'/team/candidates/candidate/turnin',{
                method:'post',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({email:e.target.id})
            })
                .then(response => {
                    if(!response.ok) throw new Error('Server encountered an error')
                    return response.json()
                })
                .then(data => {
                    if(data.err) throw new Error(data.err);
                    window.location = fetchUrl+'/team/candidates/candidate/turnin';
                })
                .catch(err => showMsg(err.message,'warning'))
        }
    }
    const stuckForm = document.getElementById('stuck');
    stuckForm.onsubmit = function(e){
        e.preventDefault()
        fetch(fetchUrl+'/team/candidate/stuck',{
            method:'post',
            body: new FormData(stuckForm)
        })
            .then(response => {
                if(!response.ok) throw new Error('Server encountered an error')
                return response.json()
            })
            .then(data => {
                if(data.err) throw new Error(data.err)
                showMsg(data.msg,'success')
            })
            .catch(err=> showMsg(err.message,'danger'))
    }

})();