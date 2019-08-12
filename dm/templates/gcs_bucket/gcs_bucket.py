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
""" This template creates a Google Cloud Storage bucket. """


def generate_config(context):
    """ Entry point for the deployment resources. """

    resources = []
    project_id = context.env['project']
    bucket_name = context.properties.get('name', context.env['name'])

    # output variables
    bucket_selflink = '$(ref.{}.selfLink)'.format(bucket_name)
    bucket_uri = 'gs://' + bucket_name + '/'

    bucket = {
        'name': bucket_name,
        'type': 'storage.v1.bucket',
        'properties': {
            'project': project_id,
            'name': bucket_name
        }
    }

    # WARNING: USING ANY OF THESE MAY BREAK YOUR BUCKET!
    # They are applied using the bucket UPDATE API, which can strip IAMs if changes
    # are made here, but not in IAMs.
    optional_props = [
        'billing',
        'location',
        'versioning',
        'storageClass',
        'predefinedAcl',
        'predefinedDefaultObjectAcl',
        'logging',
        'lifecycle',
        'labels',
        'website',
    ]

    for prop in optional_props:
        if prop in context.properties:
            bucket['properties'][prop] = context.properties[prop]

    resources.append(bucket)

    # If IAM policy bindings are defined, apply these bindings.
    storage_provider_type = 'gcp-types/storage-v1:storage.buckets.setIamPolicy'
    bindings = context.properties.get('bindings', [])
    if bindings:
        iam_policy = {
            'name': bucket_name + '-iampolicy',
            'action': (storage_provider_type),
            'properties':
                {
                    'bucket': '$(ref.' + bucket_name + '.name)',
                    'project': project_id,
                    'bindings': bindings
                }
        }
        resources.append(iam_policy)

    # If CORS provided, configure it separately using the PATCH API
    # ref: https://cloud.google.com/storage/docs/json_api/v1/buckets/patch
    storage_provider_type_patch = 'gcp-types/storage-v1:storage.buckets.patch'
    cors = context.properties.get('cors', [])
    if cors:
        cors_patch = {
            'name': bucket_name + '-cors-patch',
            'action': (storage_provider_type_patch),
            'properties': {
                'bucket': '$(ref.' + bucket_name + '.name)',
                'project': project_id,
                'cors': cors
            }
        }
        resources.append(cors_patch)

    return {
        'resources':
            resources,
        'outputs':
            [
                {
                    'name': 'name',
                    'value': bucket_name
                },
                {
                    'name': 'selfLink',
                    'value': bucket_selflink
                },
                {
                    'name': 'url',
                    'value': bucket_uri
                }
            ]
    }
