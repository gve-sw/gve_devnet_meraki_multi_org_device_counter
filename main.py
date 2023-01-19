""" Copyright (c) 2022 Cisco and/or its affiliates.
This software is licensed to you under the terms of the Cisco Sample
Code License, Version 1.1 (the "License"). You may obtain a copy of the
License at
           https://developer.cisco.com/docs/licenses
All use of the material herein must be in accordance with the terms of
the License. All rights not expressly granted by the License are
reserved. Unless required by applicable law or agreed to separately in
writing, software distributed under the License is distributed on an "AS
IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
or implied.
"""

import meraki
import pprint as pp
import json
import config
import csv
from collections import Counter

# initialize Meraki SDK instance to query API call from the Meraki Dashboard
dashboard = meraki.DashboardAPI(api_key=config.meraki_api_key, print_console=False,output_log=False)

# initialize the different lists that will count the # of device models for every org and the total sum
orgs = []
device_list = []
model_list = []
counter_list = []
switch_total_count = 0
ap_total_count = 0

# read CSV file
with open("orgs.csv") as fp:
    reader = csv.reader(fp, delimiter=",", quotechar='"')
    # next(reader, None)  # skip the headers
    data_read = [row for row in reader]

# grab data from orgs.csv
for index,data in enumerate(data_read):
    if index == 0:
        continue

    org_tuple = (data[0],data[1])
    orgs.append(org_tuple)

# iterate through each Meraki Organization to query the list of devices
for org in orgs:
    devices = dashboard.organizations.getOrganizationDevices(organizationId=org[0],total_pages=-1)
    temp_list = []
    switch_count = 0
    ap_count = 0

    for device in devices:
        if str(device["model"]).startswith("MS"):
            switch_count = switch_count + 1
            switch_total_count = switch_total_count + 1
        elif str(device["model"]).startswith("MR"):
            ap_count = ap_count + 1
            ap_total_count = ap_total_count + 1
        model_list.append(device["model"])
        temp_list.append(device["model"])

    device_counter = dict(Counter(temp_list))
    device_counter["org_id"] = org[0]
    device_counter["org_name"] = org[1]
    device_counter["switch_count"] = switch_count
    device_counter["ap_count"] = ap_count

    print("Counter Org ID " + device_counter["org_id"] + ":")
    print("Counter Org Name " + device_counter["org_name"] + ":")
    pp.pprint(device_counter)
    counter_list.append(device_counter)
    print("=====================")

    device_list = device_list + devices

# use Counter object to count the different models from the list of devices
total_counter = dict(Counter(model_list))

total_counter["org_name"] = "Total"
total_counter["switch_count"] = switch_total_count
total_counter["ap_count"] = ap_total_count
counter_list.append(total_counter)


# create header to save dataset to csv
header = list(total_counter.keys())
#header.append("org_id")
header.insert(0,"org_name")
header.insert(1,"switch_count")
header.insert(2,"ap_count")


# create csv file and dump dataset while inserting None to values that do not exist
with open("output.csv", 'w') as f:
    writer = csv.writer(f)
    writer.writerow(header)
    for d in counter_list:
        writer.writerow([d.get(i, "None") for i in header])