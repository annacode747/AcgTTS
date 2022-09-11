# -*- coding: utf-8 -*-
import sys, re
from torch import no_grad, LongTensor
import logging


logging.getLogger('numba').setLevel(logging.WARNING)

import commons
import utils
from models import SynthesizerTrn
from text import text_to_sequence, _clean_text
from mel_processing import spectrogram_torch

from scipy.io.wavfile import write


config = "config/config.json"
api_hps_ms = utils.get_hparams_from_file(config)
api_net_g_ms = SynthesizerTrn(
    len(api_hps_ms.symbols),
    api_hps_ms.data.filter_length // 2 + 1,
    api_hps_ms.train.segment_size // api_hps_ms.data.hop_length,
    n_speakers=api_hps_ms.data.n_speakers,
    **api_hps_ms.model)
_ = api_net_g_ms.eval()
utils.load_checkpoint("model/1374_epochs.pth", api_net_g_ms)


def get_text(text, hps, cleaned=False):
    if cleaned:
        text_norm = text_to_sequence(text, hps.symbols, [])
    else:
        text_norm = text_to_sequence(text, hps.symbols, hps.data.text_cleaners)
    if hps.data.add_blank:
        text_norm = commons.intersperse(text_norm, 0)
    text_norm = LongTensor(text_norm)
    return text_norm


def ask_if_continue():
    """原方法是是否继续，这里直接结束"""
    # sys.exit(0)
    # while True:
    #     answer = input('Continue? (y/n): ')
    #     if answer == 'y':
    #         break
    #     elif answer == 'n':
    #         sys.exit(0)


def print_speakers(speakers):
    pass
    # print('ID\tSpeaker')
    # for id, name in enumerate(speakers):
    #     print(str(id) + '\t' + name)


def get_speaker_id(message):
    """
    speaker_id :
        0	綾地寧々
        1	在原七海
        2	小茸
        3	唐乐吟
    """
    speaker_id = input(message)
    try:
        speaker_id = int(speaker_id)
    except:
        print(str(speaker_id) + ' is not a valid ID!')
        sys.exit(1)
    return speaker_id


class Interact:
    def __init__(self, text, out_path, hps_ms=None, speaker_id=0, choice='t', model='model/1374_epochs.pth',
                 config="config/config.json"):
        speaker_id = speaker_id if speaker_id is not None else 0
        choice = choice if choice is not None else 't'
        model = model if model is not None else 'model/1374_epochs.pth'
        config = config if config is not None else "config/config.json"
        self.run(model, config, choice, text, out_path, speaker_id=speaker_id, audio_path=None, hps_ms=hps_ms)

    def run(self, model, config, choice, text, out_path, speaker_id=0, audio_path=None, hps_ms=None):
        """
        model:
            模型路径
        config:
            配置文件路径
        choice:
            选择模式：
            t :TTS
            c :CV
        text :
            参数格式 ： [ZH]中文[ZH] 或者 [JA]日本語[JA]
        out_path :
            输出路径 例：save/TTS/read.wav
        speaker_id :
            0	綾地寧々
            1	在原七海
            2	小茸
            3	唐乐吟
        audio_path :
            cv 模式的 输入音频

        """
        # model = input('Path of a VITS model: ')
        # config = input('Path of a config file: ')
        try:
            hps_ms = hps_ms if hps_ms is not None else api_hps_ms
            net_g_ms = api_net_g_ms if hps_ms is not None else SynthesizerTrn(
                len(hps_ms.symbols),
                hps_ms.data.filter_length // 2 + 1,
                hps_ms.train.segment_size // hps_ms.data.hop_length,
                n_speakers=hps_ms.data.n_speakers,
                **hps_ms.model)
            if hps_ms is not None:
                _ = net_g_ms.eval()
                utils.load_checkpoint(model, net_g_ms)
        except:
            print('Failed to load!')
            sys.exit(1)

        # while True:
        # choice = input('TTS or VC? (t/v):')
        if choice == 't':
            # text = input('Text to read: ')
            if text == '[ADVANCED]':
                text = input('Raw text:')
                print('Cleaned text is:')
                print(_clean_text(text, hps_ms.data.text_cleaners))
                # continue

            length_scale = re.search(r'\[LENGTH=(.+?)\]', text)
            if length_scale:
                try:
                    text = re.sub(r'\[LENGTH=(.+?)\]', '', text)
                    length_scale = float(length_scale.group(1))
                except:
                    print('Invalid length scale!')
                    sys.exit(1)
            else:
                length_scale = 1

            if '[CLEANED]' in text:
                try:
                    stn_tst = get_text(text.replace('[CLEANED]', ''), hps_ms, cleaned=True)
                except:
                    print('Invalid text!')
                    sys.exit(1)
            else:
                try:
                    stn_tst = get_text(text, hps_ms)
                except EOFError:
                    print(EOFError)
                    print('Invalid text!')
                    sys.exit(1)

            print_speakers(hps_ms.speakers)
            # speaker_id = get_speaker_id('Speaker ID: ')
            # speaker_id = get_speaker_id('Speaker ID: ')
            length_scale
            # out_path = input('Path to save: ')

            try:
                with no_grad():
                    x_tst = stn_tst.unsqueeze(0)
                    x_tst_lengths = LongTensor([stn_tst.size(0)])
                    sid = LongTensor([speaker_id])
                    audio = net_g_ms.infer(x_tst, x_tst_lengths, sid=sid, noise_scale=.667, noise_scale_w=0.8,
                                           length_scale=length_scale)[0][0, 0].data.cpu().float().numpy()
                write(out_path, hps_ms.data.sampling_rate, audio)
            except EOFError:
                print(EOFError)
                print('Failed to generate!')
                sys.exit(1)

            print('Successfully saved!')
            ask_if_continue()


        elif choice == 'v':
            # audio_path = input('Path of an audio file to convert:\n')
            print_speakers(hps_ms.speakers)
            audio = utils.load_audio_to_torch(audio_path, hps_ms.data.sampling_rate)

            originnal_id = get_speaker_id('Original speaker ID: ')
            target_id = get_speaker_id('Target speaker ID: ')
            # out_path = input('Path to save: ')

            y = audio.unsqueeze(0)

            spec = spectrogram_torch(y, hps_ms.data.filter_length,
                                     hps_ms.data.sampling_rate, hps_ms.data.hop_length, hps_ms.data.win_length,
                                     center=False)
            spec_lengths = LongTensor([spec.size(-1)])
            sid_src = LongTensor([originnal_id])

            try:
                with no_grad():
                    sid_tgt = LongTensor([target_id])
                    audio = net_g_ms.voice_conversion(spec, spec_lengths, sid_src=sid_src, sid_tgt=sid_tgt)[0][
                        0, 0].data.cpu().float().numpy()
                write(out_path, hps_ms.data.sampling_rate, audio)
            except:
                print('Failed to generate!')
                sys.exit(1)

            print('Successfully saved!')
            ask_if_continue()


if __name__ == '__main__':
    model = "model/1374_epochs.pth"
    config = "config/config.json"
    choice = "t"
    text = "[ZH]风萧萧兮易水寒[ZH]"
    # text = "[JA]風蕭蕭として易水寒[JA]"
    out_path = "save/TTS/read.wav"
    speaker_id = 0
    Interact(text, out_path, speaker_id)
