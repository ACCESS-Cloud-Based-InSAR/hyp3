from os import environ, path

import pytest
import yaml
from moto import mock_dynamodb2

from dynamo import DYNAMODB_RESOURCE


@pytest.fixture
def table_properties():
    class TableProperties:
        jobs_table = get_table_properties_from_template('JobsTable')
        users_table = get_table_properties_from_template('UsersTable')
        subscriptions_table = get_table_properties_from_template('SubscriptionsTable')
    return TableProperties()


def get_table_properties_from_template(resource_name):
    yaml.SafeLoader.add_multi_constructor('!', lambda loader, suffix, node: None)
    template_file = path.join(path.dirname(__file__), '../apps/main-cf.yml')
    with open(template_file, 'r') as f:
        template = yaml.safe_load(f)
    table_properties = template['Resources'][resource_name]['Properties']
    return table_properties


@pytest.fixture
def tables(table_properties):
    with mock_dynamodb2():
        class Tables:
            jobs_table = DYNAMODB_RESOURCE.create_table(
                TableName=environ['JOBS_TABLE_NAME'],
                **table_properties.jobs_table,
            )
            users_table = DYNAMODB_RESOURCE.create_table(
                TableName=environ['USERS_TABLE_NAME'],
                **table_properties.users_table,
            )
            subscriptions_table = DYNAMODB_RESOURCE.create_table(
                TableName=environ['SUBSCRIPTIONS_TABLE_NAME'],
                **table_properties.subscriptions_table
            )
        tables = Tables()
        yield tables
