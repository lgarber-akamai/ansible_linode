#!/usr/bin/python
# -*- coding: utf-8 -*-

"""This module contains all of the functionality for Linode NodeBalancers."""

from __future__ import absolute_import, division, print_function

from typing import Optional, cast, Any, List, Set, Tuple

import linode_api4

from ansible_collections.linode.cloud.plugins.module_utils.linode_helper import \
    paginated_list_to_json, dict_select_matching, filter_null_values

from ansible_collections.linode.cloud.plugins.module_utils.linode_common import LinodeModuleBase

# pylint: disable=unused-import
from linode_api4 import NodeBalancer, NodeBalancerConfig, NodeBalancerNode, PaginatedList

ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'supported_by': 'Linode'
}

DOCUMENTATION = '''
---
module: nodebalancer
description: Manage Linode NodeBalancers.
requirements:
  - python >= 2.7
  - linode_api4 >= 3.0
author:
  - Luke Murphy (@decentral1se)
  - Charles Kenney (@charliekenney23)
  - Phillip Campbell (@phillc)
  - Lena Garber (@lbgarber)
options:
  label:
    description:
      - The unique label to give this NodeBalancer
    required: true
    type: string
  region:
    description:
      - The location to deploy the instance in.
      - See U(https://api.linode.com/v4/regions)
    required: true
    type: str

  configs:
    description:
      - A list of configs to be added to the NodeBalancer.
    required: false
    type: list
    elements: dict
    suboptions:
      algorithm:
        description:
          - What algorithm this NodeBalancer should use for routing traffic to backends.
        choices:
          - roundrobin
          - leastconn
          - source
        type: str

      check:
        description:
          - The type of check to perform against backends to ensure they are serving requests.
          - This is used to determine if backends are up or down.
        choices:
          - none
          - connection
          - http
          - http_body
        type: str

      check_attempts:
        description:
          - How many times to attempt a check before considering a backend to be down.
        type: int

      check_body:
        description:
          - This value must be present in the response body of the check in order for it to pass.
          - If this value is not present in the response body of a check request, the backend is considered to be down.
        type: str

      check_interval:
        description:
          - How often, in seconds, to check that backends are up and serving requests.
        type: int

      check_passive:
        description:
          - If true, any response from this backend with a 5xx status code will be enough for it to be considered unhealthy and taken out of rotation.
        type: bool

      check_path:
        description:
          - The URL path to check on each backend. If the backend does not respond to this request it is considered to be down.
        type: str

      check_timeout:
        description:
          - How long, in seconds, to wait for a check attempt before considering it failed.
        type: int

      cipher_suite:
        description:
          - What ciphers to use for SSL connections served by this NodeBalancer.
          - C(legacy) is considered insecure and should only be used if necessary.
        choices:
          - recommended
          - legacy
        default: recommended
        type: str

      port:
        description:
          - The port for the Config to listen on.
        type: int

      protocol:
        description:
          - The protocol this port is configured to serve.
        choices:
          - http
          - https
          - tcp
        type: str

      proxy_protocol:
        description:
          - ProxyProtocol is a TCP extension that sends initial TCP connection information such as source/destination IPs and ports to backend devices.
        choices:
          - none
          - v1
          - v2
        type: str

      ssl_cert:
        description:
          - The PEM-formatted public SSL certificate (or the combined PEM-formatted SSL certificate and Certificate Authority chain) that should be served on this NodeBalancerConfig’s port.
        type: str

      ssl_key:
        description:
          - The PEM-formatted private key for the SSL certificate set in the ssl_cert field.
        type: str

      stickiness:
        description:
          - Controls how session stickiness is handled on this port.
        choices:
          - none
          - table
          - http_cookie
        type: str

      nodes:
        description:
          - A list of Nodes to be created with the parent Config.
        type: list
        elements: dict
        suboptions:
          label:
            description:
              - The label to give to this Node.
            type: str
            required: true

          address:
            description:
              - The private IP Address where this backend can be reached.
            type: str
            required: true

          mode:
            description:
              - The mode this NodeBalancer should use when sending traffic to this backend.
            choices:
              - accept
              - reject
              - drain
              - backup
            type: str

          weight:
            description:
              - Nodes with a higher weight will receive more traffic.
            type: int
'''

EXAMPLES = '''
- name: Create a Linode NodeBalancer
  linode.cloud.nodebalancer:
    label: my-loadbalancer
    region: us-east
    tags: [ prod-env ]
    state: present
    configs:
      - port: 80
        protocol: http
        algorithm: roundrobin
        nodes:
          - label: node1
            address: 0.0.0.0:80

- name: Delete the NodeBalancer
  linode.cloud.nodebalancer:
    label: my-loadbalancer
    region: us-east
    state: absent
'''

RETURN = '''
nodebalancer:
  description: The NodeBalancer in JSON serialized form.
  linode_api_docs: "https://www.linode.com/docs/api/nodebalancers/#nodebalancer-view__responses"
  returned: always
  type: dict
  sample: {
      "client_conn_throttle": 0,
      "created": "",
      "hostname": "xxxx.newark.nodebalancer.linode.com",
      "id": xxxxxx,
      "ipv4": "xxx.xxx.xxx.xxx",
      "ipv6": "xxxx:xxxx::xxxx:xxxx:xxxx:xxxx",
      "label": "my-loadbalancer",
      "region": "us-east",
      "tags": [

      ],
      "transfer": {
        "in": 0,
        "out": 0,
        "total": 0
      },
      "updated": ""
    }

configs:
  description: A list of configs applied to the NodeBalancer.
  linode_api_docs: "https://www.linode.com/docs/api/nodebalancers/#config-view__responses"
  returned: always
  type: list
  sample: [
      {
        "algorithm": "roundrobin",
        "check": "none",
        "check_attempts": 3,
        "check_body": "",
        "check_interval": 0,
        "check_passive": true,
        "check_path": "",
        "check_timeout": 30,
        "cipher_suite": "recommended",
        "id": xxxxxx,
        "nodebalancer_id": xxxxxx,
        "nodes_status": {
          "down": 1,
          "up": 0
        },
        "port": 80,
        "protocol": "http",
        "proxy_protocol": "none",
        "ssl_cert": null,
        "ssl_commonname": "",
        "ssl_fingerprint": "",
        "ssl_key": null,
        "stickiness": "none"
      }
    ]

nodes:
  description: A list of all nodes associated with the NodeBalancer.
  linode_api_docs: "https://www.linode.com/docs/api/nodebalancers/#node-view__responses"
  returned: always
  type: list
  sample: [
      {
        "address": "xxx.xxx.xxx.xx:80",
        "config_id": xxxxxx,
        "id": xxxxxx,
        "label": "node1",
        "mode": "accept",
        "nodebalancer_id": xxxxxx,
        "status": "Unknown",
        "weight": 1
      }
    ]
'''

linode_nodes_spec = dict(
    label=dict(type='str', required=True),
    address=dict(type='str', required=True),
    weight=dict(type='int', required=False),
    mode=dict(type='str', required=False),
)

linode_configs_spec = dict(
    algorithm=dict(type='str', required=False),
    check=dict(type='str', required=False),
    check_attempts=dict(type='int', required=False),
    check_body=dict(type='str', required=False, default=''),
    check_interval=dict(type='int', required=False),
    check_passive=dict(type='bool', required=False),
    check_path=dict(type='str', required=False),
    check_timeout=dict(type='int', required=False),
    cipher_suite=dict(type='str', required=False, default='recommended'),
    port=dict(type='int', required=False),
    protocol=dict(type='str', required=False),
    proxy_protocol=dict(type='str', required=False),
    ssl_cert=dict(type='str', required=False),
    ssl_key=dict(type='str', required=False),
    stickiness=dict(type='str', required=False),
    nodes=dict(type='list', required=False, elements='dict', options=linode_nodes_spec)
)

linode_nodebalancer_spec = dict(
    client_conn_throttle=dict(type='int'),
    region=dict(type='str'),
    configs=dict(type='list', elements='dict', options=linode_configs_spec)
)

linode_nodebalancer_mutable: Set[str] = {
    'client_conn_throttle',
    'tags'
}


class LinodeNodeBalancer(LinodeModuleBase):
    """Configuration class for Linode NodeBalancer resource"""

    def __init__(self) -> None:
        self.module_arg_spec = linode_nodebalancer_spec
        self.required_one_of = ['state', 'label']
        self.results = dict(
            changed=False,
            actions=[],
            node_balancer=None,
            configs=[],
            nodes=[]
        )

        self._node_balancer: Optional[NodeBalancer] = None

        super().__init__(module_arg_spec=self.module_arg_spec,
                         required_one_of=self.required_one_of)

    def __get_nodebalancer_by_label(self, label: str) -> Optional[NodeBalancer]:
        """Gets the NodeBalancer with the given label"""

        try:
            return self.client.nodebalancers(NodeBalancer.label == label)[0]
        except IndexError:
            return None
        except Exception as exception:
            return self.fail(msg='failed to get nodebalancer {0}: {1}'.format(label, exception))

    def __get_node_by_label(self, config: NodeBalancerConfig, label: str) \
            -> Optional[NodeBalancerNode]:
        """Gets the node within the given config by its label"""
        try:
            return config.nodes(NodeBalancerNode.label == label)[0]
        except IndexError:
            return None
        except Exception as exception:
            return self.fail(msg='failed to get nodebalancer node {0}, {1}'
                             .format(label, exception))

    def __create_nodebalancer(self) -> Optional[NodeBalancer]:
        """Creates a NodeBalancer with the given kwargs"""

        params = self.module.params
        label = params.get('label')
        region = params.get('region')

        try:
            return self.client.nodebalancer_create(region, label=label)
        except Exception as exception:
            return self.fail(msg='failed to create nodebalancer: {0}'.format(exception))

    def __create_config(self, node_balancer: NodeBalancer, config_params: dict) \
            -> Optional[NodeBalancerConfig]:
        """Creates a config with the given kwargs within the given NodeBalancer"""

        try:
            return node_balancer.config_create(None, **config_params)
        except Exception as exception:
            return self.fail(msg='failed to create nodebalancer config: {0}'.format(exception))

    def __create_node(self, config: NodeBalancerConfig, node_params: dict) \
            -> Optional[NodeBalancerNode]:
        """Creates a node with the given kwargs within the given config"""

        label = node_params.pop('label')

        try:
            return config.node_create(label, **node_params)
        except Exception as exception:
            return self.fail(msg='failed to create nodebalancer node: {0}'.format(exception))

    def __create_config_register(self, node_balancer: NodeBalancer, config_params: dict) \
            -> NodeBalancerConfig:
        """Registers a create action for the given config"""

        config = self.__create_config(node_balancer, config_params)
        self.register_action('Created config: {0}'.format(config.id))

        return config

    def __delete_config_register(self, config: NodeBalancerConfig) -> None:
        """Registers a delete action for the given config"""

        self.register_action('Deleted config: {0}'.format(config.id))
        config.delete()

    def __create_node_register(self, config: NodeBalancerConfig, node_params: dict) \
            -> NodeBalancerNode:
        """Registers a create action for the given node"""

        node = self.__create_node(config, node_params)
        self.register_action('Created Node: {0}'.format(node.id))
        cast(list, self.results['nodes']).append(node._raw_json)

        return node

    def __delete_node_register(self, node: NodeBalancerNode) -> None:
        """Registers a delete action for the given node"""

        self.register_action('Deleted Node: {0}'.format(node.id))
        node.delete()

    def __handle_config_nodes(self, config: NodeBalancerConfig, new_nodes: List[dict]) -> None:
        """Updates the NodeBalancer nodes defined in new_nodes within the given config"""

        node_map = {}
        nodes = config.nodes

        for node in nodes:
            node._api_get()
            node_map[node.label] = node

        for node in new_nodes:
            node_label = node.get('label')

            if node_label in node_map:
                node_match, remote_node_match = dict_select_matching(
                    filter_null_values(node), node_map[node_label]._raw_json)

                if node_match == remote_node_match:
                    cast(list, self.results['nodes']).append(node_map[node_label]._raw_json)
                    del node_map[node_label]
                    continue

                self.__delete_node_register(node_map[node_label])

            self.__create_node_register(config, node)

        for node in node_map.values():
            self.__delete_node_register(node)

    @staticmethod
    def __check_config_exists(target: Set[NodeBalancerConfig], config: dict) \
            -> Tuple[bool, Optional[NodeBalancerConfig]]:
        """Returns whether a config exists in the target set"""

        for remote_config in target:
            config_match, remote_config_match = \
                dict_select_matching(filter_null_values(config), remote_config._raw_json)

            if config_match == remote_config_match:
                return True, remote_config

        return False, None

    def __handle_configs(self) -> None:
        """Updates the configs defined in new_configs under this NodeBalancer"""

        new_configs = self.module.params.get('configs') or []
        remote_configs = set(self._node_balancer.configs)

        for config in new_configs:
            config_exists, remote_config = self.__check_config_exists(remote_configs, config)

            if config_exists:
                self.__handle_config_nodes(remote_config, config.get('nodes'))
                remote_configs.remove(remote_config)
                continue

            new_config = self.__create_config_register(self._node_balancer, config)
            self.__handle_config_nodes(new_config, config.get('nodes'))

        # Remove remaining configs
        for config in remote_configs:
            self.__delete_config_register(config)

        cast(list, self.results['configs']) \
            .extend(paginated_list_to_json(self._node_balancer.configs))

    def __update_nodebalancer(self) -> None:
        """Update instance handles all update functionality for the current nodebalancer"""
        should_update = False

        params = filter_null_values(self.module.params)

        # "configs" is defined in NodeBalancer, but is a property method
        if 'configs' in params.keys():
            params.pop('configs')

        for key, new_value in params.items():
            if not hasattr(self._node_balancer, key):
                continue

            old_value = getattr(self._node_balancer, key)

            if isinstance(old_value, linode_api4.objects.linode.Region):
                old_value = old_value.id

            if new_value != old_value:
                if key in linode_nodebalancer_mutable:
                    setattr(self._node_balancer, key, new_value)
                    self.register_action('Updated nodebalancer {0}: "{1}" -> "{2}"'.
                                         format(key, old_value, new_value))

                    should_update = True
                    continue

                self.fail(
                    'failed to update nodebalancer {0}: {1} is a non-updatable field'
                        .format(self._node_balancer.label, key))

        if should_update:
            self._node_balancer.save()

    def __handle_nodebalancer(self) -> None:
        """Updates the NodeBalancer defined in kwargs"""

        nb_label: str = self.module.params.get('label')

        self._node_balancer = self.__get_nodebalancer_by_label(nb_label)

        # Create NodeBalancer if doesn't exist
        if self._node_balancer is None:
            self._node_balancer = self.__create_nodebalancer()
            self.register_action('Created NodeBalancer {}'.format(nb_label))

        if self._node_balancer is None:
            return self.fail('failed to create nodebalancer')

        self.__update_nodebalancer()
        self._node_balancer._api_get()

        self.results['node_balancer'] = self._node_balancer._raw_json

    def __handle_nodebalancer_absent(self) -> None:
        """Updates the NodeBalancer for the absent state"""

        label = self.module.params.get('label')

        self._node_balancer = self.__get_nodebalancer_by_label(label)

        if self._node_balancer is not None:
            self.results['node_balancer'] = self._node_balancer._raw_json
            self._node_balancer.delete()
            self.register_action('Deleted NodeBalancer {}'.format(label))

    def exec_module(self, **kwargs: Any) -> Optional[dict]:
        """Entrypoint for NodeBalancer module"""
        state = kwargs.get('state')

        if state == 'absent':
            self.__handle_nodebalancer_absent()
            return self.results

        self.__handle_nodebalancer()
        self.__handle_configs()

        return self.results


def main() -> None:
    """Constructs and calls the Linode NodeBalancer module"""
    LinodeNodeBalancer()


if __name__ == '__main__':
    main()