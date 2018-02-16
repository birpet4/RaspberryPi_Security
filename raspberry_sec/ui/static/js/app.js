// Base
$(document).ready(function() {
    if(window.location.pathname === '/login')
        $('#logout_btn').hide();
});

// Feed
$('.dropdown-menu li a').click(function() {
    var selected = $(this).text();
    $('#feed_dropdown:first-child').html(selected + ' <span class="caret"></span>');

    var ws = new WebSocket('wss://' + $('#feed_ip').text() + ':63973/feed/websocket');

    ws.onmessage = function(content) {
       $('#feed_content').html(content.data);
       setTimeout(() => ws.send(selected), 1000);
    };

    ws.onopen = function(e) {
        ws.send(selected);
    };
});

// Configure
$('#cfg_form').submit(function(e){
    $.ajax({
        type : 'POST',
        data: $('#cfg_form').serialize(),
        url : 'configure',
        beforeSend: function(xhr) {
            xhr.setRequestHeader('X-CSRFToken', getXSRFCookie());
        },
        success : function(data){
            $('#cfg_info_alert').html(data)
            $('#cfg_info_alert').fadeTo(2000, 500).slideUp(500, function(){
                $('#cfg_info_alert-alert').slideUp(500);
            });
        }
    });
    return false;
});

// Control
function ctrlButtonSend(onStr) {
    $.ajax({
        type : 'POST',
        data: {'on': onStr},
        beforeSend: function(xhr) {
            xhr.setRequestHeader('X-CSRFToken', getXSRFCookie());
        },
        url : 'control',
        success : function(data){
            location.reload();
        }
    });
}
$('#ctrl_start').click(
    function(){
        ctrlButtonSend('true');
});
$('#ctrl_stop').click(
    function(){
        ctrlButtonSend('false');
});

// Login
$('#login_form').submit(function(){
    $('#logout_btn').show();
    $.ajax({
        type : 'POST',
        data : $('#login_form').serialize(),
        beforeSend: function(xhr) {
            xhr.setRequestHeader('X-CSRFToken', getXSRFCookie());
        },
        url : 'login'
    });
});
$('#login_pwd').on('keypress', function(e) {
    if (e.which == 32)
        return false;
});

// Logout
$('#logout_btn').click(function(){
    $.ajax({
        type : 'DELETE',
        url : 'login',
        beforeSend: function(xhr) {
            xhr.setRequestHeader('X-CSRFToken', getXSRFCookie());
        },
        success : function(data){
            location.reload();
        }
    });
});

// XSRF Protection
function getXSRFCookie() {
    var r = document.cookie.match('\\b_xsrf=([^;]*)\\b');
    return r ? r[1] : undefined;
}