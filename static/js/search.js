(function searchHandler(){
    const searchForm = document.getElementById('searchForm');
    searchForm.onsubmit = function(e){
        e.preventDefault();
        fetchData('/team/candidates/candidate/search/records',function(data){
            let html = '';
            for(let i=0;i<data.length;i++) {
                html += `<tr>                                                                  
                            <th scope="row">${i + 1}</th>                             
                            <td>${data[i][0]}</td>                                     
                            <td>${data[i][1]}</td>                                    
                            <td>${data[i][2]}</td>                             
                            <td>${data[i][3]}</td>                                     
                            <td>${data[i][4]}</td>                               
                            <td>                                                              
                                <button data-email="${data[i][1]}" type="button" class="btn btn-success turninBtn">Turn In</button>
                            </td>                                                             
                         </tr>`
            }
            document.getElementById('tableBody').innerHTML = html;
        },new PostFormData(searchForm))
    }

    function handleOnChange() {
        if (search.value.length >= 3)
            fetchSuggestions(search.value.slice(0, 3));
    }

    const domain = document.getElementById('domain');
    domain.addEventListener('change',handleOnChange);

    const type = document.getElementById('type');
    type.addEventListener('change',handleOnChange);

    let lastQuery = '';
    let suggestions = [];

    const search = document.getElementById('search');
    search.addEventListener('input',function (){
        const val = this.value;
        if(val.length>=3){
            if(val.length === 3){
                if(val === lastQuery){
                    const suggestionsList = document.getElementById('searchSuggestions').innerHTML;
                    if(!suggestionsList)
                        loadSuggestions(suggestions);
                }else{
                    lastQuery = val;
                    fetchSuggestions(val);
                }
            }
        }else{
            document.getElementById('searchSuggestions').innerHTML = '';
        }
    });
    function fetchSuggestions(val){
        const formBody = new FormData();
        formBody.append('search',val);
        formBody.append('type',type.value);
        formBody.append('domain',domain.value);
        fetchData('/team/candidates/candidate/search/suggestions',function(data){
             suggestions = data;
             loadSuggestions(data);
        },{method:'post',body:formBody})
    }
    function loadSuggestions(data){
        let html = '';
        for(let i=0;i<data.length;i++){
            html += `<option value="${data[i]}">`;
        }
        document.getElementById('searchSuggestions').innerHTML = html;
    }
})()