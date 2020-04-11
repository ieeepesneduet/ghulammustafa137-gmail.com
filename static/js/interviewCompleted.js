(function handleLoadMore(){
    let offset = 10;
    const loadMoreBtn = document.getElementById('loadMoreBtn');
    loadMoreBtn.onclick = function(){
        const next = document.getElementById('numRecords').value || 10;
        fetch(`https://ieee-registration.herokuapp.com/team/completed`,{
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
                                <td>${data[i].year}</td>                                     
                                <td>${data[i].discipline}</td>                               
                                <td>  
                                     <a href="#" class="btn1 btn-primary btn-sm"
                                   style="text-decoration: none;">View<span
                                    class="underscroll">_</span>Details</a>                                                            
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

})();