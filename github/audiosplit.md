## How Audio is separated
So the problem is that the model is now able to distinguish each letters using sound. However it does not know how to separate each letter sounds from original sound captcha. This document describes the trial and errors on how audio is separated.

### Using dBFS values
The main idea of separating sounds with dBFS values was following:
- When the dBFS is -inf, it means silent.
- There might be 4 types of transitions that can occur on dBFS values:

| Current dBFS value | Before dBFS value | Meaning |
|--|--|--|
|-inf|-inf|This is a silent segment|
|-inf|not -inf|Not silent segment starts|
|not -inf| -inf| Not silent segment ends
|not -inf| not -inf| Inside not silent segment.

- So split the audio on *not silent segment*. 
- Since there might be audios such as "ad" which is "a" and "d" spoken almost in a connected manner, there must be a way of cutting non silent segment into two when it is too long (0.5 seconds)
- Check `AudioSplitter.ipynb` for more information on the implementation.

#### Result
Was terrible. 

Most of the part, it can distinguish each sound letters. However, in some cases like connected sounds, it cannot distinguish each letter sounds correctly. For example, if there was an audio sound going "3x", it will cut the audio in "the ending sound of 3" and "starting sound of x", which results in broken segments. 
