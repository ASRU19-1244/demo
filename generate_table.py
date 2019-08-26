#!/usr/bin/env python

# wujian@2019

import glob
import os.path as op


def generate_header(name):
    print("<thead>")
    print("<tr>")
    # print("<tr style=\"border-bottom:1px solid black\">")
    for sstr in name:
        print("<th>{}</th>".format(sstr))
    print("</tr>")
    print("</thead>")


def generate_body(flist, fdir, audio_dir, num_spks):
    print("<tbody>")
    for utt in flist:
        for spkid in range(1, 1 + num_spks):
            if spkid == 1:
                print("<tr style=\"border-top:1px solid black\">")
            else:
                print("<tr>")
            for adir in audio_dir:
                if adir == "mix":
                    if spkid == 1:
                        print(
                            "<td rowspan=\"{0}\"><audio controls class=\"audio-player\" "
                            "preload=\"metadata\" style=\"width: 180px;\"><source "
                            "src=\"{1}/{2}/{3}\" type=\"audio/wav\"></audio></td>"
                            .format(num_spks, fdir, adir, utt))
                else:
                    # ref tas tavs upit favs
                    print(
                        "<td><audio controls class=\"audio-player\" "
                        "preload=\"metadata\" style=\"width: 180px;\"><source "
                        "src=\"{0}/{1}/spk{2}/{3}\" type=\"audio/wav\"></audio></td>"
                        .format(fdir, adir, spkid, utt))
            print("</tr>")
    print("</tbody>")


default_name = [
    "Mixture input", "BLSTM-uPIT", "Conv-TasNet", "Conv-FavsNet", "Proposed",
    "Ground Truth"
]

default_dir = ["mix", "upit", "tas", "favs", "tavs", "ref"]

default_3spk_flist = [
    "6300370419826092098-00001_6340299442417279404-00006_6329151425173313518-00006_-0.16_+3.46.wav",
    "6323817075791736335-00056_6339758276407584924-00082_6306811582279909115-00014_+3.18_-3.56.wav",
    "6328393792942295524-00005_6324764116080445123-00001_6334563083966338309-00106_+0.26_+1.37.wav",
    "6352157417494386368-00051_6316024287129869379-00016_6325894121976022773-00008_+0.42_-0.13.wav",
    "6360322579951237696-00004_6329151425173313518-00062_6309468449049188125-00024_-2.96_+0.98.wav"
]
default_2spk_flist = [
    "6306870852828565379-00004_6306811582279909115-00009_+0.02.wav",
    "6326414672012357313-00085_6323956232732126743-00016_-1.87.wav",
    "6348834401297406331-00002_6311014637275749987-00036_+1.98.wav",
    "6360322579951237696-00006_6327713470253076639-00017_+3.40.wav",
    "6383716407688597209-00035_6326553828952690654-00007_-4.40.wav"
]


def run(fdir, spk_flist, num_spks):
    # print("<table style=\"margin: auto; width: 80%; border-collapse: collapse;\">")
    print("<table>")
    generate_header(default_name)
    generate_body(spk_flist, fdir, default_dir, num_spks)
    print("</table>")


if __name__ == "__main__":
    # run("audio/2spk", default_2spk_flist, 2)
    run("audio/3spk", default_3spk_flist, 3)