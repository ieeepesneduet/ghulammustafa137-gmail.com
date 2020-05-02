(function handleForm(){
    const registrationForm = document.getElementById('registration-form');
    var code= document.getElementById('code');
    
    registrationForm.onsubmit = function(e){
        e.preventDefault();
        window.scrollTo(0,0);
        fetchData('/candidatearea/registration',function(data){
            showMsg(`Your application has been received.Your application id is pes/20/${data.id} .You can use this id to check the status of your application.Your code will be emailed to you shortly yy.`,'primary')
            registrationForm.reset();
        },new PostFormData(registrationForm))
    }
    const fileInput = document.getElementById('image');
    fileInput.onchange = function() {
        if (this.files[0].size >= 500*1024) {
            window.scrollTo(0,0);
            showMsg('Image is too big.Make sure image is less than 500kb.')
            this.value = "";
        }
    }
})();
