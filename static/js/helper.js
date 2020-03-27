function showMsg(text,type){
    document.getElementById('msg-box').innerHTML = `<div class="alert alert-${type}" role="alert">${text}</div>`
}