"""
Copyright (C) 2016 STFC.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

@author Greg Corbett
"""
__version__ = '1, 4, 0'

# Example output from the provider list on the CMDB
PROVIDERS = {'total_rows': 735,
             'offset': 695,
             'rows': [
                 {'id': '1',
                  'key': ['service'],
                  'value':{
                      'sitename': 'TEST2',
                      'provider_id': 'TEST2',
                      'type': 'cloud'}},
                 {'id': '2',
                  'key': ['service'],
                  'value':{
                      'sitename': 'TEST',
                      'provider_id': 'TEST',
                      'hostname': 'allowed_host.test',
                      'type': 'cloud'}},
                 {'id': '3',
                  'key': ['service'],
                  'value':{
                      'sitename': 'TEST',
                      'provider_id': 'TEST',
                      'hostname': 'allowed_host2.test',
                      'type': 'cloud'}}]}

# An example APEL Cloud Message V0.2
MESSAGE = """APEL-cloud-message: v0.2
VMUUID: TestVM1 2013-02-25 17:37:27+00:00
SiteName: CESGA
MachineName: one-2421
LocalUserId: 19
LocalGroupId: 101
GlobalUserName: NULL
FQAN: NULL
Status: completed
StartTime: 1361813847
EndTime: 1361813870
SuspendDuration: NULL
WallDuration: NULL
CpuDuration: NULL
CpuCount: 1
NetworkType: NULL
NetworkInbound: 0
NetworkOutbound: 0
Memory: 1000
Disk: NULL
StorageRecordId: NULL
ImageId: NULL
CloudType: OpenNebula
%%
VMUUID: TestVM1 2015-06-25 17:37:27+00:00
SiteName: CESGA
MachineName: one-2422
LocalUserId: 13
LocalGroupId: 131
GlobalUserName: NULL
FQAN: NULL
Status: completed
StartTime: 1361413847
EndTime: 1361811870
SuspendDuration: NULL
WallDuration: NULL
CpuDuration: NULL
CpuCount: 1
NetworkType: NULL
NetworkInbound: 0
NetworkOutbound: 0
Memory: 1000
Disk: NULL
StorageRecordId: NULL
ImageId: NULL
CloudType: OpenNebula
%%"""
