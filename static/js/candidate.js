(function handleLoadMore(){
    let offset = 10;
    const loadMoreForm = document.getElementById('loadMore');
    loadMoreForm.onsubmit = function(e){
        e.preventDefault();
        const match = /\/candidate\/(All|First|Second|Third|Fourth)/.exec(window.location);
        const next = loadMoreForm.numOfRecords.value || 10;
        fetch(`https://ieee-registration.herokuapp.com/candidate/${match[1]}/loadmore`,{
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
                                    <button type="button" class="btn btn-success">Turn In</button>
                                </td>                                                             
                            </tr>`;
                }
                if(data.length < next)
                    loadMoreForm.submitBtn.disabled = true;
                document.getElementById('tableBody').insertAdjacentHTML('beforeend',html);
                offset += data.length;
            })
            .catch(err => showMsg(err.message,'danger'))
    }
})();