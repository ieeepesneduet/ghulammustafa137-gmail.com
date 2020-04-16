(function handleLoadMore(){
    const cache = [];
    window.onload = function(){
        let data = sessionStorage.getItem('data');
        if(data !== null){
            data = JSON.parse(data);
            cache.push(...data);
            let html = '';
            for(let i=0;i<data.length;i++){
                html+=`<tr id="${data[i][1]}">                                                                  
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
            document.getElementById('tableBody').insertAdjacentHTML('beforeend',html);
            sessionStorage.removeItem('data')
        }
        const offs = sessionStorage.getItem('offset');
        if(offs !== null) {
            offset = parseInt(offs);
            sessionStorage.removeItem('offset')
        }
        const lM = sessionStorage.getItem('loadmore');
        if(lM !== null) {
            loadMoreBtn.disabled = lM === 'true';
            sessionStorage.removeItem('loadmore')
        }
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
           fetch(fetchUrl+`/team/candidates/${match[1]}/loadmore`,{
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
                cache.push(...data);
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
            })
            .catch(err => showMsg(err.message,'danger'))
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

    const tbody = document.getElementById('tableBody');
    tbody.onclick = function(e){
        if(e.target.tagName === 'BUTTON'){
            fetch(fetchUrl+'/team/candidates/candidate/turnin',{
                method:'post',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({email:e.target.getAttribute('data-email')})
            })
                .then(response => {
                    if(!response.ok) throw new Error('Server encountered an error')
                    return response.json()
                })
                .then(data => {
                    if(data.err) throw new Error(data.err);
                    sessionStorage.setItem('email', e.target.getAttribute('data-email'));
                    sessionStorage.setItem('data',JSON.stringify(cache));
                    sessionStorage.setItem('offset',offset);
                    sessionStorage.setItem('loadmore',loadMoreBtn.disabled);
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