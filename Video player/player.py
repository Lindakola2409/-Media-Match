import webbrowser

video = "../Video Dataset/video6.mp4"

frame = 12416
start_time = frame / 30

html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Video Player</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    <div class="container">
        <video id="player" controls>
            <source src="{video}" type="video/mp4">
            Your browser does not support the video tag.
        </video>
        <div id="controls">
            <button onclick="playPause()">Play/Pause</button>
            <button onclick="reset()">Reset</button>
        </div>
    </div>
    <script>
        function playPause() {{
            if (video.paused) {{
                video.play();
            }} else {{
                video.pause();
            }}
        }}

        function reset() {{
            video.currentTime = {start_time};
            video.pause();
        }}
        const video = document.getElementById("player");
        reset();
    </script>
</body>
</html>
"""

with open("index.html", "w") as file:
    file.write(html_content)

# open the html file
webbrowser.open("index.html",new=1)