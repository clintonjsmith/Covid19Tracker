import json
import datetime
import wget
import os
import requests
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates


class CovidDB:
    def __init__(self, start_date, end_date):
        base_url = 'https://covidtracking.com/api/states/daily?date='
        date = start_date
        self.jsons = []
        self.stats = {}
        while date <= end_date:
            url = base_url + date.strftime("%y%y%m%d")
            myfile = requests.get(url)
            self.jsons += myfile.json()
            date += datetime.timedelta(days=1)

    def get_state_stats(self, state_name):
        index = 0
        buf = 300
        state_stats = {'dates': np.empty([buf,], dtype=np.uint32), 'positives': np.empty(buf, ), 'negatives': np.empty(buf, ),
                 'deaths': np.empty(buf, )}
        for item in self.jsons:
            if item['state'] == state_name:
                try:
                    tdate = str(item['date'])
                    tdate = datetime.datetime.strptime(tdate, '%Y%m%d')
                    state_stats['dates'][index] = mdates.date2num(tdate)
                    state_stats['positives'][index] = item['positive']
                    state_stats['negatives'][index] = item['negative']
                    state_stats['deaths'][index] = item['death']
                    index += 1
                except NameError:
                    print("Undefined variable")
                except:
                    print("something else wrong")

        state_stats['dates'] = state_stats['dates'][:index]
        state_stats['positives'] = state_stats['positives'][:index]
        state_stats['negatives'] = state_stats['negatives'][:index]
        state_stats['deaths'] = state_stats['deaths'][:index]
        state_stats['tests'] = state_stats['positives']+state_stats['negatives']

        self.stats[state_name] = state_stats
        return state_stats

    def plot_state_totals(self, state='all', pop_list=None):
        fig, axs = plt.subplots(2,3,figsize=(20,8))
        if pop_list is None:
            pop_list = np.ones(len(state),)
        if state == 'all':
            pass
        for i, item in enumerate(state):
            axs[0, 0].semilogy(self.stats[item]['dates'], self.stats[item]['tests']/pop_list[i], label=item)
            axs[0, 0].text(self.stats[item]['dates'][-1], self.stats[item]['tests'][-1]/pop_list[i], item)
            axs[0, 1].semilogy(self.stats[item]['dates'], self.stats[item]['positives']/pop_list[i], label=item)
            axs[0, 1].text(self.stats[item]['dates'][-1], self.stats[item]['positives'][-1] / pop_list[i], item)
            axs[0, 2].plot(self.stats[item]['dates'], self.stats[item]['positives']/self.stats[item]['tests'], label=item)
            axs[0, 2].text(self.stats[item]['dates'][-1], self.stats[item]['positives'][-1] / self.stats[item]['tests'][-1],
                           item)

            axs[1, 0].semilogy(self.stats[item]['dates'], self.stats[item]['deaths']/pop_list[i], label=item)
            axs[1, 0].text(self.stats[item]['dates'][-1], self.stats[item]['deaths'][-1] / pop_list[i], item)
            axs[1, 1].plot(self.stats[item]['dates'], self.stats[item]['deaths']/self.stats[item]['positives'], label=item)
            axs[1, 1].text(self.stats[item]['dates'][-1], self.stats[item]['deaths'][-1] / self.stats[item]['positives'][-1],
                           item)
            axs[1, 2].plot(self.stats[item]['dates'], self.stats[item]['deaths']/self.stats[item]['tests'], label=item)
            axs[1, 2].text(self.stats[item]['dates'][-1], self.stats[item]['deaths'][-1] / self.stats[item]['tests'][-1],
                           item)

        axs[0,0].set_title('No. of Tests')
        axs[0,1].set_title('No. of Positives')
        axs[0,2].set_title('Positives/Tests')

        axs[1,0].set_title('No. of Deaths')
        axs[1,1].set_title('Deaths/Positives')
        axs[1,2].set_title('Deaths/Tests')

        fig.autofmt_xdate()
        myFmt = mdates.DateFormatter('%Y-%m-%d')
        axs[1, 0].xaxis.set_major_formatter(myFmt)
        axs[1, 1].xaxis.set_major_formatter(myFmt)
        axs[1, 2].xaxis.set_major_formatter(myFmt)

        for i in range(2):
            for j in range(3):
                axs[i, j].spines["top"].set_visible(False)
                axs[i, j].spines["right"].set_visible(False)

        return fig, axs
    
    
    def plot_state_deltas(self, state='all', pop_list=None):
        fig, axs = plt.subplots(2,3,figsize=(20,8))
        if pop_list is None:
            pop_list = np.ones(len(state),)
        if state == 'all':
            pass
        for i, item in enumerate(state):
            d_tests = self.stats[item]['tests'][1:]-self.stats[item]['tests'][:-1]
            d_positives = self.stats[item]['positives'][1:] - self.stats[item]['positives'][:-1]
            d_deaths = self.stats[item]['deaths'][1:] - self.stats[item]['deaths'][:-1]

            axs[0, 0].plot(self.stats[item]['dates'][1:], d_tests/pop_list[i], marker='.', label=item)
            axs[0, 0].text(self.stats[item]['dates'][-1], d_tests[-1]/pop_list[i], item)
            axs[0, 1].plot(self.stats[item]['dates'][1:], d_positives/pop_list[i], marker='.', label=item)
            axs[0, 1].text(self.stats[item]['dates'][-1], d_positives[-1] / pop_list[i], item)
            axs[0, 2].plot(self.stats[item]['dates'][1:], d_positives/d_tests, marker='.', label=item)
            axs[0, 2].text(self.stats[item]['dates'][-1], d_positives[-1] / d_tests[-1], item)

            axs[1, 0].plot(self.stats[item]['dates'][1:], d_deaths/pop_list[i], marker='.', label=item)
            axs[1, 0].text(self.stats[item]['dates'][-1], d_deaths[-1] / pop_list[i], item)
            axs[1, 1].plot(self.stats[item]['dates'][1:], d_deaths/d_positives, marker='.', label=item)
            axs[1, 1].text(self.stats[item]['dates'][-1], d_deaths[-1] / d_positives[-1], item)
            axs[1, 2].plot(self.stats[item]['dates'][1:], d_deaths/d_tests, marker='.', label=item)
            axs[1, 2].text(self.stats[item]['dates'][-1], d_deaths[-1] / d_tests[-1], item)

        axs[0,0].set_title('Daily No. of Tests')
        axs[0,1].set_title('Daily No. of Positives')
        axs[0,2].set_title('Daily Positives/Tests')

        axs[1,0].set_title('Daily No. of Deaths')
        axs[1,1].set_title('Daily Deaths/Positives')
        axs[1,2].set_title('Daily Deaths/Tests')

        fig.autofmt_xdate()
        myFmt = mdates.DateFormatter('%Y-%m-%d')
        axs[1, 0].xaxis.set_major_formatter(myFmt)
        axs[1, 1].xaxis.set_major_formatter(myFmt)
        axs[1, 2].xaxis.set_major_formatter(myFmt)

        for i in range(2):
            for j in range(3):
                axs[i, j].spines["top"].set_visible(False)
                axs[i, j].spines["right"].set_visible(False)

        return fig, axs

if __name__ == "__main__":
    date = datetime.date(2020, 3, 4)
    end_date = datetime.date(2020, 3, 28)

    DB = CovidDB(start_date=date, end_date=end_date)

    all_states = []
    print(len(DB.jsons))
    print(DB.jsons[0]['state'])

    for i in range(len(DB.jsons)):
        if DB.jsons[i]['state'] not in all_states:
            all_states.append(DB.jsons[i]['state'])
    print(len(all_states))

    for name in all_states:
        DB.get_state_stats(name)

    state_list = ['LA', 'CA', 'NY', 'GA', 'MD']
    pop_list = [4.66E6, 39.56E6, 19.54E6, 10.52E6, 6.043E6]
    #
    # for name in state_list:
    #     DB.get_state_stats(name)
    print(len(DB.stats))
    DB.plot_state_totals(state=all_states)
    DB.plot_state_deltas(state=all_states)
    DB.plot_state_totals(state=state_list, pop_list=pop_list)
    plt.show()
    # url = base_url + date.strftime("%y%y%m%d")
    # print(url)



