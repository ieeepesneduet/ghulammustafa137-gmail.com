(function statusFormHandle(){
    const statusForm = document.getElementById('statusForm');
    statusForm.onsubmit = function(e){
        e.preventDefault();
        const appID = statusForm.id.value;
        const match = /pes\/\d{2}\/([A-Za-z0-9]{5})/.exec(appID);
        if(match){
            fetchData('/candidatearea/status',function(data){
                let htmlData = '';
                const dataValues = {a:'Full Name',b:'Year',c:'Email',d:'Domain',j:'Interview Conducted',i:'Remarks',h:'Selection Status'};
                for(const prop in data){
                    if(prop === 'h'){
                        if(data[prop] === 'selected')
                            htmlData += `<tr class='tableDesign'><td>${dataValues[prop]}</td><td id='candSelected'>${data[prop]}</td></tr>`;
                        else
                            htmlData += `<tr class='tableDesign'><td>${dataValues[prop]}</td><td id='candNotSelected'>${data[prop]}</td></tr>`;
                    }
                    else
                        htmlData += `<tr class='tableDesign'><td>${dataValues[prop]}</td><td>${data[prop]}</td></tr>`
                }
                document.getElementById('applicationData').innerHTML = htmlData;
                showMsg(`Your interview has ${data.j?`been conducted ${data.h?' and your application has been reviewed.':'and your application is under review process'}`:'not been conducted yet.'}`,'primary')
            },new PostJsonData({id:match[1]}))
        }else{
            showMsg('Application ID is in wrong format.Correct format pes/20/Kn5sU');
        }
    }
})();