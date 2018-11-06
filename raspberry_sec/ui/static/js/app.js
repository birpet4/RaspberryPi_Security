// Base
$(document).ready(function() {
    if(window.location.pathname === '/login')
        $('#logout_btn').hide();
});

// Feed
$('.dropdown-menu li a').click(function() {
    var selected = $(this).text();
    $('#feed_dropdown:first-child').html(selected + ' <span class="caret"></span>');

    var ws = new WebSocket('wss://' + location.host + '/feed/websocket');

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
function ctrlButtonSend(onStr, zone) {
    $.ajax({
        type : 'POST',
 //       data: {'on': onStr,'zone': zone},
        data: {'on': onStr, 'zone': zone},
        beforeSend: function(xhr) {
            xhr.setRequestHeader('X-CSRFToken', getXSRFCookie());
        },
        url : 'control',
        success : function(data){
            location.reload();
        }
    });
}

// Wait until the window finishes loaded before executing any script
window.onload = function() {

        // Initialize the activityNumber
        var activityNumber = 3;

        // Select the add_activity button
        var addButton = document.getElementById("add_zone");
	
        // Select the table element
        var tracklistTable = document.getElementById("zones");

        // Attach handler to the button click event
        addButton.onclick = function() {
	var zone = document.getElementById("text_zone").value;
        var zone_id = zone.toLowerCase();
        // Add a new row to the table using the correct activityNumber
          tracklistTable.innerHTML += '<input type="checkbox" name="zone" value="' + zone_id + '">' + zone;

          // Increment the activityNumber
          activityNumber += 1;
        }

}

function printChecked(){
	var items = document.getElementsByName('zone');
	var selectedItems ='{';
	for(var i = 0; i < items.length; i++)
		if(items[i].type == 'checkbox'){
			selectedItems += '\"';
			selectedItems += items[i].value + '\":';
			if(items[i].checked == true)
				selectedItems += 'true ,';
			else
				selectedItems += 'false ,';
	}
	selectedItems = selectedItems.slice(0,-1);
	selectedItems += '}';
	if(!selectedItems)
		alert('No zone selected, please select one');
	return selectedItems;
}

$('#ctrl_start').click(
    function(){
	var zone = printChecked();
        ctrlButtonSend('true', zone);
});
$('#ctrl_stop').click(
    function(){
	zone = null
        ctrlButtonSend('false', zone);
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
