(function release(){
    const noBtn = document.getElementById('noBtn');
    function closeBox(){
        document.getElementById('confirmBox').style.display='none';
    }
    noBtn.onclick = closeBox;
    const yesBtn = document.getElementById('yesBtn');
    yesBtn.onclick = function(){
        fetchData("/team/completed/release");
        closeBox();
    }

    const releaseBtn = document.getElementById('release');
    releaseBtn.onclick = function(){
        document.getElementById('confirmBox').style.display='block';
    }
})();