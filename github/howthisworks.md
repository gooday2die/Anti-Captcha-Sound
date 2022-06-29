## Procedures - How captcha is solved:
This section is about how this project recognizes each captcha sounds and find which letter that captcha has in order.

### 1. Downloading the sound
It is obvious that in order to process the captcha, we need a sound captcha. For example, we would like to solve a captcha like this.

![Captcha Example](https://raw.githubusercontent.com/gooday2die/Anti-Captcha-Sound/main/github/pics/example_1.png)

When we inspect the *listen to captcha* button with Chrome or other browsers, you can pretty much find out direct link to the sound captcha's file. An example is like below:
```
<a rel="nofollow" class="BDC_SoundLink" id="LoginCaptcha_SoundLink" href="botdetect.php?get=sound&amp;c=LoginCaptcha&amp;t=2f43c84fa7e5fbb7afe7fcdb1fb347a4" title="Speak the CAPTCHA code" target="_blank"><img class="BDC_SoundIcon" id="LoginCaptcha_SoundIcon" src="http://220.149.231.241/captcha/botdetect-captcha-lib/botdetect/public/bdc-sound-icon.gif" alt="Speak the CAPTCHA code"></a>
```
`wget` or do a `GET` request on the url that is serving the sound of captcha. Then the captcha sound file will be downloaded.

### 2. Preprocessing the sound
So the downloaded sound has a lot of noise in background. For example, echos, noises, flanger, phaser, and a wierd bass rolling. I guess this was intended for robots to be difficult for them to literally do STT. 

However, thanks to Python, there is a library called  [noisereduce](https://github.com/timsainb/noisereduce), we can solve this problem a bit! Using the library, we can reduce the noise in the background significantly.

### 3. Splitting the sound
The `.wav` file that has the sound captcha now has reduced noise. Now it is time for splitting the sound into multiple parts. 

At first, I tried using VAD from [py-webrtcvad](https://github.com/wiseman/py-webrtcvad), however it turned out that the VAD is not suitable for our situation. So I made a simple Python script that splits sliences. You can find this script [here](https://github.com/gooday2die/Anti-Captcha-Sound/blob/main/AudioSpliter.ipynb). 

By simply using following expressions below, this script will split our audio into non silent segments. (This also includes noises)
```
# This will generate segments of 100ms to 500ms.
segments = generate_non_silent_segments("./test/captcha_6b11d4ebc70e4eb79614c1acc756f1da.wav", max_segment_length=500, min_segment_length=100)
# This will generate each segments into different .wav files
separate_audio_segments(segments)
```

Now with this step, the audio is splitted into multiple `.wav` files that does not have silence in them.

### 4. Classifying each segments
The model was trained by `tensorflow` (yes, I do not prefer using ML however this is the right place for ML to kick in). The model can distinguish following classes:

- a ~ z (English alphabets)
- 0 ~ 9 (Numerical numbers spoken in English)
- noise

The model will now try to classify each splitted sounds into those classes. Then it will generate a single `list` object containing how each values are classified.

## Procedures - How model is trained
### Dataset
The dataset that I used for training and evaluating this model can be found [here](https://github.com/gooday2die/Captcha-Dataset). Since there were no captcha dataset, I really had to label each data one by one for days. There are 1000 images of total captcha letters and 1000 sounds of total captcha sounds. (Yes, I labeled each dataset one by one myself :dizzy_face:)

### 1. Preprocessing data
Since I labled each data using [LabelStudio](https://labelstud.io/), the files come out in `.csv` file. Before I start training data with ML, I need to preprocess data. [Here](https://github.com/gooday2die/Anti-Captcha-Sound/blob/main/ProcessCSV.ipynb) you can find how each `.csv` is processed and how it generates each sound samples. Basically it does things in following order:

1. Read `.csv` into `pandas.DataFrame`.
2. Turn `DataFrame` into a format that is going to be used later.
3. Then it will append noise time lines (start, end) into the `DataFrame`.
4. Cut all audio files using `DataFrame` that was generated.
5. Place each splitted audio sample files into their respective directory (For example, if sound 'a' was generated, it will be placed in `./training_data/a/` directory.

*I know that if we do this kind of stuff, it will generate way more noises than other classes. Meaning that there is a potential of overfitting and bias on the model. Will be trying for better dataset in the future.*

### 2. Training model
Yes, I am not a huge fan of ML. So I copied code from [here](https://www.tensorflow.org/tutorials/audio/simple_audio). Check [here](https://github.com/gooday2die/Anti-Captcha-Sound/blob/main/DoML.ipynb) for full code. There are following classes:

- a ~ z (English alphabets)
- 0 ~ 9 (Numerical numbers spoken in English)
- noise

### 3. Verifying and testing model
Test set accuracy was set as 89%. Yay! This means each letters have 89% of being recognized correctly.


