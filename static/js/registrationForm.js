(function handleForm(){
    const registrationForm = document.getElementById('registration-form');
    registrationForm.onsubmit = function(e){
        e.preventDefault();
        window.scrollTo(0,0);
        showMsg('Please wait here while we process your submission','warning')
        fetchData('/candidatearea/registration',function(data){
            showMsg(`Your application has been received.Your application id is pes/20/${data.id} .You can use this id to check the status of your application.Your code will be emailed to you shortly.`,'primary')
            registrationForm.reset();
        },new PostFormData(registrationForm))
    }
    const fileInput = document.getElementById('image');
    fileInput.onchange = function() {
        if (this.files[0].size > 1.5*1024*1024) {
            window.scrollTo(0,0);
            showMsg('Image is too big.Max accepted image size 1.5MB.','warning')
            this.value = "";
        }
    }
})();
