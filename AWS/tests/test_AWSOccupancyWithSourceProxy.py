import pandas as pd
import mock
import datetime
import boto3
import numpy

import utils
import decisionengine.framework.modules.SourceProxy as SourceProxy
import decisionengine_modules.AWS.sources.AWSOccupancyWithSourceProxy as Occupancy

config={"channel_name": "channel_aws_config_data",
                               "Dataproducts":["spot_occupancy_config"],
                               "retries": 3,
                               "retry_timeout": 20,
    }

account = {'spot_occupancy_config': pd.read_csv('occupancy_config.csv')}

expected_pandas_df = pd.read_csv('AWSOcupancyWithSourceProxy_expected_acquire.csv')

produces = ['AWS_Occupancy']

class SessionMock(object):
    def resource(self, service = None, region_name = None):
        return None
                    
class TestAWSOccupancyWithSourceProxy:
    def test_produces(self):
        aws_occ = Occupancy.AWSOccupancy(config)
        assert (aws_occ.produces() == produces)
    
    def test_acquire(self):
        aws_occ = Occupancy.AWSOccupancy(config)
        with mock.patch.object(SourceProxy.SourceProxy, 'acquire') as acquire:
            acquire.return_value = account
            with mock.patch.object(boto3.session, 'Session') as s:
                s.return_value = SessionMock()
                with mock.patch.object(Occupancy.OccupancyForRegion, 'get_ec2_instances') as get_instances:
                    cap = utils.input_from_file('occupancy.fixture')
                    get_instances.return_value = cap
                    res = aws_occ.acquire()
                    assert produces == res.keys()
                    df1 = expected_pandas_df.sort_values(['AvailabilityZone', 'InstanceType'])
                    new_df = res.get(produces[0]).sort_values(['AvailabilityZone', 'InstanceType'])
                    assert utils.compare_dfs(df1, new_df)
