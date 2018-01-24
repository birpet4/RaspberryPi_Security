// Feed
/*$(document > feed_content).ready(function() {
    var ws = new WebSocket('ws://localhost:8080/feed/websocket');

    ws.onmessage = function(e) {
       alert(e.data);
    };

    ws.onopen = function(e) {
        ws.send('OLA');
    };
})*/


// Configure
$('#cfg_form').submit(function(e){
    e.preventDefault();
    $.ajax({
        type : 'POST',
        data: $('#cfg_form').serialize(),
        url : 'configure',
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
$('#ctrl_start').click(function(){
    $.ajax({
        type : 'POST',
        data: {'on': 'true'},
        url : 'control',
        success : function(data){
            location.reload();
        }
    });
});
$('#ctrl_stop').click(function(){
    $.ajax({
        type : 'POST',
        data: {'on': 'false'},
        url : 'control',
        success : function(data){
            location.reload();
        }
    });
});


// Login
