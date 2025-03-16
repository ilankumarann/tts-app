Yet another attempt to make a tts app that runs a fastapi app with websocket. 
You send a json with the text property set to the sentence or words you want to be converted to audio. 
You get a response with a base64 encoded float32 audio. 
The audio is 16khz rate and mono.

[See the sample static HTML file](/public/index.html) to learn how to create an HTML audio element to play audio. 
After converting the base64 string to a byte buffer, Add a wav header and play.
You need to convert it to an int16 buffer before creating audio source

