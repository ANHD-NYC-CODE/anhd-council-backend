from os import path
import glob
import importlib

# Find all the model names to be imported
modules = glob.glob(path.join(path.dirname(__file__), "*.py"))
names = [path.splitext(path.basename(n))[0] for n in modules]
names = [n for n in names if n != "__init__"]

# Determine the app name assuming appname/models/*.py structure
app = path.basename(path.abspath(path.join(__file__, '..', '..')))

# Import each, assuming that e.g. Mymodel lives in models/mymodel.py
for name in names:
    mpath = "%s.views.%s" % (app, name)
    mo = importlib.import_module(mpath)
    clsname = name
    try:
        globals()[clsname] = mo.__dict__[clsname]
    except KeyError:
        print("No class named %s in %s.py" % (clsname, name))
