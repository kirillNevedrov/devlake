/*
 * Licensed to the Apache Software Foundation (ASF) under one or more
 * contributor license agreements.  See the NOTICE file distributed with
 * this work for additional information regarding copyright ownership.
 * The ASF licenses this file to You under the Apache License, Version 2.0
 * (the "License"); you may not use this file except in compliance with
 * the License.  You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 *
 */

import { IPluginConfig } from '@/types';

import Icon from './assets/icon.svg?react';

export const ClickUpConfig: IPluginConfig = {
  plugin: 'clickup',
  name: 'ClickUp',
  icon: ({ color }) => <Icon fill={color} />,
  sort: 13.5,
  connection: {
    docLink: 'https://clickup.com/api',
    initialValues: {
      endpoint: 'https://api.clickup.com/api/v2',
    },
    fields: [
      'name',
      {
        key: 'token',
        label: 'API Token',
        subLabel: 'Your ClickUp personal API token (Settings → Apps → API Token).',
      },
      'proxy',
      {
        key: 'rateLimitPerHour',
        subLabel: 'Maximum number of API requests per hour. Leave blank for the default (6000).',
        defaultValue: 6000,
      },
    ],
  },
  dataScope: {
    title: 'Folders',
    millerColumn: {
      columnCount: 2,
      firstColumnTitle: 'Spaces',
    },
    searchPlaceholder: 'Search folders...',
  },
  scopeConfig: {
    entities: ['TICKET', 'CROSS'],
    transformation: {
      issueTypeRequirement: '(feat|feature|story|requirement)',
      issueTypeBug: '(bug|defect|broken)',
      issueTypeIncident: '(incident|outage|failure)',
    },
  },
};
