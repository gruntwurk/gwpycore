from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.properties import ObjectProperty
from kivy.logger import Logger, LOG_LEVELS

from gwpycore import NamedColor

Logger.setLevel(LOG_LEVELS["debug"])


class ColorChart(BoxLayout):
    chart: ObjectProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.populate()

    def populate(self):
        count = len(NamedColor)
        self.chart.rows = int(count / self.chart.cols) + 2
        for color in NamedColor:
            b = Button(text=color.name,
                       color=color.subdued().float_tuple(),
                       background_normal='',
                       background_color=color.float_tuple())
            self.chart.add_widget(b)


class ColorChartApp(App):
    def build(self):
        return ColorChart()


    # def on_start(self):
    #     Logger.debug(f"root = {self.root}")
    #     self.root.add_widget()


def main():
    app = ColorChartApp()
    app.run()


if __name__ == '__main__':
    main()
