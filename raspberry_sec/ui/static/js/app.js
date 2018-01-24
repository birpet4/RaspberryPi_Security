var ws;

$(document > feed_content).ready(function() {
    ws = new WebSocket("ws://localhost:8080/feed/websocket");

    ws.onmessage = function(e) {
       alert(e.data);
    };

    ws.onopen = function(e) {
        ws.send('OLA');
    };
})