import os
import math
import datetime as dt
from platform import platform

import matplotlib
import matplotlib.pyplot as plt

from pvpc_bot.ree.ree_api import ReeAPI
from pvpc_bot.bot.utils.images import get_image_legend, get_image_name, get_image_title
from pvpc_bot.bot.utils.sections import get_section, get_color_info
from pvpc_bot.bot.utils.logs import log
from pvpc_bot.config import (
    DEFAULT_GEOLOCATION, DATETIME_FORMAT, ROUND_DECIMALS, LOW_PERCENTILE, HIGH_PERCENTILE, SECTION_DATA,
    IMAGE_DIR, IMAGE_X_LABEL, IMAGE_Y_LABEL
)


if "macos" in platform().lower():
    matplotlib.use('Agg')


class PriceAnalyzer:
    def __init__(self, date: 'dt.datetime', geolocation: str=DEFAULT_GEOLOCATION):
        self.ree = ReeAPI()
        self.geolocation = geolocation

        self.datetime = date
        self.day = (self.datetime.year, self.datetime.month, self.datetime.day)
        self.data = self._aggregate_data()
    
    def _aggregate_data(self) -> dict:
        def get_geo_id(data):
            for gid in data["indicator"]["geos"]:
                if gid["geo_name"] == self.geolocation:
                    return gid["geo_id"]
        # Get raw data
        prices = self.ree.get_prices(*self.day)
        sections = self.ree.get_sections(*self.day)
        geo_id = get_geo_id(prices)

        # Generate sections dictionary
        sections_dict = {
            section["datetime"]: int(section["value"])
            for section in sections["indicator"]["values"]
            if section["geo_id"] == geo_id
        }

        # Generate the aggregated data
        return [
            {
                # Transform MWh to kWh
                "price": price["value"] / 1000,
                "datetime": dt.datetime.strptime(price["datetime"].split("+")[0], DATETIME_FORMAT),
                "section": sections_dict[price["datetime"]]
            }
            for price in prices["indicator"]["values"]
            if price["geo_id"] == geo_id 
        ]

    def get_percentile(self, percentile: int) -> float:
        index = math.ceil(len(self.data) * (percentile / 100))
        sorted_data = sorted(self.data, key=lambda x: x['price'])
        return round(sorted_data[index]['price'], 5)
    
    def get_mean(self, section: int=None) -> float:
        lst_data = [x['price'] for x in self.data if section is None or x["section"] == section]
        if lst_data:
            mean = sum(lst_data)/len(lst_data)
            return round(mean, ROUND_DECIMALS)
        return 0

    def get_summary(self) -> dict:
        # Construct data
        low_percentile = self.get_percentile(LOW_PERCENTILE)
        high_percentile = self.get_percentile(HIGH_PERCENTILE)
        return {
            "day": dt.datetime(*self.day),
            "mean": self.get_mean(),
            "low_percentile": low_percentile,
            "high_percentile": high_percentile,
            "max": max(self.data, key=lambda x: x["price"]),
            "min": min(self.data, key=lambda x: x["price"]),
            "data": {
                "sections": {
                    **{
                        section_name: {
                            "color": get_color_info(section_id)[2],
                            "mean": self.get_mean(section_id),
                            "prices": [(i, price) for i, price in enumerate(self.data) if price["section"] == section_id]
                        }
                        for section_name, section_id in SECTION_DATA
                    },
                    "list": self.data
                },
                "percentiles": {
                    **{
                        section_name: {
                            "color": get_color_info(section_id)[2],
                            "prices": [(i, price) for i, price in enumerate(self.data) if get_section(price["price"], low_percentile, high_percentile) == section_id]
                        }
                        for section_name, section_id in SECTION_DATA
                    },
                    "list": [{**price, "percentile_section": get_section(price["price"], low_percentile, high_percentile)} for price in self.data]
                }
            }
        }
    
    def generate_png(self, filename: str=None, colors="percentiles") -> str:
        # Get the plot filename
        if filename is None:
            filename = f"{colors}_{get_image_name(self.datetime)}"
        file_path = os.path.join(IMAGE_DIR, filename)

        # Do not create it again if it already exists
        if os.path.exists(file_path):
            return file_path
        
        log(text=f"Gennerating the PNG file '{file_path}'.", level="INFO")
        summary = self.get_summary()

        # Timeline
        time = [i for i in range(len(self.data))]

        # Percentile lines
        for p in ("low_percentile", "high_percentile"):
            log(text=f"Gennerating the PNG file '{file_path}':\np_line={p} p_value={summary[p]}", level="INFO")
            plt.plot(
                time,
                [summary[p] for _ in range(len(self.data))],
                color="black",
                linestyle=':'
            )

        # Electricity price evolution
        log(text=f"Gennerating the PNG file '{file_path}':\nprinting line with {len(self.data)} values.", level="INFO")
        log(text=f"self.data={self.data}", level="INFO")
        plt.plot(time, [price["price"] for price in self.data], color='black', linestyle='-.', linewidth=2, marker='')
        
        # Price data painted by hour sections
        plt_tramo = []
        for section in summary["data"][colors]:
            if section != "list" and summary["data"][colors][section]["prices"]:
                log(text=f"Gennerating the PNG file '{file_path}':\nprinting color {section} with {len(summary['data'][colors][section]['prices'])} values.", level="INFO")
                plt_data, = plt.plot(
                    [t for t, _ in summary["data"][colors][section]["prices"]],
                    [p["price"] for _, p in summary["data"][colors][section]["prices"]],
                    color='black',
                    linestyle='',
                    marker='o',
                    markerfacecolor=summary["data"][colors][section]["color"],
                    markersize=7
                )
                plt_data.set_label(get_image_legend(section, colors))
                plt_tramo.append(plt_data)
        
        # Asthetic
        plt.xlabel(IMAGE_X_LABEL, fontdict={'family':'monospace', 'variant': 'small-caps', 'style': 'italic', 'size':10})
        plt.ylabel(IMAGE_Y_LABEL, fontdict={'family':'monospace', 'variant': 'small-caps', 'style': 'italic', 'size':10, 'verticalalignment': 'baseline'})
        plt.title(get_image_title(self.datetime), fontdict={'family':'monospace', 'variant': 'small-caps', 'style': 'italic', 'size':15})
        plt.legend(handles=plt_tramo)

        # Save the plot
        plt.savefig(file_path)
        return file_path
