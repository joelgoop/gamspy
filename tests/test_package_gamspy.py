import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
import pytest
from gamspy.examples import TransportModel
from gamspy.utils import make_tmp_dir

class TestExample:
    def test_example(self):
        with make_tmp_dir() as d:
            ex = TransportModel(d)
            ex.run()
            assert ex.get_shipping_flows() == {
                                    ('san-diego', 'topeka'): 275.0,
                                    ('seattle', 'topeka'): 0.0,
                                    ('san-diego', 'new-york'): 275.0,
                                    ('seattle', 'new-york'): 50.0,
                                    ('san-diego', 'chicago'): 0.0,
                                    ('seattle', 'chicago'): 300.0
                                }
            assert ex.get_tot_cost() == 153.675

