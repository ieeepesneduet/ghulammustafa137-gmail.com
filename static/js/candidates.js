(function handleLoadMore(){
    window.onload = function(){
        const email = sessionStorage.getItem('email');
        if(email !== null){
            const el = document.getElementById(email);
            if(el)
                el.remove();
            sessionStorage.removeItem('email');
        }
    }
    const match = /\/team\/candidates\/(All|First|Second|Third|Fourth)/.exec(window.location);
    let offset = 10;
    const loadMoreBtn = document.getElementById('loadMoreBtn');
    loadMoreBtn.onclick = function(){
        const next = document.getElementById('numRecords').value || 10;
        if(next > 0){
            fetchData(`/team/candidates/${match[1]}/loadmore`,function(data){
                let html = '';
                for(let i=0;i<data.length;i++){
                    html += `<tr id="${data[i][1]}">                                                                  
                                <th scope="row">${i+1+offset}</th>                             
                                <td>${data[i][0]}</td>                                     
                                <td>${data[i][1]}</td>                                    
                                <td>${data[i][2]}</td>                             
                                <td>${match[1] === 'All'? data[i][4]:match[1]}</td>                                     
                                <td>${data[i][3]}</td>                               
                                <td>                                                              
                                    <button data-email="${data[i][1]}" type="button" class="btn btn-success turninBtn">Turn In</button>
                                </td>                                                             
                            </tr>`;
                }
                if(data.length < next)
                    loadMoreBtn.disabled = true;
                document.getElementById('tableBody').insertAdjacentHTML('beforeend',html);
                offset += data.length;
            },new PostJsonData({offset,next}))
        } else{
            showMsg('Enter a positive number to load more','danger')
        }

    }
    const inputRecords = document.getElementById('numRecords');
    inputRecords.onkeypress = function(e){
        if(e.code === 'Enter' && !loadMoreBtn.disabled){
            loadMoreBtn.click();
        }
    }
})();