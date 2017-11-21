# Copyright 2017-present Open Networking Foundation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import sys
from django.db.models import Q, F
from synchronizers.new_base.modelaccessor import *
from synchronizers.new_base.SyncInstanceUsingAnsible import SyncInstanceUsingAnsible

parentdir = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, parentdir)

class SyncVENBServiceInstance(SyncInstanceUsingAnsible):
    observes = VENBServiceInstance
    template_name = "venbserviceinstance_playbook.yaml"
    service_key_name = "/opt/xos/configurations/mcord/mcord_private_key"

    def __init__(self, *args, **kwargs):
        super(SyncVENBServiceInstance, self).__init__(*args, **kwargs)

    def get_service(self, o):
        if not o.owner:
            return None

        service = VENBService.objects.filter(id=o.owner.id)

        if not service:
            return None

        return service[0]

    def get_extra_attributes(self, o):

        fields = {}
        service = self.get_service(o)
        fields['login_user'] = service.login_user
        fields['login_password'] = service.login_password
        fields['venb_s1u_ip'] = self.get_ip_address('s1u_network', VENBServiceInstance, 'venb_s1u_ip')
        fields['venb_s11_ip'] = self.get_ip_address('s11_network', VENBServiceInstance, 'venb_s11_ip')
        fields['vspgwc_s11_ip'] = self.get_ip_address('s11_network', VSPGWCTenant, 'vspgwc_s11_ip')
        fields['venb_sgi_ip'] = self.get_ip_address('sgi_network', VENBServiceInstance, 'venb_sgi_ip')
        fields['vspgwu_sgi_ip'] = self.get_ip_address('sgi_network', VSPGWUTenant, 'vspgwu_sgi_ip')
        fields['venb_management_ip'] = self.get_ip_address('management', VENBServiceInstance, 'venb_management_ip')
        fields['vspgwc_management_ip'] = self.get_ip_address('management', VSPGWCTenant, 'vspgwc_management_ip')
        fields['vspgwu_management_ip'] = self.get_ip_address('management', VSPGWUTenant, 'vspgwu_management_ip')

        return fields

    def get_ip_address(self, network_name, service_instance, parameter):
        try:
            net_id = self.get_network_id(network_name)
            ins_id = service_instance.instance_id
            ip_address = Port.objects.get(network_id=net_id, instance_id=ins_id).ip

        except Exception:
            ip_address = "error"
            self.log.error("Could not fetch parameter", parameter = parameter, network_name = network_name)
            self.defer_sync("Waiting for parmaters to become available")

        return ip_address

    # To get each network id
    def get_network_id(self, network_name):
        return Network.objects.get(name=network_name).id
