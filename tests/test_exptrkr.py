from exptrkr.exptrkr import *
from pathlib import Path
from os import remove

class TestFunctioner(object):
    def setup(self):
        self.fu = Functioner()
        
    def test_load(self, monkeypatch):
        monkeypatch.setattr('builtins.input', lambda *args: 'test_file')
        Path('test_file').touch()
        assert self.fu.load() == 'test_file'
        remove('test_file')

    def test_check_load(self):
        class Tester(Functioner):
            def __init__(self):
                self.test_att = None
        te = Tester()
        assert te.check_load(te.test_att, "") ==  True
        te.test_att = 1
        assert te.check_load(te.test_att, "") ==  False

    def test_save_filename(self, monkeypatch):
        #install mock for easy multiple-input testing
        monkeypatch.setattr('builtins.input', lambda *args: 'test_file')
        assert self.fu.save_filename() == 'test_file'

    def test_check_unsaved(self):
        class Tester(Functioner):
            def __init__(self):
                self.unsaved = 0
        tester = Tester()
        assert tester.check_unsaved('datatype') == True
        tester.unsaved = 1
        assert tester.check_unsaved('datatype') == None
        
    def test_int_it(self, monkeypatch):
        monkeypatch.setattr('builtins.input', lambda *args: 2)
        assert self.fu.int_it(1) == 1
        assert self.fu.int_it('1') == 1
        assert self.fu.int_it('two') == 2

class TestTypedict(object):
    def setup(self):
        #I gotta generate a tester dict...
        self.dict = Typedict(1, 'data/dicts/aw_dict.csv')
    def test_init_0(self):
        self.dict = Typedict(0)
        assert self.dict.name == "New dict"
        assert self.dict.unsaved == 1
        assert self.dict.data.empty == True

    def test_init_1(self):
        assert self.dict.name == 'data/dicts/aw_dict.csv'
        assert self.dict.unsaved == 0
    def test_save(self, monkeypatch):
        self.dict.unsaved = 1
        monkeypatch.setattr('builtins.input', lambda *args: 'test_file')
        self.dict.save()
        assert self.dict.unsaved == 0
        remove('test_file')
    def add_dict(self):
        pass
    def view_typelist(self, capsys):
        self.dict.view_typelist()
        if "Types are" in captured.out:
            val = True
        elif all(i for i in self.dict.data.columns if i in captured.out):
            val = True
        else:
            val = False
        assert captured.out == True
    
