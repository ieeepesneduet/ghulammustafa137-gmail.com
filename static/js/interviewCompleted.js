(function handleLoadMore(){
    let offset = 10;
    const loadMoreBtn = document.getElementById('loadMoreBtn');
    loadMoreBtn.onclick = function(){
        const next = document.getElementById('numRecords').value || 10;
        if(next>0){
            fetchData(`/team/completed`,function(data){
                let html = '';
                for(let i=0;i<data.length;i++){
                    html += `<tr>                                                                  
                                <th scope="row">${i+1+offset}</th>                             
                                <td>${data[i][0]}</td>                                     
                                <td>${data[i][1]}</td>                                    
                                <td>${data[i][2]}</td>                             
                                <td>${data[i][3]}</td>                                     
                                <td>${data[i][4]}</td>                               
                                <td>  
                                     <a href="/team/completed/${data[i][1]}" class="btn1 btn-primary btn-sm"
                                   style="text-decoration: none;">View<span
                                    class="underscroll">_</span>Details</a>                                                            
                                </td>                                                             
                            </tr>`;
                }
                if(data.length < next)
                    loadMoreBtn.disabled = true;
                document.getElementById('tableBody').insertAdjacentHTML('beforeend',html);
                offset += data.length;
            },new PostJsonData({offset,next}))
        }else{
            showMsg('Number of records that you want to load should be more than zero','danger')
        }
    }
    const inputRecords = document.getElementById('numRecords');
    inputRecords.onkeypress = function(e){
        if(e.code === 'Enter' && !loadMoreBtn.disabled){
            loadMoreBtn.click();
        }
    }
    const noBtn = document.getElementById('noBtn');
    noBtn.onclick = function(){
        document.getElementById('confirmBox').style.display='none';
    }

    const releaseBtn = document.getElementById('release');
    releaseBtn.onclick = function(){
        document.getElementById('confirmBox').style.display='block';
    }

})();