(function statusFormHandle(){
    const statusForm = document.getElementById('statusForm');
    statusForm.onsubmit = function(e){
        e.preventDefault();
        const appID = statusForm.id.value;
        const match = /pes\/\d{2}\/([A-Za-z0-9]{5})/.exec(appID);
        if(match){
            fetchData('/candidatearea/status',function(data){
                let htmlData = '';
                const dataValues = {a:'Full Name',b:'Year',c:'Email',d:'Domain',j:'Application reviewed',e:'Experience rating',f:'Interview rating',g:'Potential rating',i:'Remarks',h:'Selection Status'};
                for(const prop in data){
                    htmlData += `<tr><td>${dataValues[prop]}</td><td>${data[prop]}</td></tr>`
                }
                document.getElementById('applicationData').innerHTML = htmlData;
                showMsg(`Your application has${data.j?'':' not'} been reviewed`,'primary')
            },new PostJsonData({id:match[1]}))
        }else{
            showMsg('Application ID is in wrong format.Correct format pes/20/Kn5sU');
        }
    }
})();