function showMsg(text,type){
    if(text === '')
        document.getElementById('msg-box').innerHTML = '';
    else
        document.getElementById('msg-box').innerHTML = `<div class="alert alert-${type}" role="alert">${text}</div>`
}