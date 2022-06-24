# Usage: python3 split_audio_by_silence.py -i input_audio.m4a -o segments
#  will save segments in mp3 format into the segments directory
#  based on https://github.com/mozilla/DeepSpeech/tree/master/examples/vad_transcriber
# Dependencies: webrtcvad

import os
import argparse
import collections
import subprocess
import webrtcvad

def detect_voice_segments(vad, audio, sample_rate, frame_bytes, frame_duration_ms, triggered_sliding_window_threshold = 0.9):
    padding_duration_ms = frame_duration_ms * 10
    num_padding_frames = int(padding_duration_ms / frame_duration_ms)
    ring_buffer = collections.deque(maxlen=num_padding_frames)
    triggered = False
    makeseg = lambda voiced_frames: b''.join(voiced_frames)
    voiced_frames = []
    for frame in (audio[offset:offset + frame_bytes] for offset in range(0, len(audio), frame_bytes) if offset + frame_bytes < len(audio)):
        is_speech = vad.is_speech(frame, sample_rate)
        if not triggered:
            ring_buffer.append((frame, is_speech))
            num_voiced = len([f for f, speech in ring_buffer if speech])
            if num_voiced > triggered_sliding_window_threshold * ring_buffer.maxlen:
                triggered = True
                for f, s in ring_buffer:
                    voiced_frames.append(f)
                ring_buffer.clear()
        else:
            voiced_frames.append(frame)
            ring_buffer.append((frame, is_speech))
            num_unvoiced = len([f for f, speech in ring_buffer if not speech])
            if num_unvoiced > triggered_sliding_window_threshold * ring_buffer.maxlen:
                triggered = False
                yield makeseg(voiced_frames)
                ring_buffer.clear()
                voiced_frames = []
    if triggered:
        pass
    if voiced_frames:
        yield makeseg(voiced_frames)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input-path', required = True)
    parser.add_argument('-o', '--output-dir', default = 'segments')
    parser.add_argument('--aggressive', default = 3, type = int, choices = [0, 1, 2, 3], required = False)
    parser.add_argument('--frame_duration_ms', default = 30, choices = [10, 20, 30])
    parser.add_argument('--min_segment_duration', type = int, default = 10)
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok = True)

    sample_rate, audio = 16000, subprocess.check_output(['ffmpeg', '-loglevel', 'fatal', '-hide_banner', '-nostats', '-nostdin', '-i', args.input_path, '-ar', '16000', '-f', 's16le', '-acodec', 'pcm_s16le', '-ac', '1', '-vn', '-'], stderr = subprocess.DEVNULL)
    frame_bytes = int(2 * sample_rate * (args.frame_duration_ms / 1000.0))
    segments = detect_voice_segments(webrtcvad.Vad(args.aggressive), audio, sample_rate, frame_bytes, args.frame_duration_ms)
    for i, segment in enumerate(segments):
        if len(segment) / (2 * sample_rate) > args.min_segment_duration:
            subprocess.Popen(['ffmpeg', '-loglevel', 'fatal', '-hide_banner', '-nostats', '-nostdin', '-y', '-f', 's16le', '-ar', '16000', '-ac', '1', '-i', '-', '-acodec', 'mp3', '-vn', '-ar', '16000', '-ac', '1', os.path.join(args.output_dir, f'{args.input_path}.{i:04d}.mp3')], stdin = subprocess.PIPE, stdout = subprocess.DEVNULL, stderr = subprocess.DEVNULL).communicate(segment)
