import logging
import numpy as np

# import matplotlib
# matplotlib.use('QT4Agg')
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
import opez
import opez.collector
from opez.continuous_data import OpenEphysContinuousData
from opez.events import OpenEphysEvent, OpenEphysSpikeEvent

logger = logging.getLogger("SimplePlotter")


class SimpleCollector(opez.collector.CollectorInterface):
    """Simple collector for a single channel that rolls existing data backwards."""

    continuous_data: np.ndarray
    added_samples: int = 0
    buffer_size: int

    def __init__(self, buffer_size: int = 10000):
        self.buffer_size = buffer_size
        self.continuous_data = np.empty(buffer_size, dtype=np.float32)

    def add_continuous_data(self, data: OpenEphysContinuousData):
        pass

    def get_continuous_data(self) -> OpenEphysContinuousData | np.ndarray:
        return self.continuous_data

    def add_spike(self, spike: OpenEphysSpikeEvent):
        pass

    def add_ttl(self, ttl: OpenEphysEvent):
        pass

    def add_event(self, event: OpenEphysEvent):
        pass

    def collect_data(
        self, data: OpenEphysContinuousData | OpenEphysSpikeEvent | OpenEphysEvent
    ):
        if isinstance(data, OpenEphysContinuousData):
            # append the data to the end of the buffer using np.roll
            self.continuous_data = np.roll(self.continuous_data, -data.array.size)
            self.continuous_data[-data.array.size :] = data.array
            self.added_samples += data.array.size
        elif isinstance(data, OpenEphysSpikeEvent):
            pass
        elif isinstance(data, OpenEphysEvent):
            pass

    def keep_last(self, seconds: float | None = None, samples: int | None = None):
        pass


class SimplePlotter:

    def __init__(self, sampling_rate):
        """
        :param sampling_rate: the sampling rate of the process
        :return: None
        Here all the configuration detail that is available during
        initialization. However, no matplotlib object should be defined in
        here because they can't be pickled and sent it
        through the process borders. The constructor gets called in the
        """

        logger.info("Init SimplePlotter")
        self.app_name = "Plot Process"
        self.client = opez.Client(app_name=self.app_name)
        self.collector = SimpleCollector(buffer_size=40000)
        logger.info("Client created")
        self.y = np.empty(
            self.collector.buffer_size, dtype=np.float32
        )  # the buffer for the data
        self.sampling_rate = sampling_rate
        self.app_name = "Simple Plotter"
        self.selected_channel = 0

        # matplotlib members, initialized to None
        self.ax = None
        self.hl = None
        self.figure = None
        self.num_samples = 0
        self.code = 0

    def __del__(self):
        logger.info("SimplePlotter deleted")
        del self.client

    def startup(self):
        # build the plot
        ylim0 = 200
        logger.info("Init axes")
        self.figure, self.ax = plt.subplots()
        plt.subplots_adjust(left=0.1, bottom=0.2)
        self.ax.set_facecolor("#001230")
        axcolor = "lightgoldenrodyellow"
        axylim = plt.axes([0.1, 0.05, 0.65, 0.03], facecolor=axcolor)
        sylim = Slider(axylim, "Ylim", 1, 600, valinit=ylim0)

        # noinspection PyUnusedLocal
        def update(val):
            yl = sylim.val
            self.ax.set_ylim(-yl, yl)
            plt.draw()

        sylim.on_changed(update)

        (self.hl,) = self.ax.plot([], [])
        self.hl.set_color("#d92eab")
        self.hl.set_linewidth(0.5)
        self.ax.set_autoscaley_on(True)
        self.ax.margins(y=0.1)
        self.ax.set_xlim(0.0, 1)
        self.ax.set_ylim(-ylim0, ylim0)
        # initialize timer
        timer = self.figure.canvas.new_timer(
            interval=20,
        )
        timer.add_callback(self.callback)
        timer.start()
        plt.show(block=True)

    def update_plot(self, n_arr):

        logger.info("update_plot")
        events = []
        self.y = n_arr

        # update the plot
        x = np.arange(self.y.size, dtype=np.float32) * 1000.0 / self.sampling_rate
        self.hl.set_ydata(self.y)
        self.hl.set_xdata(x)
        self.ax.set_xlim(0.0, x[-1])
        self.ax.relim()
        self.ax.autoscale_view(True, True, False)
        self.figure.canvas.draw()
        self.figure.canvas.flush_events()

        return events

    def callback(self):

        data = self.client.update()
        while data is not None and self.collector.added_samples < 10000:
            data = self.client.update()
            if (
                data is not None
                and isinstance(data, OpenEphysContinuousData)
                and data.header.content.channel_num == self.selected_channel
            ):
                self.collector.collect_data(data)

        self.collector.added_samples = 0

        self.update_plot(self.collector.get_continuous_data())

        return True


if __name__ == "__main__":
    logging.basicConfig(encoding="utf-8", level=logging.INFO)
    plotter = SimplePlotter(40000)
    plotter.startup()
