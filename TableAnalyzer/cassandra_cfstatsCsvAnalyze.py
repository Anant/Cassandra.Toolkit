#!/usr/bin/python
import csv
import sys
import pandas as pd
import numpy as np
# import matplotlib.pyplot as plt
import statistics
import json
import argparse


def endStats(path, save):
    data_issues = []
    data_empty = []
    data_all = []

    csv_columns = ['Hostname', 'Keyspace', 'Table', 'Stats', 'Value', 'Timestamp']
    df_columns = ['Keyspace', 'Table', 'Stats', 'Value_Mean', 'Value_Variance', 'Value_Standard_Deviation']
    df = pd.read_csv(path, names=csv_columns)
    del df['Timestamp']

    ar_keyspaces = df["Keyspace"].unique()
    ar_stats = df["Stats"].unique()
    ar_hosts = df["Hostname"].unique()
    ar_tables = df["Table"].unique()

    ar_stat_cols = ['Hostname', 'Keyspace', 'Table']
    ar_stat_cols += df["Stats"].unique().tolist()

    ar_stat_skew_cols = ['SpaceUsedLive', 'NumberOfKeys']
    ar_stat_wide_cols = ['CompactedPartitionMaximumBytes']
    ar_stat_tomb_cols = ['AverageTombstones', 'MaximumTombstones']
    ar_stat_prob_cols = ar_stat_skew_cols + ar_stat_wide_cols + ar_stat_tomb_cols

    df_pivot = pd.DataFrame(columns=ar_stat_cols)

    pivot_index = 0

    for keyspace in ar_keyspaces:
        df_keyspace_data = df[df['Keyspace'] == keyspace]
        ar_tables = df_keyspace_data["Table"].unique()

        for table in ar_tables:
            df_table_data = df_keyspace_data[
                (df_keyspace_data['Table'] != 'keyspace') & (df_keyspace_data['Table'] == table) & (
                            df_keyspace_data['Keyspace'] == keyspace)]
            ar_stats = df_table_data["Stats"].unique()
            for stat in ar_stats:
                df_stat_data = df_table_data[(df_table_data['Table'] == table) & (df_table_data['Stats'] == stat)]
                values = []
                if len(df_stat_data['Value']) > 1:
                    for i in range(0, len(df_stat_data['Value'])):
                        val = str(list(df_stat_data['Value'].items())[i][0])
                        if (val == "NaN") | (val == "nan") | (val == " "):
                            values.append(0)
                        else:
                            values.append(int(val))
                    value_stdev = statistics.stdev(values)
                    value_mean = statistics.mean(values)
                    value_variance = statistics.variance(values, value_mean)
                else:
                    value_stdev = 0
                    value_mean = 0
                    value_variance = 0
                value_data = [keyspace, table, stat, value_mean, value_variance, value_stdev]
                if (value_mean != 0):
                    value_stdbymean = value_stdev / value_mean
                else:
                    value_stdbymean = 0;

                # & (value_stdbymean>1.2)
                if ((value_stdev != 0) & (value_mean != 0)):
                    data_issues.append(value_data)
                elif ((value_stdev == 0) & (value_mean == 0)):
                    data_empty.append(value_data)

                data_all.append(value_data)

            for host in ar_hosts:
                s_host_data = pd.Series({'Hostname': host, 'Keyspace': keyspace, 'Table': table})
                for stat in ar_stats:
                    df_host_data = \
                    df_table_data[(df_table_data['Hostname'] == host) & (df_table_data['Stats'] == stat)]['Value']
                   # s_host_data = s_host_data.set_value(stat, df_host_data.iloc[0])
                    s_host_data.at[stat] = df_host_data.iloc[0]
                if (table != 'keyspace'):
                    df_pivot.loc[pivot_index] = s_host_data
                    pivot_index = pivot_index + 1

    if len(data_issues):
        df_issues = pd.DataFrame(data=data_issues, columns=df_columns)
    df_empty = pd.DataFrame(data=data_empty, columns=df_columns)
    df_all = pd.DataFrame(data=data_all, columns=df_columns)

    df_all.to_csv("{}.all.csv".format(save))
    df_empty.to_csv("{}.empty.csv".format(save))
    if len(data_issues):
        df_issues.to_csv("{}.issues.csv".format(save))
    df_pivot.to_csv("{}.pivot.csv".format(save))
    df_pivot["eventType"] = "TableStats"
    df_pivot.to_json("{}.pivot.json".format(save), orient='records')
    return True


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Pivoting The Data',
        usage='{path} {save}')
    parser.add_argument('path', type=str, help='Path of CSV file of Stats')
    parser.add_argument('save', type=str, help='Path of file to save [Without Extension]')
    args = parser.parse_args()
    if endStats(args.path, args.save):
        print("Success.")
