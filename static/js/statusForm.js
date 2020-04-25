(function statusFormHandle(){
    const statusForm = document.getElementById('statusForm');
    statusForm.onsubmit = function(e){
        e.preventDefault();
        const appID = statusForm.id.value;
        const match = /pes\/\d{2}\/([A-Za-z0-9]{5})/.exec(appID);
        if(match){
            fetchData('/candidatearea/status',function(data){
                console.log(data);
                let htmlData = '';
                const dataValues = {a:'Full Name',b:'Year',c:'Email',d:'Phone Number',e:'CNIC',f:'Domain',g:'Discipline',h:'About',i:'Association with volunteering work',j:'Why do you want to join IEEE PES NED',k:'Achievements',l:'Application reviewed',m:'Experience rating',n:'Interview rating',o:'Potential rating',p:'Remarks'};
                for(const prop in data){
                    htmlData += `<tr><td>${dataValues[prop]}</td><td>${data[prop]}</td></tr>`
                }
                document.getElementById('applicationData').innerHTML = htmlData;
                showMsg(`Your application has${data.l?'':' not'} been reviewed`,'primary')
            },new PostJsonData({id:match[1]}))
        }else{
            showMsg('Application ID is in wrong format.Correct format pes/20/Kn5sU');
        }
    }
})();