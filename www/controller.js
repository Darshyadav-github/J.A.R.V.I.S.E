$(document).ready(function () {

    // Display Speak Message
    eel.expose(DisplayMessage)
    function DisplayMessage(message) {
        $(".siri-message li:first").text(message);
        $('.siri-message').textillate('start');
    }

    // Display hood
    eel.expose(ShowHood)
    function ShowHood() {
        $("#Oval").attr("hidden", false);
        $("#SiriWave").attr("hidden", true);
    }

    // Functions to handle chat messages
    eel.expose(senderText)
    function senderText(message) {
        var chatBox = document.getElementById("chat-canvas-body");
        if (message.trim() !== "") {
            chatBox.innerHTML += `<div class="row justify-content-end mb-4">
            <div class = "width-size">
            <div class="sender_message">${message}</div>
        </div>`; 
    
            // Scroll to the bottom of the chat box
            chatBox.scrollTop = chatBox.scrollHeight;
        }
    }

    eel.expose(receiverText)
    function receiverText(message) {
        var chatBox = document.getElementById("chat-canvas-body");
        if (message.trim() !== "") {
            chatBox.innerHTML += `<div class="row justify-content-start mb-4">
            <div class = "width-size">
            <div class="receiver_message">${message}</div>
            </div>
        </div>`; 
    
            // Scroll to the bottom of the chat box
            chatBox.scrollTop = chatBox.scrollHeight;
        }
    }

    // Start the camera and object detection when the webpage loads
    startObjectDetection();

    function startObjectDetection() {
        const video = document.createElement('video');
        video.setAttribute('id', 'videoElement');
        video.autoplay = true;
        document.body.appendChild(video);

        navigator.mediaDevices.getUserMedia({ video: true })
            .then(stream => {
                video.srcObject = stream;
                video.play();
            })
            .catch(err => console.error("Error accessing the webcam: ", err));

        video.addEventListener('play', () => {
            const canvas = document.createElement('canvas');
            const ctx = canvas.getContext('2d');
            document.body.appendChild(canvas);

            const processFrame = () => {
                ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
                const imageData = canvas.toDataURL('image/jpeg');

                fetch('/detect', {
                    method: 'POST',
                    body: JSON.stringify({ image: imageData }),
                    headers: { 'Content-Type': 'application/json' }
                })
                .then(response => response.json())
                .then(data => {
                    // Process detection results, e.g., display bounding boxes or log results
                    console.log(data);
                })
                .catch(err => console.error('Error:', err));

                requestAnimationFrame(processFrame);
            };

            processFrame();
        });
    }
});
