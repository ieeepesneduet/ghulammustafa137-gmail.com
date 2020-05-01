class PostFormData{
    constructor(formNode){
        this.method = 'post';
        this.body = new FormData(formNode);
    }
}

class PostJsonData{
    constructor(jsObj) {
        this.method = 'post';
        this.headers = {
            'Content-Type': 'application/json'
        };
        this.body = JSON.stringify(jsObj);
    }
}

const fetchUrl = 'https://ieee-recruitment-system.herokuapp.com/';

async function fetchData(fetchPath,handleData,fetchParam){
    try{
        const response = await fetch(fetchUrl+fetchPath,fetchParam);
        if(!response.ok)
            throw new Error('Server encountered an error')
        const data = await response.json();
        if(data.err) throw new Error(data.err)
        handleData?handleData(data):null;
    }catch(err){
        showMsg(err.message,'danger');
    }
}
