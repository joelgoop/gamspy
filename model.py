import os
import subprocess as sp
import threading


class GamsModel(object):
    """Class that contains necessary data to run a GAMS model"""
    def __init__(self, gams_dir, model_file, gams_exec='C:/GAMS/win64/23.9/gams.exe', res_file=None):
        super(GamsModel, self).__init__()
        if not os.path.isfile(gams_exec):
            raise ValueError("File {} is not a file.".format(gams_exec))
        self.gams_exec = gams_exec
        self.gams_dir = os.path.abspath(gams_dir)
        self.model_file = model_file
        self.res_file = res_file

    @property
    def results(self):
        return self._results

    def full_file_name(self,f_name):
        return self.gams_dir + '/' + f_name

    # Property containing the model file name
    @property
    def model_file(self):
        return self._model_file

    @model_file.setter
    def model_file(self,value):
        if os.path.isfile(self.gams_dir+'/'+value):
            if 'gms'==os.path.splitext(value)[1][1:]:
                self._model_file = value
            else:
                raise IOError('Model file type is not .gms.\n'+value)
        else:
            raise IOError('Model file does not exist.\n'+value)

    def create_thread(self):
        return threading.Thread(target=self.run_model)

    def run_model(self):
        p = sp.Popen([self.gams_exec,self.model_file],cwd=self.gams_dir)
        # Cannot read output from gams process. Why?? Output is shown when run in cmd
        # while p.poll() is None:
        #     for line in iter(p.stdout.readline, b''):
        #         print line.rstrip()
        p.wait()
        if p.returncode != 0:
            raise Exception("GAMS returned with an error. Return code is {}.".format(p.returncode))


if __name__ == '__main__':
    m = GamsModel(gams_dir='D:/git/wedd/gams',model_file='wedd.gms',gams_exec='C:/GAMS/win64/23.8/gams.exe')
    t = m.create_thread()
    t.start()
    t.join()