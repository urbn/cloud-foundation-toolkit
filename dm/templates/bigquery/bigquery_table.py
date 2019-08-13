# Copyright 2018 Google Inc. All rights reserved.
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

""" This template creates a BigQuery table. """


def generate_config(context):
    """ Entry point for the deployment resources. """

    table_id = context.properties['name']
    name = context.env['name']

    properties = {
        'tableReference':
            {
                'tableId': table_id,
                'datasetId': context.properties['datasetId'],
                'projectId': context.env['project']
            },
        'datasetId': context.properties['datasetId']
    }

    optional_properties = [
        'description',
        'friendlyName',
        'expirationTime',
        'schema',
        'timePartitioning',
        'clustering',
        'view'
    ]

    for prop in optional_properties:
        if prop in context.properties:
            if prop == 'schema':
                properties[prop] = {'fields': context.properties[prop]}
            else:
                properties[prop] = context.properties[prop]

    resources = [
        {
            'type': 'bigquery.v2.table',
            'name': name,
            'properties': properties,
            'metadata': {
                'dependsOn': []  # NB Table dependencies must be added explicitly
            }
        }
    ]

    # Add explicit dependencies for intra-deployment resources
    if 'dependsOn' in context.properties:
        resources[0]['metadata'] = {'dependsOn': context.properties['dependsOn']}

    # Add additional dependencies
    if 'view' in context.properties and \
       'additionalDependencies' in context.properties['view']:
        deps = [
            d['name']
            for d in context.properties['view']['additionalDependencies']
        ]
        resources[0]['metadata']['dependsOn'].extend(deps)

    outputs = [
        {
            'name': 'selfLink',
            'value': '$(ref.{}.selfLink)'.format(name)
        },
        {
            'name': 'etag',
            'value': '$(ref.{}.etag)'.format(name)
        },
        {
            'name': 'creationTime',
            'value': '$(ref.{}.creationTime)'.format(name)
        },
        {
            'name': 'lastModifiedTime',
            'value': '$(ref.{}.lastModifiedTime)'.format(name)
        },
        {
            'name': 'location',
            'value': '$(ref.{}.location)'.format(name)
        },
        {
            'name': 'numBytes',
            'value': '$(ref.{}.numBytes)'.format(name)
        },
        {
            'name': 'numLongTermBytes',
            'value': '$(ref.{}.numLongTermBytes)'.format(name)
        },
        {
            'name': 'numRows',
            'value': '$(ref.{}.numRows)'.format(name)
        },
        {
            'name': 'tableId',
            'value': table_id
        },
        {
            'name': 'type',
            'value': '$(ref.{}.type)'.format(name)
        }
    ]

    return {'resources': resources, 'outputs': outputs}
