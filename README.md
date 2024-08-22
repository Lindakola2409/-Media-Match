# Media Match
The project focuses on developing a system for searching and indexing video and audio content, akin to how text can be searched in documents. Unlike text, searching within video and audio is complex due to the lack of straightforward metaphors. The system aims to take a short snippet of video (with synchronized audio) and find the matching video in a database, pinpointing the exact starting frame. The key tasks involve preprocessing videos to create digital signatures based on various descriptors (e.g., shot boundaries, color, motion, sound) and then matching the query's sub-signature to these preprocessed signatures to find the best match.

# Ideas We Implemented 

Digital Signature Creation: Developed an innovative method to preprocess videos by creating digital signatures based on key descriptors such as shot boundaries, color themes, motion statistics, and sound frequencies.

Sub-Signature Matching: Implemented a pattern-matching algorithm to compare the sub-signature of the query video with preprocessed signatures, enabling precise identification of matching content in the database.

Custom Video Player Interface: Designed and built a custom video player with basic functionality (play, pause, reset) that supports synchronized audio/video output, defaulting to the first frame of the matched query video.
