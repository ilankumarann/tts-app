Yet another attempt to make a tts app that runs a fastapi app with websocket. You send a json with text property set to the sentence or words you want to be converted to audio and you get a 
response with a base64 encoded float32  16khz rate mono audio.

See the sample static html file  /public/index.html to see how to create a html audio element to play audio. After converting the base64 string to byte buffer you need to convert to an int16 buffer before
creating a blob audio source adding wav header and playing
