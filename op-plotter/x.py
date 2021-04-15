import argparse
import csv
import collections
import json
import pprint
from datetime import datetime

from matplotlib import pyplot as plt


class Plotter:
    def __init__(self, conf):
        self.conf = conf
        self.merchant_totals = {}
        self.plots = collections.defaultdict(dict)

    def plot_file(self, plt):
        with open(self.conf.infile) as infile_fp:
            infile_csv = csv.DictReader(infile_fp)
            m = 0
            for row in infile_csv:
                if 'sequential' in row['message']:
                    if not self.conf.include_sequential:
                        continue
                if 'periodic' in row['message']:
                    if not self.conf.include_periodic:
                        continue

                op = row['operation']
                merchant = row['merchantPublicId']
                dt = datetime.fromtimestamp(int(row['timestamp'])/1000).replace(microsecond=0)

                if not op:
                    continue
                if self.conf.start_at and dt < self.conf.start_at:
                    continue
                if self.conf.end_at and dt > self.conf.end_at:
                    continue

                self.merchant_totals[merchant] = self.merchant_totals.get(merchant, 0) + 1
                if self.conf.filter_merchants:
                    if merchant in self.conf.filter_merchants:
                        self.add_row_to_plots(row, dt)
                else:
                    self.add_row_to_plots(row, dt)

        plt.figure(figsize=(20,5))
        plt = self.plot_from_data(plt)
        plt.legend()
        plt.savefig(self.conf.outfile)

    def add_row_to_plots(self, row):
        raise NotImplementedError

    def output_plot(self):
        raise NotImplementedError


class OperationPlotter(Plotter):
    def add_row_to_plots(self, row, dt):
        self.plots[row['operation']][dt] = self.plots[row['operation']].get(dt, 0) + 1

    def plot_from_data(self, plt):
        for op in self.plots:
            plt.plot(self.plots[op].keys(), self.plots[op].values(), label=op)
        return plt


class MerchantPlotter(Plotter):
    def add_row_to_plots(self, row, dt):
        self.plots[row['merchantPublicId']][dt] = self.plots[row['merchantPublicId']].get(dt, 0) + 1

    def plot_from_data(self, plt):
        for merchant in self.plots:
            plt.plot(self.plots[merchant].keys(), self.plots[merchant].values(), label=merchant)
        return plt


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--infile', required=True)
    parser.add_argument('--outfile', required=True)
    parser.add_argument('--start-at', type=datetime.fromisoformat)
    parser.add_argument('--end-at', type=datetime.fromisoformat)
    parser.add_argument('--include-sequential', action='store_true', default=False)
    parser.add_argument('--include-periodic', action='store_true', default=False)
    parser.add_argument('--filter-merchants', nargs='*')
    parser.add_argument('--plot-operations', action='store_true', default=False)
    conf = parser.parse_args()

    plotter = OperationPlotter(conf) if conf.plot_operations else MerchantPlotter(conf)
    plotter.plot_file(plt)
