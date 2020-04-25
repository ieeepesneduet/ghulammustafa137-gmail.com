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
    function handleOnChange(){
        showMsg('');
        end = false;
        fetchData('/team/candidates/count',function(data){
            const numCan = document.getElementsByClassName('numCan');
            numCan[0].textContent = numCan[1].textContent = data.count;
        },new PostJsonData({domain:domainSelect.value,year:yearSelect.value}))
    }
    const domainSelect = document.getElementById('domainSelect');
    domainSelect.onchange = handleOnChange;
    const yearSelect = document.getElementById('yearSelect');
    yearSelect.onchange = handleOnChange;
    let offset,year,domain,end;
    offset = 0;
    const loadMoreBtn = document.getElementById('loadMoreBtn');
    loadMoreBtn.onclick = function(){
        if(end)
            showMsg('No more records to load','warning');
        else{
            const next = inputRecords.value;
            if(next>0){
                if(typeof domain === 'undefined' && typeof year === 'undefined'){
                    domain = domainSelect.value;
                    year = yearSelect.value;
                    handleOnChange();
                }else if(domainSelect.value !== domain || yearSelect.value !== year) {
                    offset = 0;
                    domain = domainSelect.value;
                    year = yearSelect.value;
                }
                fetchData('/team/candidates/more',function(data){
                    let html = '';
                    for(let i=0;i<data.length;i++){
                        html += `<tr id="${data[i][1]}">                                                                  
                                    <th scope="row">${i+1+offset}</th>                             
                                    <td>${data[i][0]}</td>                                     
                                    <td>${data[i][1]}</td>                                    
                                    <td>${data[i][2]}</td>                             
                                    <td>${year}</td>                                     
                                    <td>${data[i][3]}</td>                               
                                    <td>                                                              
                                        <button data-email="${data[i][1]}" type="button" class="btn btn-success turninBtn">Turn In</button>
                                    </td>                                                             
                                </tr>`;
                }
                if(data.length < next)
                    end = true;
                if(offset)
                    document.getElementById('tableBody').insertAdjacentHTML('beforeend',html);
                else
                    document.getElementById('tableBody').innerHTML = html;
                offset += data.length;
                },new PostJsonData({domain,year,offset,next}))
            }else{
                showMsg('Value should be greater than zero','warning')
            }

        }
    }

    const inputRecords = document.getElementById('numRecords');
    inputRecords.onkeypress = function(e){
        if(e.code === 'Enter'){
            loadMoreBtn.click();
        }
    }
})();