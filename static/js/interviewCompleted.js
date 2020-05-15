(function handleLoadMore(){
    const tbody = document.getElementById('tableBody');
    tbody.onclick = function(e){
        if(e.target.tagName === 'BUTTON'){
            const pNode = e.target.parentNode.parentNode;
            fetchData('/team/completed/selection',null,new PostJsonData({selectionStatus:e.target.getAttribute('data-ss'),email:pNode.getAttribute('data-email')}))
            offset--;
            pNode.className = '';
            setTimeout(function () {
                pNode.remove()
            },400);
        }
    }
    const domainSelect = document.getElementById('domainSelect');
    domainSelect.onchange = function (){
        reset();
        fetchData('/team/candidates/count',function(data){
            const numCan = document.getElementsByClassName('numCan');
            numCan[0].textContent = numCan[1].textContent = data.count;
        },new PostJsonData({domain:domainSelect.value}))
    }
    const selectionStatusSelect = document.getElementById('selectionStatus');
    function reset(){
        end = false;
        showMsg('');
    }
    selectionStatusSelect.onchange = reset;
    let offset,domain,selectionStatus,end;
    const loadMoreBtn = document.getElementById('loadMoreBtn');
    loadMoreBtn.onclick = function(){
        if(end){
            showMsg('No more records to load','warning');
        }else{
            const next = inputRecords.value || 10;
            if(next > 0){
                if(domainSelect.value !== domain || selectionStatusSelect.value !== selectionStatus){
                    if(selectionStatus === '3' && selectionStatusSelect.value !== '3'){
                        document.getElementById('contactOrScores').textContent = 'Contact No.'
                        document.getElementById('tableHeadings').lastChild.remove()
                    }else if(selectionStatusSelect.value === '3' && selectionStatus !== '3'){
                        document.getElementById('contactOrScores').textContent = 'Scores';
                        document.getElementById('tableHeadings').insertAdjacentHTML('beforeend','<th scope="col">Selection</th>')
                    }
                    offset = 0;
                    domain = domainSelect.value;
                    selectionStatus = selectionStatusSelect.value;
                }
                fetchData('/team/candidates/more',function (data){
                    let btns = '';
                    if(selectionStatus === '3'){
                        btns = '<td><button class="ssbtn" data-ss="1">&#10004;</button><button class="ssbtn" data-ss="2">&#10008;</button></td>';
                    }
                    let html = '';
                    for(let i=0;i<data.length;i++){
                        html += `<tr class="show" data-email="${data[i][1]}">                                                                  
                                    <th scope="row">${i+1+offset}</th>                             
                                    <td>${data[i][0]}</td>                                     
                                    <td>${data[i][1]}</td>                                    
                                    <td>${data[i][4]}</td>                             
                                    <td>${data[i][2]}</td>                                     
                                    <td>${data[i][3]}</td>                               
                                    <td>  
                                     <a href="/team/completed/${data[i][1]}" class="btn1 btn-primary btn-sm"
                                   style="text-decoration: none;">View<span
                                    class="underscroll">_</span>Details</a>                                                            
                                </td>`
                                +btns+'</tr>';
                }
                if(data.length < next)
                    end = true;
                if(offset)
                    document.getElementById('tableBody').insertAdjacentHTML('beforeend',html);
                else
                    document.getElementById('tableBody').innerHTML = html;
                offset += data.length;
                },new PostJsonData({domain,selectionStatus,offset,next}))
            }else{
                showMsg('Number of records to load should be greater than zero','warning')
            }
        }
    }
    const inputRecords = document.getElementById('numRecords');
    inputRecords.onkeypress = function(e){
        if(e.code === 'Enter'){
            loadMoreBtn.click();
        }
    }

    loadMoreBtn.click();
    domainSelect.onchange();
})();