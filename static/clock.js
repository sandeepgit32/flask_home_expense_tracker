window.addEventListener( 'DOMContentLoaded', function () {
    var width = 300
    var height = 300
    var clock = document.querySelector('#clock').getContext('2d');
    clock.canvas.width = width;
    clock.canvas.height = height;
    clock.strokeStyle = '#2e4a66';
    clock.lineWidth = 10;
    clock.lineCap = 'round';

    function degreeToRadian (degree) {
        return degree * Math.PI / 180;
    }

    function renderTime () {

        var now = new Date();
        var today = now.toDateString(now);
        var time = now.toLocaleTimeString(now);
        var hours = now.getHours();
        var minutes = now.getMinutes();
        var seconds = now.getSeconds();
        var miliSeconds = now.getMilliseconds();
        var newSeconds = seconds + ( miliSeconds / 1000 );

        // BACKGROUND
        clock.fillStyle = '#f3f4f6e0';
        clock.fillRect( 0, 0, width, height );

        // // HOURS
        // clock.beginPath();
        // clock.arc( width/2, height/2, 0.32*width, degreeToRadian(270), degreeToRadian( hours * 15 - 90 ) );
        // clock.stroke();

        // // MINUTES
        // clock.beginPath();
        // clock.arc( width/2, height/2, 0.36*width, degreeToRadian(270), degreeToRadian( minutes * 6 - 90 ) );
        // clock.stroke();

        // SECONDS
        clock.beginPath();
        clock.arc( width/2, height/2, 0.4*width, degreeToRadian(270), degreeToRadian( newSeconds * 6 - 90 ) );
        clock.stroke();

        // DATE
        clock.font = '700 24px Arial, sans-serif';
        clock.fillStyle = '#2e4a66';
        clock.fillText(today, 0.18*width, 0.48*width);

        // TIME
        clock.font = '20px Arial, sans-serif';
        clock.fillText(time, 0.35*width, 0.58*width);

    }

    setInterval( renderTime, 40 );

}, false);