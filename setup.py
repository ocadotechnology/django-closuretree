from distutils.core import setup
from infmis.version import __version__

setup(
    name='django-closuretree',
    version=__version__,
    packages=[root for root,dir,files in  os.walk('closuretree') if '__init__.py' in files]
)
