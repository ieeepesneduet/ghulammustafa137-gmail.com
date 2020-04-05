(function configLoader(){
    const form = document.getElementById('loginForm');
    form.onsubmit = function(){
        document.getElementById('loader').style.display='block';
    }
})();