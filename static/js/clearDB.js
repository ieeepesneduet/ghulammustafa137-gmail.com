(function clearDB(){
    document.getElementById('clearDB').onclick = function(){
        document.getElementById('confirmClearDBBox').style.display = 'block';
    }
    function closeBox(){
        document.getElementById('confirmClearDBBox').style.display = 'none';
    }
    document.getElementById('noClearBtn').onclick = closeBox;
    document.getElementById('yesClearBtn').onclick = function(){
        fetchData('/delete')
        closeBox();
    }
})();