#!/usr/bin/env python
# wujian@2018

import os
import tqdm
import argparse
import random

import numpy as np

from audio import WaveReader
from utils import get_logger, write_wav

logger = get_logger(__name__)


def signal_power(signal, dim=0):
    """
    Compute signal power:
        P = \sum_{n=0}^{T-1} s[n]^2 / T
    And:
        E = \sum_{n=0}^{T-1} s[n]^2
    """
    if signal.ndim != 1:
        raise RuntimeError("Input signal is expected to be a vector")
    if not dim:
        return np.linalg.norm(signal, 2)**2 / signal.size
    else:
        return np.linalg.norm(signal, 2)**2 / dim


def sample_spks(reader, num_spks, min_dur=0):
    """
    Sample num_spks from reader
    """
    num_done = 0
    keys = reader.index_keys
    fs = reader.samp_rate
    spks = []
    srcs = []
    nsamps = []
    while num_done < num_spks:
        key = random.sample(keys, 1)[0]
        wav = reader[key]
        spkid = key.split("-")[0]
        # spk not repeat && long enough
        if spkid not in spks and wav.size / fs > min_dur:
            num_done += 1
            spks.append(spkid)
            srcs.append({
                "key": key,
                "wav": wav,
                "pow": signal_power(wav),
                "dur": wav.size
            })
            nsamps.append(wav.size)
    return min(nsamps), srcs


def run(args):
    min_sdr, max_sdr = list(map(float, args.sdr.split(",")))
    wav_reader = WaveReader(args.wav_scp, sample_rate=args.fs)

    logger.info(
        "Start simulate {:d} utterances from {}, with sdr = {} ...".format(
            args.num_utts, args.wav_scp, args.sdr))
    statsf = open(args.simu_stats, "w") if args.simu_stats else None
    # 640 = 0.04 * 16000
    frame_shift = int(args.fs * args.shift)
    for _ in tqdm.trange(args.num_utts):
        # list of dict object
        min_dur, spks = sample_spks(wav_reader, args.num_spks, args.min_dur)

        mixture = np.zeros(min_dur)
        # treat first speaker as target
        ref_pow = spks[0]["pow"]
        ref_dur = spks[0]["dur"]
        ref_spk = spks[0]["wav"]

        stats = []
        # shift for target video
        shift = random.randint(0, (ref_dur - min_dur) // frame_shift)
        stats.append((spks[0]["key"], shift))
        # target segment
        segment = ref_spk[shift * frame_shift:shift * frame_shift + min_dur]
        mixture += segment
        # interference speakers
        sdrs = []
        infs = []
        for spk in spks[1:]:
            sdr_db = random.uniform(min_sdr, max_sdr)
            scaler = np.sqrt(ref_pow / spk["pow"] * 10**(-sdr_db / 10))
            # video shift
            shift = random.randint(0, (spk["dur"] - min_dur) // frame_shift)
            stats.append((spk["key"], shift))
            # mixture
            spkseg = spk["wav"][shift * frame_shift:shift * frame_shift +
                                min_dur]
            mixture += scaler * spkseg
            infs.append(scaler * spkseg)
            sdrs.append("{:+.2f}".format(sdr_db))

        uttid = "{0}_{1}".format("_".join([d["key"] for d in spks]),
                                 "_".join(sdrs))
        scaler = random.uniform(0.6, 0.9) / np.linalg.norm(mixture, np.inf)

        write_wav(
            os.path.join(args.dump_dir, "mix/{}.wav".format(uttid)),
            mixture * scaler,
            fs=args.fs)
        write_wav(
            os.path.join(args.dump_dir, "spk1/{}.wav".format(uttid)),
            segment * scaler,
            fs=args.fs)

        if not args.target_only:
            for idx, spk in enumerate(infs):
                write_wav(
                    os.path.join(args.dump_dir, "spk{}/{}.wav".format(
                        idx + 2, uttid)),
                    spk * scaler,
                    fs=args.fs)

        if statsf:
            record = uttid
            for pair in stats:
                record += " {0} {1}".format(pair[0], pair[1])
            statsf.write("{}\n".format(record))

    if statsf:
        statsf.close()
    logger.info(
        "Start simulate {:d} utterances from {}, with sdr = {} done".format(
            args.num_utts, args.wav_scp, args.sdr))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Command to create mixture data for LRS2 dataset")
    parser.add_argument(
        "wav_scp",
        type=str,
        help="Source wave rspecifier for mixture simulation")
    parser.add_argument(
        "--shift",
        type=float,
        default=0.04,
        help="Frame shift in seconds, keep same as video's fps")
    parser.add_argument(
        "--sdr",
        type=str,
        default="-5,5",
        help="Range of sdr for speaker mixture")
    parser.add_argument(
        "--num-utts",
        required=True,
        type=int,
        help="Number of utterance to generate")
    parser.add_argument(
        "--num-spks",
        type=int,
        default=2,
        help="Number of speakers to mixture per utterance")
    parser.add_argument(
        "--simu-stats",
        type=str,
        default="",
        help="If assigned, generate statistics during data simulation")
    parser.add_argument(
        "--min-dur",
        type=float,
        default=0,
        help="Minimum durations for each utterances")
    parser.add_argument(
        "--fs", type=float, default=16000, help="Sample rate for raw waveform")
    parser.add_argument(
        "--dump-dir",
        type=str,
        default="simu_av",
        help="Directory to dump simulated data")
    parser.add_argument(
        "--target-only",
        action="store_true",
        help="If true, dump target speakers only")
    args = parser.parse_args()
    run(args)
