from os.path import exists

class Functioner(object):

    def load(self):
        while True:
            infile = input("File name:\n> ")
            if not exists(infile):
                print("File not found. Try again.")
            else:
                break
        return infile
            
    def check_load(self, which, datatype):
        if which == None:
            print(f"Load {datatype} first.")
            return 1
        else:
            return 0
        
    def save_filename(self):
        while True:
            sv_filename = input("Input filename to write:\n> ")
            if exists(sv_filename):
                if input("File already exists. Overwrite? y\\n\n> ") == 'y':
                    break
            else:
                break        
        return sv_filename

    def check_unsaved(self, datatype):
        if self.unsaved == 0:
            print(f"{datatype} has no unsaved changes.")
            return 1
    def int_it(self, inp):
        while True:
            try:
                intp = int(inp)
                return intp
            except:
                print(f"{inp} is not an integer, please correct:")
                inp = input("> ")
