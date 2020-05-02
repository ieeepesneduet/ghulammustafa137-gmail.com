(function handleForm(){
    const registrationForm = document.getElementById('registration-form');
    registrationForm.onsubmit = function(e){
        e.preventDefault();
        window.scrollTo(0,0);
        fetchData('/candidatearea/registration',function(data){
            
            var $form = $('form#registration-form'),
            url = 'https://script.google.com/macros/s/AKfycbyvJRlJ7IRg0ayR8yZzo2XSwcvzGDKnjei1PGLcSxLKxFtvnB6K/exec'

            $('#submit-form').on('click', function(e) {
                    e.preventDefault();
                    var jqxhr = $.ajax({
                    url: url,
                    method: "GET",
                    dataType: "json",
                    data: $form.serializeObject()
                    });
            })
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
