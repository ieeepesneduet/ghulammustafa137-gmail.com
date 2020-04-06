(function statusFormHandle(window){
    const statusForm = document.getElementById('statusForm');
    statusForm.onsubmit = function(e){
        e.stopImmediatePropagation();
        e.preventDefault();
        const appID = statusForm.id.value;
        const match = /pes\/\d{2}\/([A-Za-z0-9]{5})/.exec(appID);
        if(match){
            fetch('http://127.0.0.1:5000/candidatearea/status',{
                method:'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({id:match[1]})
            })
                .then(response => {
                    if(!response.ok) throw new Error('Server encountered an error');
                    return response.json();
                })
                .then(data => {
                    if(data.err) throw new Error(data.err);
                    let htmlData = '';
                    const dataValues = {a:'Full Name',b:'Year',c:'Email',d:'Phone Number',e:'CNIC',f:'Domain',g:'Discipline',h:'About',i:'Association with volunteering work',j:'Why do you want to join IEEE PES NED',k:'Achievements',l:'Application reviewed'};
                    for(const prop in data){
                        htmlData += `<tr><td>${dataValues[prop]}</td><td>${data[prop]}</td></tr>`
                    }
                    document.getElementById('applicationData').innerHTML = htmlData;
                    showMsg(`Your application has${data.l?'':' not'} been reviewed`,'primary')
                })
                .catch(err => showMsg(err.message,'danger'))
        }else{
            showMsg('Application ID is in wrong format.Correct format pes/20/Kn5sU');
        }
    }
})(window);