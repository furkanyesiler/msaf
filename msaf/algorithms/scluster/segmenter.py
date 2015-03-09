#!/usr/bin/env python
# coding: utf-8
"""
This script identifies the boundaries of a given track using the Spectral
Clustering method published here:

    Mcfee, B., & Ellis, D. P. W. (2014). Analyzing Song Structure with Spectral
    Clustering. In Proc. of the 15th International Society for Music Information
    Retrieval Conference (pp. 405–410). Taipei, Taiwan.

Original code by Brian McFee from:
    https://github.com/bmcfee/laplacian_segmentation
"""

__author__ = "Oriol Nieto"
__copyright__ = "Copyright 2014, Music and Audio Research Lab (MARL)"
__license__ = "GPL"
__version__ = "1.0"
__email__ = "oriol@nyu.edu"

import logging
import main
import numpy as np

import msaf
from msaf.algorithms.interface import SegmenterInterface


class Segmenter(SegmenterInterface):
    def process(self):
        """Main process.
        Returns
        -------
        est_idxs : np.array(N)
            Estimated times for the segment boundaries in frame indeces.
        est_labels : np.array(N-1)
            Estimated labels for the segments.
        """
        # Preprocess to obtain features, times, and input boundary indeces
        F = self._preprocess()

        # Read frame_times
        self.hpcp, self.mfcc, self.tonnetz, beats, dur, self.anal = \
            msaf.io.get_features(self.audio_file, annot_beats=self.annot_beats,
                                 framesync=self.framesync,
                                 pre_features=self.features)
        frame_times = beats
        if self.framesync:
            frame_times = msaf.utils.get_time_frames(dur, self.anal)

        # Brian wants HPCP and MFCC
        # (transosed, because he's that kind of person)
        F = (self.hpcp.T, self.mfcc.T)

        # Do actual segmentation
        est_idxs, est_labels = main.do_segmentation(F, frame_times,
                                                      self.config,
                                                      self.in_bound_idxs)
        assert est_idxs[0] == 0 and est_idxs[-1] == F[0].shape[1] - 1

        # Post process estimations
        est_idxs, est_labels = self._postprocess(est_idxs, est_labels)

        return est_idxs, est_labels
