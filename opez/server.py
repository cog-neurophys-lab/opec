"""A small test server acting as Open Ephys GUI."""

import numpy as np
import pyzmq

from opez import OpenEphysEvent, OpenEphysContinuousData
from opez.connection import Connection
from opez.messages import HeartBeatMessage, ContinuousDataHeaderMessage
from opez.collector import Collector

import logging
