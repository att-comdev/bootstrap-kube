# Copyright 2018 AT&T Intellectual Property.  All other rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from .. import logging

LOG = logging.getLogger(__name__)


class AgentEngine:
    def __init__(self,
                 *,
                 service_manager,
                 status_manager,
                 expected_services=None):
        if expected_services is None:
            expected_services = ['docker', 'kubelet']
        self.expected_services = expected_services
        self.service_manager = service_manager
        self.status_manager = status_manager

    def report_state(self):
        current_status = self.status_manager.get_current_status()
        for name, status in current_status.get('services', {}).items():
            LOG.info('Current status recorded in Kubernetes: %s = %s', name,
                     status)

        statuses = {}
        for expected_service in self.expected_services:
            status = self.service_manager.get_status(expected_service)
            statuses[expected_service] = status
            LOG.info('%s: %s', expected_service, status)

        self.status_manager.set_service_statuses(statuses)

    def apply(self, object_):
        self._apply_event_for_services(object_.get('services', {}))

        self.report_state()

    def _apply_event_for_services(self, service_config):
        for name, data in service_config.items():
            enabled = data.get('enabled')
            if enabled is None:
                LOG.info('%s status unspecified, taking no action', name)
            elif enabled:
                self.service_manager.set_up(name)
            else:
                self.service_manager.set_down(name)
