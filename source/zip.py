import zipfile, os
import makefile_plugin.constants

def zip_pvn():
    if not os.path.isdir(os.path.join(os.environ.get('PVN_HOME'), 'plugins')):
        os.makedirs(os.path.join(os.environ.get('PVN_HOME'), 'plugins'))
    zf = zipfile.ZipFile(os.path.join(os.environ.get('PVN_HOME'), 'plugins', 'makefile-plugin_' + makefile_plugin.constants.VERSION + '.zip'), mode='w')
    
    zf.write('__init__.py')
    
    zf.write('makefile_plugin/__init__.py')
    zf.write('makefile_plugin/constants.py')
    zf.write('makefile_plugin/parser.py')
    zf.write('makefile_plugin/makefile.py')
    
if __name__ == '__main__':
    zip_pvn()
