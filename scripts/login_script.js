var auth = arguments[0] || {};

if(console && console.log) {
    console.log('[test] do_auth')
}

var $ = document.querySelector.bind(document);
$('#user_name').value = auth.username;
$('#password').value = auth.password;
$('#login').click();