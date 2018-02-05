// Feed
$('.dropdown-menu li a').click(function() {
    var selected = $(this).text();
    $('#feed_dropdown:first-child').html(selected + ' <span class="caret"></span>');

    var ws = new WebSocket('ws://localhost:59787/feed/websocket');

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
