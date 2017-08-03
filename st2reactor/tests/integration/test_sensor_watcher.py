# Licensed to the StackStorm, Inc ('StackStorm') under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import eventlet
from monotonic import monotonic
from pyrabbit.api import Client

from st2common.services.sensor_watcher import SensorWatcher
from st2tests.base import IntegrationTestCase

__all__ = [
    'SensorWatcherTestCase'
]


class SensorWatcherTestCase(IntegrationTestCase):

    @classmethod
    def setUpClass(cls):
        super(SensorWatcherTestCase, cls).setUpClass()

    def test_sensor_watch_queue_gets_deleted_on_stop(self):

        def create_handler(sensor_db):
            pass

        def update_handler(sensor_db):
            pass

        def delete_handler(sensor_db):
            pass

        sensor_watcher = SensorWatcher(create_handler, update_handler, delete_handler,
                                       queue_suffix='covfefe')
        sensor_watcher.start()
        sw_queues = self._get_sensor_watcher_amqp_queues(queue_name='st2.sensor.watch.covfefe')

        start = monotonic()
        done = False
        while not done:
            eventlet.sleep(0.01)
            sw_queues = self._get_sensor_watcher_amqp_queues(queue_name='st2.sensor.watch.covfefe')
            done = len(sw_queues) > 0 or (monotonic() - start() < 5)

        sensor_watcher.stop()
        print('All queues post SW stop: %s' % sw_queues)
        sw_queues = self._get_sensor_watcher_amqp_queues(queue_name='st2.sensor.watch.covfefe')
        self.assertTrue(len(sw_queues) == 0)

    def _list_amqp_queues(self):
        rabbit_client = Client('localhost:15672', 'guest', 'guest')
        queues = [q['name'] for q in rabbit_client.get_queues()]
        return queues

    def _get_sensor_watcher_amqp_queues(self, queue_name):
        all_queues = self._list_amqp_queues()
        return set(filter(lambda q_name: queue_name in q_name, all_queues))
