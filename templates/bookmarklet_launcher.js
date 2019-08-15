(function(){
    if (document.getElementById('bookmarklet')){
                console.log('Bookmarklet is found, skipping new creation.....');
    }
    else {
        document.body.appendChild(document.createElement('script')).src='http://127.0.0.1:8000/static/js/bookmarklet.js?r='+Math.floor(Math.random()*99999999999999999999);
        console.log('MyBookmarklet is not found, so created element <script> and bookmarklet.js file is added to the page!');
    }
})();
