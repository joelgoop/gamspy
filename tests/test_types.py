import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from gamspy.types import GamspyElementList, GamspyParameter, GamspySet
import pytest

el_names =  ["test1","test2","test3"]
class TestGamspyElementList:
    @pytest.fixture(scope="class",params=[GamspyParameter,GamspySet])
    def element_list(self,request):
        return GamspyElementList([request.param(name) for name in el_names])

    def test_retrieve_by_name_and_index(self,element_list):
        assert element_list[el_names[-1]]==element_list[-1]

    def test_iterate(self,element_list):
        for name,el in zip(el_names,element_list):
            assert name==el.name

    def test_length(self,element_list):
        assert len(element_list)==len(el_names)


class TestGamspyElements:
    @pytest.fixture(scope="class",params=[(10,5,True),(10,5,False)])
    def p_matr(self,request):
        import numpy.random as rnd
        rnd.seed(42)
        m,n,gen_data = request.param
        rows = GamspySet('s_rows',["r{}".format(i) for i in range(m)])
        cols = GamspySet('s_cols',["c{}".format(i) for i in range(n)])
        if gen_data:
            data = rnd.rand(m,n)
            return GamspyParameter('p_matr',data=data,indices=[rows,cols])
        return GamspyParameter('p_matr',indices=[rows,cols])

    def test_parameter_matrix_dim(self,p_matr):
        assert p_matr.ndim==2

    def test_parameter_data_load(self,p_matr):
        assert (p_matr.load and p_matr.data is not None) or \
                    (p_matr.data is None and not p_matr.load)
